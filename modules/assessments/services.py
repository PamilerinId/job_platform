
from typing import Annotated, Union
from uuid import UUID, uuid4
from fastapi import Depends, HTTPException, status, APIRouter, Response, Path, UploadFile, Form

from core.exceptions import NotFoundException, BadRequestException
from core.dependencies.sessions import get_db
from core.dependencies.auth import get_current_user
from core.helpers.schemas import CustomResponse, CustomListResponse
from core.helpers.s3client import upload_files
from core.helpers.text_utils import to_slug
from core.helpers.csv_utils import generate_questions
from modules.users.schemas import BaseUser

from modules.files.models import FileType, File
from .models import Assessment, Question, Answer, UserResult, AssessmentDifficulty
from .schemas import BaseAssessment, BaseQuestion, CreateQuestionSchema, BaseUserResults, CreateAssessmentSchema, CreateAssessmentResults
from .repository import AssessmentRepository, QuestionRepository, UserResultRepository

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from modules.users.models import User
import magic

router = APIRouter(
    prefix="/assessments"
)


assessmentRepo = AssessmentRepository()
questionRepo = QuestionRepository()
resultRepo = UserResultRepository()

KB = 1024
MB = 1024 * KB

SUPPORTED_FILE_TYPES = {
    'text/csv': 'csv',
}

