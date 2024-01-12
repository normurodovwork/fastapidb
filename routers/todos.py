from fastapi.exceptions import HTTPException
from fastapi import Depends, Path, APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from app.database import SessionLocal
from typing import Annotated
from app.models import Todo
from .auth import get_current_user

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)


def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_database)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoItem(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=255)
    completed: bool = Field(default=False)


@router.get("/")
async def todos(db: db_dependency):
    return db.query(Todo).all()


@router.get("/{todo_id}")
async def todo_detail(db: db_dependency, todo_id: int):
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=404, detail="Todo not founded")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def todo_create(user: user_dependency,
                      db: db_dependency,
                      todo: TodoItem):
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Authentication credentials were not provided")

    todo_model = Todo(**todo.__dict__, owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()
    return todo_model


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
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


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def todo_delete(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not founded")

    db.delete(todo_model)
    db.commit()
