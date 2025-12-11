from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .server import Server

AUTO_START = os.getenv("FETCHER_AUTO_START", "true").lower() in {"1", "true", "yes"}

service = Server()
app = FastAPI(title="Mastodon Fetcher Control API", version="0.1.0")


class RunRequest(BaseModel):
    limit: int | None = Field(default=None, gt=0)
    send_to_kafka: bool = True


class ConfigureRequest(BaseModel):
    fetch_limit: int | None = Field(default=None, gt=0)
    loop_delay: float | None = Field(default=None, ge=0)


@app.on_event("startup")
async def _startup() -> None:
    if AUTO_START:
        service.start()


@app.on_event("shutdown")
async def _shutdown() -> None:
    service.stop()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/state")
def read_state() -> dict:
    return service.status().as_dict()


@app.post("/start")
def start_service() -> dict:
    service.start()
    return service.status().as_dict()


@app.post("/stop")
def stop_service() -> dict:
    service.stop()
    return service.status().as_dict()


@app.post("/run")
def run_once(payload: RunRequest) -> dict:
    if service.is_running:
        raise HTTPException(
            status_code=409,
            detail="Stop the service before running a single iteration.",
        )
    result = service.run_iteration(
        limit=payload.limit, send_to_kafka=payload.send_to_kafka
    )
    return {"result": result, "state": service.status().as_dict()}


@app.post("/configure")
def configure(payload: ConfigureRequest) -> dict:
    service.configure(fetch_limit=payload.fetch_limit, loop_delay=payload.loop_delay)
    return service.status().as_dict()
