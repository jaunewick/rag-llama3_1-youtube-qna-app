from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class VideoBase(BaseModel):
    title: str

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

@app.post("/videos/", status_code=status.HTTP_201_CREATED)
async def create_video(video: VideoBase, db: db_dependency):
    db_video = models.Video(**video.model_dump())
    db.add(db_video)
    db.commit()

@app.get("/videos/{video_id}", status_code=status.HTTP_200_OK)
async def read_video(video_id: int, db: db_dependency):
    video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if video is None:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return video

@app.post("/questions/", status_code=status.HTTP_201_CREATED)
async def create_question(question: QuestionBase, db: db_dependency):
    db_question = models.Question(**question.model_dump())
    db.add(db_question)
    db.commit()

@app.get("/questions/{question_id}", status_code=status.HTTP_200_OK)
async def read_question(question_id: int, db: db_dependency):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if question is None:
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Question not found")
    return question

@app.post("/answers/", status_code=status.HTTP_201_CREATED)
async def create_answer(answer: AnswerBase, db: db_dependency):
    db_answer = models.Answer(**answer.model_dump())
    db.add(db_answer)
    db.commit()

@app.get("/answers/{answer_id}", status_code=status.HTTP_200_OK)
async def read_answer(answer_id: int, db: db_dependency):
    answer = db.query(models.Answer).filter(models.Answer.id == answer_id).first()
    if answer is None:
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Answer not found")
    return answer