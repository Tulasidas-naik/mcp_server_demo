from flask import Flask, request, jsonify
from flask_cors import CORS
# import librosa
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from io import BytesIO
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters, types
import asyncio
import os
from mcp.shared.context import RequestContext
# client = stdio_client("AudioRegistryServer")

server_params = StdioServerParameters(
    command="python",  # Using uv to run the server
    args=["run", "server", "main", "stdio"],  # We're already in snippets dir
    env={"UV_INDEX": os.environ.get("UV_INDEX", "")},
)

app = Flask(__name__)
CORS(app)

# Optional: create a sampling callback
async def handle_sampling_message(
    context: RequestContext, params: types.CreateMessageRequestParams
) -> types.CreateMessageResult:
    print(f"Sampling request: {params.messages}")
    return types.CreateMessageResult(
        role="assistant",
        content=types.TextContent(
            type="text",
            text="Hello, world! from model",
        ),
        model="gpt-3.5-turbo",
        stopReason="endTurn",
    )

@app.route('/audioAnalyze', methods= ['POST'])
async def analyze():
    async with stdio_client(server_params) as (read, write):
        print(read, write, "????????????????")
        async with ClientSession(read, write, sampling_callback=handle_sampling_message) as session:
            print(session,"-----------------------")
            # Initialize the connection
            try:
                await session.initialize()

            # List available tools
                tools = await session.list_tools()
                print(f"Available tools: {[t.name for t in tools.tools]}")

                context_id = "ctx1" 
                result = await session.call_tool("get_audio_by_contextId", arguments={context_id:context_id})
                result_unstructured = result.content[0]
                print(result_unstructured, "//////////////////////")
        
            
            except Exception as e:
                print(f"Unhandled exception: {e}")


    # print(request.files, "...................")
    # if 'audio' not in request.files:
    #     return jsonify({'error': 'no audio file'}), 400

    # audio_file = request.files['audio']

    # if not audio_file.filename.lower().endswith('.wav') and \
    #    audio_file.mimetype != 'audio/wav':
    #     print(f"Unsupported file type: {audio_file.filename}, Mime: {audio_file.mimetype}")
    #     return jsonify({"error": "Unsupported file type. Please upload a WAV audio file."}), 415 
    # context_id = "ctx1" 
    # audio_bytes = stdio_client("get_audio_by_contextId")(context_id=context_id)

    # try:
    #     # Read the incoming blob
    #     audio_segment = AudioSegment.from_file(BytesIO(result_unstructured))

    #     # Export to a standard PCM WAV format (e.g., 16-bit, 44.1kHz, mono)
    #     # Create an in-memory buffer for the converted audio , convet the audio which can be easily analysed by soundfile
    #     pcm_wav_buffer = BytesIO()
    #     audio_segment.export(pcm_wav_buffer, format="wav", 
    #                         parameters=["-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1"])
    #     pcm_wav_buffer.seek(0) # Rewind the buffer to the beginning

    #     # Now use your analysis library with the converted audio
    #     audio_data, samplerate = sf.read(pcm_wav_buffer) 

    #     if audio_data.ndim > 1: # If stereo, take the mean across channels
    #         average_amplitude = np.mean(np.abs(audio_data)) #calculate abs and avergae of all the audio neg and positive
    #     else: # If mono
    #         average_amplitude = np.mean(np.abs(audio_data))
        
    #     # Scale average amplitude to a 0-1 range for a "score"
    #     # This is a very simplistic example. Adjust logic as needed.
    #     score = min(1.0, average_amplitude * 10.0) # Adjust multiplier based on expected amplitude range

    #     # Example: Determine anomaly based on score threshold
    #     anomaly = False
    #     if score < 0.3 or score > 0.95: # Very low or very high amplitude could be an "anomaly"
    #         anomaly = True

    #     # ----------------------------------------------------

    #     # 6. Return the analysis results as JSON
    #     return jsonify({
    #         "score": float(f"{score:.2f}"), # Format to 2 decimal places
    #         "anomaly": anomaly,
    #         "message": "Audio analyzed successfully!"
    #     }), 200 

    # except Exception as e:
        # print(f"Error during audio conversion/processing: {e}")
        # return jsonify({"error": f"Failed to process audio. Details: {str(e)}"}), 500


def main():
    """Entry point for the client script."""
    asyncio.run(analyze())


if __name__ == '__main__':
    main()


        
    