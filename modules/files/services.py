from datetime import datetime
from typing import Annotated, List
from uuid import UUID, uuid4
from slugify import slugify

import magic

from fastapi import Depends, status, APIRouter, File, UploadFile
from modules.users.schemas import BaseUser
from sqlalchemy.orm import Session, joinedload

from core.dependencies.sessions import get_db
from core.dependencies.auth import get_current_user
from core.exceptions import NotFoundException, BadRequestException
from core.helpers.schemas import CustomListResponse, CustomResponse
from core.helpers.s3client import upload_files

from .models import File

router = APIRouter(
    prefix="/files",
)


KB = 1024
MB = 1024 * KB

SUPPORTED_FILE_TYPES = {
    'image/png': 'png',
    'image/jpeg': 'jpg',
    'application/pdf': 'pdf',
    'video/mp4': 'mp4'
}



@router.get("/", response_model=CustomListResponse, tags=["Files"])
async def fetch_my_files(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = '', 
                          current_user: str = Depends(get_current_user)):
    skip = (page - 1) * limit

    files = db.query(File).filter(
        File.owner_id == current_user.id).limit(limit).offset(skip).all()
    
    if len(files) < 1: 
        raise NotFoundException('No Files found')
    return {'message': 'File list retrieved successfully', 'count': len(files),'data': files}


@router.post("/upload", response_model=CustomResponse, tags=["Files"])
async def create_upload_file(file: UploadFile, 
                    current_user: Annotated[BaseUser, Depends(get_current_user)],
                   db: Session = Depends(get_db)):
    if not file:
        raise NotFoundException('No upload file sent')
    # else:
    #     return {"filename": file.name, "fileUrl": file.url}
    
    # check file size
    contents = await file.read()
    size = len(contents)

    if not 0 < size <= 5 * MB:
        raise BadRequestException('Supported file size is 0 - 5 MB')

    # filetype
    file_type = magic.from_buffer(buffer=contents, mime=True)
    if file_type not in SUPPORTED_FILE_TYPES:
        raise BadRequestException(f'Unsupported file type: {file_type}. Supported types are {SUPPORTED_FILE_TYPES}')
    file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES[file_type]}'

    # upload to s3
    uploaded_file_url = await upload_files(contents, file_name)

    print(uploaded_file_url, flush=True)

    # commit details to db
    # new_file = File({'owner_id': current_user.id, })
    # db.add(new_file)
    # db.commit()
    # db.refresh(new_file)

    return {'message': 'File uploaded successfully',
            'data': {"filename": 'new_file.name', "fileUrl": 'new_file.url'}}
# Admin Routes