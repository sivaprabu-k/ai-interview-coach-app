from typing import Any
from fastapi.responses import JSONResponse

def global_response_format(
    status_value: bool,
    data: Any,
    status_code: int,
    status_message: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status": status_value,
            "data": data,
            "status_code": status_code,
            "message": status_message,
        },
    )
