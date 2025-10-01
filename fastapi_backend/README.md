# FastAPI ML Analytics Backend

## Overview
A high-performance FastAPI backend for ML Analytics Dashboard with UiPath integration. Provides RESTful APIs for file upload, ML analysis, and data retrieval.

## Features
- 🚀 **FastAPI Framework**: High-performance async API
- 📊 **ML Analysis**: Churn, Segmentation, Sales Forecasting
- 🔄 **Background Processing**: Non-blocking file analysis
- 📝 **Auto Documentation**: Swagger UI and ReDoc
- 🔒 **CORS Support**: Cross-origin requests
- 💾 **Caching**: In-memory result caching
- 🧪 **Health Checks**: API monitoring endpoints

## Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
```bash
# Clone or navigate to the fastapi_backend directory
cd fastapi_backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Using Startup Scripts
```bash
# Windows
start_server.bat

# Linux/Mac
chmod +x start_server.sh
./start_server.sh
```

## API Endpoints

### Base URL
```
http://localhost:8000
```

### 1. Root Endpoint
**GET** `/`
Returns API information and available endpoints.

**Response:**
```json
{
  "message": "ML Analytics API is running",
  "version": "1.0.0",
  "endpoints": {
    "upload": "POST /upload",
    "status": "GET /status",
    "analysis": "GET /analysis/{file_id}",
    "health": "GET /health"
  },
  "docs": "/docs"
}
```

### 2. Health Check
**GET** `/health`
Returns API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-30T10:30:00.000Z",
  "cache_size": 5
}
```

### 3. API Status
**GET** `/status`
Returns detailed API status and configuration.

**Response:**
```json
{
  "status": "running",
  "timestamp": "2024-01-30T10:30:00.000Z",
  "supported_formats": ["csv", "xlsx", "xls"],
  "max_file_size": "50MB",
  "python_available": true,
  "uploads_directory": true
}
```

### 4. File Upload
**POST** `/upload`
Uploads a file and triggers ML analysis.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**: Form data with `file` field

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully. Analysis started.",
  "file_id": "1759025000000",
  "file_info": {
    "file_id": "1759025000000",
    "filename": "uipath_1759025000000.csv",
    "original_name": "customer_data.csv",
    "file_path": "uploads/uipath_1759025000000.csv",
    "size": 1024000,
    "upload_time": "2024-01-30T10:30:00.000Z",
    "status": "uploaded"
  },
  "analysis_url": "/analysis/1759025000000"
}
```

### 5. Get Analysis Results
**GET** `/analysis/{file_id}`
Retrieves analysis results for a specific file.

**Response:**
```json
{
  "success": true,
  "file_id": "1759025000000",
  "file_info": {
    "file_id": "1759025000000",
    "filename": "uipath_1759025000000.csv",
    "original_name": "customer_data.csv",
    "file_path": "uploads/uipath_1759025000000.csv",
    "size": 1024000,
    "upload_time": "2024-01-30T10:30:00.000Z",
    "status": "completed"
  },
  "analysis": {
    "status": "completed",
    "results": {
      "churn": {
        "success": true,
        "data": {
          "metrics": {
            "current_churn_rate": 0.15,
            "average_churn_prob": 0.23,
            "total_churners": 150
          },
          "churn_rate_trends": [...],
          "top_churn_customers": [...],
          "churn_factors": [...]
        }
      },
      "segmentation": {
        "success": true,
        "data": {
          "segmented_customers": [...],
          "cluster_metrics": [...]
        }
      },
      "sales": {
        "success": true,
        "data": {
          "forecast": [...],
          "top10_products": [...],
          "seasonal_patterns": [...]
        }
      }
    },
    "completed_at": "2024-01-30T10:35:00.000Z"
  },
  "timestamp": "2024-01-30T10:35:00.000Z"
}
```

### 6. Get All Analyses
**GET** `/analysis`
Retrieves all cached analyses.

**Response:**
```json
{
  "success": true,
  "analyses": {
    "1759025000000": {
      "status": "completed",
      "results": {...},
      "completed_at": "2024-01-30T10:35:00.000Z"
    }
  },
  "count": 1,
  "timestamp": "2024-01-30T10:35:00.000Z"
}
```

### 7. Delete Analysis
**DELETE** `/analysis/{file_id}`
Deletes analysis results and associated file.

**Response:**
```json
{
  "success": true,
  "message": "Analysis 1759025000000 deleted successfully"
}
```

## UiPath Integration

### HTTP Request Activity Configuration
```
Method: POST
URL: http://localhost:8000/upload
Content-Type: multipart/form-data
Body:
  file: [Your Excel/CSV file variable]
```

### Response Handling
1. Check `success` field in response
2. Extract `file_id` for subsequent requests
3. Use `analysis_url` to check analysis status
4. Poll `/analysis/{file_id}` until `status: "completed"`

### Example UiPath Workflow
1. **Upload File**: POST to `/upload`
2. **Get File ID**: Extract `file_id` from response
3. **Poll Analysis**: GET `/analysis/{file_id}` every 30 seconds
4. **Process Results**: Use analysis data when `status: "completed"`

## API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Testing with curl
```bash
# Upload file
curl -X POST \
  -F "file=@test_data.csv" \
  http://localhost:8000/upload

# Check analysis status
curl http://localhost:8000/analysis/1759025000000

# Get all analyses
curl http://localhost:8000/analysis

# Health check
curl http://localhost:8000/health
```

## Error Handling

### Common Error Responses
```json
{
  "detail": "Invalid file type. Allowed: .csv, .xlsx, .xls"
}
```

```json
{
  "detail": "Analysis not found or still in progress"
}
```

### HTTP Status Codes
- **200**: Success
- **400**: Bad Request (invalid file type, missing file)
- **404**: Not Found (analysis not found)
- **500**: Internal Server Error (ML analysis failed)

## Configuration

### Environment Variables
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `RELOAD`: Auto-reload on changes (default: True)

### File Limits
- **Max File Size**: 50MB
- **Supported Formats**: CSV, Excel (.xlsx, .xls)
- **Upload Directory**: `uploads/`

## Performance Features

### Caching
- In-memory analysis result caching
- File metadata caching
- Automatic cache cleanup

### Background Processing
- Non-blocking file uploads
- Async ML analysis execution
- Progress tracking

### Monitoring
- Health check endpoints
- Request logging
- Error tracking

## Production Deployment

### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Gunicorn
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Troubleshooting

### Common Issues
1. **Python not found**: Ensure Python 3.8+ is installed
2. **ML scripts not found**: Check `scripts/ml_analyzer.py` exists
3. **Permission errors**: Ensure write access to `uploads/` directory
4. **Analysis fails**: Check Python dependencies are installed

### Logs
- Server logs: Console output
- Analysis logs: Check ML script output
- Error logs: FastAPI error responses



