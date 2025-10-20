# String Analyzer API

A RESTful API built with Django and Django REST Framework that analyzes strings and provides detailed information about their properties, including palindrome detection, character frequency analysis, and natural language filtering capabilities.

## Features

- ✅ **String Analysis**: Automatically calculate and store string properties
  - Length
  - Palindrome detection
  - Unique character count
  - Word count
  - SHA256 hash generation
  - Character frequency mapping

- ✅ **CRUD Operations**: Full create, read, update, and delete functionality
- ✅ **Advanced Filtering**: Filter strings by multiple criteria
  - Palindrome status
  - Length range (min/max)
  - Word count
  - Contains specific character

- ✅ **Natural Language Queries**: Filter using human-readable queries
  - "single word palindrome"
  - "longer than 10 characters"
  - "containing letter a"
  - "5 words"

- ✅ **Production Ready**: 
  - CORS support
  - PostgreSQL database support
  - Security headers
  - Rate limiting
  - Environment-based configuration

## Tech Stack

- **Backend Framework**: Django 4.2+
- **API Framework**: Django REST Framework 3.14+
- **Database**: PostgreSQL (production), SQLite (development)
- **CORS**: django-cors-headers
- **Environment Management**: python-dotenv
- **Database URL Parser**: dj-database-url

## Local Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- PostgreSQL (optional, for production-like environment)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd string-analyzer-api
   ```

2. **Create a virtual environment**
   ```bash
   # Windows
   python -m venv env
   env\Scripts\activate

   # macOS/Linux
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Generate a new SECRET_KEY
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

   # Edit .env and add your SECRET_KEY
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://localhost:8000/api/`

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (leave empty for SQLite)
DATABASE_URL=

# For PostgreSQL:
# DATABASE_URL=postgresql://username:password@host:port/database_name

# CORS settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

See [.env.example](.env.example) for more details.

## API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### 1. Create String Analysis

**Endpoint**: `POST /api/strings/`

**Request Body**:
```json
{
  "value": "Hello World"
}
```

**Response** (201 Created):
```json
{
  "id": "c0535e4be2b79ffd93291305436bf889314e4a3faec05ecffcbb7df31ad9e51a",
  "value": "Hello World",
  "properties": {
    "length": 11,
    "is_palindrome": false,
    "unique_characters": 8,
    "word_count": 2,
    "sha256_hash": "c0535e4be2b79ffd93291305436bf889314e4a3faec05ecffcbb7df31ad9e51a",
    "character_frequency_map": {
      "H": 1,
      "e": 1,
      "l": 3,
      "o": 2,
      " ": 1,
      "W": 1,
      "r": 1,
      "d": 1
    }
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Response** (400 Bad Request):
```json
{
  "value": ["This field is required."]
}
```

### 2. Retrieve String Analysis

**Endpoint**: `GET /api/strings/<string_value>/`

**Example**: `GET /api/strings/Hello%20World/`

**Response** (200 OK):
```json
{
  "id": "c0535e4be2b79ffd93291305436bf889314e4a3faec05ecffcbb7df31ad9e51a",
  "value": "Hello World",
  "properties": {
    "length": 11,
    "is_palindrome": false,
    "unique_characters": 8,
    "word_count": 2,
    "sha256_hash": "c0535e4be2b79ffd93291305436bf889314e4a3faec05ecffcbb7df31ad9e51a",
    "character_frequency_map": {
      "H": 1,
      "e": 1,
      "l": 3,
      "o": 2,
      " ": 1,
      "W": 1,
      "r": 1,
      "d": 1
    }
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Response** (404 Not Found):
```json
{
  "error": "String not found",
  "details": "No string analysis found with value: Hello World"
}
```

### 3. List and Filter Strings

**Endpoint**: `GET /api/strings/`

**Query Parameters**:
- `is_palindrome` (boolean): Filter by palindrome status
- `min_length` (integer): Minimum string length
- `max_length` (integer): Maximum string length
- `word_count` (integer): Filter by exact word count
- `contains_character` (string): Filter strings containing this character

**Examples**:

```bash
# Get all strings
GET /api/strings/

# Get palindromes only
GET /api/strings/?is_palindrome=true

# Get strings with 5 to 10 characters
GET /api/strings/?min_length=5&max_length=10

# Get strings with exactly 3 words
GET /api/strings/?word_count=3

# Get strings containing letter 'a'
GET /api/strings/?contains_character=a

# Combine multiple filters
GET /api/strings/?is_palindrome=true&min_length=5
```

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "hash1...",
      "value": "racecar",
      "properties": { ... },
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": "hash2...",
      "value": "madam",
      "properties": { ... },
      "created_at": "2024-01-15T10:25:00Z"
    }
  ],
  "count": 2,
  "filters_applied": {
    "is_palindrome": true,
    "min_length": 5
  }
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "Invalid query parameters",
  "details": {
    "min_length": "Must be a valid integer.",
    "is_palindrome": "Must be a boolean value (true/false)."
  }
}
```

### 4. Natural Language Filter

**Endpoint**: `GET /api/strings/filter-by-natural-language/`

**Query Parameter**: `query` (string, required)

**Supported Patterns**:
- `"palindrome"` or `"palindromic"` → is_palindrome=true
- `"single word palindrome"` → word_count=1, is_palindrome=true
- `"longer than X characters"` → min_length=X+1
- `"shorter than X characters"` → max_length=X-1
- `"at least X characters"` → min_length=X
- `"at most X characters"` → max_length=X
- `"containing letter X"` → contains_character=X
- `"X words"` or `"X word"` → word_count=X
- Text numbers: `"one word"`, `"two words"`, etc.

**Examples**:

```bash
# Find palindromes
GET /api/strings/filter-by-natural-language/?query=palindrome

