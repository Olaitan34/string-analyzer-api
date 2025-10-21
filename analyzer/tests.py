from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import StringAnalysis
from .views import parse_natural_language_query


class NaturalLanguageParserTestCase(TestCase):
    """
    Unit tests for parse_natural_language_query function.
    
    Tests each pattern to ensure correct filter dictionary is returned:
    - Single word palindromes
    - Length constraints
    - Character containment
    - Word count
    - Combined patterns
    """
    
    def test_single_word_palindrome(self):
        """
        Test pattern: "all single word palindromic strings"
        
        Expected: {word_count: 1, is_palindrome: True}
        """
        query = "all single word palindromic strings"
        
        result = parse_natural_language_query(query)
        
        # Assert both filters are present
        self.assertIn('word_count', result)
        self.assertIn('is_palindrome', result)
        
        # Assert correct values
        self.assertEqual(result['word_count'], 1)
        self.assertEqual(result['is_palindrome'], True)
    
    def test_longer_than_characters(self):
        """
        Test pattern: "strings longer than 10 characters"
        
        Expected: {min_length: 11}
        """
        query = "strings longer than 10 characters"
        
        result = parse_natural_language_query(query)
        
        # Assert filter is present
        self.assertIn('min_length', result)
        
        # Assert correct value (10 + 1 = 11)
        self.assertEqual(result['min_length'], 11)
    
    def test_palindrome_with_first_vowel(self):
        """
        Test pattern: "palindromic strings that contain the first vowel"
        
        Expected: {is_palindrome: True, contains_character: 'a'}
        """
        query = "palindromic strings that contain the first vowel"
        
        result = parse_natural_language_query(query)
        
        # Assert both filters are present
        self.assertIn('is_palindrome', result)
        self.assertIn('contains_character', result)
        
        # Assert correct values
        self.assertEqual(result['is_palindrome'], True)
        self.assertEqual(result['contains_character'], 'a')
    
    def test_containing_letter_z(self):
        """
        Test pattern: "strings containing the letter z"
        
        Expected: {contains_character: 'z'}
        """
        query = "strings containing the letter z"
        
        result = parse_natural_language_query(query)
        
        # Assert filter is present
        self.assertIn('contains_character', result)
        
        # Assert correct value
        self.assertEqual(result['contains_character'], 'z')
    
    def test_three_words(self):
        """
        Test pattern: "strings with 3 words"
        
        Expected: {word_count: 3}
        """
        query = "strings with 3 words"
        
        result = parse_natural_language_query(query)
        
        # Assert filter is present
        self.assertIn('word_count', result)
        
        # Assert correct value
        self.assertEqual(result['word_count'], 3)
    
    def test_two_word_palindrome(self):
        """
        Test pattern: "two word palindrome"
        
        Expected: {word_count: 2, is_palindrome: True}
        """
        query = "two word palindrome"
        
        result = parse_natural_language_query(query)
        
        # Assert both filters are present
        self.assertIn('word_count', result)
        self.assertIn('is_palindrome', result)
        
        # Assert correct values
        self.assertEqual(result['word_count'], 2)
        self.assertEqual(result['is_palindrome'], True)
    
    def test_palindrome_simple(self):
        """
        Additional test: Simple "palindrome" query.
        
        Expected: {is_palindrome: True}
        """
        query = "palindrome"
        
        result = parse_natural_language_query(query)
        
        self.assertEqual(result, {'is_palindrome': True})
    
    def test_palindromes_plural(self):
        """
        Additional test: "palindromes" (plural form).
        
        Expected: {is_palindrome: True}
        """
        query = "palindromes"
        
        result = parse_natural_language_query(query)
        
        self.assertEqual(result, {'is_palindrome': True})
    
    def test_single_word(self):
        """
        Additional test: "single word" without palindrome.
        
        Expected: {word_count: 1}
        """
        query = "single word"
        
        result = parse_natural_language_query(query)
        
        self.assertEqual(result, {'word_count': 1})
    
    def test_numeric_word_count(self):
        """
        Additional test: Numeric word count variations.
        
        Test: "5 words", "1 word", "10 words"
        """
        # Test "5 words"
        result = parse_natural_language_query("5 words")
        self.assertEqual(result['word_count'], 5)
        
        # Test "1 word" (singular)
        result = parse_natural_language_query("1 word")
        self.assertEqual(result['word_count'], 1)
        
        # Test "10 words"
        result = parse_natural_language_query("10 words")
        self.assertEqual(result['word_count'], 10)
    
    def test_text_word_count(self):
        """
        Additional test: Text-based word count (one, two, three, etc.).
        
        Expected: Correct numeric word_count
        """
        test_cases = {
            'one word': 1,
            'two words': 2,
            'three words': 3,
            'four words': 4,
            'five words': 5,
            'six words': 6,
            'seven words': 7,
            'eight words': 8,
            'nine words': 9,
            'ten words': 10
        }
        
        for query, expected_count in test_cases.items():
            result = parse_natural_language_query(query)
            self.assertEqual(result['word_count'], expected_count, 
                           f"Failed for query: '{query}'")
    
    def test_contains_letter_variations(self):
        """
        Additional test: Various "containing letter X" patterns.
        
        Test multiple variations of the pattern.
        """
        # "containing letter a"
        result = parse_natural_language_query("containing letter a")
        self.assertEqual(result['contains_character'], 'a')
        
        # "contains letter b"
        result = parse_natural_language_query("contains letter b")
        self.assertEqual(result['contains_character'], 'b')
        
        # "containing the letter c"
        result = parse_natural_language_query("containing the letter c")
        self.assertEqual(result['contains_character'], 'c')
        
        # "contains the letter z"
        result = parse_natural_language_query("contains the letter z")
        self.assertEqual(result['contains_character'], 'z')
    
    def test_vowel_patterns(self):
        """
        Additional test: Vowel patterns (first vowel, second vowel, etc.).
        
        Expected: Correct character mapping
        """
        test_cases = {
            'first vowel': 'a',
            'second vowel': 'e',
            'third vowel': 'i',
            'fourth vowel': 'o',
            'fifth vowel': 'u'
        }
        
        for query, expected_char in test_cases.items():
            result = parse_natural_language_query(query)
            self.assertEqual(result['contains_character'], expected_char,
                           f"Failed for query: '{query}'")
    
    def test_longer_than_variations(self):
        """
        Additional test: "longer than X characters" with different numbers.
        
        Expected: min_length = X + 1
        """
        # "longer than 5 characters"
        result = parse_natural_language_query("longer than 5 characters")
        self.assertEqual(result['min_length'], 6)
        
        # "longer than 20 characters"
        result = parse_natural_language_query("longer than 20 characters")
        self.assertEqual(result['min_length'], 21)
        
        # "longer than 100 characters"
        result = parse_natural_language_query("longer than 100 characters")
        self.assertEqual(result['min_length'], 101)
    
    def test_case_insensitive(self):
        """
        Additional test: Parser is case-insensitive.
        
        Test: "PALINDROME", "Palindrome", "pAlInDrOmE"
        """
        queries = ["PALINDROME", "Palindrome", "pAlInDrOmE"]
        
        for query in queries:
            result = parse_natural_language_query(query)
            self.assertEqual(result, {'is_palindrome': True},
                           f"Failed for query: '{query}'")
    
    def test_complex_combined_query(self):
        """
        Additional test: Complex query with multiple filters.
        
        Test: "palindromic strings with 2 words containing letter a"
        Expected: All three filters present
        """
        query = "palindromic strings with 2 words containing letter a"
        
        result = parse_natural_language_query(query)
        
        # Assert all three filters
        self.assertEqual(result['is_palindrome'], True)
        self.assertEqual(result['word_count'], 2)
        self.assertEqual(result['contains_character'], 'a')
    
    def test_invalid_query_raises_error(self):
        """
        Additional test: Invalid/unparseable query raises ValueError.
        
        Given: A query that doesn't match any patterns
        When: parse_natural_language_query is called
        Then: ValueError is raised
        """
        invalid_queries = [
            "this is nonsense",
            "random text here",
            "xyz abc def"
        ]
        
        for query in invalid_queries:
            with self.assertRaises(ValueError):
                parse_natural_language_query(query)


