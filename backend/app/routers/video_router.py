from fastapi import  APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import backend.app.models as models
from backend.app.database import SessionLocal
from sqlalchemy.orm import Session
from backend.app.langchain_app import store_into_pinecone, delete_index_pinecone
router = APIRouter()

class VideoBase(BaseModel):
    title: str
    url: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/videos/", status_code=status.HTTP_201_CREATED)
async def create_video(video: VideoBase, db: db_dependency):
    db_video = models.Video(**video.model_dump())
    db.add(db_video)
    db.commit()
    store_into_pinecone(video.url)
    db_video = db.query(models.Video).filter(models.Video.id == db_video.id).first()
    return {
        "video": db_video
    }

@router.get("/videos/{video_id}", status_code=status.HTTP_200_OK)
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

@router.delete("/videos/{video_id}", status_code=status.HTTP_200_OK)
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
    delete_index_pinecone()
    return {"message": "Video deleted successfully"}