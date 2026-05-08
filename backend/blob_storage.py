"""Azure Blob Storage handler for file uploads"""

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import AzureError
from config import (
    AZURE_STORAGE_CONNECTION_STRING,
    AZURE_BLOB_CONTAINER_NAME,
    ALLOWED_MEDIA_TYPES,
    MAX_UPLOAD_SIZE
)
import os
from datetime import datetime
import mimetypes


class BlobStorageManager:
    """Manages Azure Blob Storage operations for file uploads"""
    
    def __init__(self):
        """Initialize Blob Storage client"""
        if not AZURE_STORAGE_CONNECTION_STRING:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable not set")
        
        self.blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_STORAGE_CONNECTION_STRING
        )
        self.container_name = AZURE_BLOB_CONTAINER_NAME
        self._ensure_container_exists()
    
    def _ensure_container_exists(self):
        """Ensure the blob container exists, create if it doesn't"""
        try:
            self.blob_service_client.get_container_client(self.container_name).get_container_properties()
        except AzureError:
            # Container doesn't exist, create it
            self.blob_service_client.create_container(name=self.container_name)
    
    def upload_file(self, file_content: bytes, filename: str, user_id: str, content_type: str) -> dict:
        """
        Upload a file to Azure Blob Storage
        
        Args:
            file_content: The file content as bytes
            filename: Original filename
            user_id: User ID for organization
            content_type: MIME type of the file
        
        Returns:
            Dictionary with upload metadata including blob URL
        
        Raises:
            ValueError: If file validation fails
            AzureError: If upload fails
        """
        # Validate file type
        if content_type not in ALLOWED_MEDIA_TYPES:
            raise ValueError(f"File type {content_type} not allowed. Allowed types: {ALLOWED_MEDIA_TYPES}")
        
        # Validate file size
        file_size = len(file_content)
        if file_size > MAX_UPLOAD_SIZE:
            raise ValueError(f"File size {file_size} exceeds maximum allowed size of {MAX_UPLOAD_SIZE}")
        
        # Create blob path: users/{user_id}/{timestamp}_{filename}
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        blob_path = f"users/{user_id}/{timestamp}_{filename}"
        
        try:
            # Get container client
            container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Upload file
            blob_client = container_client.upload_blob(
                name=blob_path,
                data=file_content,
                overwrite=False,
                metadata={
                    "original_filename": filename,
                    "user_id": str(user_id),
                    "upload_timestamp": timestamp,
                    "content_type": content_type
                }
            )
            
            return {
                "blob_url": blob_client.url,
                "blob_name": blob_path,
                "file_size": file_size,
                "content_type": content_type,
                "upload_timestamp": timestamp
            }
        
        except AzureError as e:
            raise Exception(f"Failed to upload file to Azure Blob Storage: {str(e)}")
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Delete a file from Azure Blob Storage
        
        Args:
            blob_name: Name/path of the blob to delete
        
        Returns:
            True if deletion successful
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            container_client.delete_blob(blob_name)
            return True
        except AzureError as e:
            raise Exception(f"Failed to delete file from Azure Blob Storage: {str(e)}")
    
    def get_blob_url(self, blob_name: str, expiry_hours: int = 24) -> str:
        """
        Get a blob URL with optional SAS token for temporary access
        
        Args:
            blob_name: Name/path of the blob
            expiry_hours: Hours until SAS token expires (0 for permanent link)
        
        Returns:
            Full blob URL
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_client = container_client.get_blob_client(blob_name)
            return blob_client.url
        except AzureError as e:
            raise Exception(f"Failed to get blob URL: {str(e)}")
    
    def list_user_files(self, user_id: str) -> list:
        """
        List all files uploaded by a specific user
        
        Args:
            user_id: User ID to filter files
        
        Returns:
            List of blob properties
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_list = container_client.list_blobs(name_starts_with=f"users/{user_id}/")
            
            files = []
            for blob in blob_list:
                files.append({
                    "blob_name": blob.name,
                    "size": blob.size,
                    "created_at": blob.creation_time.isoformat() if blob.creation_time else None,
                    "metadata": blob.metadata or {}
                })
            return files
        except AzureError as e:
            raise Exception(f"Failed to list user files: {str(e)}")


# Singleton instance
_blob_manager = None


def get_blob_manager() -> BlobStorageManager:
    """Get or initialize the Blob Storage Manager singleton"""
    global _blob_manager
    if _blob_manager is None:
        _blob_manager = BlobStorageManager()
    return _blob_manager
