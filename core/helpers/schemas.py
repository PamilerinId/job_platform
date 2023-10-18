from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ValidationError

DataT = TypeVar('DataT')


# Response Schemas
class CustomResponse(BaseModel, Generic[DataT]):
    status: Optional[str] = 'success'
    code: Optional[str] = "200"
    message: Optional[str] = None
    data: Optional[DataT] = None

class CustomListResponse(BaseModel, Generic[DataT]):
    status: Optional[str] = 'success'
    code: Optional[str] = "200"
    message: Optional[str] = None
    count: Optional[int] = None
    total_count: Optional[int] =None
    next_page: Optional[int] = None
    data: Optional[List[DataT]] = None

# Mailing Schemas
class EmailParameters(BaseModel, Generic[DataT]):
    recipient_mail : str
    subject   : str
    template_id: Optional[int] = None
    template_values: Optional[DataT] = None


class WelcomeEmail(BaseModel):
    first_name: str
    last_name: str
    confirm_url: str
