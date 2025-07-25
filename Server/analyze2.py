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
import base64
# client = stdio_client("AudioRegistryServer")

server_params = StdioServerParameters(
    command="python",  # Adjust as needed
    args=["main.py"],  # Your actual server script path
    env={}
)

app = Flask(__name__)
CORS(app)

AUDIO_DIR = "audio_store"
os.makedirs(AUDIO_DIR, exist_ok=True)

# def fix_base64_padding(data):
#     return data + '=' * (-len(data) % 4)

@app.route('/audioAnalyze', methods= ['POST'])
async def analyze():
    file = request.files['audio']
    context_id = request.form.get('context_id')

    print(file, context_id,"////////////////")
    if not file or not context_id:
        return jsonify({"error": "Missing file or context ID"}), 400

    if not file.filename.lower().endswith('.wav') and \
    file.mimetype != 'audio/wav':
        print(f"Unsupported file type: {file.filename}, Mime: {file.mimetype}")
        return jsonify({"error": "Unsupported file type. Please upload a WAV audio file."}), 415 
    

    file_path = os.path.join(AUDIO_DIR, f"{context_id}.wav")
    audio = AudioSegment.from_file(file.stream)
    audio.export(file_path, format="wav", parameters=["-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1"])
    
#-----------------------------------------------------------------------------------------------------

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print(session,"-----------------------")
            # Initialize the connection
            # try:
            await session.initialize()

            # List available tools
            # tools = await session.list_tools()
            # print(f"Available tools: {[t.name for t in tools.tools]}")

            result = await session.call_tool("get_audio_by_contextId", arguments={"context_id": context_id})
            # print("Tool result object:", result)
            if result.content and isinstance(result.content[0], types.TextContent):
                # print("Raw base64 received:----------------=================>", repr(result.content[0].text))
                # b64_data = result.content[0].text.strip().replace("\n", "").replace(" ", "")  # remove whitespace/newlines
                # b64_data = fix_base64_padding(b64_data) 
                b64_data = result.content[0].text
                audio_bytes = base64.b64decode(b64_data)
    
    

            try:
                # Read the incoming blob
                audio_segment = AudioSegment.from_file(BytesIO(audio_bytes), format="wav")

                # Export to a standard PCM WAV format (e.g., 16-bit, 44.1kHz, mono)
                # Create an in-memory buffer for the converted audio , convet the audio which can be easily analysed by soundfile
                pcm_wav_buffer = BytesIO()
                audio_segment.export(pcm_wav_buffer, format="wav", 
                                    parameters=["-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1"])
                pcm_wav_buffer.seek(0) # Rewind the buffer to the beginning

                # Now use your analysis library with the converted audio
                audio_data, samplerate = sf.read(pcm_wav_buffer) 

                if audio_data.ndim > 1: # If stereo, take the mean across channels
                    average_amplitude = np.mean(np.abs(audio_data)) #calculate abs and avergae of all the audio neg and positive
                else: # If mono
                    average_amplitude = np.mean(np.abs(audio_data))
                
                # Scale average amplitude to a 0-1 range for a "score"
                # This is a very simplistic example. Adjust logic as needed.
                score = min(1.0, average_amplitude * 10.0) # Adjust multiplier based on expected amplitude range

                # Example: Determine anomaly based on score threshold
                anomaly = False
                if score < 0.3 or score > 0.95: # Very low or very high amplitude could be an "anomaly"
                    anomaly = True

                # ----------------------------------------------------

                # 6. Return the analysis results as JSON
                return jsonify({
                    "score": float(f"{score:.2f}"), # Format to 2 decimal places
                    "anomaly": anomaly,
                    "message": "Audio analyzed successfully!"
                }), 200 

            except Exception as e:
                print(f"Error during audio conversion/processing: {e}")
                return jsonify({"error": f"Failed to process audio. Details: {str(e)}"}), 500


# def main():
#     """Entry point for the client script."""
#     asyncio.run(analyze())


if __name__ == '__main__':
    app.run(debug=True, port=5000)

        
    