from django.db import models
import json

class AnalyzedString(models.Model):
    id = models.CharField(max_length=64, primary_key=True)  # SHA256 hash
    value = models.TextField()
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    character_frequency_map = models.TextField()  # Store JSON as string
    created_at = models.DateTimeField(auto_now_add=True)
    
    def set_character_frequency(self, freq_dict):
        self.character_frequency_map = json.dumps(freq_dict)
    
    def get_character_frequency(self):
        return json.loads(self.character_frequency_map)
    
    class Meta:
        db_table = 'analyzed_strings'