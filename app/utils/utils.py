from typing import Dict, Optional

from fastapi.responses import JSONResponse


def success_response(message, data):
    return {"success": True, "message": message, "data": data}


def error_response(message: str, errors: dict | None = None, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message, "errors": errors},
    )
