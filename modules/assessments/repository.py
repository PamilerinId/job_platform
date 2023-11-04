from sqlalchemy.orm import Session, joinedload
from typing import List


from fastapi import Depends

from core.exceptions.base import BadRequestException, NotFoundException
from core.dependencies.sessions import get_db

from .models import Assessment, Question, Answer, UserResult, AssessmentDifficulty, QuestionDifficulty, QuestionType
from .schemas import *


class AssessmentRepository:
    def __init__(
        self, db: Session = get_db().__next__()
    ) -> None:
        self.db = db

    
    async def getOrCreate(self, payload: CreateAssessmentSchema):
        if payload.id:
            assessment = self.db.query(Assessment).filter(Assessment.id==payload.id).first()
            if assessment is None:
                raise NotFoundException("No assessment not found!")
        else:            
            assessment = self.create(payload=payload)

        return assessment

    
    async def create(self, payload: CreateAssessmentSchema):
        
        assessment = self.db.query(Assessment).filter(Assessment.name==payload.name).first()
        if assessment is not None:
            raise BadRequestException("Assessment already exists!")
        
        assessment = Assessment(
            name = payload.name,
            slug = payload.slug,
            description = payload.description,
            instructions = payload.instructions,
            difficulty = payload.difficulty,
            tags = payload.tags,
            skills = payload.skills,
            duration = payload.duration,
        )
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        for question_item in payload.questions:
            question =  Question(
             title = question_item.title,
             category = question_item.category,
             assessment_id = assessment.id,
             question_type = question_item.question_type,
             difficulty = question_item.difficulty,
             tags = question_item.tags,
            )
            self.db.add(question)
            self.db.commit()
            print(f"Question id is {question.id}")
            for answer_item in question_item.answers:
                answer = Answer(
                    question_id = question.id,
                    answer_text = answer_item.answer_text,
                    boolean_text = answer_item.boolean_text,
                    is_correct = answer_item.is_correct,
                    feedback = answer_item.feedback
                )
                self.db.add(answer)
            self.db.commit()
            self.db.refresh(answer)
        
        self.db.commit()
        self.db.refresh(question)
        self.db.refresh(assessment)
        return assessment

    
    async def get_by_id(self, assessment_id: str):
        assessment = self.db.query(Assessment).options(joinedload(Assessment.questions)
                                                       .joinedload(Question.answers)).filter(Assessment.id==assessment_id).first()
        if assessment is None:
            raise NotFoundException("Assessment not found!")
        
        return assessment

    
    async def get_list(self,  page: int, limit: int, filter: str):
        self.db.rollback()
        skip = (page - 1) * limit

        assessments = self.db.query(Assessment
                                    ).order_by(Assessment.created_at.desc()
                                                         ).limit(limit).offset(skip).all()
        
        if len(assessments) < 1:
            raise NotFoundException("Assessments not found!")  
        return assessments
    

    async def get_by_difficulty(self,  page: int, limit: int, difficulty: AssessmentDifficulty):
        skip = (page - 1) * limit
        assessments = self.db.query(Assessment).filter(Assessment.difficulty == difficulty
            ).order_by(Assessment.created_at.desc()
                       ).limit(limit).offset(skip).all()
        return assessments

    
    async def update(self, payload: BaseAssessment):
        print(payload)
        assessment_query = self.db.query(Assessment).filter(Assessment.id==payload.id)
        assessment = assessment_query.first()
        
        if assessment is None:
            raise NotFoundException("Assessment not found!")
        
        for quest in range(0, len(assessment.questions)):
            for ans in range(0, len(assessment.questions[quest].answers)):
                answer_query = self.db.query(Answer).filter(Answer.id == assessment.questions[quest].answers[ans].id)
                answer_query = answer_query.__dict__
                assessment.questions[quest].answers[ans].__dict__.pop("_sa_instance_state")
                answer_query.update(assessment.questions[quest].answers[ans].__dict__, synchronize_session=False)
                self.db.commit()
            
            question_obj = self.db.query(Question).filter(Question.id == assessment.questions[quest].id)
            payload.questions[quest].__dict__.pop("answers")
            question_obj.update(payload.questions[quest].__dict__, synchronize_session=False)
            self.db.commit()
        payload.__dict__.pop("questions")
        assessment_query.update(payload.__dict__, synchronize_session=False)
        self.db.commit()
        
        return assessment

    
    async def delete(self, assessment_id: str):
        assessment_query = self.db.query(Assessment).filter(Assessment.id==assessment_id)
        assessment = assessment_query.first()
        if assessment is None:
            raise NotFoundException("Assessment not found!")
        
        try:
            self.db.delete(assessment)
            self.db.commit()
            return {"message": "Assessment deleted successfully"}
        except BadRequestException:
            self.db.rollback()
            raise BadRequestException("Assessment delete failed")



