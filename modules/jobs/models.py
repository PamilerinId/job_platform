import uuid
from sqlalchemy import (TIMESTAMP, Column, ForeignKey, 
                        String, Boolean, text, Enum, Integer, Text, cast, Index)
from sqlalchemy.dialects.postgresql import ARRAY, array
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_mixins import AllFeaturesMixin


from core.dependencies.sessions import Base

# from services.users.models import Company
from .enums import (
    ExperienceLevel, Currency, JobType, JobStatus, 
                    LocationType, Qualification, ApplicationStatus)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    title = Column(String,  nullable=False) 
    slug = Column(String, nullable=False)
    description = Column(Text()) #extract keywords from text
    
    # Metadata
    type = Column(Enum(JobType), nullable=False)
    experienceLevel = Column(Enum(ExperienceLevel), nullable=False)
    status = Column(Enum(JobStatus), server_default=JobStatus.DRAFT, nullable=False)
    location = Column(String, nullable=False)
    locationType = Column(Enum(LocationType), nullable=False)
    qualifications = Column(ARRAY(Enum(Qualification)), nullable=False)
    salaryRangeFrom = Column(Integer(), nullable=False)
    salaryRangeTo = Column(Integer(), nullable=False)
    currency = Column(Enum(Currency))
    skills = Column(ARRAY(String), nullable=False)
    benefits = Column(ARRAY(String), nullable=False)

    deadline = Column(TIMESTAMP(timezone=True), nullable=False)

    # Tags (auto slugify, title, slug, type, experience, locationType, qualification,
    # currency, benefits)
    # tier = 
    tags = Column(ARRAY(Text), nullable=False, default=cast(array([], type_=Text), ARRAY(Text)))
    __table_args__ = (Index('ix_job_tags', tags, postgresql_using="gin"), )
# db.session.query(Post).filter(Post.tags.contains([tag]))
    # Company owner
    company_id=Column(UUID(as_uuid=True), ForeignKey("companies.id"))
    company = relationship("Company")

    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))
    

class Application(Base):
    __tablename__ = "applications"
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    status = Column(Enum(ApplicationStatus), server_default=ApplicationStatus.PENDING,nullable=False)

    # 
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))#one to many
    applicant_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))#many to one
    comment = Column(Text(),  nullable=True)

    job = relationship("Job")
    applicant = relationship("User")

    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))