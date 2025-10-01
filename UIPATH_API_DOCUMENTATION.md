# UiPath Integration API Documentation

## Overview
This API allows UiPath to upload Excel/CSV files directly to the ML Analytics Dashboard and automatically trigger comprehensive analysis.

## Base URL
```
https://your-domain.com/api/uipath
```

## Endpoints

### 1. Upload File and Run Analysis
**POST** `/api/uipath/upload`

Uploads a file and automatically runs all ML analyses (churn, segmentation, sales forecasting).

#### Request
- **Content-Type**: `multipart/form-data`
- **Method**: POST
- **Body**: Form data with file field

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | File | Yes | Excel (.xlsx, .xls) or CSV file |

#### Supported File Types
- CSV files (`text/csv`)
- Excel files (`.xlsx`, `.xls`)
- Maximum file size: 50MB

#### Response
```json
{
  "success": true,
  "message": "File uploaded and analysis completed successfully",
  "fileName": "uipath_1759025000000.csv",
  "filePath": "/path/to/uploads/uipath_1759025000000.csv",
  "originalName": "customer_data.csv",
  "uploadTime": "2024-01-30T10:30:00.000Z",
  "analysis": {
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
  "dashboardUrl": "https://your-domain.com/dashboard"
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Error message description"
}
```

### 2. Check API Status
**GET** `/api/uipath/upload`

Returns API status and supported formats.

#### Response
```json
{
  "success": true,
  "message": "UiPath Upload API is running",
  "endpoints": {
    "upload": "POST /api/uipath/upload",
    "status": "GET /api/uipath/upload"
  },
  "supportedFormats": ["CSV", "Excel (.xlsx)", "Excel (.xls)"],
  "maxFileSize": "50MB"
}
```

## UiPath Implementation Example

### HTTP Request Activity
```
Method: POST
URL: https://your-domain.com/api/uipath/upload
Headers: 
  Content-Type: multipart/form-data
Body:
  file: [Your Excel/CSV file variable]
```

### Response Handling
1. Check `success` field in response
2. If `success: true`, the file was uploaded and analysis completed
3. Access `dashboardUrl` to redirect users to updated dashboard
4. Use `analysis` data for any additional processing

### Error Handling
- **400 Bad Request**: Invalid file type or no file provided
- **500 Internal Server Error**: Server-side processing error
- Check `error` field in response for details

## Dashboard Integration

After successful upload:
1. Dashboard automatically detects new file via localStorage
2. All charts and metrics update with new analysis results
3. Users can access updated data immediately
4. No manual refresh required

## File Processing Flow

1. **Upload**: File saved to `/uploads` directory
2. **Analysis**: Python ML scripts process the file
3. **Results**: Analysis results returned in API response
4. **Dashboard**: Frontend automatically updates with new data

## Security Considerations

- Files are validated for type and size
- Unique filenames prevent conflicts
- Server-side processing ensures data integrity
- No sensitive data exposed in API responses

## Testing

Use the GET endpoint to verify API availability:
```bash
curl -X GET https://your-domain.com/api/uipath/upload
```

Test file upload:
```bash
curl -X POST \
  -F "file=@your_test_file.csv" \
  https://your-domain.com/api/uipath/upload
```



