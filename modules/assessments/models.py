import uuid
import enum
from sqlalchemy import (TIMESTAMP, Column, ForeignKey, 
                        String, Boolean, text, Enum, Integer, 
                        Text, cast, Index)
from sqlalchemy.dialects.postgresql import ARRAY, array, JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy_mixins import AllFeaturesMixin

from core.dependencies.sessions import Base


class AssessmentDifficulty(str, enum.Enum):
    GRADUATE = 'GRADUATE'
    ENTRY = 'ENTRY'
    JUNIOR = 'JUNIOR'
    INTERMEDIATE = 'INTERMEDIATE'
    SENIOR = 'SENIOR'
    C_LEVEL = 'C_LEVEL'


class QuestionDifficulty(str, enum.Enum):
    EASY='Easy'
    MEDIUM='Medium'
    HARD='Hard'

class QuestionType(str, enum.Enum):
    SINGLE_CHOICE = "Single_Choice"
    MULTIPLE_CHOICE = "Multiple_Choice"
    TRUE_FALSE= "True_False"

class Status(str, enum.Enum):
    PASS = "Pass"
    FAIL="Fail"
    


class Assessment(Base):
    __tablename__ = 'assessments'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    name = Column(String,  nullable=False, unique=True) 
    slug = Column(String, nullable=True)
    description = Column(Text,  nullable=False)
    instructions = Column(Text,  nullable=False)
    difficulty = Column(Enum(AssessmentDifficulty))
    questions = relationship('Question', back_populates='assessment')

    tags = Column(ARRAY(Text), nullable=False, default=cast(array([], type_=Text), ARRAY(Text)))
    __table_args__ = (Index('ix_assessments_tags', tags, postgresql_using="gin"), )

    skills = Column(ARRAY(String), nullable=False)
    duration = Column(String, nullable=False) # In Minutes
    

    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))
    
    def __repr__(self):
        return f"<Assessment {self.id}>"
    

class Question(Base):
    __tablename__ = 'questions'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    assessment_id = Column(UUID(), ForeignKey('assessments.id'), index=True,)
    difficulty = Column(Enum(QuestionDifficulty))
    question_type = Column(Enum(QuestionType))
    category = Column(String, nullable=False)

    title = Column(String, nullable=False)
    options = Column(ARRAY(String), nullable=True)
    assessment = relationship('Assessment', back_populates='questions')
    answers = relationship('Answer', back_populates='question')

    tags = Column(ARRAY(Text), nullable=False, default=cast(array([], type_=Text), ARRAY(Text)))
    __table_args__ = (Index('ix_questions_tags', tags, postgresql_using="gin"), )

    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))
    
    def __repr__(self):
        return f"<Question {self.title}>"


class Answer(Base):
    __tablename__ = 'answers'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    question_id = Column(UUID(), ForeignKey('questions.id'), index=True,)
    answer_text = Column(String, nullable=True)
    boolean_text = Column(Boolean, nullable=True)
    is_correct = Column(Boolean, nullable=False)
    feedback = Column(Text,  nullable=False)

    question = relationship('Question', back_populates='answers')

    
    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"),)
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))
    
    def __repr__(self):
        return f"{self.id}"
    

class JobAssessment(Base):
    __tablename__ = 'job_assessments'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    assessment_id = Column(UUID(), ForeignKey('assessments.id'), index=True,)
    job_id =  Column(UUID(), ForeignKey('jobs.id'), index=True,)


class UserResult(Base):
    __tablename__ = 'user_assessments'
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False,
                default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey('users.id'), index=True,)
    results = Column(JSONB)  # TODO: change to JSONB when supported by SQLAlchemy
    assessment_id = Column(UUID(), ForeignKey('assessments.id'), index=True,)
    score = Column(Integer, nullable=True)
    status = Column(Enum(Status))
    cooldown = Column(TIMESTAMP(timezone=True), nullable=False)

    # Audit logs
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text("now()"), onupdate=text("now()"))
    
    def __repr__(self):
        return f"<Assessment Result: {self.id}>"