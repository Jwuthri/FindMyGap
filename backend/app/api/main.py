from fastapi import FastAPI
import sentry_sdk

from app.config import get_settings


sentry_sdk.init(
    dsn=get_settings().SENTRY_DSN,
    send_default_pii=True,
    enable_logs=True,
    traces_sample_rate=.5,
)

app = FastAPI()
