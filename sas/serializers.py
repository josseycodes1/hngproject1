from rest_framework import serializers
from .models import AnalyzedString
from .utils import analyze_string

class AnalyzedStringSerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()
    
    class Meta:
        model = AnalyzedString
        fields = ['id', 'value', 'properties', 'created_at']
    
    def get_properties(self, obj):
        return {
            "length": obj.length,
            "is_palindrome": obj.is_palindrome,
            "unique_characters": obj.unique_characters,
            "word_count": obj.word_count,
            "sha256_hash": obj.id,
            "character_frequency_map": obj.get_character_frequency()
        }

class StringInputSerializer(serializers.Serializer):
    value = serializers.CharField(allow_blank=True, required=True)


class StringInputSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=1000)