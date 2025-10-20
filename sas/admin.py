from django.contrib import admin
from .models import AnalyzedString

@admin.register(AnalyzedString)
class AnalyzedStringAdmin(admin.ModelAdmin):
    list_display = ('value', 'length', 'is_palindrome', 'unique_characters', 'word_count', 'created_at')
    list_filter = ('is_palindrome', 'length', 'word_count', 'created_at')
    search_fields = ('value',)
    readonly_fields = ('id', 'created_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'value', 'created_at')
        }),
        ('Analysis Results', {
            'fields': ('length', 'is_palindrome', 'unique_characters', 'word_count', 'character_frequency_map')
        }),
    )