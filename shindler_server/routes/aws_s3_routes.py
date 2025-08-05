from fastapi import APIRouter, HTTPException
from controllers.aws_s3_controller import generate_presigned_url
from models.base_models import StandardResponse

from utils.response_formatter import ResponseFormatter
from fastapi import status

s3_router = APIRouter()


@s3_router.get("/generate-presigned-url", response_model=StandardResponse)
async def get_presigned_url():
    try:
        presigned_data = generate_presigned_url()
        return ResponseFormatter.success_response(
            message="Presigned URL generated successfully",
            body=presigned_data,
            status_code=status.HTTP_200_OK
        )
    except HTTPException as e:
        return ResponseFormatter.error_response(
            message=str(e.detail),
            status_code=e.status_code,
            body={}
        )
    except Exception as e:
        return ResponseFormatter.server_error_response(
            message="Internal server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            body={"detail": str(e)}
        )


