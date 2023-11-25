# FastAPI deps
from fastapi import FastAPI, Request
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


if __name__ == '__main__':
    run("r2ditto.__main__:app", host="127.0.0.1", port=8090, reload=True)