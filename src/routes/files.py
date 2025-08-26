"""
Files API routes for Lite-RAG-App
"""

from fastapi import APIRouter, UploadFile, status
from fastapi.responses import JSONResponse
from controllers import FileController, ProjectController

files_router = APIRouter(prefix="/api/v1/p/{project_id}/files", tags=["files", "v1"])


@files_router.post("/upload")
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

    success, error_msg = await file_controller.write_file(file, project_id)
    if not success:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": error_msg},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Uploaded {file.filename} to project {project_id}"},
    )
