# FastAPI deps
<<<<<<< HEAD
from fastapi import FastAPI, Request
=======
from fastapi import FastAPI, Request, File, UploadFile
>>>>>>> e741503 (PUT request model)
from fastapi.responses import Response, StreamingResponse
from contextlib import asynccontextmanager

# Other deps
from dotenv import load_dotenv
from uvicorn import run
import boto3
import random
import string
import botocore
import os
<<<<<<< HEAD


# globals
s3_obj = None
bucket = None

@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    # App lifespan begins
    
    # startup event here
    global   s3_obj, bucket
    load_dotenv()
    s3_obj = boto3.client(
        service_name = os.getenv("SERVICE_NAME"),
        endpoint_url = os.getenv("ENDPOINT_URL"),
        aws_access_key_id = os.getenv("ACCESS_KEY_ID"),
        aws_secret_access_key = os.getenv("SECRET_ACCESS_KEY"),
        region_name = os.getenv("REGION")
    )
    bucket = os.getenv("BUCKET")   

    yield

    # shutdown event here


app = FastAPI(lifespan=lifespan)


@app.get("/{filename}", response_model=None, response_class=Response | StreamingResponse)
async def getter(filename: str, request: Request) -> Response | StreamingResponse: # type: ignore
    try:
        object_information = s3_obj.head_object(Bucket=bucket, Key=filename)
        mimetype = object_information["ContentType"]

        file_data = None
        with open(f"temp.{filename.split('.')[-1]}", "wb") as file_data:
            s3_obj.download_fileobj(Bucket=bucket, Key=filename, Fileobj=file_data)
    
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return Response(content="Nuh uh", status_code=404, media_type="text/html")
        else:
            raise

    def iterfile():  # 
        with open(f"temp.{filename.split('.')[-1]}", mode="rb") as file_data:
            yield from file_data

    return StreamingResponse(content=iterfile(), status_code=200, media_type=mimetype)
=======
from typing import Annotated

# globals
s3_obj = None
bucket = None

@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    # App lifespan begins
    
    # startup event here
    global s3_obj, bucket
    s3_obj = boto3.client(
        service_name = os.getenv("SERVICE_NAME"),
        endpoint_url = os.getenv("ENDPOINT_URL"),
        aws_access_key_id = os.getenv("ACCESS_KEY_ID"),
        aws_secret_access_key = os.getenv("SECRET_ACCESS_KEY"),
        region_name = os.getenv("REGION")
    )
    bucket = os.getenv("BUCKET")   

    yield

    # shutdown event here
    try:
        os.remove("temp.png")
    except FileNotFoundError:
        pass

app = FastAPI(lifespan=lifespan)


@app.get("/{filename}", response_model=None, response_class=Response)
async def getter(filename: str, request: Request) -> Response: # type: ignore
    if filename == 'openapi.json':
        return Response(content="", media_type="application/json")
    try:
        object_information = s3_obj.head_object(Bucket=bucket, Key=filename)
        mimetype = object_information["ContentType"]

        file_data = None
        with open(f"temp.{filename.split('.')[-1]}", "wb") as file_data:
            s3_obj.download_fileobj(Bucket=bucket, Key=filename, Fileobj=file_data)
    
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return Response(content="Nuh uh", status_code=404, media_type="text/html")
        else:
            raise

    def iterfile():
        with open(f"temp.{filename.split('.')[-1]}", mode="rb") as file_data:
            yield from file_data

    return StreamingResponse(content=iterfile(), status_code=200, media_type=mimetype)


@app.get("/", response_model=None, response_class=Response)
def upload_page() -> Response:
    return Response(content=
                    "<pre><span style='color: #4BB543;'>GET</span> <span style='color: #4BB543;'>/{filename}</span>  HTTP/1.1</pre>" \
                    +"<br><hr>" \
                    +"<pre><span style='color: #3944BC;'>PUT</span> <span style='color: #4BB543;'>/</span>  HTTP/1.1</pre>" \
                    + "<pre>Content-Type: multipart/form-data</pre>" \
                    , status_code=200, media_type="text/html")


@app.put("/", response_model=None, response_class=Response)
def putter(file: UploadFile = File(...)) -> Response:
    extension = file.filename.split('.')[-1]

    # a 6-character randomized string for file names
    new_name = str(''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(6)))

    s3_obj.upload_fileobj(Fileobj=file.file, Bucket=bucket, Key=f"{new_name}.{extension}")

    file_host = os.getenv('PERSONAL_ENDPOINT')
    file_url = f"{file_host}{'/' if file_host[-1]!='/' else ''}{new_name}.{extension}"

    return Response(content=file_url, status_code=200, media_type="text/plain")
>>>>>>> e741503 (PUT request model)


if __name__ == '__main__':
    load_dotenv()
    run("r2ditto.__main__:app", host="127.0.0.1", port=int(os.getenv("PORT")), reload=True)