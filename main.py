from fastapi import FastAPI
import models
from database import engine
from routers import question_router, video_router

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(question_router.router)
app.include_router(video_router.router)