import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from src.infrastructure.mongodb import load_collection, MongoConfig
from src.controllers import files_controller, schemas_controller, pipelines_controller


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Execute before application starts
    await load_collection(
        MongoConfig(user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"))
    )
    yield
    # Execute after the application has finished


app = FastAPI(
    title="Docuxtract API",
    summary="A simple way of extracting document data.",
    description="This API is intended to be easy for developers to add value with document extraction tools.",
    lifespan=lifespan,
)

app.include_router(files_controller.router)
app.include_router(schemas_controller.router)
app.include_router(pipelines_controller.router)
