import os
import sys
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

FILE_LOCATION = f"{os.path.dirname(__file__)}/upload_file.py"

# Add root dir and handle potential import errors
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
    from config import get_settings, Settings
    from controllers import get_clean_file_name
except Exception as e:
    msg = f"Import Error in: {FILE_LOCATION}, Error: {e}"
    raise ImportError(msg)

upload_route = APIRouter()

UPLOAD_DIR = get_settings().DOC_LOCATION_SAVE
os.makedirs(UPLOAD_DIR, exist_ok=True)


@upload_route.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    app_settings: Settings = Depends(get_settings)
):
    try:
        # Generate a clean and sanitized file name
        unique_filename = get_clean_file_name(file.filename)
        file_location = os.path.join(UPLOAD_DIR, unique_filename)

        # Extract file extension
        file_extension = os.path.splitext(unique_filename)[1].lower()
        print(file_extension)
        # Check if the file type is allowed
        if file_extension in app_settings.FILE_ALLOWED_TYPES:
            # Save the file to disk
            with open(file_location, "wb") as f:
                shutil.copyfileobj(file.file, f)

            log_info(f"File uploaded and saved as '{unique_filename}' at '{file_location}'")

            return JSONResponse(
                status_code=200,
                content={
                    "message": "File uploaded successfully.",
                    "filename": unique_filename,
                    "saved_to": file_location
                }
            )
        else:
            return JSONResponse(
                content="The file type is not supported.",
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
            )
    except Exception as e:
        log_error(f"Failed to upload file '{file.filename}': {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File upload failed.")