# Find single word palindromes
GET /api/strings/filter-by-natural-language/?query=single%20word%20palindrome

# Find strings longer than 10 characters
GET /api/strings/filter-by-natural-language/?query=longer%20than%2010%20characters

# Find strings containing letter 'a'
GET /api/strings/filter-by-natural-language/?query=containing%20letter%20a

# Find strings with 3 words
GET /api/strings/filter-by-natural-language/?query=3%20words
```

**Response** (200 OK):
```json
{
  "query": "single word palindrome",
  "parsed_filters": {
    "word_count": 1,
    "is_palindrome": true
  },
  "data": [
    {
      "id": "hash1...",
      "value": "racecar",
      "properties": { ... },
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 1
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "Unable to parse query",
  "details": "Could not parse any recognizable patterns from the query.",
  "query": "invalid query"
}
```

**Error Response** (422 Unprocessable Entity):
```json
{
  "error": "Conflicting filters detected",
  "details": "Conflicting length constraints: min_length (15) cannot be greater than max_length (10)",
  "parsed_filters": {
    "min_length": 15,
    "max_length": 10
  },
  "query": "longer than 14 characters and shorter than 11 characters"
}
```

### 5. Delete String Analysis

**Endpoint**: `DELETE /api/strings/<string_value>/`

**Example**: `DELETE /api/strings/Hello%20World/`

**Response** (204 No Content):
```
(empty response body)
```

**Error Response** (404 Not Found):
```json
{
  "error": "String not found",
  "details": "No string analysis found with value: Hello World"
}
```

## Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific Test Module
```bash
python manage.py test analyzer.tests
```

### Run with Coverage (requires coverage package)
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # generates HTML report in htmlcov/
```

### Manual Testing with cURL

**Create a string analysis**:
```bash
curl -X POST http://localhost:8000/api/strings/ \
  -H "Content-Type: application/json" \
  -d '{"value": "racecar"}'
```

**Retrieve a string analysis**:
```bash
curl http://localhost:8000/api/strings/racecar/
```

**List with filters**:
```bash
curl "http://localhost:8000/api/strings/?is_palindrome=true&min_length=5"
```

**Natural language filter**:
```bash
curl "http://localhost:8000/api/strings/filter-by-natural-language/?query=palindrome"
```

**Delete a string analysis**:
```bash
curl -X DELETE http://localhost:8000/api/strings/racecar/
```

## Deployment

### PostgreSQL Setup

1. **Install PostgreSQL** on your server

2. **Create a database**:
   ```sql
   CREATE DATABASE string_analyzer;
   CREATE USER string_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE string_analyzer TO string_user;
   ```

3. **Update environment variables**:
   ```env
   DEBUG=False
   DATABASE_URL=postgresql://string_user:your_password@localhost:5432/string_analyzer
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   SECRET_KEY=your-production-secret-key
   ```

### Production Deployment Steps

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables** in your hosting platform

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Collect static files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

5. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Use a production WSGI server** (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn string_analyzer.wsgi:application --bind 0.0.0.0:8000
   ```

### Deployment Platforms

#### Heroku
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

#### AWS/DigitalOcean/Other VPS

1. Set up NGINX as reverse proxy
2. Use Gunicorn as WSGI server
3. Set up systemd service for auto-restart
4. Configure SSL/TLS with Let's Encrypt
5. Set up PostgreSQL database

## Project Structure

```
string-analyzer-api/
├── analyzer/                 # Main application
│   ├── migrations/          # Database migrations
│   ├── __init__.py
│   ├── admin.py            # Django admin configuration
│   ├── apps.py             # App configuration
│   ├── models.py           # StringAnalysis model
│   ├── serializers.py      # DRF serializers
│   ├── tests.py            # Unit tests
│   ├── urls.py             # URL routing
│   ├── utils.py            # Utility functions
│   └── views.py            # API views
├── string_analyzer/         # Project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # Django settings
│   ├── urls.py             # Root URL configuration
│   └── wsgi.py
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── manage.py               # Django management script
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## Database Schema

### StringAnalysis Model

| Field | Type | Description |
|-------|------|-------------|
| `sha256_hash` | CharField(64) | Primary key, SHA256 hash of the value |
| `value` | TextField | The original string |
| `length` | IntegerField | Length of the string |
| `is_palindrome` | BooleanField | Whether the string is a palindrome |
| `unique_characters` | IntegerField | Number of unique characters |
| `word_count` | IntegerField | Number of words in the string |
| `character_frequency_map` | JSONField | Character frequency dictionary |
| `created_at` | DateTimeField | Timestamp of creation |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.

## Acknowledgments

- Django REST Framework for excellent API tools
- Django community for comprehensive documentation
- Contributors and testers
