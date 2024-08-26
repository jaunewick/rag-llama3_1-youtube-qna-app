from fastapi import  APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter()

class QuestionBase(BaseModel):
    video_id: str
    question_text: str

class AnswerBase(BaseModel):
    question_id: str
    answer_text: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/questions/", status_code=status.HTTP_201_CREATED)
async def create_question(question: QuestionBase, db: db_dependency):
    db_question = models.Question(**question.model_dump())
    db.add(db_question)
    db.commit()
    answer_text = "blah"
    db_answer = models.Answer(question_id=db_question.id, answer_text=answer_text)
    db.add(db_answer)
    db.commit()
    return {
        "question": db_question,
        "answer": db_answer
    }