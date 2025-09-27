"""
Assets API routes for Lite-RAG-App
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Request, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from controllers import FileController
from dependencies import get_session
from models.asset import Asset, AssetModel
from models.enums import AssetType, ResponseSignals
from models.file import File, FileModel
from models.project import ProjectModel
from routes.schemas import AssetListResponse, AssetResponse

assets_router = APIRouter(prefix="/api/v1/p/{project_id}/assets", tags=["assets", "v1"])


@assets_router.post(
    "/upload",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def upload_file(
    request: Request,
    project_id: UUID,
    file: UploadFile,
    db_session: AsyncSession = Depends(get_session),
):
    """Uploads a file to a specific project.

    Args:
        project_id (UUID): The ID of the project to which the file will be uploaded.
        file (UploadFile): The file to upload.

    Returns:
        AssetResponse: The response containing the uploaded asset details or an error message.
    """
    settings = request.app.state.settings
    file_controller = FileController(settings)
    is_valid, error_msg = file_controller.validate_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"msg": error_msg}
        )

    project_model = ProjectModel(db_session)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )

    if not file.filename:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"msg": ResponseSignals.FILE_NO_NAME_PROVIDED.value},
        )
    unique_filename = file_controller.generate_unique_filename(file.filename)

    asset_model = AssetModel(db_session)
    asset_record = await asset_model.insert_asset(
        Asset(
            project_id=project_record.id,
            type=AssetType.FILE.value,
            name=unique_filename,
            size=file_controller.get_file_size_mb(file),
            config={"filename": file.filename, "content_type": file.content_type},
        )
    )

    if asset_record is None:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": ResponseSignals.ASSET_CREATION_FAILED.value},
        )

    file_model = FileModel(db_session)
    file_data = await file.read()
    file_record = await file_model.insert_file(
        File(
            asset_id=asset_record.id,
            name=unique_filename,
            content_type=file.content_type,
            data=file_data,
        )
    )

    if file_record is None:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": ResponseSignals.ASSET_CREATION_FAILED.value},
        )

    return {"value": asset_record}


@assets_router.post(
    "/upload/batch",
    response_model=AssetListResponse,
    status_code=status.HTTP_201_CREATED,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def upload_files(
    request: Request,
    project_id: UUID,
    files: List[UploadFile],
    db_session: AsyncSession = Depends(get_session),
):
    """Uploads multiple files to a specific project.

    Args:
        project_id (UUID): The ID of the project to which the files will be uploaded.
        files (List[UploadFile]): The list of files to upload.

    Returns:
        AssetListResponse: The response containing the list of uploaded assets or error messages.
    """
    settings = request.app.state.settings
    file_controller = FileController(settings)
    project_model = ProjectModel(db_session)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )

    responses = []
    assets: List[Asset] = []
    db_files: List[File] = []
    for file in files:
        is_valid, error_msg = file_controller.validate_file(file)
        if not is_valid:
            responses.append({"filename": file.filename, "msg": error_msg})
            continue

        if not file.filename:
            responses.append(
                {
                    "filename": file.filename,
                    "msg": ResponseSignals.FILE_NO_NAME_PROVIDED.value,
                }
            )
            continue
        unique_filename = file_controller.generate_unique_filename(file.filename)

        assets.append(
            Asset(
                project_id=project_record.id,
                type=AssetType.FILE.value,
                name=unique_filename,
                size=file_controller.get_file_size_mb(file),
                config={"filename": file.filename, "content_type": file.content_type},
            )
        )
        file_data = await file.read()
        db_files.append(
            File(
                name=unique_filename,
                content_type=file.content_type,
                data=file_data,
            )
        )

    if not assets or not db_files:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"project_id": project_id, "msgs": responses},
        )

    asset_model = AssetModel(db_session)
    asset_records = await asset_model.insert_many_assets(assets)

    file_model = FileModel(db_session)
    for asset_record, db_file in zip(asset_records, db_files):
        if not asset_record:
            responses.append(
                {
                    "filename": db_file.name,
                    "msg": ResponseSignals.ASSET_CREATION_FAILED.value,
                }
            )
            continue
        if asset_record.name == db_file.name:
            db_file.asset_id = asset_record.id
    file_records = await file_model.insert_many_files(db_files)

    if not file_records or len(file_records) != len(asset_records):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"project_id": project_id, "msgs": responses},
        )

    payload = {
        "values": asset_records,
        "count": len(asset_records),
        "total": len(files),
    }
    if responses:
        payload["msgs"] = responses

    return payload


@assets_router.get(
    "/",
    response_model=AssetListResponse,
    status_code=status.HTTP_200_OK,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
)
async def list_assets(
    project_id: UUID, db_session: AsyncSession = Depends(get_session)
):
    """Lists all assets for a specific project.

    Args:
        project_id (UUID): The ID of the project for which to list assets.

    Returns:
        AssetListResponse: The response containing the list of assets or an error message.
    """
    project_model = ProjectModel(db_session)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )
    assets = project_record.assets or []

    return {
        "values": assets,
        "count": len(assets),
        "total": len(assets),
    }


@assets_router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    project_id: UUID,
    asset_id: str,
    db_session: AsyncSession = Depends(get_session),
):
    """Deletes a specific asset by its ID.

    Args:
        asset_id (str): The ID of the asset to delete.
    """
    project_model = ProjectModel(db_session)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )
    asset_model = AssetModel(db_session)
    asset_record = await asset_model.get_asset_by_name(project_record.id, asset_id)
    if asset_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
        )
    deletion_status = await asset_model.delete_asset(project_record.id, asset_id)
    if not deletion_status:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": ResponseSignals.ASSET_DELETION_FAILED.value},
        )
    return


@assets_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_assets(
    project_id: UUID, db_session: AsyncSession = Depends(get_session)
):
    """Deletes all assets for a specific project.

    Args:
        project_id (UUID): The ID of the project for which to delete assets.
    """
    project_model = ProjectModel(db_session)
    project_record = await project_model.get_project_by_id(project_id)
    if project_record is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.PROJECT_NOT_FOUND.value},
        )
    asset_model = AssetModel(db_session)
    asset_records = project_record.assets
    if not asset_records:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"msg": ResponseSignals.ASSET_NOT_FOUND.value},
        )
    deleted_count = await asset_model.delete_assets_by_project(project_record.id)
    asset_model.logger.info(
        "Deleted assets for project '%s': %d", str(project_record.id), deleted_count
    )
    if deleted_count == 0:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": ResponseSignals.ASSET_DELETION_FAILED.value},
        )
    return
