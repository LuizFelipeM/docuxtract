import logging
import os
import time
from uuid import uuid4
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from src.infrastructure.mongodb import load_collection, MongoConfig
from src.controllers import files_controller, schemas_controller, pipelines_controller
from threading import local

# Configure logging
# logging.basicConfig(
#     format="%(asctime)s - %(request_id)s - %(message)s", level=logging.INFO
# )
# logger = logging.getLogger(__name__)

# # Thread-local storage to store request context
# log_context = local()


# # Custom logging filter to add request_id
# class RequestIdFilter(logging.Filter):
#     def filter(self, record):
#         record.request_id = getattr(log_context, "request_id", "N/A")
#         return True


# # Add the filter to logger
# logger.addFilter(RequestIdFilter())

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


# @app.middleware("http")
# async def add_logging_context(request: Request, call_next):
#     request_id = request.headers.get("X-Request-ID", str(uuid4()))
#     request.state.request_id = request_id
#     log_context.request_id = request_id  # Add to log context for logging
#     logger.info(f"Starting request with ID: {request_id}")

#     start_time = time.perf_counter()
#     response = await call_next(request)
#     process_time = time.perf_counter() - start_time

#     response.headers["X-Process-Time"] = str(process_time)
#     response.headers["X-Request-ID"] = request_id
#     logger.info(f"Ending request with ID: {request_id} in {process_time}s")
#     return response


app.include_router(files_controller.router)
app.include_router(schemas_controller.router)
app.include_router(pipelines_controller.router)
