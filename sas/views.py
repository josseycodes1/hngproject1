from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import AnalyzedString
from .serializers import AnalyzedStringSerializer, StringInputSerializer
from .utils import analyze_string
import json

@api_view(['GET'])
def health_check(request):
    return Response({
        "status": "OK", 
        "message": "String Analysis Service is running",
        "endpoints": {
            "POST /strings/": "Create and analyze string",
            "GET /strings/<string>/": "Get specific string", 
            "GET /strings-list/": "Get all strings with filtering",
            "GET /strings/filter-by-natural-language/?query=...": "Natural language filtering",
            "DELETE /strings/<string>/delete/": "Delete string"
        }
    }, status=status.HTTP_200_OK)
@api_view(['POST'])
def create_analyze_string(request):
    serializer = StringInputSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {"error": "Invalid request body or missing 'value' field"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    value = serializer.validated_data['value']
    

    if not isinstance(value, str):
        return Response(
            {"error": "Value must be a string"}, 
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
  
    try:
        properties = analyze_string(value)
    except ValueError as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    

    if AnalyzedString.objects.filter(id=properties['sha256_hash']).exists():
        return Response(
            {"error": "String already exists in the system"}, 
            status=status.HTTP_409_CONFLICT
        )
    

    analyzed_string = AnalyzedString(
        id=properties['sha256_hash'],
        value=value,
        length=properties['length'],
        is_palindrome=properties['is_palindrome'],
        unique_characters=properties['unique_characters'],
        word_count=properties['word_count'],
    )
    analyzed_string.set_character_frequency(properties['character_frequency_map'])
    analyzed_string.save()
    
    response_serializer = AnalyzedStringSerializer(analyzed_string)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_string(request, string_value):

    analyzed_string = get_object_or_404(AnalyzedString, value=string_value)
    serializer = AnalyzedStringSerializer(analyzed_string)
    return Response(serializer.data)


@api_view(['GET'])
def get_all_strings(request):
    queryset = AnalyzedString.objects.all()
    
 
    is_palindrome = request.GET.get('is_palindrome')
    min_length = request.GET.get('min_length')
    max_length = request.GET.get('max_length')
    word_count = request.GET.get('word_count')
    contains_character = request.GET.get('contains_character')
    
    filters_applied = {}
    
    if is_palindrome is not None:
        if is_palindrome.lower() == 'true':
            queryset = queryset.filter(is_palindrome=True)
            filters_applied['is_palindrome'] = True
        elif is_palindrome.lower() == 'false':
            queryset = queryset.filter(is_palindrome=False)
            filters_applied['is_palindrome'] = False
    
    if min_length is not None:
        try:
            queryset = queryset.filter(length__gte=int(min_length))
            filters_applied['min_length'] = int(min_length)
        except ValueError:
            return Response(
                {"error": "min_length must be an integer"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if max_length is not None:
        try:
            queryset = queryset.filter(length__lte=int(max_length))
            filters_applied['max_length'] = int(max_length)
        except ValueError:
            return Response(
                {"error": "max_length must be an integer"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if word_count is not None:
        try:
            queryset = queryset.filter(word_count=int(word_count))
            filters_applied['word_count'] = int(word_count)
        except ValueError:
            return Response(
                {"error": "word_count must be an integer"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if contains_character is not None:
        if len(contains_character) != 1:
            return Response(
                {"error": "contains_character must be a single character"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        queryset = [obj for obj in queryset if contains_character in obj.value]
        filters_applied['contains_character'] = contains_character
    
    serializer = AnalyzedStringSerializer(queryset, many=True)
    
    return Response({
        "data": serializer.data,
        "count": len(serializer.data),
        "filters_applied": filters_applied
    })


@api_view(['GET'])
def filter_by_natural_language(request):
    print("Natural language filter endpoint hit!") 
    query = request.GET.get('query', '')
    
    if not query:
        return Response(
            {"error": "Query parameter is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    print(f"Query received: {query}") 
    
    query = query.lower()
    parsed_filters = {}
    
   
    if "single word" in query or "one word" in query:
        parsed_filters["word_count"] = 1
    
    if "palindrome" in query or "palindromic" in query:
        parsed_filters["is_palindrome"] = True
    
    if "longer than" in query:
       
        if "10" in query:
            parsed_filters["min_length"] = 11
        elif "5" in query:
            parsed_filters["min_length"] = 6
    
    if "contain" in query:
        if "letter z" in query:
            parsed_filters["contains_character"] = "z"
        elif "vowel" in query:
            parsed_filters["contains_character"] = "a"
        elif "letter" in query:
            
            words = query.split()
            for i, word in enumerate(words):
                if word == "letter" and i + 1 < len(words):
                    letter = words[i + 1]
                    if len(letter) == 1 and letter.isalpha():
                        parsed_filters["contains_character"] = letter
                        break
    
    
    queryset = AnalyzedString.objects.all()
    
    for key, value in parsed_filters.items():
        if key == "word_count":
            queryset = queryset.filter(word_count=value)
        elif key == "is_palindrome":
            queryset = queryset.filter(is_palindrome=value)
        elif key == "min_length":
            queryset = queryset.filter(length__gte=value)
        elif key == "contains_character":
            queryset = [obj for obj in queryset if value in obj.value]
    
    serializer = AnalyzedStringSerializer(queryset, many=True)
    
    print(f"Returning {len(serializer.data)} results") 
    
    return Response({
        "data": serializer.data,
        "count": len(serializer.data),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed_filters
        }
    })


@api_view(['DELETE'])
def delete_string(request, string_value):
    analyzed_string = get_object_or_404(AnalyzedString, value=string_value)
    analyzed_string.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