class PostStringsEndpointTestCase(TestCase):
    """
    Test cases for POST /strings endpoint.
    
    Tests cover:
    - Successful string creation (201)
    - Duplicate detection (409)
    - Missing field validation (400)
    - Invalid data type validation (422)
    """
    
    def setUp(self):
        """Set up test client and clear database before each test."""
        self.client = APIClient()
        self.url = '/strings/'
        # Ensure clean state
        StringAnalysis.objects.all().delete()
    
    def test_post_success_returns_201(self):
        """
        Test case 1: Valid string returns 201 Created.
        
        Given: A valid string value
        When: POST request is made to /strings/
        Then: Response status is 201 Created
        And: Response contains id, value, properties, created_at
        """
        payload = {'value': 'hello world'}
        
        response = self.client.post(self.url, payload, format='json')
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Assert response structure
        self.assertIn('id', response.data)
        self.assertIn('value', response.data)
        self.assertIn('properties', response.data)
        self.assertIn('created_at', response.data)
        
        # Assert value is correct
        self.assertEqual(response.data['value'], 'hello world')
        
        # Assert properties exist
        self.assertIn('length', response.data['properties'])
        self.assertIn('is_palindrome', response.data['properties'])
        self.assertIn('word_count', response.data['properties'])
        self.assertIn('character_frequency_map', response.data['properties'])
        
        # Verify object was created in database
        self.assertTrue(StringAnalysis.objects.filter(value='hello world').exists())
    
    def test_post_duplicate_returns_409(self):
        """
        Test case 2: Submitting same string twice returns 409 Conflict.
        
        Given: A string that already exists in the database
        When: POST request is made with the same string value
        Then: Response status is 409 Conflict
        And: Error message indicates duplicate
        """
        payload = {'value': 'duplicate test'}
        
        # First POST - should succeed
        first_response = self.client.post(self.url, payload, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        
        # Second POST - should return 409 Conflict
        second_response = self.client.post(self.url, payload, format='json')
        
        # Assert status code
        self.assertEqual(second_response.status_code, status.HTTP_409_CONFLICT)
        
        # Assert error message
        self.assertIn('error', second_response.data)
        self.assertEqual(second_response.data['error'], 'String already exists in the system')
        
        # Verify only one object exists in database
        self.assertEqual(StringAnalysis.objects.filter(value='duplicate test').count(), 1)
    
    def test_post_missing_value_returns_400(self):
        """
        Test case 3: Request without 'value' field returns 400 Bad Request.
        
        Given: A request payload without the 'value' field
        When: POST request is made to /strings/
        Then: Response status is 400 Bad Request
        And: Error message indicates missing field
        """
        # Empty payload
        payload = {}
        
        response = self.client.post(self.url, payload, format='json')
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Assert error message
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], "Missing 'value' field")
        
        # Verify no object was created
        self.assertEqual(StringAnalysis.objects.count(), 0)
    
    def test_post_invalid_type_number_returns_422(self):
        """
        Test case 4a: Request with number value returns 422 Unprocessable Entity.
        
        Given: A request payload with numeric value instead of string
        When: POST request is made to /strings/
        Then: Response status is 422 Unprocessable Entity
        And: Error message indicates invalid data type
        """
        payload = {'value': 123}
        
        response = self.client.post(self.url, payload, format='json')
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        # Assert error message
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], "Invalid data type for 'value' (must be string)")
        
        # Verify no object was created
        self.assertEqual(StringAnalysis.objects.count(), 0)
    
    def test_post_invalid_type_null_returns_422(self):
        """
        Test case 4b: Request with null value returns 422 Unprocessable Entity.
        
        Given: A request payload with null/None value
        When: POST request is made to /strings/
        Then: Response status is 422 Unprocessable Entity
        """
        payload = {'value': None}
        
        response = self.client.post(self.url, payload, format='json')
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        # Assert error message
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], "Invalid data type for 'value' (must be string)")
        
        # Verify no object was created
        self.assertEqual(StringAnalysis.objects.count(), 0)
    
    def test_post_invalid_type_array_returns_422(self):
        """
        Test case 4c: Request with array value returns 422 Unprocessable Entity.
        
        Given: A request payload with array/list value
        When: POST request is made to /strings/
        Then: Response status is 422 Unprocessable Entity
        """
        payload = {'value': ['hello', 'world']}
        
        response = self.client.post(self.url, payload, format='json')
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        # Assert error message
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], "Invalid data type for 'value' (must be string)")
        
        # Verify no object was created
        self.assertEqual(StringAnalysis.objects.count(), 0)
    
    def test_post_invalid_type_object_returns_422(self):
        """
        Test case 4d: Request with object/dict value returns 422 Unprocessable Entity.
        
        Given: A request payload with nested object value
        When: POST request is made to /strings/
        Then: Response status is 422 Unprocessable Entity
        """
        payload = {'value': {'nested': 'object'}}
        
        response = self.client.post(self.url, payload, format='json')
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        # Assert error message
        self.assertIn('error', response.data)
        
        # Verify no object was created
        self.assertEqual(StringAnalysis.objects.count(), 0)
    
    def test_post_palindrome_detected(self):
        """
        Additional test: Verify palindrome detection works correctly.
        
        Given: A palindrome string
        When: POST request is made
        Then: Response properties should indicate is_palindrome=True
        """
        payload = {'value': 'racecar'}
        
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['properties']['is_palindrome'])
    
    def test_post_special_characters(self):
        """
        Additional test: Verify special characters are handled correctly.
        
        Given: A string with special characters
        When: POST request is made
        Then: String should be stored and analyzed correctly
        """
        payload = {'value': 'hello@world!123'}
        
        response = self.client.post(self.url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['value'], 'hello@world!123')
        self.assertIn('character_frequency_map', response.data['properties'])


