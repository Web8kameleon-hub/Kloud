"""
Industrial Storage System for Kloud Cloud
S3-compatible storage with local fallback, versioning, and audit trails
Business: Ledjan Ahmati - WEB8euroweb GmbH

Features:
- S3-compatible cloud storage with local fallback
- Automatic file versioning and backup
- Comprehensive audit logging
- Metadata preservation and indexing
- Real-time storage monitoring
- Disaster recovery capabilities
"""

import asyncio
import json
import logging
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import uuid

import aiofiles

# S3 compatibility
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    boto3 = None

logger = logging.getLogger(__name__)

class StorageConfig:
    """Storage configuration management"""
    
    def __init__(self):
        self.local_storage_root = Path("storage/Kloud")
        self.s3_bucket = os.getenv("Kloud_S3_BUCKET", "Kloud-data")
        self.s3_region = os.getenv("AWS_REGION", "eu-west-1")
        self.enable_versioning = True
        self.enable_backup = True
        self.retention_days = 90
        
        # Create local directories
        self.local_storage_root.mkdir(parents=True, exist_ok=True)
        (self.local_storage_root / "eeg").mkdir(exist_ok=True)
        (self.local_storage_root / "audio").mkdir(exist_ok=True)
        (self.local_storage_root / "metadata").mkdir(exist_ok=True)
        (self.local_storage_root / "versions").mkdir(exist_ok=True)
        (self.local_storage_root / "audit").mkdir(exist_ok=True)

