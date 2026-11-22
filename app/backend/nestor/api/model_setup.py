from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.memory import model_setup

AUTO = True
router = APIRouter()


@router.get("/ocr/setup")
def ocr_status():
    return model_setup.ocr_status()


@router.post("/ocr/setup", status_code=202)
def install_ocr():
    status = model_setup.ocr_status()
    if status["ready"] or status["job"]["phase"] == "running":
        return status
    if not status["can_install"]:
        raise HTTPException(409, "Máy chủ chưa hỗ trợ cài tự động. Hãy dùng hướng dẫn cài thủ công.")
    model_setup.ocr_job.start(model_setup.install_ocr, step="checking")
    return {**status, "job": model_setup.ocr_job.snapshot()}


class ModelPull(BaseModel):
    model: str = Field(min_length=1, max_length=160, pattern=r"^(?:[a-zA-Z0-9_-]+/)?[a-zA-Z0-9_][a-zA-Z0-9_.-]*(?::[a-zA-Z0-9_.-]+)?$")


@router.get("/memory/model-pull")
def embedding_status():
    return model_setup.embedding_job.snapshot()


@router.post("/memory/model-pull", status_code=202)
def pull_embedding(body: ModelPull):
    model_setup.embedding_job.start(lambda job: model_setup.pull_embedding(job, body.model), model=body.model, percent=None)
    return model_setup.embedding_job.snapshot()
