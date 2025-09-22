# Flow ML Backend

A production-ready FastAPI backend for Flow's ML automation platform, providing end-to-end data preprocessing and analysis capabilities.

## Features

### Core Features
- **User Authentication**: JWT-based authentication with user registration/login
- **File Upload**: Support for CSV and Excel (XLS/XLSX) tabular data
- **Data Preprocessing**: Automated preprocessing with customizable options
- **User Tiers**: Free and Premium tiers with different limits and features
- **API Access**: RESTful API (API keys removed in this MVP; use the Python library)
- **LLM Integration**: GroqCloud integration for intelligent data analysis and recommendations

### Free Tier Features
- 3 datasets per month
- Max 50MB file size
- Max 50,000 rows for CSV files
- Basic preprocessing (mean imputation, MinMax scaling, one-hot encoding)
- 3 API calls per month

### Premium Tier Features
- Unlimited datasets and file sizes
- Advanced preprocessing options
- Data augmentation
- Feature engineering
- Outlier removal
- Custom scaling methods
- Unlimited API calls
- LLM-powered insights and recommendations

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Dataset Management

#### Upload Dataset
```http
POST /datasets/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <file>
dataset_name: "My Dataset" (optional)
```

#### Get Datasets
```http
GET /datasets?limit=50&offset=0
Authorization: Bearer <access_token>
```

#### Get Dataset Details
```http
GET /datasets/{dataset_id}
Authorization: Bearer <access_token>
```

#### Delete Dataset
```http
DELETE /datasets/{dataset_id}
Authorization: Bearer <access_token>
```

### Preprocessing

#### Start Preprocessing
```http
POST /datasets/{dataset_id}/preprocess
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "scaling_method": "minmax",
  "missing_value_strategy": "mean",
  "outlier_removal": false,
  "data_augmentation": false,
  "feature_engineering": false,
  "train_test_split": 0.8
}
```

#### Get Preprocessing Status
```http
GET /datasets/{dataset_id}/preprocessing-status
Authorization: Bearer <access_token>
```

#### Download Processed Dataset
```http
GET /datasets/{dataset_id}/download?processed=true
Authorization: Bearer <access_token>
```

### LLM-Powered Features

#### Analyze Dataset
```http
POST /datasets/{dataset_id}/analyze
Authorization: Bearer <access_token>
```

#### Get Preprocessing Recommendations
```http
POST /datasets/{dataset_id}/recommend-preprocessing
Authorization: Bearer <access_token>
```

#### Explain Preprocessing Steps
```http
POST /datasets/{dataset_id}/explain-preprocessing
Authorization: Bearer <access_token>
```

### User Management

#### Get Usage Statistics
```http
GET /user/usage
Authorization: Bearer <access_token>
```

#### Upgrade to Premium
```http
POST /user/upgrade
Authorization: Bearer <access_token>
```

### Programmatic Access

API keys and external preprocess endpoint are removed for this MVP. Use the official Python library `flow_ml` for programmatic preprocessing from your applications.

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=sqlite:///./flow.db

# JWT Settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage
UPLOAD_DIR=./data
MAX_FILE_SIZE=52428800

# Groq API
GROQ_API_KEY=your-groq-api-key-here

# App Settings
APP_NAME=Flow ML Backend
DEBUG=True
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Free Tier Limits
FREE_TIER_DATASETS_PER_MONTH=3
FREE_TIER_MAX_FILE_SIZE=52428800
FREE_TIER_MAX_ROWS=50000
FREE_TIER_API_CALLS_PER_MONTH=3
```

## Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique email address
- `hashed_password`: Bcrypt hashed password
- `full_name`: User's full name
- `is_active`: Account status
- `is_premium`: Premium tier status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

### Datasets Table
- `id`: Primary key
- `name`: Dataset name
- `original_filename`: Original file name
- `file_path`: Path to uploaded file
- `processed_file_path`: Path to processed file
- `file_type`: Type of file (csv, image, text)
- `file_size`: File size in bytes
- `rows_count`: Number of rows (for CSV)
- `columns_count`: Number of columns (for CSV)
- `preprocessing_status`: Current preprocessing status
- `preprocessing_log`: Log of preprocessing steps
- `user_id`: Foreign key to users table
- `created_at`: Upload timestamp
- `updated_at`: Last update timestamp

### Preprocessing Jobs Table
- `id`: Primary key
- `status`: Job status (pending, processing, completed, failed)
- `progress`: Progress percentage (0.0 to 1.0)
- `error_message`: Error message if failed
- `preprocessing_options`: JSON string of options used
- `dataset_id`: Foreign key to datasets table
- `created_at`: Job creation timestamp
- `completed_at`: Job completion timestamp

### API Keys Table
- `id`: Primary key
- `key`: API key string
- `name`: User-defined name for the key
- `is_active`: Key status
- `user_id`: Foreign key to users table
- `created_at`: Key creation timestamp
- `last_used`: Last usage timestamp

### Usage Stats Table
- `id`: Primary key
- `month`: Month (1-12)
- `year`: Year
- `datasets_uploaded`: Number of datasets uploaded this month
- `api_calls_made`: Number of API calls made this month
- `total_file_size`: Total file size uploaded this month
- `user_id`: Foreign key to users table

## File Structure

```
backend/
├── main.py                 # FastAPI application
├── config.py              # Configuration settings
├── database.py            # Database models and connection
├── auth.py                # Authentication logic
├── schemas.py             # Pydantic models
├── preprocessing.py       # Data preprocessing engine
├── dataset_manager.py     # Dataset management
├── user_tiers.py          # User tier management
├── groq_integration.py    # GroqCloud LLM integration
├── error_handlers.py      # Error handling and logging
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── data/                 # Uploaded files directory
├── logs/                 # Log files directory
└── flow.db              # SQLite database
```

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password hashing
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Input Validation**: Comprehensive input validation using Pydantic
- **File Type Validation**: Strict file type and size validation
- **Security Logging**: Comprehensive security event logging
- **CORS Protection**: Configurable CORS settings

## Monitoring and Logging

### Log Files
- `logs/flow_backend.log`: General application logs
- `logs/errors.log`: Error logs
- `logs/security.log`: Security event logs
- `logs/performance.log`: Performance metrics

### Health Check
```http
GET /health
```

## Deployment

### Production Considerations

1. **Environment Variables**: Set all environment variables in production
2. **Database**: Consider using PostgreSQL for production
3. **File Storage**: Use cloud storage (AWS S3, GCP Cloud Storage) for production
4. **Security**: Use strong secret keys and HTTPS
5. **Monitoring**: Set up proper monitoring and alerting
6. **Backup**: Implement database and file backup strategies

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t flow-backend .
docker run -p 8000:8000 flow-backend
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.
