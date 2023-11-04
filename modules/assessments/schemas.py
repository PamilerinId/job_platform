from uuid import UUID
from datetime import datetime
from typing import Any, List, Optional
from modules.assessments.models import AssessmentDifficulty, QuestionDifficulty, QuestionType, Status, Answer
from pydantic import field_validator, ConfigDict, BaseModel, Field, EmailStr, constr, HttpUrl, Json


class BaseAnswer(BaseModel):
    id: Optional[UUID] = None
    question_id: Optional[UUID] = None
    answer_text: str
    boolean_text: Optional[bool] = None
    is_correct: Optional[bool] = False
    feedback: str


class BaseQuestion(BaseModel):
    id: Optional[UUID] = None
    title: str
    category: Optional[str] = None
    assessment_id: UUID
    question_type: QuestionType
    difficulty: QuestionDifficulty
    # options: Optional[List[str]] = None
    answers: Optional[List[BaseAnswer]]  = None
    tags: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)


class BaseAssessment(BaseModel):
    id: Optional[UUID] = None
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    instructions: str
    difficulty: AssessmentDifficulty
    tags: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    duration: str
    questions: Optional[List[BaseQuestion]] = None
    model_config = ConfigDict(from_attributes=True)

class CreateAnswerSchema(BaseModel):
    answer_text: Optional[str] = None
    boolean_text: Optional[bool] = None
    is_correct: Optional[bool] = None
    feedback: str


class CreateQuestionSchema(BaseModel):
    title: str
    category: Optional[str] = None
    question_type: QuestionType
    difficulty: QuestionDifficulty
    # options: Optional[List[str]] = None
    answers: Optional[List[CreateAnswerSchema]]  = []
    tags: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)


class CreateAssessmentSchema(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    instructions: str
    difficulty: AssessmentDifficulty
    tags: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    duration: str
    questions: Optional[List[CreateQuestionSchema]] = []
    model_config = ConfigDict(from_attributes=True)



class BaseUserResults(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    assessment_id: Optional[UUID] = None
    score: Optional[int] = None
    status: Optional[Status] = None
    result: Optional[Json[Any]] = None
    cooldown: Optional[datetime] = None 