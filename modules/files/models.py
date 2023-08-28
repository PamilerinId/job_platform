import enum
import uuid

from sqlalchemy import (TIMESTAMP, Column, ForeignKey, 
                        String, Boolean, text, Enum, Integer, 
                        Text, cast, Index)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from core.dependencies.sessions import Base

class FileType(str, enum.Enum):
    PROFILE_PHOTO = 'PROFILE_PHOTO'
    RESUME = 'RESUME'
    COVER_LETTER = 'COVER_LETTER'
    VIDEO = 'VIDEO'
    LOGO = 'LOGO'

class File(Base):
    __tablename__ = "files"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    name = Column(String,  nullable=False) 
    url = Column(String, nullable=False, unique=True)
    type = Column(Enum(FileType), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))#one to many
    owner = relationship('User')

    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))
    
    def __repr__(self):
        return f"<File {self.name}>"