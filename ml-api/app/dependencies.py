from fastapi import Request

from app.model import ModelService


def get_model_service(request: Request) -> ModelService:
    return request.app.state.model_service
