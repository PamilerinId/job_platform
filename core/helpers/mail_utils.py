from core.dependencies.mail import EmailSender
from core.helpers.schemas import EmailParameters, CandidateWelcomeEmail, ClientWelcomeEmail, PasswordResetEmail
from typing import Union



CLIENT_WELCOME_MAIL = 32987230
CANDIDATE_WELCOME_MAIL = 33384666
PASSWORD_RESET_MAIL = 32990683


def mail_notify(mail_to: str, template: int, req_parameters: Union[CandidateWelcomeEmail, ClientWelcomeEmail, PasswordResetEmail]) -> None:
    
    EmailSender.send_mail( EmailParameters(
        recipient_mail= mail_to,
        template_id= template,
        template_values= req_parameters.dict())
    )

    print("Email sent")