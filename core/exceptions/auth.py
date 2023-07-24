from core.exceptions import CustomException


class DecodeTokenException(CustomException):
    code = 400
    error_code = "TOKEN__DECODE_ERROR"
    message = "token decode error"


class ExpiredTokenException(CustomException):
    code = 400
    error_code = "TOKEN__EXPIRE_TOKEN"
    message = "Expired token"

    
class IncorrectEmailException(CustomException):
    code = 401
    error_code = "USER__PASSWORD_DOES_NOT_MATCH"
    message = "Incorrect email match"

class PasswordDoesNotMatchException(CustomException):
    code = 401
    error_code = "USER__PASSWORD_DOES_NOT_MATCH"
    message = "Incorrect password match"

class UnauthorisedUserException(CustomException):
    code = 403
    error_code = "USER__UNAUTHORIZED"
    message = "User does not have access to this resource"

class DuplicateEmailException(CustomException):
    code = 409
    error_code = "USER__DUPLICATE_EMAIL"
    message = "User already exists"


class UserNotFoundException(CustomException):
    code = 404
    error_code = "USER__NOT_FOUND"
    message = "user not found"
