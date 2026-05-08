# Azure Blob Storage File Upload Setup

## Overview
The Toddly application is configured to support file uploads to **Azure Blob Storage**, which is a cloud-based solution for storing media files (images and videos) uploaded by users.

## Requirements Added

### Python Dependencies
The following packages have been added to `requirements.txt`:
- `azure-storage-blob==12.18.3` - Azure Blob Storage SDK for Python
- `python-multipart==0.0.6` - Required for handling file uploads in FastAPI

## File Structure

### New Files Created

#### 1. **blob_storage.py**
Handles all Azure Blob Storage operations:
- `BlobStorageManager` class - Main manager for blob operations
- `upload_file()` - Upload files to Azure Blob Storage
- `delete_file()` - Delete files from Azure Blob Storage
- `get_blob_url()` - Get blob URLs
- `list_user_files()` - List all files for a user
- `get_blob_manager()` - Singleton factory function

### Modified Files

#### 1. **config.py**
Added Azure Blob Storage configuration:
```python
AZURE_STORAGE_ACCOUNT_NAME      # Storage account name
AZURE_STORAGE_ACCOUNT_KEY       # Storage account key
AZURE_STORAGE_CONNECTION_STRING # Full connection string
AZURE_BLOB_CONTAINER_NAME       # Container name (default: toddly-uploads)
MAX_UPLOAD_SIZE                 # Max file size: 50 MB
ALLOWED_IMAGE_TYPES             # Allowed image MIME types
ALLOWED_VIDEO_TYPES             # Allowed video MIME types
ALLOWED_MEDIA_TYPES             # Combined allowed types
```

#### 2. **models.py**
Added `Post` model for storing file metadata:
- `id` - Unique post ID (UUID)
- `user_id` - Foreign key to User
- `blob_name` - Path in Azure Blob Storage
- `blob_url` - Public URL of the uploaded file
- `content_type` - MIME type of the file
- `file_size` - Size of the file in bytes
- `caption` - Optional description
- `created_at` / `updated_at` - Timestamps

#### 3. **schemas.py**
Added Pydantic schemas for file uploads:
- `PostCreate` - Request schema for creating posts
- `PostResponse` - Response schema for individual posts
- `PostListResponse` - Response schema for post listings
- `FileUploadResponse` - Response schema for upload confirmation
- `PostWithUserResponse` - Post with user information
- `UserWithPostsResponse` - User with their posts

#### 4. **.env.example**
Updated with Azure Blob Storage configuration examples

## Environment Setup

### 1. Azure Storage Account Configuration
Create an Azure Storage Account and add to `.env`:

```env
# Option 1: Use Connection String (Recommended)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=mystorageacct;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net

# Option 2: Use Individual Values
AZURE_STORAGE_ACCOUNT_NAME=mystorageacct
AZURE_STORAGE_ACCOUNT_KEY=YOUR_KEY

# Container configuration
AZURE_BLOB_CONTAINER_NAME=toddly-uploads
```

### 2. Get Azure Credentials
1. Go to [Azure Portal](https://portal.azure.com)
2. Create or select a Storage Account
3. Navigate to **Access Keys** → **Connection string**
4. Copy the connection string to your `.env` file

### 3. File Organization in Azure
Files are organized by user:
```
toddly-uploads/
├── users/
│   ├── {user-id-1}/
│   │   ├── 20240508_143022_photo.jpg
│   │   └── 20240508_143045_video.mp4
│   └── {user-id-2}/
│       └── 20240508_150101_family.jpg
```

## Supported File Types

### Images
- `image/jpeg` (.jpg, .jpeg)
- `image/png` (.png)
- `image/webp` (.webp)
- `image/gif` (.gif)

### Videos
- `video/mp4` (.mp4)
- `video/quicktime` (.mov)
- `video/x-msvideo` (.avi)

### Limits
- **Maximum file size**: 50 MB
- **Container**: `toddly-uploads` (or custom via `AZURE_BLOB_CONTAINER_NAME`)

## Usage Example

### Upload a File
```python
from blob_storage import get_blob_manager

# Get the manager
blob_manager = get_blob_manager()

# Upload file
result = blob_manager.upload_file(
    file_content=file_bytes,
    filename="my-photo.jpg",
    user_id="user-123",
    content_type="image/jpeg"
)

# Returns:
# {
#     "blob_url": "https://mystorageacct.blob.core.windows.net/...",
#     "blob_name": "users/user-123/20240508_143022_my-photo.jpg",
#     "file_size": 2048576,
#     "content_type": "image/jpeg",
#     "upload_timestamp": "20240508_143022"
# }
```

### List User Files
```python
files = blob_manager.list_user_files(user_id="user-123")
# Returns list of files with metadata
```

### Delete a File
```python
success = blob_manager.delete_file(blob_name="users/user-123/20240508_143022_my-photo.jpg")
```

## FastAPI Integration

### Example Upload Endpoint (To be added to main.py)
```python
from fastapi import File, UploadFile, Depends
from blob_storage import get_blob_manager

@app.post("/api/posts/upload")
async def upload_post(
    file: UploadFile = File(...),
    caption: Optional[str] = None,
    current_user_id: str = Depends(get_user_id_from_token),
    db: Session = Depends(get_db)
):
    """Upload a file and create a post"""
    
    blob_manager = get_blob_manager()
    file_content = await file.read()
    
    # Upload to blob storage
    upload_result = blob_manager.upload_file(
        file_content=file_content,
        filename=file.filename,
        user_id=current_user_id,
        content_type=file.content_type
    )
    
    # Create post record in database
    new_post = Post(
        user_id=current_user_id,
        blob_name=upload_result["blob_name"],
        blob_url=upload_result["blob_url"],
        content_type=upload_result["content_type"],
        file_size=upload_result["file_size"],
        caption=caption
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return FileUploadResponse(
        post_id=str(new_post.id),
        blob_url=new_post.blob_url,
        content_type=new_post.content_type,
        file_size=new_post.file_size
    )
```

## Database Migration

After updating models, run database migration:
```bash
# If using Alembic (recommended for production)
alembic revision --autogenerate -m "Add Post model for file uploads"
alembic upgrade head

# For development with SQLite/auto-migration
# Just restart the application and it will create the new table
```

## Security Considerations

1. **File Type Validation**: Only allowed MIME types are accepted
2. **File Size Limits**: 50 MB maximum per file
3. **User Isolation**: Files are organized by user ID in blob storage
4. **Authentication**: All endpoints require authentication tokens
5. **Metadata Tracking**: Upload metadata stored for auditing

## Troubleshooting

### Connection String Issues
- Verify `AZURE_STORAGE_CONNECTION_STRING` in `.env`
- Check that the storage account is accessible
- Ensure the container name is correctly configured

### File Upload Fails
- Check file type is in `ALLOWED_MEDIA_TYPES`
- Verify file size < 50 MB
- Ensure user is authenticated

### Container Not Found
- The container is auto-created on first upload
- Verify connection string has proper permissions
- Check `AZURE_BLOB_CONTAINER_NAME` in config

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Add Azure credentials to `.env` file
3. Add upload endpoints to `main.py` (example provided above)
4. Add file upload UI to frontend (HTML/JavaScript)
5. Test with curl or Postman

## References

- [Azure Blob Storage Documentation](https://docs.microsoft.com/azure/storage/blobs/)
- [azure-storage-blob Python SDK](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/storage/azure-storage-blob)
- [FastAPI File Uploads](https://fastapi.tiangolo.com/tutorial/request-files/)
