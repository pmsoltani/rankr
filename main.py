from fastapi import FastAPI
import uvicorn

from rankr.api.v1.api import api_router
from config import appc

app = FastAPI(title=appc.APP_NAME)

app.include_router(api_router, prefix=appc.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=appc.APP_HOST, port=appc.APP_PORT, reload=True,
    )
