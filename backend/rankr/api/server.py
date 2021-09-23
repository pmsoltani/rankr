from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import backc
from rankr.api.v1.routers import router as api_router


def get_application() -> FastAPI:  # Server factory function
    app = FastAPI(
        title=backc.BACKEND_NAME,
        description=backc.DESCRIPTION,
        version=backc.VERSION,
        docs_url=f"{backc.API_V1_STR}/docs",
        openapi_url=f"{backc.API_V1_STR}",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=backc.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=backc.API_V1_STR)

    return app


app = get_application()


@app.get(backc.API_V1_STR, name="root")
async def root():
    return {"message": "Hello World"}
