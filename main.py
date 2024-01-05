import datetime

from fastapi.exceptions import HTTPException

from fastapi import FastAPI, Depends, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from app import models
from app.database import engine, SessionLocal
from typing import Annotated

from app.models import Todo

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_database)]


class TodoItem(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=255)
    completed: bool
    created_at: datetime.datetime


@app.get("/")
async def todos(db: db_dependency):
    return db.query(Todo).all()


@app.get("/{id}")
async def todo_detail(db: db_dependency, todo_id: int):
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=404, detail="Todo not founded")


@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def todo_create(db: db_dependency, todo: TodoItem):
    todo_model = Todo(**todo.__dict__)

    db.add(todo_model)
    db.commit()
    return todo_model


@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def todo_edit(db: db_dependency, todo_id: int, todo: TodoItem):
    todo_model = db.query(Todo).filter(todo_id == Todo.id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not founded")

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_detail.completed = todo.completed
    todo_model.created_at = todo.created_at

    db.add(todo_model)
    db.commit()


@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def todo_delete(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todo).filter(todo_id == Todo.id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not founded")

    db.delete(todo_model)
    db.commit()
