"""
Files API routes for Lite-RAG-App
"""

from fastapi import APIRouter, status, UploadFile
from fastapi.responses import JSONResponse
from controllers import FileController, ProjectController
from routes.schemas import FileUploadResponse

files_router = APIRouter(prefix="/api/v1/p/{project_id}/files", tags=["files", "v1"])


@files_router.post("/upload", response_model=FileUploadResponse)
async def upload_file(project_id: str, file: UploadFile):
    """Uploads a file to a specific project.

    Args:
        project_id (str): The ID of the project to which the file will be uploaded.
        file (UploadFile): The file to upload.

    Returns:
        JSONResponse: The response containing the upload status.
    """
    file_controller = FileController()
    is_valid, error_msg = file_controller.validate_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"error": error_msg}
        )

    project_controller = ProjectController()
    if not project_controller.validate_project(project_id):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Project not found"},
        )

    success, response = await file_controller.write_file(file, project_id)
    if not success:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"project_id": project_id, "msg": response},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"file_id": response, "project_id": project_id},
    )
