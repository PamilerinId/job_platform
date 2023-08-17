import boto3  # pip install boto3

from core.env import config
from core.exceptions.base import BadRequestException


session = boto3.Session(
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
)

# Let's use Amazon S3
s3Client = session.client('s3')

# bucket = s3Client.Bucket(config.AWS_S3_BUCKET)

# Get file from s3
# Upload to s3 folder

async def generate_presigned_url(key: str):
    try:
        url = s3Client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': config.AWS_S3_BUCKET,
                'Key': key
            }
        )
        return url
    except Exception as err:
        raise BadRequestException(f'Error generating public url: {err}')

async def upload_files(contents: bytes, key: str):
    try:
        s3Client.put_object(Bucket=config.AWS_S3_BUCKET, Key=key, Body=contents)
        return await generate_presigned_url(key)
    except Exception as err:
        raise BadRequestException(f'Error uploading file: {err}')
