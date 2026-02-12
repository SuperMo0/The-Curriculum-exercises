import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import base64

load_dotenv()

endpoint = "https://models.github.ai/inference"
client = OpenAI(api_key=os.getenv("GITHUB_TOKEN"), base_url=endpoint)
model = "openai/gpt-4o"


def create_file(file_path):
    with open(file_path, "rb") as file_content:
        result = client.files.create(
            file=file_content,
            purpose="assistants",
        )
        return result.id


app = FastAPI()

app.mount(
    "/public",
    StaticFiles(
        directory="public",
    ),
    name="static",
)


class FocalPoint(BaseModel):
    x_percent: Annotated[
        float, Field(description="X coordinate as a percentage of the image width")
    ]
    y_percent: Annotated[
        float, Field(description="Y coordinate as a percentage of the image height")
    ]


def get_image_main_subject(imageUrl):
    response = client.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What is the main subject of this image? Please provide a brief description.",
                    },
                    {"type": "image_url", "image_url": imageUrl},
                ],
            }
        ],
    )
    return response.choices[0].message.content


def get_image_analysis(imageUrl, main_subject):
    response = client.chat.completions.parse(
        model=model,
        response_format=FocalPoint,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "send the exact coordintes in percentage of the main subject in the image make sure that the main subject is accurately represented in the center when scaling image 2.5x, which is: "
                        + main_subject,
                    },
                    {"type": "image_url", "image_url": imageUrl},
                ],
            }
        ],
    )
    return response.choices[0].message.parsed


@app.post("/upload")
async def handle_image_upload(
    image: Annotated[UploadFile, File(description="Uploaded User Image")],
):

    image_bytes = await image.read()

    mime_type = image.content_type or "application/octet-stream"
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:{mime_type};base64,{image_base64}"

    try:
        print("calling get_image_main_subject")
        main_subject = get_image_main_subject(image_data_url)
        print("calling get_image_analysis")
        analysis = get_image_analysis(image_data_url, main_subject)
        return {"analysis": analysis, "main_subject": main_subject}
    except Exception as e:
        print("Error during image analysis:", e)
        raise e


@app.get("/")
async def root():
    return FileResponse("views/index.html", status_code=200, media_type="text/html")
