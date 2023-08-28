import boto3  # pip install boto3
from botocore.client import Config


from core.env import config
from core.exceptions.base import BadRequestException
from modules.files.models import FileType


session = boto3.Session(
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    region_name=config.AWS_S3_REGION
)

# Let's use Amazon S3
s3Client = session.client('s3', config=Config(signature_version='s3v4'))

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

async def upload_files(contents: bytes, key: str, type: FileType):
    try:
        if type == FileType.PROFILE_PHOTO or type == FileType.LOGO:
            folder = config.AWS_S3_FOLDER_PHOTOS 
        elif type == FileType.RESUME or type == FileType.COVER_LETTER:
            folder = config.AWS_S3_FOLDER_CVS
        elif type == FileType.VIDEO:
            folder = config.AWS_S3_FOLDER_PROCTOR

        file_name = folder + '/' + key
        s3Client.put_object(Bucket=config.AWS_S3_BUCKET, Key=file_name, Body=contents)
        return await generate_presigned_url(file_name)
    except Exception as err:
        raise BadRequestException(f'Error uploading file: {err}')
