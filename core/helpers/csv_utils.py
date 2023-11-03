import csv
from modules.assessments.repository import AssessmentRepository
from modules.assessments.schemas import *

assessmentRepo = AssessmentRepository()
def generate_assessment(file):
    
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            # answer = BaseAnswer(
                
            # )
            #     row["Question"]
            # )
            # assessmentRepo.create()