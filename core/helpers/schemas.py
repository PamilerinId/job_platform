from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ValidationError

DataT = TypeVar('DataT')



class CustomResponse(BaseModel, Generic[DataT]):
    status: Optional[str] = 'success'
    code: Optional[str] = "200"
    message: Optional[str]
    data: Optional[DataT] = None