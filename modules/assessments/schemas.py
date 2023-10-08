from uuid import UUID
from datetime import datetime
from typing import Any, List, Optional
from modules.assessments.models import AssessmentDifficulty, QuestionDifficulty, QuestionType, Status
from pydantic import field_validator, ConfigDict, BaseModel, Field, EmailStr, constr, HttpUrl, Json


class BaseAnswer(BaseModel):
    id: Optional[UUID] = None
    question_id: Optional[UUID] = None
    answer_text: Optional[str] = None
    boolean_text: Optional[bool] = None
    feedback: Optional[str] = None


class BaseQuestion(BaseModel):
    id: Optional[UUID] = None
    title: Optional[str] = None
    category: Optional[str] = None
    assessment_id: Optional[UUID]= None
    question_type: Optional[QuestionType] = None
    difficulty: Optional[QuestionDifficulty]
    options: Optional[List[str]] = None
    answers: Optional[List[BaseAnswer]] = None
    tags: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)


class BaseAssessment(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    slug: Optional[str]= None
    description: Optional[str] = None
    instruction: Optional[str] = None
    difficulty: Optional[AssessmentDifficulty]
    tags: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    duration: Optional[str] = None
    questions: List[BaseQuestion] = None
    model_config = ConfigDict(from_attributes=True)



class BaseUserResults(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    assessment_id: Optional[UUID] = None
    score: Optional[int] = None
    status: Optional[Status] = None
    result: Optional[Json[Any]] = None
    cooldown: Optional[datetime] = None 