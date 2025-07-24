from mcp.server.fastmcp import FastMCP
from typing import Optional
import os

mcp = FastMCP("AudioRegistryServer")

AUDIO_CONTEXT_MAP = {
    "ctx1": ".wav",
    "ctx2": ".wav"
}

@mcp.tool()
def get_audio_by_contextId(context_id: str) -> Optional[bytes]:
    
    file_path = AUDIO_CONTEXT_MAP.get(context_id)
    if not file_path or not os.path.exists(file_path):
        raise ValueError(f"Audio file for context_id '{context_id}' not found.")

    with open(file_path, "rb") as file:
        return file.read()


if __name__ == "__main__":
    mcp.run()