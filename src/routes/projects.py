"""
Projects API routes for Lite-RAG-App
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from controllers import ProjectController
from routes.schemas import ProjectCreationResponse, ProjectListResponse

projects_router = APIRouter(prefix="/api/v1/projects", tags=["projects", "v1"])


@projects_router.post("/create", response_model=ProjectCreationResponse)
def create_project():
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
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content={"project_id": project_id}
    )


@projects_router.get("/list", response_model=ProjectListResponse)
def list_projects():
    """
    Lists all existing projects.
    """
    project_controller = ProjectController()
    projects = project_controller.list_projects()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"projects": projects, "count": len(projects)},
    )
