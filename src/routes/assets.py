"""
Assets API routes for Lite-RAG-App
"""

from fastapi import APIRouter, status, UploadFile, Depends
from fastapi.responses import JSONResponse
from pymongo.asynchronous.database import AsyncDatabase
from controllers import FileController, ProjectController
from routes.schemas import AssetPushResponse, AssetListResponse
from models import AssetModel, Asset, ProjectModel
from models.enums import ResponseSignals, AssetType
from dependencies import get_db

assets_router = APIRouter(prefix="/api/v1/p/{project_id}/assets", tags=["assets", "v1"])


@assets_router.post("/upload", response_model=AssetPushResponse)
async def upload_file(
    project_id: str, file: UploadFile, mongo_db: AsyncDatabase = Depends(get_db)
):
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
            status_code=status.HTTP_400_BAD_REQUEST, content={"msg": error_msg}
        )

    project_controller = ProjectController()
    project_model = await ProjectModel.create_instance(mongo_db)
    project_record = await project_model.get_project_by_id(project_id)
    if (
        not project_controller.validate_project(project_id)
        or project_record is None
        or project_record.object_id is None
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )

    success, response = await file_controller.write_file(file, project_id)
    if not success:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"project_id": project_id, "msg": response},
        )

    asset_model = await AssetModel.create_instance(mongo_db)
    record = await asset_model.insert_asset(
        Asset(
            project_id=project_record.object_id,
            type=AssetType.FILE.value,
            name=response,
            size=file_controller.get_file_size_mb(file),
            config={"filename": file.filename, "content_type": file.content_type},
        )
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "project_id": project_id,
            **record.model_dump(
                mode="json", exclude={"object_id", "project_id"}, exclude_defaults=True
            ),
        },
    )


@assets_router.get("/", response_model=AssetListResponse)
async def list_assets(project_id: str, mongo_db: AsyncDatabase = Depends(get_db)):
    """Lists all assets for a specific project.

    Args:
        project_id (str): The ID of the project for which to list assets.

    Returns:
        JSONResponse: The response containing the list of assets.
    """
    project_controller = ProjectController()
    project_model = await ProjectModel.create_instance(mongo_db)
    project_record = await project_model.get_project_by_id(project_id)
    if (
        not project_controller.validate_project(project_id)
        or project_record is None
        or project_record.object_id is None
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )

    asset_model = await AssetModel.create_instance(mongo_db)
    assets = await asset_model.get_project_assets(project_record.object_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "assets": [
                AssetPushResponse(
                    project_id=project_id,
                    **asset.model_dump(
                        mode="json",
                        exclude={"object_id", "project_id"},
                        exclude_defaults=True,
                    ),
                ).model_dump(mode="json", exclude_defaults=True)
                for asset in assets
            ],
            "count": len(assets),
        },
    )


@assets_router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    project_id: str, asset_id: str, mongo_db: AsyncDatabase = Depends(get_db)
):
    """Deletes a specific asset by its ID.

    Args:
        asset_id (str): The ID of the asset to delete.

    Returns:
        JSONResponse: The response containing the deletion status.
    """
    project_model = await ProjectModel.create_instance(mongo_db)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None or project_record.object_id is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )
    asset_model = await AssetModel.create_instance(mongo_db)
    asset_record = await asset_model.get_asset_by_name(
        project_record.object_id, asset_id
    )
    if asset_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
        )
    await asset_model.delete_asset(project_record.object_id, asset_id)
    if asset_record.type == AssetType.FILE.value:
        project_controller = ProjectController()
        if not project_controller.validate_project(project_id):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
            )
        if not project_controller.delete_file(project_id, asset_id):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
            )
    return


@assets_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_assets(
    project_id: str, mongo_db: AsyncDatabase = Depends(get_db)
):
    """Deletes all assets for a specific project.

    Args:
        project_id (str): The ID of the project for which to delete assets.

    Returns:
        JSONResponse: The response containing the deletion status.
    """
    project_model = await ProjectModel.create_instance(mongo_db)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None or project_record.object_id is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )
    asset_model = await AssetModel.create_instance(mongo_db)
    asset_records = await asset_model.get_project_assets(project_record.object_id)
    if not asset_records:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
        )
    await asset_model.delete_assets_by_project(project_record.object_id)
    file_assets = [
        asset.name for asset in asset_records if asset.type == AssetType.FILE.value
    ]
    if file_assets:
        project_controller = ProjectController()
        if not project_controller.validate_project(project_id):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
            )
        if not project_controller.delete_project_files(project_id, file_assets):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
            )
    return
