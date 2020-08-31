from fastapi import FastAPI
import uvicorn

from rankr.api.v1.api import api_router
from config import APPConfig

app = FastAPI(title=APPConfig.APP_NAME)

app.include_router(api_router, prefix=APPConfig.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=APPConfig.APP_HOST,
        port=APPConfig.APP_PORT,
        reload=True,
    )
