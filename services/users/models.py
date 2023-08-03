import uuid
import enum
from sqlalchemy import (TIMESTAMP, Column, ForeignKey, 
                        String, Boolean, text, Enum, Integer, 
                        Text, cast, Index)
from sqlalchemy.dialects.postgresql import ARRAY, array
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_mixins import AllFeaturesMixin

from core.dependencies.sessions import Base

class UserType(str, enum.Enum):
    CANDIDATE = 'CANDIDATE'
    CLIENT = 'CLIENT'
    ADMIN = 'ADMIN'
    SUPER_ADMIN = 'SUPER_ADMIN'


class CompanySize(str, enum.Enum):
    UNDER_50 = 'UNDER_50'
    UNDER_100 = 'UNDER_100'
    UNDER_500 = 'UNDER_500'
    OVER_1000 = 'OVER_1000'
    


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

    profile = relationship(
            "CompanyProfile",
            back_populates="company", uselist=False)

    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))
    
    def __repr__(self):
        return f"<Company {self.name}>"
    
class CompanyProfile(Base):
    __tablename__ = "company_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    company = relationship("Company", back_populates='profile')
    address = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    website = Column(String, nullable=True)
    support_mail = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    funding = Column(String, nullable=True)
    size = Column(Enum(CompanySize), nullable=True)
    # type = Column(Enum(UserType), nullable=True)
    # settings, type,  rating as foreign key   

    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))



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
    # candidate_profile = relationship('CandidateProfile', uselist=False, backref="users")
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
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))
    
    def __repr__(self):
        return f"<User {self.email}>"

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    phone = Column(String, nullable=True)
    industry_role = Column(String, nullable=True)
    
    industries = Column(ARRAY(String), nullable=True, default=cast(array([], type_=String), ARRAY(String)))
    __table_args__ = (Index('ix_candidate_industries', industries, postgresql_using="gin"), )
    
    cv = Column(ARRAY(String), nullable=True) # Foreign key to Files
    years_of_experience = Column(Integer, nullable=True)
    
    skills =  Column(ARRAY(String), nullable=False, default=cast(array([], type_=String), ARRAY(String)))
    __table_args__ = (Index('ix_candidate_skills', industries, postgresql_using="gin"), )

    current_earnings = Column(String, nullable=True)
    desired_earnings = Column(String, nullable=True)

    user =  relationship('User')

    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))

