import math
import random
from typing import List
from modules.assessments.schemas import CreateAssessmentResults, ScoreDetails
from modules.assessments.models import Status
from modules.assessments.schemas import BaseQuestion
from core.exceptions import BadRequestException


def mark_questions(paylod: CreateAssessmentResults):
    review = ScoreDetails()
    for question in paylod.submission:
        review.total_questions+=1
        if question.answer.is_correct and question.answer.boolean_text:
            review.total_score+=1
    
    review.percentage = math.ceil((review.total_score / review.total_questions) * 100)
    
    # if review.percentage >= 70:
    #     review.status = Status.DISTINCTION
        
    if review.percentage >= 50:
        review.status = Status.PASS
        
    else:
        review.status = Status.FAIL
    
    return review

