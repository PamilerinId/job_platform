import uuid
import enum
from sqlalchemy import (
    TIMESTAMP, Column, ForeignKey, String, 
    Boolean, text, Enum, Integer, Text, ARRAY)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_mixins import AllFeaturesMixin

from core.dependencies.sessions import Base

class UserType(str, enum.Enum):
    CANDIDATE = 'CANDIDATE'
    CLIENT = 'CLIENT'
    ADMIN = 'ADMIN'
    SUPER_ADMIN = 'SUPER_ADMIN'
    


class Company(Base):
    __tablename__ = "companies"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    name = Column(String,  nullable=False) 
    slug = Column(String, nullable=False, unique=True)
    secret_key = Column(String, nullable=False, unique=True)#add client key and secret
    description = Column(Text, nullable=False)
    logo_url = Column(String, nullable=True) # TODO add file upload support for this
    owner_id=Column(String,  nullable=False) 
    members = relationship("User", back_populates="company")
    files_url = Column(ARRAY(String), nullable=True)
    # company verified checks [not a ble to post jobs unless verified]
    verified = Column(Boolean, nullable=False, server_default='False')

    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, onupdate=text("now()"))
    
    def __repr__(self):
        return f"<Compay {self.name}>"


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    first_name = Column(String,  nullable=False)
    last_name = Column(String,  nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    photo = Column(String, nullable=True)
    role = Column(Enum(UserType), server_default = UserType.CANDIDATE, nullable=False)

    # candidates by default have no company id
    company_id = Column(UUID, ForeignKey("companies.id"))
    company = relationship('Company')

    # user active checks
    email_verified = Column(Boolean, nullable=False, server_default='False')
    is_active = Column(Boolean, nullable=False, server_default='True')
    is_superuser = Column(Boolean, nullable=False, server_default='False')

    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, onupdate=text("now()"))
    
    def __repr__(self):
        return f"<User {self.email}>"



# class CandidateProfile(Base):
#     __tablename__ = "candidate_profiles"
#     industry_role, industries, cv(s), score, years of experience, 
#        current/desired earnings, skills
#      applications = relationship("Application")

# class CompanyProfile(Base):
#     __tablename__ = "company_profiles"
#     address, location, website, social, support_mail, funding, settings, 
# size, type,  rating as foreign key
#    


