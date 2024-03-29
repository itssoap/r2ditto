# FastAPI deps
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import Response, StreamingResponse
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# Other deps
from dotenv import load_dotenv
from uvicorn import run
import boto3
import random
import string
import botocore
import os

# globals
s3_obj = None
bucket = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # App lifespan begins

    # startup event here
    global s3_obj, bucket
    s3_obj = boto3.client(
        service_name=os.getenv("SERVICE_NAME"),
        endpoint_url=os.getenv("ENDPOINT_URL"),
        aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
        region_name=os.getenv("REGION"),
    )
    bucket = os.getenv("BUCKET")

    yield

    # shutdown event here
    try:
        for filename in os.listdir():
            if filename[:4] == 'temp':
                os.remove(filename)

    except FileNotFoundError:
        pass


app = FastAPI(lifespan=lifespan)


@app.get("/{filename}", response_model=None, response_class=Response)
async def getter(filename: str, request: Request) -> Response:  # type: ignore
    if filename == "openapi.json":
        return Response(content="", media_type="application/json")
    try:
        object_information = s3_obj.head_object(Bucket=bucket, Key=filename)
        mimetype = object_information["ContentType"]

        file_data = None
        with open(f"temp.{filename.split('.')[-1]}", "wb") as file_data:
            s3_obj.download_fileobj(Bucket=bucket, Key=filename, Fileobj=file_data)

    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return Response(content="Nuh uh", status_code=404, media_type="text/html")
        else:
            raise

    def iterfile():
        with open(f"temp.{filename.split('.')[-1]}", mode="rb") as file_data:
            yield from file_data

    return StreamingResponse(content=iterfile(), status_code=200, media_type=mimetype)


@app.get("/", response_model=None, response_class=Response)
def upload_page() -> Response:
    resp = "<pre><span style='color: #4BB543;'>GET</span> <span style='color: #4BB543;'>/{filename}</span>  HTTP/1.1</pre>"
    resp += "<br><hr>"
    resp += "<pre><span style='color: #3944BC;'>PUT</span> <span style='color: #4BB543;'>/</span>  HTTP/1.1</pre>"
    resp += "<pre>Content-Type: multipart/form-data</pre>"
    resp += "<pre>cURL:</pre>"
    resp += "<textarea id='curl' readonly>curl --request PUT \
                    --url https://img.itssoap.ninja/ \
                    --header 'content-type: multipart/form-data' \
                    --form file=@file</textarea>"
    resp += "<button onclick=\"copyText()\">Copy</button>"
    resp += "<script> \
                function copyText() {\
                    let text = document.getElementById('curl').innerHTML; \
                    navigator.clipboard.writeText(text); } \
            </script>" 
    return Response(
        content=resp,
        status_code=200,
        media_type="text/html",
    )


@app.put("/", response_model=None, response_class=Response)
def putter(file: UploadFile = File(...)) -> Response:
    extension = file.filename.split(".")[-1]

    # a 6-character randomized string for file names
    new_name = str(
        "".join(
            random.SystemRandom().choice(string.ascii_lowercase + string.digits)
            for _ in range(6)
        )
    )

    s3_obj.upload_fileobj(
        Fileobj=file.file, Bucket=bucket, Key=f"{new_name}.{extension}"
    )

    file_host = os.getenv("PERSONAL_ENDPOINT")
    file_url = f"{file_host}{'/' if file_host[-1]!='/' else ''}{new_name}.{extension}"

    return Response(content=file_url, status_code=200, media_type="text/plain")


if __name__ == "__main__":
    load_dotenv()
    run(
        "r2ditto.__main__:app",
        host="127.0.0.1",
        port=int(os.getenv("PORT")),
        reload=True,
    )
