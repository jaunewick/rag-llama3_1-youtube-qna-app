from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import backend.app.models as models
from backend.app.database import engine
from backend.app.routers import question_router, video_router

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(question_router.router)
app.include_router(video_router.router)