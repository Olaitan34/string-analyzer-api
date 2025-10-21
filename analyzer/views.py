import re
import hashlib
from urllib.parse import unquote
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import StringAnalysis
from .serializers import StringAnalysisSerializer


def parse_natural_language_query(query: str) -> dict:
    """
    Comprehensive natural language query parser for string analysis filters.
    
    Handles ALL these patterns (case-insensitive):
    1. "palindrome" or "palindromic" → is_palindrome=True
    2. "single word" → word_count=1
    3. "X words" or "X word" (where X is a number) → word_count=X
    4. "longer than X characters" → min_length=X+1
    5. "containing letter X" or "contains the letter X" → contains_character=X
    6. "first vowel" → contains_character='a'
    7. "strings containing the letter z" → contains_character='z'
    
    Args:
        query: Natural language query string
        
    Returns:
        Dictionary of parsed filters that can be applied to Django queryset
        Example: {'is_palindrome': True, 'word_count': 1}
        
    Raises:
        ValueError: If query cannot be parsed into any recognizable pattern
        
    Examples:
        >>> parse_natural_language_query("palindrome")
        {'is_palindrome': True}
        
        >>> parse_natural_language_query("single word")
        {'word_count': 1}
        
        >>> parse_natural_language_query("3 words containing letter a")
        {'word_count': 3, 'contains_character': 'a'}
        
        >>> parse_natural_language_query("longer than 5 characters")
        {'min_length': 6}
    """
    filters = {}
    query_lower = query.lower()
    
    # Pattern 1: "palindrome" or "palindromic"
    if re.search(r'\bpalindrom(e|ic|es)?\b', query_lower):
        filters['is_palindrome'] = True
    
    # Pattern 2: "single word"
    if re.search(r'\bsingle\s+word\b', query_lower):
        filters['word_count'] = 1
    
    # Pattern 3: "X words" or "X word" (numeric)
    word_count_match = re.search(r'\b(\d+)\s+words?\b', query_lower)
    if word_count_match:
        filters['word_count'] = int(word_count_match.group(1))
    
    # Pattern 3b: "one word", "two words", etc. (text numbers)
    word_text_map = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
    }
    for word_text, word_num in word_text_map.items():
        if re.search(rf'\b{word_text}\s+words?\b', query_lower):
            filters['word_count'] = word_num
            break
    
    # Pattern 4: "longer than X characters"
    longer_match = re.search(r'\blonger\s+than\s+(\d+)\s+characters?\b', query_lower)
    if longer_match:
        min_length = int(longer_match.group(1)) + 1
        filters['min_length'] = min_length
    
    # Additional: "shorter than X characters"
    shorter_match = re.search(r'\bshorter\s+than\s+(\d+)\s+characters?\b', query_lower)
    if shorter_match:
        max_length = int(shorter_match.group(1)) - 1
        if max_length < 0:
            raise ValueError('Length constraints result in invalid max_length (< 0)')
        filters['max_length'] = max_length
    
    # Additional: "at least X characters"
    at_least_match = re.search(r'\bat\s+least\s+(\d+)\s+characters?\b', query_lower)
    if at_least_match:
        filters['min_length'] = int(at_least_match.group(1))
    
    # Additional: "at most X characters"
    at_most_match = re.search(r'\bat\s+most\s+(\d+)\s+characters?\b', query_lower)
    if at_most_match:
        filters['max_length'] = int(at_most_match.group(1))
    
    # Pattern 5 & 7: "containing letter X" or "contains the letter X"
    # Matches: "containing letter a", "contains the letter z", "strings containing the letter z"
    containing_match = re.search(r'\bcontain(?:ing|s)?\s+(?:the\s+)?(?:letter|character)\s+([a-z])\b', query_lower)
    if containing_match:
        filters['contains_character'] = containing_match.group(1)
    
    # Pattern 6: "first vowel"
    if re.search(r'\bfirst\s+vowel\b', query_lower):
        filters['contains_character'] = 'a'
    
    # Additional vowel patterns
    if re.search(r'\bsecond\s+vowel\b', query_lower):
        filters['contains_character'] = 'e'
    if re.search(r'\bthird\s+vowel\b', query_lower):
        filters['contains_character'] = 'i'
    if re.search(r'\bfourth\s+vowel\b', query_lower):
        filters['contains_character'] = 'o'
    if re.search(r'\bfifth\s+vowel\b', query_lower):
        filters['contains_character'] = 'u'
    
    if not filters:
        raise ValueError(
            'Could not parse any recognizable patterns from the query. '
            'Supported patterns include: "palindrome", "X words", '
            '"longer than X characters", "containing letter X", "first vowel"'
        )
    
    return filters