class GetStringEndpointTestCase(TestCase):
    """
    Test cases for GET /strings/{value} endpoint.
    
    Tests cover:
    - Retrieving existing string (200)
    - Non-existent string (404)
    - URL encoding with spaces and special characters
    """
    
    def setUp(self):
        """Set up test client and create test data."""
        self.client = APIClient()
        # Create test strings
        StringAnalysis.objects.all().delete()
        self.test_string = StringAnalysis.objects.create(value='test string')
        self.test_string_with_spaces = StringAnalysis.objects.create(value='hello world')
    
    def test_get_existing_returns_200(self):
        """
        Test case 1: Valid string returns 200 OK.
        
        Given: A string that exists in the database
        When: GET request is made to /strings/{value}/
        Then: Response status is 200 OK
        And: Response contains the string data
        """
        url = '/strings/test string/'
        
        response = self.client.get(url)
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assert response structure
        self.assertIn('id', response.data)
        self.assertIn('value', response.data)
        self.assertIn('properties', response.data)
        self.assertIn('created_at', response.data)
        
        # Assert correct value
        self.assertEqual(response.data['value'], 'test string')
    
    def test_get_nonexistent_returns_404(self):
        """
        Test case 2: Non-existent string returns 404 Not Found.
        
        Given: A string value that does not exist in the database
        When: GET request is made to /strings/{value}/
        Then: Response status is 404 Not Found
        And: Error message indicates string not found
        """
        url = '/strings/nonexistent string/'
        
        response = self.client.get(url)
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Assert error message
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'String does not exist in the system')
    
    def test_get_with_spaces_url_encoded(self):
        """
        Test case 3: String with spaces works when URL encoded.
        
        Given: A string with spaces that exists in the database
        When: GET request is made with URL-encoded value
        Then: Response status is 200 OK
        And: String is correctly retrieved and decoded
        """
        from urllib.parse import quote
        
        # URL encode the string with spaces
        encoded_value = quote('hello world')
        url = f'/strings/{encoded_value}/'
        
        response = self.client.get(url)
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assert correct value (should be decoded)
        self.assertEqual(response.data['value'], 'hello world')
    
    def test_get_with_special_characters(self):
        """
        Additional test: String with special characters is URL encoded correctly.
        
        Given: A string with special characters
        When: GET request is made with URL-encoded value
        Then: String is correctly retrieved
        """
        from urllib.parse import quote
        
        # Create string with special characters
        special_string = StringAnalysis.objects.create(value='hello@world!')
        
        encoded_value = quote('hello@world!')
        url = f'/strings/{encoded_value}/'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'hello@world!')
    
    def test_get_with_forward_slash(self):
        """
        Additional test: String with forward slash is handled correctly.
        
        Given: A string containing forward slash
        When: GET request is made with URL-encoded value
        Then: String is correctly retrieved
        """
        from urllib.parse import quote
        
        # Create string with forward slash
        slash_string = StringAnalysis.objects.create(value='test/path')
        
        # URL encode the string (forward slash becomes %2F)
        encoded_value = quote('test/path', safe='')
        url = f'/strings/{encoded_value}/'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 'test/path')


