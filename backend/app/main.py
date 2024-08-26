from fastapi import FastAPI
import backend.app.models as models
from backend.app.database import engine
from backend.app.routers import question_router, video_router

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(question_router.router)
app.include_router(video_router.router)