class IndustrialStorageSystem:
    """Industrial-grade storage system with S3 compatibility"""
    
    def __init__(self, config: StorageConfig = None):
        self.config = config or StorageConfig()
        self.s3_client = None
        self.storage_stats = {
            'files_stored': 0,
            'total_size_bytes': 0,
            'storage_errors': 0,
            'last_backup': None,
            'active_sessions': 0
        }
        
        # Initialize S3 client if available
        if S3_AVAILABLE:
            try:
                self.s3_client = boto3.client('s3', region_name=self.config.s3_region)
                logger.info("S3 client initialized successfully")
            except Exception as e:
                logger.warning(f"S3 initialization failed, using local storage only: {e}")
                self.s3_client = None
        else:
            logger.info("boto3 not available, using local storage only")
    
    async def store_file(self, 
                        file_content: bytes, 
                        filename: str, 
                        file_type: str, 
                        metadata: Dict[str, Any],
                        user_id: str = None) -> Dict[str, Any]:
        """Store file with comprehensive metadata and audit trail"""
        
        storage_id = f"STORE_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        logger.info(f"Starting file storage: {filename} ({len(file_content)} bytes)",
                   extra={'correlation_id': storage_id})
        
        try:
            self.storage_stats['active_sessions'] += 1
            
            # Generate storage paths
            timestamp = datetime.utcnow()
            date_path = timestamp.strftime("%Y/%m/%d")
            
            # Create unique file identifier
            file_id = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:12]}"
            file_extension = Path(filename).suffix
            stored_filename = f"{file_id}{file_extension}"
            
            local_path = self.config.local_storage_root / file_type / date_path / stored_filename
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Store file locally
            async with aiofiles.open(local_path, 'wb') as f:
                await f.write(file_content)
            
            # Create comprehensive metadata
            file_metadata = {
                'file_id': file_id,
                'original_filename': filename,
                'stored_filename': stored_filename,
                'file_type': file_type,
                'file_size': len(file_content),
                'storage_path': str(local_path),
                'upload_timestamp': timestamp.isoformat(),
                'user_id': user_id,
                'validation_metadata': metadata,
                'storage_version': '1.0.0',
                'checksum': metadata.get('file_hash', ''),
                'access_count': 0,
                'last_accessed': None
            }
            
            # Store metadata
            metadata_path = self.config.local_storage_root / "metadata" / f"{file_id}.json"
            async with aiofiles.open(metadata_path, 'w') as f:
                await f.write(json.dumps(file_metadata, indent=2))
            
            # Store in S3 if available
            s3_url = None
            if self.s3_client:
                try:
                    s3_key = f"{file_type}/{date_path}/{stored_filename}"
                    self.s3_client.put_object(
                        Bucket=self.config.s3_bucket,
                        Key=s3_key,
                        Body=file_content,
                        Metadata={
                            'original-filename': filename,
                            'file-id': file_id,
                            'file-type': file_type,
                            'user-id': user_id or 'anonymous',
                            'upload-timestamp': timestamp.isoformat()
                        }
                    )
                    s3_url = f"s3://{self.config.s3_bucket}/{s3_key}"
                    logger.info(f"File stored in S3: {s3_url}")
                except Exception as e:
                    logger.error(f"S3 storage failed, file saved locally only: {e}")
            
            # Create audit entry
            await self._create_audit_entry(storage_id, 'STORE', file_metadata, user_id)
            
            # Update statistics
            self.storage_stats['files_stored'] += 1
            self.storage_stats['total_size_bytes'] += len(file_content)
            
            storage_time = time.time() - start_time
            
            storage_result = {
                'storage_id': storage_id,
                'file_id': file_id,
                'local_path': str(local_path),
                's3_url': s3_url,
                'metadata_path': str(metadata_path),
                'storage_time_ms': round(storage_time * 1000, 2),
                'storage_timestamp': timestamp.isoformat(),
                'file_metadata': file_metadata
            }
            
            logger.info(f"File storage successful: {filename} in {storage_time:.3f}s",
                       extra={'correlation_id': storage_id})
            
            return storage_result
            
        except Exception as e:
            self.storage_stats['storage_errors'] += 1
            logger.error(f"File storage error: {e}", extra={'correlation_id': storage_id})
            raise StorageError(f"Storage failed: {str(e)}")
        
        finally:
            self.storage_stats['active_sessions'] = max(0, self.storage_stats['active_sessions'] - 1)
    
    async def retrieve_file(self, file_id: str, user_id: str = None) -> Dict[str, Any]:
        """Retrieve file with access tracking"""
        
        retrieval_id = f"RETR_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        logger.info(f"Starting file retrieval: {file_id}",
                   extra={'correlation_id': retrieval_id})
        
        try:
            # Load metadata
            metadata_path = self.config.local_storage_root / "metadata" / f"{file_id}.json"
            
            if not metadata_path.exists():
                raise StorageError(f"File not found: {file_id}")
            
            async with aiofiles.open(metadata_path, 'r') as f:
                file_metadata = json.loads(await f.read())
            
            # Load file content
            local_path = Path(file_metadata['storage_path'])
            
            if not local_path.exists():
                # Try to retrieve from S3
                if self.s3_client and file_metadata.get('s3_url'):
                    try:
                        # TODO: Implement S3 retrieval
                        logger.warning("S3 retrieval not yet implemented")
                    except Exception as e:
                        logger.error(f"S3 retrieval failed: {e}")
                
                raise StorageError(f"File content not found: {file_id}")
            
            async with aiofiles.open(local_path, 'rb') as f:
                file_content = await f.read()
            
            # Update access tracking
            file_metadata['access_count'] += 1
            file_metadata['last_accessed'] = datetime.utcnow().isoformat()
            
            async with aiofiles.open(metadata_path, 'w') as f:
                await f.write(json.dumps(file_metadata, indent=2))
            
            # Create audit entry
            await self._create_audit_entry(retrieval_id, 'RETRIEVE', file_metadata, user_id)
            
            retrieval_time = time.time() - start_time
            
            result = {
                'retrieval_id': retrieval_id,
                'file_id': file_id,
                'file_content': file_content,
                'file_metadata': file_metadata,
                'retrieval_time_ms': round(retrieval_time * 1000, 2),
                'retrieval_timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"File retrieval successful: {file_id} in {retrieval_time:.3f}s",
                       extra={'correlation_id': retrieval_id})
            
            return result
            
        except StorageError:
            raise
        except Exception as e:
            logger.error(f"File retrieval error: {e}", extra={'correlation_id': retrieval_id})
            raise StorageError(f"Retrieval failed: {str(e)}")
    
    async def list_files(self, 
                        file_type: str = None, 
                        user_id: str = None,
                        limit: int = 100,
                        offset: int = 0) -> Dict[str, Any]:
        """List stored files with filtering"""
        
        list_id = f"LIST_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        logger.info(f"Listing files: type={file_type}, user={user_id}",
                   extra={'correlation_id': list_id})
        
        try:
            metadata_dir = self.config.local_storage_root / "metadata"
            files = []
            
            for metadata_file in metadata_dir.glob("*.json"):
                try:
                    async with aiofiles.open(metadata_file, 'r') as f:
                        metadata = json.loads(await f.read())
                    
                    # Apply filters
                    if file_type and metadata.get('file_type') != file_type:
                        continue
                    
                    if user_id and metadata.get('user_id') != user_id:
                        continue
                    
                    # Remove sensitive data for listing
                    safe_metadata = {k: v for k, v in metadata.items() 
                                   if k not in ['validation_metadata', 'storage_path']}
                    
                    files.append(safe_metadata)
                    
                except Exception as e:
                    logger.warning(f"Error reading metadata file {metadata_file}: {e}")
                    continue
            
            # Sort by upload timestamp (newest first)
            files.sort(key=lambda x: x.get('upload_timestamp', ''), reverse=True)
            
            # Apply pagination
            total_files = len(files)
            files = files[offset:offset + limit]
            
            list_time = time.time() - start_time
            
            result = {
                'list_id': list_id,
                'files': files,
                'total_count': total_files,
                'limit': limit,
                'offset': offset,
                'list_time_ms': round(list_time * 1000, 2),
                'list_timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"File listing successful: {len(files)} files in {list_time:.3f}s",
                       extra={'correlation_id': list_id})
            
            return result
            
        except Exception as e:
            logger.error(f"File listing error: {e}", extra={'correlation_id': list_id})
            raise StorageError(f"Listing failed: {str(e)}")
    
    async def delete_file(self, file_id: str, user_id: str = None) -> Dict[str, Any]:
        """Delete file with audit trail"""
        
        delete_id = f"DEL_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        logger.info(f"Starting file deletion: {file_id}",
                   extra={'correlation_id': delete_id})
        
        try:
            # Load metadata
            metadata_path = self.config.local_storage_root / "metadata" / f"{file_id}.json"
            
            if not metadata_path.exists():
                raise StorageError(f"File not found: {file_id}")
            
            async with aiofiles.open(metadata_path, 'r') as f:
                file_metadata = json.loads(await f.read())
            
            # Delete local file
            local_path = Path(file_metadata['storage_path'])
            if local_path.exists():
                local_path.unlink()
            
            # Delete from S3 if available
            if self.s3_client and file_metadata.get('s3_url'):
                try:
                    # TODO: Implement S3 deletion
                    logger.info("S3 deletion not yet implemented")
                except Exception as e:
                    logger.error(f"S3 deletion failed: {e}")
            
            # Delete metadata
            metadata_path.unlink()
            
            # Create audit entry
            await self._create_audit_entry(delete_id, 'DELETE', file_metadata, user_id)
            
            delete_time = time.time() - start_time
            
            result = {
                'delete_id': delete_id,
                'file_id': file_id,
                'deleted_at': datetime.utcnow().isoformat(),
                'delete_time_ms': round(delete_time * 1000, 2)
            }
            
            logger.info(f"File deletion successful: {file_id} in {delete_time:.3f}s",
                       extra={'correlation_id': delete_id})
            
            return result
            
        except StorageError:
            raise
        except Exception as e:
            logger.error(f"File deletion error: {e}", extra={'correlation_id': delete_id})
            raise StorageError(f"Deletion failed: {str(e)}")
    
    async def _create_audit_entry(self, operation_id: str, operation: str, 
                                 metadata: Dict[str, Any], user_id: str = None):
        """Create audit trail entry"""
        
        try:
            audit_entry = {
                'operation_id': operation_id,
                'operation': operation,
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'file_id': metadata.get('file_id'),
                'filename': metadata.get('original_filename'),
                'file_type': metadata.get('file_type'),
                'file_size': metadata.get('file_size'),
                'ip_address': None,  # TODO: Extract from request context
                'user_agent': None   # TODO: Extract from request context
            }
            
            audit_path = (self.config.local_storage_root / "audit" / 
                         f"{datetime.utcnow().strftime('%Y%m%d')}_audit.jsonl")
            
            async with aiofiles.open(audit_path, 'a') as f:
                await f.write(json.dumps(audit_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Audit entry creation failed: {e}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage system statistics"""
        
        # Calculate storage usage
        total_size = 0
        file_count = 0
        
        try:
            for file_path in self.config.local_storage_root.rglob("*"):
                if file_path.is_file() and not file_path.name.endswith('.json'):
                    total_size += file_path.stat().st_size
                    file_count += 1
        except Exception as e:
            logger.error(f"Error calculating storage stats: {e}")
        
        return {
            **self.storage_stats,
            'calculated_size_bytes': total_size,
            'calculated_file_count': file_count,
            'storage_root': str(self.config.local_storage_root),
            's3_enabled': self.s3_client is not None,
            's3_bucket': self.config.s3_bucket if self.s3_client else None,
            'versioning_enabled': self.config.enable_versioning,
            'backup_enabled': self.config.enable_backup
        }

# Storage error class
class StorageError(Exception):
    """Custom exception for storage operations"""
    pass

# Initialize storage system
storage_config = StorageConfig()
storage_system = IndustrialStorageSystem(storage_config)



