from dotenv import load_dotenv
from fastapi.responses import JSONResponse

load_dotenv()

import os
import time
from secure import (
    Secure,
    ContentSecurityPolicy,
    StrictTransportSecurity,
    ReferrerPolicy,
    CacheControl,
    XFrameOptions,
)
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.infrastructure.mongodb import load_collection, MongoConfig
from src.controllers import files_controller, schemas_controller, pipelines_controller
from src.logger import logger, log_context


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CLIENT_ORIGIN_URLS").split(","),
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=86400,
)

secure_headers = Secure(
    csp=ContentSecurityPolicy().default_src("'self'").frame_ancestors("'none'"),
    hsts=StrictTransportSecurity().max_age(31536000).include_subdomains(),
    referrer=ReferrerPolicy().no_referrer(),
    cache=CacheControl().no_cache().no_store().max_age(0).must_revalidate(),
    xfo=XFrameOptions().deny(),
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    request.state.request_id = request_id
    log_context.request_id = request_id  # Add to log context for logging
    logger.info(f"Starting request with ID: {request_id}")

    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time

    # secure_headers.set_headers(response)
    logger.info(f"Ending request with ID: {request_id} in {process_time}s")
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    message = str(exc.detail)

    return JSONResponse({"message": message}, status_code=exc.status_code)


app.include_router(files_controller.router)
app.include_router(schemas_controller.router)
app.include_router(pipelines_controller.router)
