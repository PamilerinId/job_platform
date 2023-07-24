# from uuid import uuid4, UUID  
# from datetime import datetime  
  
# from sqlalchemy import text  
# from sqlalchemy.ext.declarative import declared_attr
# from sqlalchemy.orm import as_declarative
# from sqlmodel import Field, SQLModel  

# class UUIDModel(SQLModel):  
#     id: UUID = Field(  
#         default_factory=uuid4,  
#         primary_key=True,  
#         index=True,  
#         nullable=False,  
#     )  
  
  
# class TimestampModel(SQLModel):  
#     created_at: datetime = Field(  
#         default_factory=datetime.utcnow,  
#         nullable=False,  
#         sa_column_kwargs={"server_default": text("current_timestamp(0)")},  
#     )
#     updated_at: datetime = Field(  
#         default_factory=datetime.utcnow,  
#         nullable=False,  
#         sa_column_kwargs={"server_default": text("current_timestamp(0)")},  
#     )

# @as_declarative()
# class CoreModel(SQLModel, UUIDModel, TimestampModel):
#     __name__: str

#     #to generate tablename from classname
#     @declared_attr
#     def __tablename__(cls) -> str:
#         return cls.__name__.lower()