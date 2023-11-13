import pandas as pd
from core.exceptions import NotFoundException, BadRequestException
from modules.assessments.repository import AssessmentRepository, QuestionRepository
from modules.assessments.schemas import *
from modules.assessments.models import *

assessmentRepo = AssessmentRepository()
questionRepo = QuestionRepository()
CSV_HEADERS = [
    "Question",
    "A",
    "B",
    "C",
    "D",
    # "E",
    "Answer"
]

async def generate_questions(file: str, id: UUID): 
    '''
        Questions are genrated by reading each row of the csv file and
        creating objects used to create question istances with the id
        of the assessment passed
    '''

    df = pd.read_csv(file, encoding='cp1252') 
    
    for header in CSV_HEADERS: 
        #Checking for the required column headers 
        if header not in df.columns:
            raise BadRequestException(f'Missing column "{header}"!')
    
    row = df.shape[0]   #Number of rows
    for cell in range(0, row):
        new_question = {
            "title": df.loc[cell, "Question"]
        }
        
        answer_list = [] 

        if df.loc[cell, 'A'].strip().upper() == "TRUE" and df.loc[cell,'B'].strip().upper() == "FALSE":
            answer_list.append({"answer_text": df.loc[cell, "A"]})
            answer_list.append({"answer_text": df.loc[cell, "B"]})

            
            if df.loc[cell, "Answer"] == "A":
                answer_list[0].update({"boolean_text": True})
                answer_list[0].update({"is_correct": True})
            else:
                answer_list[1].update({"boolean_text": True})
                answer_list[1].update({"is_correct": True})
            
            new_question.update({"question_type": QuestionType.TRUE_FALSE})

        else:
            for alph in range(65, 69):
                #Using ASCII values to iterate from letter A - D
                if df.loc[cell, "Answer"] == "E":
                    new_question.update({"question_type": QuestionType.MULTIPLE_CHOICE})
                    multi_ans = df.loc[cell, "E"].strip(" ")
                    multi_ans = df.loc[cell, "E"].strip(",")
                    for choice in multi_ans:  
                        #Checking if letters of multi choice are among the requied column headers

                        if choice.isalpha() and choice.upper() == chr(alph) and choice.upper() in CSV_HEADERS:
                            # Comparing the current ASCII iteration/letter with the 
                            # current iteration/letter in multi choice answer
                            answer_list.append(
                                {
                                    "answer_text": df.loc[cell, f"{chr(alph)}"],
                                    "boolean_text": True,
                                    "is_correct": True
                                }           
                            )
                        
                        elif choice.isalpha() == True and choice.upper() not in CSV_HEADERS:
                            raise BadRequestException(f'Answer may contain a missing option "{choice}", Column "E", Row {cell}')
                            
                        else:
                            answer_list.append(
                                {
                                    "answer_text": df.loc[cell, f"{chr(alph)}"]
                                }
                            )
                            
                else:
                    new_question.update({"question_type": QuestionType.SINGLE_CHOICE})     
                    if df.loc[cell, "Answer"].strip(" ") == chr(alph):
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
                        
        #Adding answers to quesion
        new_question.update({"Answer": answer_list})
        
        #Creating the question instance 
        question_obj = await questionRepo.create(CreateQuestionSchema(**new_question), id)
    
    
    # return
        
        
        
        
    
    