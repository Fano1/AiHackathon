import asyncio
from typing import Annotated
from genai_session.session import GenAISession
from genai_session.utils.context import GenAIContext
from protocolReggessor import analyze_location as al

AGENT_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNTMyN2YzMi02YzhiLTQ0M2ItOGE4Mi1jNDAzZmUyNDQ3NDIiLCJleHAiOjI1MzQwMjMwMDc5OSwidXNlcl9pZCI6ImY2NWIzNTBmLTY0NWQtNGIzYy1hZDUzLTMzY2RmOTU4OWVjZSJ9.20DdAkSg2P-0uuLpMLNfrszrsczSFtGhQ93agchAtJw" # noqa: E501
session = GenAISession(jwt_token=AGENT_JWT)

@session.bind(
    name="croprecommandationbot",
    description="This bot is used to give the recommanded crop for certain area, this tool uses location, current climate, current season to pick best crops to farm and give the best suggestion on how to grow them"
)
async def croprecommandationbot(
    agent_context: GenAIContext,
    location: Annotated[str, "The current user loaction"]    
):
    
    """This bot is used to give the recommanded crop for certain area, this tool uses location, current climate, current season to pick best crops to farm and give the best suggestion on how to grow them"""
    return (await (al(location)))


async def main():
    print(f"Agent with token '{AGENT_JWT}' started")
    await session.process_events()

if __name__ == "__main__":
    asyncio.run(main())