@method_decorator(csrf_exempt, name='dispatch')
class StringListCreateView(APIView):
    """
    API view to list strings with filtering and create new string analyses.
    
    GET: List all strings with optional filtering
    POST: Create a new string analysis
    """
    
    def get(self, request):
        """
        Handle GET request to retrieve filtered string analyses.
        
        Args:
            request: HTTP request object with query parameters
            
        Returns:
            Response with filtered data, count, and applied filters
        """
        # Start with all objects
        queryset = StringAnalysis.objects.all()
        filters_applied = {}
        errors = {}
        
        # Get query parameters
        is_palindrome = request.query_params.get('is_palindrome')
        min_length = request.query_params.get('min_length')
        max_length = request.query_params.get('max_length')
        word_count = request.query_params.get('word_count')
        contains_character = request.query_params.get('contains_character')
        
        # Validate and apply is_palindrome filter
        if is_palindrome is not None:
            is_palindrome_lower = is_palindrome.lower()
            if is_palindrome_lower in ['true', '1', 'yes']:
                queryset = queryset.filter(is_palindrome=True)
                filters_applied['is_palindrome'] = True
            elif is_palindrome_lower in ['false', '0', 'no']:
                queryset = queryset.filter(is_palindrome=False)
                filters_applied['is_palindrome'] = False
            else:
                errors['is_palindrome'] = 'Must be a boolean value (true/false).'
        
        # Validate and apply min_length filter
        if min_length is not None:
            try:
                min_length_int = int(min_length)
                if min_length_int < 0:
                    errors['min_length'] = 'Must be a non-negative integer.'
                else:
                    queryset = queryset.filter(length__gte=min_length_int)
                    filters_applied['min_length'] = min_length_int
            except ValueError:
                errors['min_length'] = 'Must be a valid integer.'
        
        # Validate and apply max_length filter
        if max_length is not None:
            try:
                max_length_int = int(max_length)
                if max_length_int < 0:
                    errors['max_length'] = 'Must be a non-negative integer.'
                else:
                    queryset = queryset.filter(length__lte=max_length_int)
                    filters_applied['max_length'] = max_length_int
            except ValueError:
                errors['max_length'] = 'Must be a valid integer.'
        
        # Validate min_length <= max_length
        if (min_length is not None and max_length is not None and 
            'min_length' not in errors and 'max_length' not in errors):
            if filters_applied.get('min_length', 0) > filters_applied.get('max_length', 0):
                errors['length_range'] = 'min_length cannot be greater than max_length.'
        
        # Validate and apply word_count filter
        if word_count is not None:
            try:
                word_count_int = int(word_count)
                if word_count_int < 0:
                    errors['word_count'] = 'Must be a non-negative integer.'
                else:
                    queryset = queryset.filter(word_count=word_count_int)
                    filters_applied['word_count'] = word_count_int
            except ValueError:
                errors['word_count'] = 'Must be a valid integer.'
        
        # Validate and apply contains_character filter
        if contains_character is not None:
            if len(contains_character) != 1:
                errors['contains_character'] = 'Must be a single character.'
            else:
                queryset = queryset.filter(value__icontains=contains_character)
                filters_applied['contains_character'] = contains_character
        
        # Return 400 if there are validation errors
        if errors:
            return Response(
                {
                    'error': 'Invalid query parameters',
                    'details': errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Execute query and serialize results
        results = queryset.all()
        serializer = StringAnalysisSerializer(results, many=True)
        
        # Return response with data, count, and applied filters
        return Response(
            {
                'data': serializer.data,
                'count': results.count(),
                'filters_applied': filters_applied
            },
            status=status.HTTP_200_OK
        )
    
    def post(self, request):
        """
        Handle POST request to create a new string analysis.
        
        Args:
            request: HTTP request object with string value
            
        Returns:
            Response with created string analysis data or error
            
        Status Codes:
            - 201 Created: Successfully created new string
            - 400 Bad Request: Missing 'value' field
            - 422 Unprocessable Entity: Invalid data type
            - 409 Conflict: String already exists
        """
        # STEP 1: Check if 'value' field exists in request.data
        if 'value' not in request.data:
            return Response(
                {'error': "Doesn\'t Exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # STEP 2: Check if 'value' is a string type
        value = request.data.get('value')
        if value is None or not isinstance(value, str):
            return Response(
                {'error': "Not A String"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        # STEP 3: Calculate SHA-256 hash for duplicate check
        sha256_hash = hashlib.sha256(value.encode('utf-8')).hexdigest()
        
        # STEP 4: Check if string already exists (duplicate detection)
        if StringAnalysis.objects.filter(sha256_hash=sha256_hash).exists():
            return Response(
                {'error': 'Already Exists'},
                status=status.HTTP_409_CONFLICT
            )
        
        # STEP 5: Use serializer to create object with all calculated properties
        serializer = StringAnalysisSerializer(data=request.data)
        
        if serializer.is_valid():
            # This calls the serializer's create() method which calculates everything
            serializer.save()
            
            # STEP 6: Return 201 Created with serialized data
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # If serializer validation fails (shouldn't happen with our checks above)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@method_decorator(csrf_exempt, name='dispatch')
class StringRetrieveDeleteView(APIView):
    """
    API view to retrieve or delete a specific string analysis by its value.
    
    GET: Retrieve a string analysis
    DELETE: Delete a string analysis
    """
    
    def get(self, request, string_value):
        """
        Handle GET request to retrieve a string analysis.
        
        Args:
            request: HTTP request object
            string_value: URL-encoded string value to retrieve
            
        Returns:
            Response with string analysis data or 404
        """
        # Decode URL-encoded value
        decoded_value = unquote(string_value)
        
        try:
            string_analysis = StringAnalysis.objects.get(value=decoded_value)
            serializer = StringAnalysisSerializer(string_analysis)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except StringAnalysis.DoesNotExist:
            return Response(
                {'error': 'Doesn\'t Exist'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def delete(self, request, string_value):
        """
        Handle DELETE request to remove a string analysis.
        
        Args:
            request: HTTP request object
            string_value: URL-encoded string value to delete
            
        Returns:
            204 No Content on success, 404 if not found
        """
        # Decode URL-encoded value
        decoded_value = unquote(string_value)
        
        try:
            # Look up StringAnalysis by exact value match
            string_analysis = StringAnalysis.objects.get(value=decoded_value)
            
            # Delete the object
            string_analysis.delete()
            
            # Return 204 No Content on success (empty response body)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except StringAnalysis.DoesNotExist:
            # Return 404 if not found
            return Response(
                {'error': 'String does not exist in the system'},
                status=status.HTTP_404_NOT_FOUND
            )


@method_decorator(csrf_exempt, name='dispatch')
class NaturalLanguageFilterView(APIView):
    """
    API view to filter strings using natural language queries.
    
    Query Parameters:
        - query (str): Natural language query to parse into filters
        
    Supported patterns:
        - "single word palindrome" -> word_count=1, is_palindrome=true
        - "longer than X characters" -> min_length=X+1
        - "shorter than X characters" -> max_length=X-1
        - "containing letter X" -> contains_character=X
        - "palindrome" or "palindromic" -> is_palindrome=true
        - "X words" -> word_count=X
        - "X word" -> word_count=X
    """
    
    def get(self, request):
        """
        Handle GET request with natural language query.
        
        Args:
            request: HTTP request object with query parameter
            
        Returns:
            Response with parsed filters and filtered data
            
        Status Codes:
            - 200 OK: Successfully parsed and filtered
            - 400 Bad Request: Unable to parse query
            - 422 Unprocessable Entity: Conflicting filters
        """
        # Step 1: Get the 'query' parameter from request.query_params
        query = request.query_params.get('query', '').strip()
        
        if not query:
            return Response(
                {'error': 'Query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Step 2: Call parse_natural_language_query(query) to get filters
        try:
            filters = parse_natural_language_query(query)
        except ValueError as e:
            # Step 3: If no filters could be parsed, return error
            return Response(
                {'error': 'Unable to parse natural language query'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Step 4: Check for conflicting filters
        validation_error = self._validate_filters(filters)
        if validation_error:
            return Response(
                {
                    'error': 'Conflicting filters detected',
                    'details': validation_error
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        # Step 5: Apply filters to StringAnalysis.objects.filter()
        queryset = StringAnalysis.objects.all()
        queryset = self._apply_filters(queryset, filters)
        
        # Serialize results
        results = queryset.all()
        serializer = StringAnalysisSerializer(results, many=True)
        
        # Step 6: Return response with data, count, and interpreted_query
        return Response(
            {
                'data': serializer.data,
                'count': results.count(),
                'interpreted_query': {
                    'original': query,
                    'parsed_filters': filters
                }
            },
            status=status.HTTP_200_OK
        )
    
    def _validate_filters(self, filters):
        """Validate that filters don't conflict with each other."""
        if 'min_length' in filters and 'max_length' in filters:
            if filters['min_length'] > filters['max_length']:
                return (
                    f"Conflicting length constraints: min_length ({filters['min_length']}) "
                    f"cannot be greater than max_length ({filters['max_length']})"
                )
        
        if 'word_count' in filters and filters['word_count'] < 0:
            return f"Invalid word_count: {filters['word_count']} (must be non-negative)"
        
        if 'min_length' in filters and filters['min_length'] < 0:
            return f"Invalid min_length: {filters['min_length']} (must be non-negative)"
        
        if 'max_length' in filters and filters['max_length'] < 0:
            return f"Invalid max_length: {filters['max_length']} (must be non-negative)"
        
        if 'contains_character' in filters and len(filters['contains_character']) != 1:
            return f"Invalid contains_character: must be a single character"
        
        return None
    
    def _apply_filters(self, queryset, filters):
        """Apply parsed filters to queryset."""
        if 'is_palindrome' in filters:
            queryset = queryset.filter(is_palindrome=filters['is_palindrome'])
        
        if 'min_length' in filters:
            queryset = queryset.filter(length__gte=filters['min_length'])
        
        if 'max_length' in filters:
            queryset = queryset.filter(length__lte=filters['max_length'])
        
        if 'word_count' in filters:
            queryset = queryset.filter(word_count=filters['word_count'])
        
        if 'contains_character' in filters:
            queryset = queryset.filter(value__icontains=filters['contains_character'])
        
        return queryset