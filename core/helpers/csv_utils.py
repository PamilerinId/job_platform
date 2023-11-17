import pandas as pd
import re
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

async def generate_questions(file: str, assessment_id: UUID): 
    '''
        Questions are genrated by reading each row of the csv file and
        creating objects used to create question istances with the id
        of the assessment passed
    '''
    try:
        df = pd.read_csv(file, encoding='utf8')
    except:
        raise BadRequestException(f'CSV file contains forbidden characters!')
    
    for header in CSV_HEADERS: 
        #Checking for the required column headers 
        if header not in df.columns:
            raise BadRequestException(f'Missing column "{header}"!')
    
    row = df.shape[0]   #Number of rows
    for cell in range(0, row):
        new_question = {
            "title": f'{df.loc[cell, "Question"]}'
        }
        
        answer_list = []
        
        if type(df.loc[cell, "Answer"]) != str:   #Value must be a string
            raise BadRequestException(f'Answer may contain a missing option "{choice}", Column "Answer" Row {cell}')
            
        df.loc[cell, "Answer"].strip(" ")  #Removing all spaces in the string
        re.sub('[\W_]+', '', df.loc[cell, "Answer"])  #Removing all non-alphabetical characters from the string

        if ("TRUE" in df.loc[cell, 'A'].strip(" ").upper() and "False" in df.loc[cell,'B'].strip(" ").upper()) or ("FALSE" in df.loc[cell, 'A'].strip(" ").upper() and "TRUE" in df.loc[cell,'B'].strip(" ").upper()):
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
                    
                    if type(df.loc[cell, "E"]) != str:   #Value must be a string
                        raise BadRequestException(f'Answer may contain a missing option "{choice}", Column "E", Row {cell}')
                    
                    df.loc[cell, "E"].strip(" ")  #Removing all spaces in the string
                    re.sub('[\W_]+', '', df.loc[cell, "E"])  #Removing all non-alphabetical characters from the string
                    
                    multi_ans = df.loc[cell, "E"]
                    for choice in multi_ans: 
                        #Checking if letters of multi choice are among the requied column headers

                        if choice.isalpha() and choice.upper() == chr(alph) and choice.upper() in CSV_HEADERS:
                            # Comparing the current ASCII iteration/letter with the 
                            # current iteration/letter in multi choice answer
                            answer_list.append(
                                {
                                    "answer_text": f'{df.loc[cell, chr(alph)]}',
                                    "boolean_text": True,
                                    "is_correct": True
                                }           
                            )
                        
                        elif choice.isalpha() == True and choice.upper() not in CSV_HEADERS:
                            raise BadRequestException(f'Answer may contain a missing option "{choice}", Column "E", Row {cell}')
                            
                        else:
                            answer_list.append(
                                {
                                    "answer_text": f'{df.loc[cell, chr(alph)]}'
                                }
                            )
                            
                else:
                    new_question.update({"question_type": QuestionType.SINGLE_CHOICE})
                    
                    if df.loc[cell, "Answer"].upper()[0] == chr(alph):
                        answer_list.append(
                            {
                                "answer_text": f'{df.loc[cell, chr(alph)]}',
                                "boolean_text": True,
                                "is_correct": True
                            }                                
                        )
                    else:
                        answer_list.append(
                            {
                                "answer_text": f'{df.loc[cell, chr(alph)]}'
                            }                   
                        )
                        
        #Adding answers to quesion
        new_question.update({"answers": answer_list})
        
        #Creating the question instance 
        question_obj = await questionRepo.create(CreateQuestionSchema(**new_question), assessment_id)
    
    
    # return
        
        
        
        
    
    