from uuid import UUID
from datetime import datetime
from typing import Any, List, Optional
from modules.assessments.models import AssessmentDifficulty, QuestionDifficulty, QuestionType, Status, Answer
from pydantic import field_validator, ConfigDict, BaseModel, Field, EmailStr, constr, HttpUrl, Json


class BaseAnswer(BaseModel):
    id: Optional[UUID] = None
    question_id: Optional[UUID] = None
    answer_text: Optional[str] = None
    boolean_text: Optional[bool] = None
    is_correct: Optional[bool] = False
    feedback: Optional[str] 


class BaseQuestion(BaseModel):
    id: Optional[UUID] = None
    title: Optional[str] = None
    category: Optional[str] = None
    assessment_id: Optional[UUID]= None
    question_type: Optional[QuestionType] = None
    difficulty: Optional[QuestionDifficulty] = None
    # options: Optional[List[str]] = None
    answers: Optional[List[BaseAnswer]]  = None
    tags: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)


class BaseAssessment(BaseModel):
    id: Optional[UUID] = None
    name: Optional[str] = None
    slug: Optional[str]= None
    description: Optional[str] = None
    instructions: Optional[str] = None
    difficulty: Optional[AssessmentDifficulty] = None
    tags: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    duration: Optional[str] = None
    questions: Optional[List[BaseQuestion]] = None
    model_config = ConfigDict(from_attributes=True)

class CreateAnswerSchema(BaseModel):
    question_id: Optional[UUID] = None
    answer_text: Optional[str] = None
    boolean_text: Optional[bool] = None
    is_correct: Optional[bool] = None
    feedback: Optional[str] 


class CreateQuestionSchema(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    assessment_id: Optional[UUID]= None
    question_type: Optional[QuestionType] = None
    difficulty: Optional[QuestionDifficulty] = None
    # options: Optional[List[str]] = None
    answers: Optional[List[CreateAnswerSchema]]  = []
    tags: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)


class CreateAssessmentSchema(BaseModel):
    name: Optional[str] = None
    slug: Optional[str]= None
    description: Optional[str] = None
    instructions: Optional[str] = None
    difficulty: Optional[AssessmentDifficulty] = None
    tags: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    duration: Optional[str] = None
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