class QuestionRepository:
    def __init__(self) -> None:
        self.db: Session = get_db().__next__()

    async def create(self, payload: BaseQuestion, assessment_id: str):
        question = Question(**payload.__dict__)
        question.assessment_id = assessment_id
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)

        return question
    
    async def create_with_answers(self, payload:BaseQuestion, assessment_id: str):
        new_question = await self.create(payload, assessment_id)  # Create the base question first
        for answer in payload.answers:
            await AnswerRepository().create(answer)
        return new_question 


    async def get(self, question_id: str):
        question = self.db.query(Question).filter(Question.id==question_id).first()
        if question is None:
            raise NotFoundException("Question not found!")
        
        return question


    async def get_list(self,  page: int, limit: int, filter):
        skip = (page - 1) * limit

        questions = self.db.query(Question
                                    ).order_by(Question.created_at.desc()
                                                         ).limit(limit).offset(skip).all()

        if len(questions) is None:
            raise NotFoundException("Question not found!")  
        return questions
    

    async def get_by_assessment(self,  page: int, limit: int, assessment_id: str):
        skip = (page - 1) * limit
        questions = self.db.query(Question).filter(Question.assessment_id == assessment_id
            ).order_by(Question.created_at.desc()
                       ).limit(limit).offset(skip).all()
        return questions
    

    async def get_by_difficulty(self,  page: int, limit: int, difficulty: QuestionDifficulty):
        skip = (page - 1) * limit
        questions = self.db.query(Question).filter(Question.difficulty == difficulty
            ).order_by(Question.created_at.desc()
                       ).limit(limit).offset(skip).all()
        return questions
    

    async def get_by_type(self,  page: int, limit: int, type: QuestionType):
        skip = (page - 1) * limit
        questions = self.db.query(Question).filter(Question.type == type
            ).order_by(Question.created_at.desc()
                       ).limit(limit).offset(skip).all()
        return questions
    

    async def get_by_category(self,  page: int, limit: int, category: str):
        skip = (page - 1) * limit
        questions = self.db.query(Question).filter(Question.category == category
            ).order_by(Question.created_at.desc()
                       ).limit(limit).offset(skip).all()
        return questions


    async def update(self, payload):
        question_query = self.db.query(Question).filter(Question.id==payload.id)
        question = question_query.first()
        if question is None:
            raise NotFoundException("Question not found!")
        
        question_query.update(payload.dict(exclude_unset=True), synchronize_session=False)

        self.db.add(question)
        self.db.commit()

        return question
    

    async def delete(self, question_id: str):
        question_query = self.db.query(Question).filter(Question.id==question_id)
        question = question_query.first()
        if question is None:
            raise NotFoundException("Question not found!")
        
        try:
            self.db.delete(question)
            self.db.commit()
            return {"message": "Question deleted successfully"}
        except BadRequestException:
            self.db.rollback()
            raise BadRequestException("Question delete failed")


