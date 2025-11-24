"""
Supabase Storage utilities for file uploads
Replaces local filesystem storage for Vercel deployment
"""
import os
from werkzeug.utils import secure_filename
from config import Config
from datetime import datetime
from models import Database
import io
from PIL import Image


def get_storage_client():
    """Get Supabase storage client"""
    db = Database()
    return db.get_client().storage


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def upload_to_supabase(file, bucket_name, folder, prefix=''):
    """
    Upload file to Supabase Storage
    Returns: public URL of uploaded file
    """
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        # Create unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = secure_filename(file.filename)
        filename = f"{prefix}_{timestamp}_{original_filename}" if prefix else f"{timestamp}_{original_filename}"
        
        # Full path in bucket
        file_path = f"{folder}/{filename}"
        
        # Read file content
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Get storage client
        storage = get_storage_client()
        
        # Upload to Supabase
        storage.from_(bucket_name).upload(
            file_path,
            file_content,
            file_options={"content-type": get_mime_type(filename)}
        )
        
        # Get public URL
        public_url = storage.from_(bucket_name).get_public_url(file_path)
        
        return public_url
        
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")
        return None


def save_contractor_signature(file, contractor_name):
    """Save contractor signature to Supabase Storage"""
    prefix = secure_filename(contractor_name.replace(' ', '_'))
    return upload_to_supabase(file, 'signatures', 'contractor_signatures', prefix)


def save_employee_photo(file, employee_name):
    """Save employee photo to Supabase Storage"""
    prefix = secure_filename(employee_name.replace(' ', '_'))
    # Optimize image before upload
    optimized_file = optimize_image_file(file)
    return upload_to_supabase(optimized_file, 'photos', 'employee_photos', prefix)


def save_employee_signature(file, employee_name):
    """Save employee signature to Supabase Storage"""
    prefix = secure_filename(employee_name.replace(' ', '_'))
    return upload_to_supabase(file, 'signatures', 'employee_signatures', prefix)


def save_approval_signature(file, department, approver_name):
    """Save approval signature (Medical, Safety) to Supabase Storage"""
    prefix = f"{department}_{secure_filename(approver_name.replace(' ', '_'))}"
    return upload_to_supabase(file, 'signatures', 'approval_signatures', prefix)


def save_hod_signature(file, department):
    """Save HOD signature to Supabase Storage"""
    prefix = f"HOD_{secure_filename(department.replace(' ', '_'))}"
    return upload_to_supabase(file, 'signatures', 'hod_signatures', prefix)


def optimize_image_file(file, max_size=(800, 800)):
    """
    Optimize image file size while maintaining quality
    Returns file-like object
    """
    try:
        img = Image.open(file)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if too large
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        output = io.BytesIO()
        img.save(output, 'JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # Create file-like object with filename
        from werkzeug.datastructures import FileStorage
        return FileStorage(
            stream=output,
            filename=file.filename,
            content_type='image/jpeg'
        )
    except Exception as e:
        print(f"Error optimizing image: {e}")
        file.seek(0)
        return file


def get_mime_type(filename):
    """Get MIME type from filename"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    mime_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'pdf': 'application/pdf'
    }
    return mime_types.get(ext, 'application/octet-stream')


def create_storage_buckets():
    """
    Create Supabase Storage buckets if they don't exist
    Run this once during initial setup
    """
    storage = get_storage_client()
    
    buckets = ['signatures', 'photos', 'idcards']
    
    for bucket in buckets:
        try:
            # Create bucket with public access
            storage.create_bucket(bucket, options={"public": True})
            print(f"Created bucket: {bucket}")
        except Exception as e:
            print(f"Bucket {bucket} may already exist: {e}")
