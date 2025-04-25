from pydantic import BaseModel
from fastapi import status

class ErrorResponse(BaseModel):
    detail: str
    
common_responses = {
    status.HTTP_200_OK: {"description": "OK"},
    status.HTTP_201_CREATED: {"description": "Created"},
    status.HTTP_400_BAD_REQUEST: {
        "description": "Bad Request",
        "model": ErrorResponse,
    },
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Unauthorized",
        "model": ErrorResponse,
        "content": {
                "application/json": {
                    "example": {
                        "detail": "Not authenticated"
                    }
                }
        }
    },
    status.HTTP_403_FORBIDDEN: {
        "description": "Forbidden",
        "model": ErrorResponse,
        "content": {
                "application/json": {
                    "example": {
                        "detail": "Not enough permissions"
                    }
                }
        }
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Not Found",
        "model": ErrorResponse,
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict",
        "model": ErrorResponse,
    },
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "description": "Validation Error",
        "model": ErrorResponse,  # Optional
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal Server Error",
        "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal Server Error"
                    }
                }
        }
        
    },
}
