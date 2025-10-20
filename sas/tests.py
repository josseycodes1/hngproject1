from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import AnalyzedString
from .utils import analyze_string
import json

class StringAnalysisUtilsTests(TestCase):
    def test_analyze_string_basic(self):
        """Test the analyze_string function with basic input"""
        result = analyze_string("hello")
        
        self.assertEqual(result['length'], 5)
        self.assertEqual(result['word_count'], 1)
        self.assertFalse(result['is_palindrome'])
        self.assertEqual(result['unique_characters'], 4)  # h, e, l, o
        self.assertEqual(result['character_frequency_map']['l'], 2)
    
    def test_analyze_string_palindrome(self):
        """Test palindrome detection"""
        result = analyze_string("A man a plan a canal Panama")
        self.assertTrue(result['is_palindrome'])
    
    def test_analyze_string_multiple_words(self):
        """Test word count with multiple words"""
        result = analyze_string("hello world test")
        self.assertEqual(result['word_count'], 3)

class StringAnalysisAPITests(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.test_string = "hello world"
        self.test_string_2 = "madam"
        self.create_url = reverse('create-string')
        self.get_all_url = reverse('get-all-strings')
    
    def test_create_analyze_string_success(self):
        """Test successful string analysis creation"""
        data = {'value': self.test_string}
        response = self.client.post(self.create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['value'], self.test_string)
        self.assertIn('properties', response.data)
        self.assertIn('id', response.data)
    
    def test_create_analyze_string_duplicate(self):
        """Test duplicate string detection"""
        # Create first time
        data = {'value': self.test_string}
        response1 = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Try to create same string again
        response2 = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_409_CONFLICT)
    
    def test_create_analyze_string_invalid_data(self):
        """Test invalid data handling"""
        # Missing value field
        response = self.client.post(self.create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Empty string
        response = self.client.post(self.create_url, {'value': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Empty string is valid
    
    def test_get_string_success(self):
        """Test retrieving a specific string"""
        # First create a string
        data = {'value': self.test_string}
        self.client.post(self.create_url, data, format='json')
        
        # Then retrieve it
        get_url = reverse('get-string', kwargs={'string_value': self.test_string})
        response = self.client.get(get_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], self.test_string)
    
    def test_get_string_not_found(self):
        """Test retrieving non-existent string"""
        get_url = reverse('get-string', kwargs={'string_value': 'nonexistent'})
        response = self.client.get(get_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_all_strings_with_filters(self):
        """Test filtering strings"""
        # Create test strings
        self.client.post(self.create_url, {'value': 'hello world'}, format='json')
        self.client.post(self.create_url, {'value': 'madam'}, format='json')
        self.client.post(self.create_url, {'value': 'test'}, format='json')
        
        # Test palindrome filter
        response = self.client.get(self.get_all_url, {'is_palindrome': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return 'madam'
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['value'], 'madam')
    
    def test_natural_language_filter(self):
        """Test natural language filtering"""
        # Create test strings
        self.client.post(self.create_url, {'value': 'madam'}, format='json')
        self.client.post(self.create_url, {'value': 'hello'}, format='json')
        
        # Test natural language query
        filter_url = reverse('natural-language-filter')
        response = self.client.get(filter_url, {'query': 'palindromic strings'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('interpreted_query', response.data)
        self.assertTrue(response.data['interpreted_query']['parsed_filters']['is_palindrome'])
    
    def test_delete_string(self):
        """Test string deletion"""
        # First create a string
        data = {'value': self.test_string}
        self.client.post(self.create_url, data, format='json')
        
        # Then delete it
        delete_url = reverse('delete-string', kwargs={'string_value': self.test_string})
        response = self.client.delete(delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify it's gone
        get_url = reverse('get-string', kwargs={'string_value': self.test_string})
        response = self.client.get(get_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ModelTests(TestCase):
    def test_analyzed_string_creation(self):
        """Test AnalyzedString model creation and methods"""
        from .utils import analyze_string
        
        test_text = "hello"
        analysis = analyze_string(test_text)
        
        string_obj = AnalyzedString.objects.create(
            id=analysis['sha256_hash'],
            value=test_text,
            length=analysis['length'],
            is_palindrome=analysis['is_palindrome'],
            unique_characters=analysis['unique_characters'],
            word_count=analysis['word_count'],
        )
        string_obj.set_character_frequency(analysis['character_frequency_map'])
        
        # Test character frequency methods
        freq_map = string_obj.get_character_frequency()
        self.assertEqual(freq_map['l'], 2)
        self.assertIsInstance(freq_map, dict)