
from typing import Annotated, Union
from uuid import UUID
from fastapi import Depends, HTTPException, status, APIRouter, Response, Path, File, UploadFile


from core.dependencies.sessions import get_db
from core.dependencies.auth import get_current_user
from core.helpers.schemas import CustomResponse, CustomListResponse
from core.helpers.text_utils import to_slug
from modules.users.schemas import BaseUser

from .models import Assessment, Question, Answer, UserResult
from .schemas import BaseAssessment, BaseQuestion, BaseAnswer, BaseUserResults, CreateAssessmentSchema
from .repository import AssessmentRepository, QuestionRepository, UserResultRepository

router = APIRouter(
    prefix="/assessments"
)


assessmentRepo = AssessmentRepository()
questionRepo = QuestionRepository()
resultRepo = UserResultRepository()

# CRUD assessments - exposed only; questions and answer not exposed
# fetch and update delete results
@router.post('/', response_model=CustomResponse[BaseAssessment], tags=["Assessment"])
async def create_assessments(payload: BaseAssessment):
    """Create a new assessment""" 
    
    try:
        newAssesment = await assessmentRepo.create(payload)
        return {"message":"Assessment fetched successfully","data": newAssesment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/', response_model=CustomListResponse[BaseAssessment], tags=["Assessment"])
async def fetch_assessments(current_user: Annotated[BaseUser, Depends(get_current_user)],
                            limit: int = 10, page: int = 1, search: str = ''):
    
    assessments = await assessmentRepo.get_list(page=page, limit=limit, filter=search)

    return {'message': 'Assessments retrieved successfully', 'count': len(assessments), 'data': assessments}


@router.get('/{assessment_id}', response_model=CustomResponse[BaseAssessment], tags=["Assessment"])
async def fetch_assessment(assessment_id: Annotated[UUID, Path(title="")],):
    assessment = await assessmentRepo.get_by_id(assessment_id=assessment_id)

    return {"message":"Assessment fetched successfully", "data": assessment}

@router.put('/{assessment_id}', response_model=CustomResponse[BaseAssessment], tags=["Assessment"])
async def update_assessments(assessment_id: Annotated[UUID, Path(title="ID of assessment being fetched")],
                             payload: BaseAssessment):
    assessment = await assessmentRepo.update(payload)

    return {"message":"Assessment fetched successfully","data": assessment}


@router.delete('/{assessment_id}', response_model=CustomResponse, tags=["Assessment"])
async def delete_assessments(assessment_id: Annotated[UUID, Path(title="The ID of the assessment to be deleted")],
               current_user: Annotated[BaseUser, Depends(get_current_user)],):
    assessment = await assessmentRepo.delete(assessment_id)
    return assessment

@router.post('/questions', response_model=CustomResponse[BaseAssessment], tags=["Question", "Assessment"])
async def add_assessment_questions(payload: BaseQuestion):
    assessment = await assessmentRepo.get(assessment_id=payload.assessment_id)

    question = await questionRepo.create_with_answers(payload, payload.assessment_id)
    # get list of question object
    # call create question on each object
    # creates question with details and options??
    # runs through options and creates answer with answer as correct bool where answer objects

    return {"message":"Assessment fetched successfully","data": assessment}


@router.get('/results/{assessment_id}', response_model=CustomListResponse[BaseUserResults], tags=["Assessment"])
async def fetch_assessment_results(assessment_id: Annotated[UUID, Path(title="ID of assessment being fetched")], 
                                    limit: int = 10, page: int = 1, search: str = ''):
    results = await resultRepo.get_by_assessment_id(page=page, limit=limit, assessment_id=assessment_id)

    return {'message': 'Assessments retrieved successfully', 'count': len(results), 'data': results}

@router.get('/results/{user_id}', response_model=CustomListResponse[BaseUserResults], tags=["Assessment"])
async def fetch_user_results(user_id: Annotated[UUID, Path(title="ID of assessment being fetched")],
                             limit: int = 10, page: int = 1, search: str = ''):
    results = await resultRepo.get_by_assessment_id(page=page, limit=limit, user_id=user_id)

    return {'message': 'Assessments retrieved successfully', 'count': len(results), 'data': results}

# @router.get('/results/{user_id}/{assessment_id}', response_model=CustomResponse[BaseUserResults], tags=["Assessment"])
# async def fetch_user_assessment_result():
#     pass

