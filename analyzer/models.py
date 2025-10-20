from django.db import models


class StringAnalysis(models.Model):
    """Model to store string analysis results."""
    sha256_hash = models.CharField(max_length=64, primary_key=True)
    value = models.TextField()
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    character_frequency_map = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'String Analysis'
        verbose_name_plural = 'String Analyses'

    def __str__(self):
        return f"{self.sha256_hash[:8]}... - {self.value[:50]}"
