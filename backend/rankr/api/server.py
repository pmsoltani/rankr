from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import appc
from rankr.api.v1.routers import router as api_router


def get_application() -> FastAPI:  # Server factory function
    app = FastAPI(
        title=appc.APP_NAME,
        description=appc.DESCRIPTION,
        version=appc.VERSION,
        docs_url=f"{appc.API_V1_STR}/docs",
        openapi_url=f"{appc.API_V1_STR}",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=appc.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=appc.API_V1_STR)

    return app


app = get_application()


@app.get(appc.API_V1_STR, name="root")
async def root():
    return {"message": "Hello World"}