# CRUD assessments - exposed only; questions and answer not exposed
# fetch and update delete results
@router.post('/', response_model=CustomResponse[BaseAssessment], tags=["Assessments"])
async def create_assessments(payload: CreateAssessmentSchema,
                             current_user: Annotated[User, Depends(get_current_user)]):
    """Create a new assessment""" 
    
    try:
        new_assessment = await assessmentRepo.create(payload)
        return {"message":"Assessment fetched successfully","data": new_assessment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.put("/upload-csv/{assessment_id}", response_model=CustomResponse[BaseAssessment], tags=["Files"])
async def update_assessment_by_csv(file: UploadFile, assessment_id: Annotated[UUID, Path(title="")],
                                current_user: Annotated[User, Depends(get_current_user)],
                                db: Session = Depends(get_db)
                            ):
    
    if not file:
        raise NotFoundException('No upload file sent')
    
    
    # check file size
    contents = await file.read()
    size = len(contents)

    if not 0 < size <= 5 * MB:
        raise BadRequestException('Supported file size is 0 - 5 MB')

    # filetype
    file_type = magic.from_buffer(buffer=contents, mime=True)
    if file_type not in SUPPORTED_FILE_TYPES:
        raise BadRequestException(f'Unsupported file type: {file_type}. Supported types are {SUPPORTED_FILE_TYPES}')
    file_name = f'{uuid4()}.{SUPPORTED_FILE_TYPES[file_type]}'
    
    # upload to s3
    uploaded_file_url = await upload_files(contents, file_name, FileType.ASSESSMENT)
    
    # new_file = File(**{'owner_id': current_user.id, 'name': file_name, 'type': FileType.ASSESSMENT, 'url': uploaded_file_url })
    # db.add(new_file)
    # db.commit()
    
    # db.refresh(new_file)
    await generate_questions(uploaded_file_url, assessment_id)
    
    payload = await assessmentRepo.get_by_id(assessment_id)
    
    return {"message":"Assessment fetched successfully", "data": payload}
    
    
    
    

@router.get('/', response_model=CustomListResponse[BaseAssessment], tags=["Assessments"])
async def fetch_assessments(current_user: Annotated[BaseUser, Depends(get_current_user)],
                            limit: int = 10, page: int = 1, search: str = ''):
    
    assessments = await assessmentRepo.get_list(page=page, limit=limit, filter=search)

    return {'message': 'Assessments retrieved successfully', 'count': len(assessments), 'data': assessments}


@router.get('/{assessment_id}', response_model=CustomResponse[BaseAssessment], tags=["Assessments"])
async def fetch_assessment(assessment_id: Annotated[UUID, Path(title="")],):
    assessment = await assessmentRepo.get_by_id(assessment_id=assessment_id)

    return {"message":"Assessment fetched successfully", "data": assessment}

@router.put('/{assessment_id}', response_model=CustomResponse[BaseAssessment], tags=["Assessments"])
async def update_assessments(assessment_id: Annotated[UUID, Path(title="ID of assessment being fetched")],
                             payload: BaseAssessment):
    
    await assessmentRepo.update(payload)
    
    assessment = await assessmentRepo.get_by_id(assessment_id) 

    return {"message":"Assessment fetched successfully","data": assessment}


@router.delete('/{assessment_id}', response_model=CustomResponse, tags=["Assessments"])
async def delete_assessments(assessment_id: Annotated[UUID, Path(title="The ID of the assessment to be deleted")],
               current_user: Annotated[BaseUser, Depends(get_current_user)]):
    assessment = await assessmentRepo.delete(assessment_id)
    return assessment













    
#Assessment questions

@router.post('/{assessment_id}/questions', response_model=CustomResponse[BaseQuestion], tags=["Questions", "Assessments"])
async def create_assessment_questions(assessment_id: Annotated[UUID, Path(title="The ID of the assessment to be fetched")],
                            payload: CreateQuestionSchema):
    
    await assessmentRepo.get_by_id(assessment_id=assessment_id)
    question = await questionRepo.create_with_answers(payload, assessment_id)
    # get list of question object
    # call create question on each object
    # creates question with details and options?s?
    # runs through options and creates answer with answer as correct bool where answer objects

    return {"message":"Question added successfully","data": question}


@router.get('/{assessment_id}/questions/{question_id}', response_model=CustomResponse[BaseQuestion], tags=["Questions", "Assessments"])
async def fetch_assessment_question(assessment_id: Annotated[UUID, Path(title="The ID of the assessment to be fetched")],
                                    question_id: Annotated[UUID, Path(title="The ID of the question to be fetched")],
                                   current_user: Annotated[BaseUser, Depends(get_current_user)]):
    
    await assessmentRepo.get_by_id(assessment_id=assessment_id)
    question = await questionRepo.get(question_id=question_id)
    
    return {"message":"Question fetched successfully","data": question}


@router.delete('/{assessment_id}/questions/{question_id}', response_model=CustomResponse, tags=["Questions", "Assessments"])
async def delete_assessment_questions(assessment_id: Annotated[UUID, Path(title="The ID of the assessment to be fetched")],
                                    question_id: Annotated[UUID, Path(title="The ID of the question to be deleted")],
                                current_user: Annotated[BaseUser, Depends(get_current_user)]):
    
    await assessmentRepo.get_by_id(assessment_id=assessment_id)
    question = await questionRepo.delete(question_id)

    return question










#Assessment results

@router.post('/results', response_model=CustomListResponse[BaseUserResults], tags=["Assessments", "Results"])
async def create_assessment_results(payload: CreateAssessmentResults, 
                                    current_user: Annotated[BaseUser, Depends(get_current_user)]):
    
    assessment: BaseAssessment = await assessmentRepo.get_by_id(payload.assessment_id)
    
    results = await resultRepo.create(payload)
    results = results.__dict__
    results.update({
        "assessment_name": assessment.name,
        "description": assessment.description,
        "difficulty": assessment.difficulty,
        "duration": assessment.duration,  
    })

    return {'message': 'Results created successfully', 'data': [results]}




@router.get('/results/{user_id}', response_model=CustomListResponse[BaseUserResults], tags=["Assessments", "Results"])
async def fetch_user_results(user_id: Annotated[UUID, Path(title="ID of user")],
                             limit: int = 10, page: int = 1, search: str = ''):
    print("here")
    results = await resultRepo.get_by_user_id(page=page, limit=limit, user_id=user_id)

    
    for result in results:
        assessment: BaseAssessment = await assessmentRepo.get_by_id(assessment_id = result.assessment_id)
        result = result.__dict__
        result.update({
            "assessment_name": assessment.name,
            "description": assessment.description,
            "difficulty": assessment.difficulty,
            "duration": assessment.duration,  
        })

    return {'message': 'Assessments retrieved successfully', 'count': len(results), 'data': results}


@router.get('/{assessment_id}/results/', response_model=CustomListResponse[BaseUserResults], tags=["Assessments", "Results"])
async def fetch_assessment_results(assessment_id: Annotated[UUID, Path(title="ID of assessment being fetched")],
                                   limit: int = 10, page: int = 1, search: str = ''):
    
    assessment: BaseAssessment = await assessmentRepo.get_by_id(assessment_id=assessment_id)
    results = await resultRepo.get_by_assessment_id(page=page, limit=limit, assessment_id=assessment_id)
    
    for result in results:
        result = result.__dict__
        result.update({
            "assessment_name": assessment.name,
            "description": assessment.description,
            "difficulty": assessment.difficulty,
            "duration": assessment.duration,  
        })

    return {'message': 'Assessments retrieved successfully', 'count': len(results), 'data': results}


@router.get('/{assessment_id}/results/{result_id}', response_model=CustomListResponse[BaseUserResults], tags=["Assessments", "Results"])
async def fetch_result(assessment_id: Annotated[UUID, Path(title="ID of assessment being fetched")],
                result_id: Annotated[UUID, Path(title="ID of result being fetched")]):
    result = await resultRepo.get_by_result_id(result_id=result_id)
    assessment: BaseAssessment = await assessmentRepo.get_by_id(assessment_id)
    result = result.__dict__
    result.update({
        "assessment_name": assessment.name,
        "description": assessment.description,
        "difficulty": assessment.difficulty,
        "duration": assessment.duration,  
    })

    return {'message': 'Assessments retrieved successfully', 'data': [result]}




# @router.get('/results/{user_id}/{assessment_id}', response_model=CustomResponse[BaseUserResults], tags=["Assessments"])
# async def fetch_user_assessment_result():
#     pass