class DeleteStringEndpointTestCase(TestCase):
    """
    Test cases for DELETE /strings/{value} endpoint.
    
    Tests cover:
    - Deleting existing string (204)
    - Deleting non-existent string (404)
    - Empty response body for 204
    """
    
    def setUp(self):
        """Set up test client and create test data."""
        self.client = APIClient()
        StringAnalysis.objects.all().delete()
    
    def test_delete_existing_returns_204(self):
        """
        Test case 1: Deleting existing string returns 204 No Content.
        
        Given: A string that exists in the database
        When: DELETE request is made to /strings/{value}/
        Then: Response status is 204 No Content
        And: String is removed from database
        """
        # Create a test string
        test_string = StringAnalysis.objects.create(value='delete me')
        url = '/strings/delete me/'
        
        # Verify string exists
        self.assertTrue(StringAnalysis.objects.filter(value='delete me').exists())
        
        response = self.client.delete(url)
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify string was deleted
        self.assertFalse(StringAnalysis.objects.filter(value='delete me').exists())
    
    def test_delete_nonexistent_returns_404(self):
        """
        Test case 2: Deleting non-existent string returns 404 Not Found.
        
        Given: A string value that does not exist in the database
        When: DELETE request is made to /strings/{value}/
        Then: Response status is 404 Not Found
        And: Error message indicates string not found
        """
        url = '/strings/does not exist/'
        
        response = self.client.delete(url)
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Assert error message
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'String does not exist in the system')
    
    def test_delete_empty_response_body(self):
        """
        Test case 3: 204 response has no body (completely empty).
        
        Given: A string that exists in the database
        When: DELETE request is made successfully
        Then: Response status is 204 No Content
        And: Response body is empty/None
        """
        # Create a test string
        test_string = StringAnalysis.objects.create(value='empty response')
        url = '/strings/empty response/'
        
        response = self.client.delete(url)
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Assert response has no content
        # In DRF, 204 responses have empty content
        self.assertEqual(response.content, b'')
        
        # Alternative check: response.data should be None or empty
        # Some versions of DRF set data to None for 204
        if hasattr(response, 'data'):
            self.assertIn(response.data, [None, '', b''])
    
    def test_delete_with_url_encoding(self):
        """
        Additional test: DELETE works with URL-encoded strings.
        
        Given: A string with spaces that exists in the database
        When: DELETE request is made with URL-encoded value
        Then: String is correctly deleted
        """
        from urllib.parse import quote
        
        # Create string with spaces
        test_string = StringAnalysis.objects.create(value='hello world')
        
        encoded_value = quote('hello world')
        url = f'/strings/{encoded_value}/'
        
        response = self.client.delete(url)
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify string was deleted
        self.assertFalse(StringAnalysis.objects.filter(value='hello world').exists())
    
    def test_delete_with_special_characters(self):
        """
        Additional test: DELETE works with special characters.
        
        Given: A string with special characters
        When: DELETE request is made
        Then: String is correctly deleted
        """
        from urllib.parse import quote
        
        # Create string with special characters
        test_string = StringAnalysis.objects.create(value='test@string!')
        
        encoded_value = quote('test@string!')
        url = f'/strings/{encoded_value}/'
        
        response = self.client.delete(url)
        
        # Assert status code
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify string was deleted
        self.assertFalse(StringAnalysis.objects.filter(value='test@string!').exists())
    
    def test_delete_idempotent(self):
        """
        Additional test: DELETE is idempotent (second DELETE returns 404).
        
        Given: A string that was already deleted
        When: DELETE request is made again
        Then: Response status is 404 Not Found
        """
        # Create and delete a string
        test_string = StringAnalysis.objects.create(value='delete twice')
        url = '/strings/delete twice/'
        
        # First DELETE - should succeed
        first_response = self.client.delete(url)
        self.assertEqual(first_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Second DELETE - should return 404
        second_response = self.client.delete(url)
        self.assertEqual(second_response.status_code, status.HTTP_404_NOT_FOUND)


