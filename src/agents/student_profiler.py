from agent import Agent
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("student_profiler")

@mcp.list_resources()
async def list_resources() -> list[types.Resources]:
    return [
        type.Resource(
            uri="file:///",
            name="Student Parameters",
            mimeType="aplication/json"
        )   
    ]

#TODO should execute BDI para definir parametros