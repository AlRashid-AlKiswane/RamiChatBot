from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os, sys

# Add the project's root directory to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(root_dir)

from utils.helpers import get_settings, Settings
from db import Asset
from controllers import DataController, ProjectController
import aiofiles
from enums import ResponseSignal, AssetTypeEnum
from logs import log_error, log_info, log_warning
from core  import AssetModel, ProjectModel, BaseDataModel

upload_router = APIRouter()

@upload_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):
    try:
        log_info(f"Upload started for project_id: {project_id}, file: {file.filename}")

        project_model = await ProjectModel.create_instance(
            db_client=request.app.db_client
        )

        project = await project_model.get_project_or_create_one(
            project_id=project_id
        )
        log_info(f"Project retrieved or created: {project.id}")

        # validate the file properties
        data_controller = DataController()

        is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

        if not is_valid:
            log_warning(f"File validation failed for {file.filename}, signal: {result_signal}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": result_signal
                }
            )

        project_dir_path = ProjectController().get_project_path(project_id=project_id)
        file_path, file_id = data_controller.generate_unique_filepath(
            orig_file_name=file.filename,
            project_id=project_id
        )
        log_info(f"Generated file path: {file_path}, file_id: {file_id}")

        try:
            async with aiofiles.open(file_path, "wb") as f:
                while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                    await f.write(chunk)
            log_info(f"File {file.filename} successfully saved at {file_path}")

        except Exception as e:
            log_error(f"Error while uploading file {file.filename}: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
                }
            )

        # store the assets into the database
        asset_model = await AssetModel.create_instance(
            db_client=request.app.db_client
        )

        asset_resource = Asset(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value,
            asset_name=file_id,
            asset_size=os.path.getsize(file_path)
        )

        asset_record = await asset_model.create_asset(asset=asset_resource)
        log_info(f"Asset {file_id} stored in the database with size {os.path.getsize(file_path)}")

        return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": str(asset_record.id),
            }
        )

    except Exception as e:
        log_error(f"Unexpected error during file upload for project_id: {project_id}, file: {file.filename}. Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )
