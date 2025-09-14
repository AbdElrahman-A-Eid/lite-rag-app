"""
Projects API routes for Lite-RAG-App
"""

from typing import Optional

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pymongo.asynchronous.database import AsyncDatabase

from controllers import ProjectController
from dependencies import get_db
from models.enums import ResponseSignals
from models.project import Project, ProjectModel
from routes.schemas import (
    ProjectCreationRequest,
    ProjectCreationResponse,
    ProjectListResponse,
)

projects_router = APIRouter(prefix="/api/v1/projects", tags=["projects", "v1"])


@projects_router.post("/create", response_model=ProjectCreationResponse)
async def create_project(
    request: Request,
    project: Optional[ProjectCreationRequest] = None,
    mongo_db: AsyncDatabase = Depends(get_db),
):
    """
    Creates a new project.
    """
    settings = request.app.state.settings
    project_controller = ProjectController(settings)
    project_id = project_controller.create_new_project()
    if not project_id:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": ResponseSignals.PROJECT_CREATION_FAILED.value},
        )

    project_model = await ProjectModel.create_instance(mongo_db)
    project_record = await project_model.insert_project(
        Project(
            id=project_id, **(project.model_dump(exclude_unset=True) if project else {})
        )
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
    project_model = await ProjectModel.create_instance(mongo_db)
    projects = await project_model.get_projects(skip=skip, limit=limit)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "projects": [
                project.model_dump(exclude={"object_id"}, exclude_unset=True)
                for project in projects
            ],
            "count": len(projects),
            "total": await project_model.count_projects(),
        },
    )


@projects_router.get("/{project_id}", response_model=ProjectCreationResponse)
async def get_project(project_id: str, mongo_db: AsyncDatabase = Depends(get_db)):
    """
    Retrieves a specific project by its ID.
    """
    project_model = await ProjectModel.create_instance(mongo_db)
    project = await project_model.get_project_by_id(project_id)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=project.model_dump(exclude={"object_id"}),
    )


@projects_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str, request: Request, mongo_db: AsyncDatabase = Depends(get_db)
):
    """
    Deletes a specific project by its ID.
    """
    settings = request.app.state.settings
    project_model = await ProjectModel.create_instance(mongo_db)
    deletion_status = await project_model.delete_project(project_id)
    if deletion_status:
        ProjectController(settings).delete_project_folder(project_id)
    if not deletion_status:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )
    return
