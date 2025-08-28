"""
Projects API routes for Lite-RAG-App
"""

from typing import Optional
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from pymongo.asynchronous.database import AsyncDatabase
from dependencies import get_db
from controllers import ProjectController
from models import ProjectModel, Project
from routes.schemas import (
    ProjectCreationResponse,
    ProjectListResponse,
    ProjectCreationRequest,
)

projects_router = APIRouter(prefix="/api/v1/projects", tags=["projects", "v1"])


@projects_router.post("/create", response_model=ProjectCreationResponse)
async def create_project(
    project: Optional[ProjectCreationRequest] = None, mongo_db: AsyncDatabase = Depends(get_db)
):
    """
    Creates a new project.
    """
    project_controller = ProjectController()
    project_id = project_controller.create_new_project()
    if not project_id:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": "Failed to create project"},
        )

    project_model = ProjectModel(mongo_db)
    project_record = await project_model.insert_project(
        Project(id=project_id, **(project.model_dump(exclude_unset=True) if project else {}))
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=project_record.model_dump(exclude={"object_id"}),
    )


@projects_router.get("/list", response_model=ProjectListResponse)
async def list_projects(
    skip: int = 0, limit: int = 10, mongo_db: AsyncDatabase = Depends(get_db)
):
    """
    Lists all existing projects.
    """
    if limit > 100:
        limit = 100
    project_model = ProjectModel(mongo_db)
    projects = await project_model.get_projects(skip=skip, limit=limit)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "projects": [
                project.model_dump(exclude={"object_id"}, exclude_unset=True)
                for project in projects
            ],
            "count": len(projects),
        },
    )
