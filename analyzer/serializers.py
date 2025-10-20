from rest_framework import serializers
from .models import StringAnalysis
from .utils import (
    calculate_sha256,
    is_palindrome,
    count_unique_characters,
    get_word_count,
    get_character_frequency
)


class StringInputSerializer(serializers.Serializer):
    """Serializer for validating string input."""
    
    value = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'The value field is required.',
            'blank': 'The value field cannot be blank.',
        }
    )
    
    def validate_value(self, value):
        """
        Validate that the value is not empty or only whitespace.
        
        Args:
            value: The input string to validate
            
        Returns:
            The validated value
            
        Raises:
            serializers.ValidationError: If value is only whitespace
        """
        if not value or not value.strip():
            raise serializers.ValidationError(
                'The value cannot be empty or contain only whitespace.'
            )
        return value


class StringAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for StringAnalysis model with nested properties."""
    
    id = serializers.CharField(source='sha256_hash', read_only=True)
    properties = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = StringAnalysis
        fields = ['id', 'value', 'properties', 'created_at']
        read_only_fields = ['id', 'properties', 'created_at']
    
    def get_properties(self, obj):
        """
        Return nested properties dictionary.
        
        Args:
            obj: StringAnalysis instance
            
        Returns:
            Dictionary containing all analysis properties
        """
        return {
            'length': obj.length,
            'is_palindrome': obj.is_palindrome,
            'unique_characters': obj.unique_characters,
            'word_count': obj.word_count,
            'sha256_hash': obj.sha256_hash,
            'character_frequency_map': obj.character_frequency_map
        }
    
    def create(self, validated_data):
        """
        Create a new StringAnalysis instance with calculated properties.
        
        Args:
            validated_data: Dictionary containing validated data
            
        Returns:
            Created StringAnalysis instance
        """
        # Extract value from validated data
        value = validated_data['value']
        
        # Calculate all properties using utility functions
        sha256_hash = calculate_sha256(value)
        length = len(value)
        is_palindrome_result = is_palindrome(value)
        unique_characters = count_unique_characters(value)
        word_count = get_word_count(value)
        character_frequency_map = get_character_frequency(value)
        
        # Create and return StringAnalysis instance
        string_analysis = StringAnalysis.objects.create(
            sha256_hash=sha256_hash,
            value=value,
            length=length,
            is_palindrome=is_palindrome_result,
            unique_characters=unique_characters,
            word_count=word_count,
            character_frequency_map=character_frequency_map
        )
        
        return string_analysis