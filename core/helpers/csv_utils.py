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



def check_str(value, is_req: bool, pos: int, column: str):
    if type(value) != str and is_req:
        raise BadRequestException(f'Answer may contain a missing option in column: {column}, Row: {pos+2}')
    
    elif type(value) != str and not is_req:
        pass
    
    elif type(value) == str:
        value = re.sub('[^A-Za-z]', '', value.strip(" "))
        
        if value == "" and is_req:
            raise BadRequestException(f'Answer may contain a missing option in column: {column}, Row: {pos+2}')
        
    return value



        
def check_truth(ans_list: List[dict], ans: str, quest: dict, cell: int, df):
    '''
        Checks if question is True/False or Yes/No
    '''
    string_txt = check_str(df.loc[cell, f'{ans.upper()}'], False, cell, ans.upper())
    
    #In uppercase, does it contain any of the substrings "TRUE", "YES", "FALSE" and "NO"?
    if ("TRUE" == string_txt.upper()) or ("FALSE" == string_txt.upper()) or ("NO" == string_txt.upper()) or ("YES" == string_txt.upper()):
        
        #True/False and Yes/No questions should have only 2 answers
        ans_list.append({"answer_text": f'{df.loc[cell, "A"]}'})
        ans_list.append({"answer_text": f'{df.loc[cell, "B"]}'})
        quest.update({"question_type": QuestionType.TRUE_FALSE})
        
        if ans == "A":
            ans_list[0].update({"boolean_text": True})
            ans_list[0].update({"is_correct": True})
        else:
            ans_list[1].update({"boolean_text": True})
            ans_list[1].update({"is_correct": True})
    
    else:
        ans_list.append({"answer_text": f'{df.loc[cell, "A"]}'})
        ans_list.append({"answer_text": f'{df.loc[cell, "B"]}'})
        ans_list.append({"answer_text": f'{df.loc[cell, "C"]}'})
        ans_list.append({"answer_text": f'{df.loc[cell, "D"]}'})
        quest.update({"question_type": QuestionType.SINGLE_CHOICE})
        
        if ans == "A":
            ans_list[0].update({"boolean_text": True})
            ans_list[0].update({"is_correct": True})
        else:
            ans_list[1].update({"boolean_text": True})
            ans_list[1].update({"is_correct": True})
            
    return ans_list, quest
        
        
        
        
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
    
    assessment_questions: dict[str, list] = {
        "questions": []
    }
    
    for header in df.columns:
        #Checking for the required column headers
         
        if header != "E" and header not in CSV_HEADERS:
            raise BadRequestException(f'Missing column "{header}"! Try removing white spaces and non alphabetical characters')
    
    row = df.shape[0]   #Number of rows
    for cell in range(0, row):
        new_question = {
            "title": f'{df.loc[cell, "Question"]}'
        }
        
        answer_list: List[dict] = []
        answer = check_str(df.loc[cell, "Answer"], True, cell, "Answer")
        
        #Checking for True or False and Yes or No questions
        if (answer.upper() == "A" or answer.upper() == "B") and (type(df.loc[cell, f'{answer.upper()}']) == str):
            answer_list, new_question = check_truth(answer_list, answer, new_question, cell, df)
        
        elif answer.upper() == "E":
            new_question.update({"question_type": QuestionType.MULTIPLE_CHOICE})
            
            for alph in range(65, 69):
                #Using ASCII values to iterate from letter A - D 
                
                multi_answer = check_str(df.loc[cell, "E"], True, cell, "E")
                
                for choice in multi_answer: 
                    #Are any of these multi answer options among the csv headers? 
                    if choice.upper() not in CSV_HEADERS:
                        raise BadRequestException(f'Answer may contain a missing option "{choice}", Column "E", Row {cell}')
                    
                    #Is the current alphabet the same as one of the multichoice options? 
                    elif choice.upper() == chr(alph):
                        #Checking if letters of multi choice are among the requied column headers
                        # Comparing letters of current iteration with the current iteration in multi choice answer
                        
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

        else:
            print("Definitely single choice!")
            new_question.update({"question_type": QuestionType.SINGLE_CHOICE})
            
            if answer.upper() not in CSV_HEADERS:
                raise BadRequestException(f'Answer may contain a missing option in Column "Answer", Row {cell}')
            
            for alph in range(65, 69):
                print("Checking A - D!")
                #Using ASCII values to iterate from letter A - D     
                
                #Is current alphabet the same as answer?
                if answer.upper()[0] == chr(alph):
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
        
        #Adding to questions
        assessment_questions["questions"].append(new_question)
        
    #Creating the question instances only after question and answer data has been collated with no errors
    for question in assessment_questions["questions"]:
        await questionRepo.create(CreateQuestionSchema(**question), assessment_id)

        
        
        
        
    
    