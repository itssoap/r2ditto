from fastapi import FastAPI, Request
from fastapi.responses import Response


from uvicorn import run

app = FastAPI()

@app.get("/", response_model=None, response_class=Response)
async def getter(request: Request) -> Response: # type: ignore
    return Response(content="Hello", status_code=200, media_type="text/html")


if __name__ == '__main__':
    run("r2ditto.__main__:app", host="127.0.0.1", port=8090, reload=True)