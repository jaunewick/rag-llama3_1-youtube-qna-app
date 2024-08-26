from fastapi import  APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import SessionLocal
from sqlalchemy.orm import Session
from langchain_app import answer_question

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
    answer_text = answer_question(question=db_question.question_text)
    db_answer = models.Answer(question_id=db_question.id, answer_text=answer_text)
    db.add(db_answer)
    db.commit()
    db_question = db.query(models.Question).filter(models.Question.id == db_question.id).first()
    db_answer = db.query(models.Answer).filter(models.Answer.id == db_answer.id).first()
    return {
        "question": db_question,
        "answer": db_answer
    }