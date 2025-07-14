import asyncio
from typing import Any, Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
from api import APIKEY
from PIL import Image
from google import genai

client = genai.Client(api_key=APIKEY)

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3M2VjMWU0Mi0wMjViLTRjMGUtOWQ2NS0wMmI0OGFlODIzYjIiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6ImY2NWIzNTBmLTY0NWQtNGIzYy1hZDUzLTMzY2RmOTU4OWVjZSJ9.NJLXyg60791a8x7dlFQWIuuq3HnxGLQgPvVrP48VhNo" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT)

def InputImage(content, path):
    image = Image.open(path)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[image, content]
    )
    return (response.text)

@session.bind(
    name="imagebot",
    description="This agent sees the content of the image and tells what crop the image is"
)
async def imagebot(
        agent_context,
        file_id: Annotated[str, "ID of the file to read"]
) -> dict[str, Any]:
    
    file = await agent_context.files.get_by_id(file_id)
    return InputImage("You are an expert farmer, you need to tell me what is the following crop, what it is used for and is there somethign that seems to be wrong with the image", path=file)


async def main():
    print(f"Agent with ID {session.jwt_token} started")
    await session.process_events()


if __name__ == "__main__":
    asyncio.run(main())

