from mcp.server.fastmcp import FastMCP
from typing import Optional
import os
from mcp import types
import base64
from pydub import AudioSegment
from io import BytesIO

mcp = FastMCP("AudioRegistryServer")

# AUDIO_CONTEXT_MAP = {
#     "ctx1": "sample-3s.wav",
#     "ctx2": "sample-6s.wav",
#     "ctx3": "sample-9s.wav",
# }

AUDIO_DIR = "audio_store"

@mcp.tool()
def get_audio_by_contextId(context_id: str) -> Optional[types.TextContent]:
    
    file_path = os.path.join(AUDIO_DIR, f"{context_id}.wav")
    if not file_path or not os.path.exists(file_path):
        raise ValueError(f"Audio file for context_id '{context_id}' not found.")
    
    audio = AudioSegment.from_file(file_path)
    buf = BytesIO()
    audio.export(buf, format="wav", parameters=["-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1"])
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    return types.TextContent(type="text", text=encoded)

if __name__ == "__main__":
    mcp.run()