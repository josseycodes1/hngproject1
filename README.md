
# String Analyzer Service

A Django RESTful API service that analyzes strings and stores their computed properties.

## Features

- Analyze strings and compute various properties
- Store and retrieve string analyses
- Filter strings by various criteria
- Natural language query support
- RESTful API design

## API Endpoints

### 1. Create/Analyze String
- **POST** `/strings`
- Analyzes a string and stores its properties
- Returns 409 if string already exists

### 2. Get Specific String
- **GET** `/strings/{string_value}`
- Retrieves analysis for a specific string
- Can use either the string value or its SHA-256 hash

### 3. Get All Strings with Filtering
- **GET** `/strings`
- Query parameters: `is_palindrome`, `min_length`, `max_length`, `word_count`, `contains_character`

### 4. Natural Language Filtering
- **GET** `/strings/filter-by-natural-language?query=...`
- Supports queries like "all single word palindromic strings"

### 5. Delete String
- **DELETE** `/strings/{string_value}`
- Removes a string analysis from the system

## Local Development

1. **Setup virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate