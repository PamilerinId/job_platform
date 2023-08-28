from uuid import UUID
from datetime import datetime
from typing import Any, List, Optional
from modules.files.models import FileType
from pydantic import field_validator, ConfigDict, BaseModel, Field, EmailStr, constr, HttpUrl


class File(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    url: Optional[HttpUrl]= None
    type: Optional[FileType] = None
    model_config = ConfigDict(from_attributes=True)