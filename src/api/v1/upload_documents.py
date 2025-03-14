from fastapi import APIRouter, Depends, UploadFile, status, Request, HTTPException
from fastapi.responses import JSONResponse
import os, sys, aiofiles
from utils.helpers import get_settings, Settings
from db import Asset
from controllers import DataController, ProjectController
from enums import ResponseSignal, AssetTypeEnum
from logs import log_error, log_info, log_warning
from core import AssetModel, ProjectModel

upload_router = APIRouter()

@upload_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings)
):
    try:
        log_info(f"Starting file upload for project: {project_id}")

        # Validate project existence
        project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
        project = await project_model.get_project_or_create_one(project_id=project_id)

        if not project:
            log_warning(f"Project {project_id} could not be found or created.")
            raise HTTPException(status_code=400, detail="Project not found or could not be created.")

        # Validate file properties
        data_controller = DataController()
        is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

        if not is_valid:
            log_warning(f"Invalid file upload attempt: {result_signal}")
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal": result_signal})

        # Generate unique file path
        file_path, file_id = data_controller.generate_unique_filepath(
            orig_file_name=file.filename, project_id=project_id
        )

        # Save the file asynchronously
        try:
            async with aiofiles.open(file_path, "wb") as f:
                while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                    await f.write(chunk)
        except Exception as e:
            log_error(f"Error writing file {file.filename} to disk: {e}")
            raise HTTPException(status_code=500, detail="Error saving file to server.")

        # Store asset information in database
        asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
        asset_resource = Asset(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value,
            asset_name=file_id,
            asset_size=os.path.getsize(file_path),
        )

        asset_record = await asset_model.create_asset(asset=asset_resource)
        log_info(f"File {file.filename} uploaded successfully as {file_id}")

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value, 
            "file_id": str(file_id)}
        )

    except HTTPException as he:
        log_warning(f"HTTP Exception: {he.detail}")
        return JSONResponse(status_code=he.status_code, content={"detail": he.detail})

    except Exception as e:
        log_error(f"Unexpected error during file upload: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal Server Error"})
