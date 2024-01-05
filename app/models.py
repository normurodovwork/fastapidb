import datetime

from .database import Base
from sqlalchemy import Column, String, Integer, DateTime, Boolean


class Todo(Base):
    __tablename__ = "todo"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)



