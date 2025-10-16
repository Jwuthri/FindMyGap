from fastapi import FastAPI
import sentry_sdk

from app.config import get_settings


sentry_sdk.init(
    dsn=get_settings().SENTRY_DSN,
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    enable_logs=True,
    traces_sample_rate=.5,
)
sentry_sdk.logger.info('This is an info log message')
sentry_sdk.logger.warning('This is a warning message')
sentry_sdk.logger.error('This is an error message')

app = FastAPI()


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
    return division_by_zero


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
