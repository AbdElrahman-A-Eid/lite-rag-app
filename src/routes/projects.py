"""
Projects API routes for Lite-RAG-App
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session
from models.enums import ResponseSignals
from models.project import Project, ProjectModel
from routes.schemas import (
    ProjectCreationRequest,
    ProjectListResponse,
    ProjectResponse,
)

projects_router = APIRouter(prefix="/api/v1/projects", tags=["projects", "v1"])


@projects_router.post(
    "/create",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def create_project(
    project: Optional[ProjectCreationRequest] = None,
    db_session: AsyncSession = Depends(get_session),
):
    """
    Creates a new project.
    """
    project_model = ProjectModel(db_session)
    project_record = await project_model.insert_project(
        Project(**(project.model_dump(exclude_unset=True) if project else {}))
    )

    if not project_record:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": ResponseSignals.PROJECT_CREATION_FAILED.value},
        )
    return {"value": project_record}


@projects_router.get(
    "/list",
    response_model=ProjectListResponse,
    status_code=status.HTTP_200_OK,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def list_projects(
    skip: int = 0, limit: int = 10, db_session: AsyncSession = Depends(get_session)
):
    """
    Lists all existing projects.
    """
    if limit > 100:
        limit = 100
    project_model = ProjectModel(db_session)
    projects = await project_model.get_projects(skip=skip, limit=limit)
    total = await project_model.count_projects()
    return {
        "values": projects,
        "count": len(projects),
        "total": total,
    }


@projects_router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def get_project(
    project_id: UUID, db_session: AsyncSession = Depends(get_session)
):
    """
    Retrieves a specific project by its ID.
    """
    project_model = ProjectModel(db_session)
    project = await project_model.get_project_by_id(project_id)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )
    return {"value": project}


@projects_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID, db_session: AsyncSession = Depends(get_session)
):
    """
    Deletes a specific project by its ID.
    """
    project_model = ProjectModel(db_session)
    deleted = await project_model.delete_project(project_id)
    if not deleted:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )
    return
