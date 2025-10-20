import re
from urllib.parse import unquote
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import StringAnalysis
from .serializers import StringAnalysisSerializer


class CreateStringView(APIView):
    """
    API view to create a new string analysis.
    
    POST: Create a new string analysis
    """
    
    def post(self, request):
        """
        Handle POST request to create a new string analysis.
        
        Args:
            request: HTTP request object with string value
            
        Returns:
            Response with created string analysis data
        """
        serializer = StringAnalysisSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetrieveStringView(APIView):
    """
    API view to retrieve a specific string analysis by its value.
    
    GET: Retrieve a string analysis
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
                {
                    'error': 'String not found',
                    'details': f'No string analysis found with value: {decoded_value}'
                },
                status=status.HTTP_404_NOT_FOUND
            )


class ListStringsView(APIView):
    """
    API view to list and filter string analyses.
    
    Query Parameters:
        - is_palindrome (bool): Filter by palindrome status
        - min_length (int): Minimum string length
        - max_length (int): Maximum string length
        - word_count (int): Filter by exact word count
        - contains_character (str): Filter strings containing this character
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
        """
        query = request.query_params.get('query', '').strip()
        
        if not query:
            return Response(
                {
                    'error': 'Query parameter is required',
                    'details': 'Please provide a natural language query using ?query='
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse the natural language query
        try:
            filters = self._parse_query(query)
        except ValueError as e:
            return Response(
                {
                    'error': 'Unable to parse query',
                    'details': str(e),
                    'query': query
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate filters for conflicts
        validation_error = self._validate_filters(filters)
        if validation_error:
            return Response(
                {
                    'error': 'Conflicting filters detected',
                    'details': validation_error,
                    'parsed_filters': filters,
                    'query': query
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        # Build queryset with parsed filters
        queryset = StringAnalysis.objects.all()
        queryset = self._apply_filters(queryset, filters)
        
        # Serialize results
        results = queryset.all()
        serializer = StringAnalysisSerializer(results, many=True)
        
        return Response(
            {
                'query': query,
                'parsed_filters': filters,
                'data': serializer.data,
                'count': results.count()
            },
            status=status.HTTP_200_OK
        )
    
    def _parse_query(self, query):
        """
        Parse natural language query into filter parameters.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary of parsed filters
            
        Raises:
            ValueError: If query cannot be parsed
        """
        filters = {}
        query_lower = query.lower()
        
        # Pattern: "single word palindrome"
        if re.search(r'\bsingle\s+word\s+palindrom(e|ic)\b', query_lower):
            filters['word_count'] = 1
            filters['is_palindrome'] = True
        
        # Pattern: "palindrome" or "palindromic" (not already matched)
        elif re.search(r'\bpalindrom(e|ic)\b', query_lower):
            filters['is_palindrome'] = True
        
        # Pattern: "longer than X characters"
        longer_match = re.search(r'\blonger\s+than\s+(\d+)\s+characters?\b', query_lower)
        if longer_match:
            min_length = int(longer_match.group(1)) + 1
            filters['min_length'] = min_length
        
        # Pattern: "shorter than X characters"
        shorter_match = re.search(r'\bshorter\s+than\s+(\d+)\s+characters?\b', query_lower)
        if shorter_match:
            max_length = int(shorter_match.group(1)) - 1
            if max_length < 0:
                raise ValueError('Length constraints result in invalid max_length (< 0)')
            filters['max_length'] = max_length
        
        # Pattern: "at least X characters"
        at_least_match = re.search(r'\bat\s+least\s+(\d+)\s+characters?\b', query_lower)
        if at_least_match:
            filters['min_length'] = int(at_least_match.group(1))
        
        # Pattern: "at most X characters"
        at_most_match = re.search(r'\bat\s+most\s+(\d+)\s+characters?\b', query_lower)
        if at_most_match:
            filters['max_length'] = int(at_most_match.group(1))
        
        # Pattern: "containing letter X" or "contains letter X"
        containing_match = re.search(r'\bcontain(ing|s)?\s+(letter|character)\s+([a-z])\b', query_lower)
        if containing_match:
            filters['contains_character'] = containing_match.group(3)
        
        # Pattern: "X words" or "X word"
        word_count_match = re.search(r'\b(\d+)\s+words?\b', query_lower)
        if word_count_match:
            filters['word_count'] = int(word_count_match.group(1))
        
        # Pattern: "one word", "two words", etc.
        word_text_map = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
        for word_text, word_num in word_text_map.items():
            if re.search(rf'\b{word_text}\s+words?\b', query_lower):
                filters['word_count'] = word_num
                break
        
        if not filters:
            raise ValueError(
                'Could not parse any recognizable patterns from the query. '
                'Supported patterns include: "palindrome", "X words", '
                '"longer than X characters", "containing letter X"'
            )
        
        return filters
    
    def _validate_filters(self, filters):
        """
        Validate that filters don't conflict with each other.
        
        Args:
            filters: Dictionary of parsed filters
            
        Returns:
            Error message string if conflict detected, None otherwise
        """
        # Check min_length <= max_length
        if 'min_length' in filters and 'max_length' in filters:
            if filters['min_length'] > filters['max_length']:
                return (
                    f"Conflicting length constraints: min_length ({filters['min_length']}) "
                    f"cannot be greater than max_length ({filters['max_length']})"
                )
        
        # Check word_count conflicts
        if 'word_count' in filters:
            if filters['word_count'] < 0:
                return f"Invalid word_count: {filters['word_count']} (must be non-negative)"
        
        # Check length constraints are non-negative
        if 'min_length' in filters and filters['min_length'] < 0:
            return f"Invalid min_length: {filters['min_length']} (must be non-negative)"
        
        if 'max_length' in filters and filters['max_length'] < 0:
            return f"Invalid max_length: {filters['max_length']} (must be non-negative)"
        
        # Check contains_character is single character
        if 'contains_character' in filters:
            if len(filters['contains_character']) != 1:
                return f"Invalid contains_character: must be a single character"
        
        return None
    
    def _apply_filters(self, queryset, filters):
        """
        Apply parsed filters to queryset.
        
        Args:
            queryset: Django queryset to filter
            filters: Dictionary of filters to apply
            
        Returns:
            Filtered queryset
        """
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


class DeleteStringView(APIView):
    """
    API view to delete a string analysis by its value.
    
    URL Parameters:
        - value (str): The exact string value to delete (URL encoded)
    """
    
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
            
            # Return 204 No Content on success
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except StringAnalysis.DoesNotExist:
            # Return 404 if not found
            return Response(
                {
                    'error': 'String not found',
                    'details': f'No string analysis found with value: {decoded_value}'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except StringAnalysis.MultipleObjectsReturned:
            # Handle edge case where multiple objects have the same value
            # Delete all matching objects
            count = StringAnalysis.objects.filter(value=decoded_value).count()
            StringAnalysis.objects.filter(value=decoded_value).delete()
            
            return Response(
                {
                    'message': f'Deleted {count} string analyses with matching value'
                },
                status=status.HTTP_204_NO_CONTENT
            )
