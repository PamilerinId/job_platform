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
    feedback: Optional[str] = ""


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
    answer_text: str
    boolean_text: Optional[bool] = False
    is_correct: Optional[bool] = False
    feedback: Optional[str] = ""


class CreateQuestionSchema(BaseModel):
    title: str
    category: Optional[str] = ""
    question_type: QuestionType 
    difficulty: Optional[QuestionDifficulty] = QuestionDifficulty.MEDIUM 
    # options: Optional[List[str]] = None
    answers: Optional[List[CreateAnswerSchema]] = []
    tags: Optional[List[str]] = []
    model_config = ConfigDict(from_attributes=True)


class CreateAssessmentSchema(BaseModel):
    name: str
    slug: Optional[str] = ""
    description: Optional[str] = None
    instructions: str
    difficulty: AssessmentDifficulty
    tags: Optional[List[str]] = []
    skills: Optional[List[str]] = []
    duration: str
    questions: Optional[List[CreateQuestionSchema]] = []
    model_config = ConfigDict(from_attributes=True)



class ScoreDetails(BaseModel):
    total_questions: Optional[int] = 0
    total_score: Optional[int] = 0
    percentage: Optional[int] = 0
    status: Optional[Status] = Status.FAIL 


class CreateQuestionResults(BaseModel):
    question_id: UUID
    answer: BaseAnswer
    model_config = ConfigDict(from_attributes=True)
    
    
    
class CreateAssessmentResults(BaseModel):
    assessment_id: UUID
    user_id: Optional[UUID] = None
    submission: List[CreateQuestionResults]
    model_config = ConfigDict(from_attributes=True)
    
    
    
class BaseUserResults(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    assessment_id: Optional[UUID] = None
    assessment_name: str
    description: Optional[str] = None
    difficulty: AssessmentDifficulty
    duration: str
    score: Optional[int] = None
    status: Optional[Status] = None
    results: Optional[Json[Any]] = None
    cooldown: Optional[datetime] = None 
    model_config = ConfigDict(from_attributes=True)