#!/usr/bin/env python3
"""
Setup MinIO bucket for file storage
"""
import boto3
from botocore.exceptions import ClientError

# MinIO configuration
MINIO_ENDPOINT = 'http://localhost:9000'
MINIO_ACCESS_KEY = 'minioadmin'
MINIO_SECRET_KEY = 'minioadmin123'
BUCKET_NAME = 'bugbounty-files'

def setup_minio():
    """Initialize MinIO bucket with proper configuration"""
    print("Connecting to MinIO...")
    
    # Create S3 client
    s3_client = boto3.client(
        's3',
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name='us-east-1'
    )
    
    # Check if bucket exists
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        print(f"✓ Bucket '{BUCKET_NAME}' already exists")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            # Create bucket
            print(f"Creating bucket '{BUCKET_NAME}'...")
            s3_client.create_bucket(Bucket=BUCKET_NAME)
            print(f"✓ Bucket '{BUCKET_NAME}' created successfully")
        else:
            print(f"✗ Error checking bucket: {e}")
            return False
    
    # Set bucket policy to allow public read access
    # This allows the frontend to access files directly
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{BUCKET_NAME}/*"]
            }
        ]
    }
    
    try:
        import json
        s3_client.put_bucket_policy(
            Bucket=BUCKET_NAME,
            Policy=json.dumps(bucket_policy)
        )
        print(f"✓ Bucket policy set to allow public read access")
    except ClientError as e:
        print(f"⚠ Warning: Could not set bucket policy: {e}")
        print("  Files may not be publicly accessible")
    
    # Set CORS configuration
    cors_configuration = {
        'CORSRules': [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': ['ETag'],
                'MaxAgeSeconds': 3000
            }
        ]
    }
    
    try:
        s3_client.put_bucket_cors(
            Bucket=BUCKET_NAME,
            CORSConfiguration=cors_configuration
        )
        print(f"✓ CORS configuration set for browser access")
    except ClientError as e:
        print(f"⚠ Warning: Could not set CORS: {e}")
    
    print("\n✓ MinIO setup complete!")
    print(f"  Bucket: {BUCKET_NAME}")
    print(f"  Endpoint: {MINIO_ENDPOINT}")
    print(f"  Console: http://localhost:9001")
    print(f"  Access Key: {MINIO_ACCESS_KEY}")
    
    return True

if __name__ == '__main__':
    setup_minio()
