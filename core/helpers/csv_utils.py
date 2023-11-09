import pandas as pd
from core.exceptions import NotFoundException, BadRequestException
from modules.assessments.repository import AssessmentRepository, QuestionRepository
from modules.assessments.schemas import *
from modules.assessments.models import *


from sqlalchemy.orm import Session

assessmentRepo = AssessmentRepository()
questionRepo = QuestionRepository()
CSV_HEADERS = [
    "questions",
    "A",
    "B",
    "C",
    "D",
    # "E",
    "answers"
]

async def generate_questions(file: str, assessment: BaseAssessment, db: Session):    

    df = pd.read_csv(file, encoding='cp1252')
    
    for header in CSV_HEADERS:
        if header not in df.columns:
            raise BadRequestException(f'Missing column "{header}"!')
    
    row = df.shape[0]
    
    for cell in range(0, row):
        new_question = {
            "title": df.loc[cell, "questions"]
        }
        
        answer_list = []

        if df.loc[cell, 'A'].strip().upper() == "TRUE" and df.loc[cell,'B'].strip().upper() == "FALSE":
            answer_list.append({"answer_text": df.loc[cell, "A"]})
            answer_list.append({"answer_text": df.loc[cell, "B"]})

            
            if df.loc[cell, "answers"] == "A":
                answer_list[0].update({"boolean_text": True})
                answer_list[0].update({"is_correct": True})
            else:
                answer_list[1].update({"boolean_text": True})
                answer_list[1].update({"is_correct": True})
            
            new_question.update({"question_type": QuestionType.TRUE_FALSE})

        else:
            for alph in range(65, 69):
                if df.loc[cell, "answers"] == "E":
                    new_question.update({"question_type": QuestionType.MULTIPLE_CHOICE})
                    multi_ans = df.loc[cell, "E"].strip(" ")
                    for choice in multi_ans:
                        if choice.uppper() not in CSV_HEADERS:
                            raise BadRequestException(f'Answers may contain a missing option, Column "E", Row {cell}!')

                        if choice.isalpha() and choice.upper() == chr(alph):
                            answer_list.append(
                                {
                                    "answer_text": df.loc[cell, f"{chr(alph)}"],
                                    "boolean_text": True,
                                    "is_correct": True
                                }           
                            ) 
                            
                        else:
                            answer_list.append(
                                {
                                    "answer_text": df.loc[cell, f"{chr(alph)}"]
                                }
                            )
                            
                else:
                    new_question.update({"question_type": QuestionType.SINGLE_CHOICE})     
                    if df.loc[cell, "answers"].strip(" ") == chr(alph):
                        answer_list.append(
                            {
                                "answer_text": df.loc[cell, f"{chr(alph)}"],
                                "boolean_text": True,
                                "is_correct": True
                            }                                
                        )
                    else:
                        answer_list.append(
                            {
                                "answer_text": df.loc[cell, f"{chr(alph)}"]
                            }                   
                        )
                        
        new_question.update({"answers": answer_list})
        question_obj = await questionRepo.create(CreateQuestionSchema(**new_question), assessment.id)
    
    
    return assessment
        
        
        
        
    
    