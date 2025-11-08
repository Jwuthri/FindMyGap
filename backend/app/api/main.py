from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk

from app.config import SETTINGS
from app.api.v1 import health, workflow


sentry_sdk.init(
    dsn=SETTINGS.SENTRY_DSN,
    send_default_pii=True,
    enable_logs=True,
    traces_sample_rate=.5,
)

app = FastAPI(
    title="Find My Gaps API",
    description="Advanced LLM analysis to identify product gaps across entire markets",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(workflow.router, prefix="/api/v1/workflow", tags=["workflow"])
