#!/usr/bin/env python3

from fastapi import APIRouter, FastAPI
from loguru import logger
from pydantic import BaseModel, BaseSettings, Field
from typing import List
import json
import uvicorn

FUNDRAISERS = [
  {
    "id": 4,
    "code": "OGP",
    "labelNl": "Online Gaming Platform",
    "licenseHolderNl": "Novamedia Gaming B.V.",
    "selectable": True
  }
]

LOG_LEVELS = {
    "error": "ERROR",
    "warning": "WARNING",
    "info": "INFO",
    "debug": "DEBUG",
}


class Fundraiser(BaseModel):
    id: int
    code: str = Field(title="code")
    labelNl: str = Field(title="labelNL")
    licenseHolderNl: str = Field(title="licenseHolderNl")
    selectable: bool = Field(title=None)


class Settings(BaseSettings):
    BUILD_DATE: str = "2021-01-01 12:00:00"
    BUILD_VERSION: str = "0.0.0"
    LISTEN_PORT: int = 8000
    LOG_LEVEL: str = "WARNING"
    ROOT_PATH: str = ""
    TZ: str = "Europe/Amsterdam"
    VCS_REF: str = "deadbeef"


settings = Settings()
app = FastAPI(
    docs_url=f"{settings.ROOT_PATH}/api-docs.html",
    openapi_url=f"{settings.ROOT_PATH}/openapi.json",
    title="Fundraiser",
    version=settings.BUILD_VERSION,
)

api = APIRouter(
    prefix=settings.ROOT_PATH,
)


@api.get("/fundraiser", response_model=List[Fundraiser])
def fundraisers():
    """Main function of the web application
    
    Returns:
        List of fundraisers
    """
    print(FUNDRAISERS)
    logger.info("Retrieve fundraisers")
    return FUNDRAISERS


@api.get("/settings")
def setting():
    logger.info("Retrieve settings")
    return settings

@api.get("/ping")
def ping():
    return {"message": "pong"}


def serialize(record):
    subset = {
        "@timestamp": record["time"].isoformat(timespec="milliseconds"),
        "@version": "1",
        "message": record["message"],
        "logger_name": record["module"],
        "thread_name": record["thread"].name,
        "level": record["level"].name,
        "level_value": record["level"].no,
    }
    return json.dumps(subset)


def sink(message):
    serialized = serialize(message.record)
    print(serialized, flush=True)


app.include_router(api)

if __name__ == "__main__":
    logger.remove()
    logger.add(
        sink,
        serialize=True,
        level=LOG_LEVELS.get(settings.LOG_LEVEL.lower(), "INFO"),
        diagnose=False,
    )
    logger.info("started")
    uvicorn.run(app, host="0.0.0.0", port=settings.LISTEN_PORT, log_config=None)
    logger.info("finished")