class AnswerRepository:
    def __init__(self) -> None:
        self.db: Session = get_db().__next__()

    async def create(self, payload):
        answer = Answer(**payload.__dict__)

        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)

        return answer


    async def get(self, answer_id: str):
        answer = self.db.query(Answer).filter(Answer.id==answer_id).first()
        if answer is None:
            raise NotFoundException("Answer not found!")
        
        return answer


    async def get_list(self, page: int, limit: int, filter):
        skip = (page - 1) * limit

        answers = self.db.query(Answer
                                    ).order_by(Answer.created_at.desc()
                                                ).limit(limit).offset(skip).all()

        if len(answers) is None:
            raise NotFoundException("Answers not found!")  
        return answers
    

    async def get_by_question_id(self,  page: int, limit: int, question_id: str):
        skip = (page - 1) * limit
        answers = self.db.query(Answer).filter(Answer.question_id == question_id
            ).order_by(Answer.created_at.desc()
                       ).limit(limit).offset(skip).all()
        return answers


    async def update(self, payload):
        answer_query = self.db.query(Answer).filter(Answer.id==payload.id)
        answer = answer_query.first()
        if answer is None:
            raise NotFoundException("Answer not found!")
        
        answer_query.update(payload.dict(exclude_unset=True), synchronize_session=False)

        self.db.add(answer)
        self.db.commit()

        return answer

    async def delete(self, answer_id: str):
        answer_query = self.db.query(Answer).filter(Answer.id==answer_id)
        answer = answer_query.first()
        if answer is None:
            raise NotFoundException("Answer not found!")
        
        try:
            self.db.delete(answer)
            self.db.commit()
            return {"message": "Answer deleted successfully"}
        except BadRequestException:
            self.db.rollback()
            raise BadRequestException("Answer delete failed")



class UserResultRepository:
    def __init__(self) -> None:
        self.db: Session = get_db().__next__()

    async def create(self, payload):
        userResult = UserResult(**payload.__dict__)

        self.db.add(userResult)
        self.db.commit()
        self.db.refresh(userResult)

        return userResult

    async def get(self, result_id: str):
        userResult = self.db.query(UserResult).filter(UserResult.id==result_id).first()
        if userResult is None:
            raise NotFoundException("Result not found!")
        
        return userResult

    async def get_list(self, page: int, limit: int, filter):
        skip = (page - 1) * limit

        userResults = self.db.query(UserResult
                                    ).order_by(UserResult.created_at.desc()
                                                ).limit(limit).offset(skip).all()

        if len(userResults) is None:
            raise NotFoundException("Result not found!")  
        return userResults
    

    async def get_by_user_id(self,  page: int, limit: int, user_id: str):
        skip = (page - 1) * limit

        userResults = self.db.query(UserResult).filter(UserResult.user_id == user_id
            ).order_by(UserResult.created_at.desc()
                       ).limit(limit).offset(skip).all()
        return userResults
    

    async def get_by_assessment_id(self,  page: int, limit: int, assessment_id: str):
        skip = (page - 1) * limit

        userResults = self.db.query(UserResult).filter(UserResult.assessment_id == assessment_id
            ).order_by(UserResult.created_at.desc()
                       ).limit(limit).offset(skip).all()
        return userResults


    async def update(self, payload):
        userResult_query = self.db.query(UserResult).filter(UserResult.id==payload.id)
        userResults = userResult_query.first()
        if userResults is None:
            raise NotFoundException("Result not found!")
        
        userResults.update(payload.dict(exclude_unset=True), synchronize_session=False)

        self.db.add(userResults)
        self.db.commit()

        return userResults

    async def delete(self, userResult_id):
        userResult_query = self.db.query(UserResult).filter(UserResult.id==userResult_id)
        userResults = userResult_query.first()
        if userResults is None:
            raise NotFoundException("Result not found!")
        
        try:
            self.db.delete(userResults)
            self.db.commit()
            return {"message": "Result deleted successfully"}
        except BadRequestException:
            self.db.rollback()
            raise BadRequestException("Result delete failed")