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
    url: str

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    questions = db.query(models.Question).filter(models.Question.video_id == video_id).all()
    questions_and_answers = []
    for question in questions:
        answer = db.query(models.Answer).filter(models.Answer.question_id == question.id).first()
        questions_and_answers.append({
            "question": question,
            "answer": answer
        })
    return {
        "video": video,
        "questions_and_answers": questions_and_answers
    }

@app.delete("/videos/{video_id}", status_code=status.HTTP_200_OK)
async def delete_video(video_id: int, db: db_dependency):
    video = db.query(models.Video).filter(models.Video.id == video_id).first()
    if video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    questions = db.query(models.Question).filter(models.Question.video_id == video_id).all()
    for question in questions:
        answer = db.query(models.Answer).filter(models.Answer.question_id == question.id).first()
        if answer:
            db.delete(answer)
        db.delete(question)
    db.delete(video)
    db.commit()
    return {"message": "Video deleted successfully"}


@app.post("/questions/", status_code=status.HTTP_201_CREATED)
async def create_question(question: QuestionBase, db: db_dependency):
    db_question = models.Question(**question.model_dump())
    db.add(db_question)
    db.commit()
    answer_text = "blah"
    db_answer = models.Answer({
        "question_id": db_question.id,
        "answer_text": answer_text
    })
    db.add(db_answer)
    db.commit()
    return {
        "question": db_question,
        "answer": db_answer
    }