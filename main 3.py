from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from app.api.orchestrate import router as orchestrate_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(orchestrate_router, prefix=settings.API_V1_STR)
