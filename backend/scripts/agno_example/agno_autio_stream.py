import base64
import wave
from typing import Iterator

import pyaudio
from agno.agent import Agent, RunOutputEvent
from agno.models.openai import OpenAIChat
from app.config import SETTINGS

# Audio Configuration
SAMPLE_RATE = 24000  # Hz (24kHz)
CHANNELS = 1  # Mono (Change to 2 if Stereo)
SAMPLE_WIDTH = 2  # Bytes (16 bits)

# Provide the agent with the audio file and audio configuration and get result as text + audio
agent = Agent(
    model=OpenAIChat(
        api_key=SETTINGS.OPENAI_API_KEY,
        id="gpt-audio-mini-2025-10-06",
        modalities=["text", "audio"],
        audio={
            "voice": "alloy",
            "format": "pcm16",
        },  # Only pcm16 is supported with streaming
    ),
)
output_stream: Iterator[RunOutputEvent] = agent.run(
    "Tell me a 10 second story", stream=True
)

filename = "tmp/response_stream.wav"

# Initialize PyAudio for real-time playback
p = pyaudio.PyAudio()
stream = p.open(
    format=p.get_format_from_width(SAMPLE_WIDTH),
    channels=CHANNELS,
    rate=SAMPLE_RATE,
    output=True,
)

# Open the file to save audio as well
with wave.open(str(filename), "wb") as wav_file:
    wav_file.setnchannels(CHANNELS)
    wav_file.setsampwidth(SAMPLE_WIDTH)
    wav_file.setframerate(SAMPLE_RATE)

    # Iterate over generated audio
    for response in output_stream:
        response_audio = response.response_audio  # type: ignore
        if response_audio:
            if response_audio.transcript:
                print(response_audio.transcript, end="", flush=True)
            if response_audio.content:
                try:
                    pcm_bytes = base64.b64decode(response_audio.content)
                    # Save to file
                    wav_file.writeframes(pcm_bytes)
                    # Play in real-time
                    stream.write(pcm_bytes)
                except Exception as e:
                    print(f"Error decoding audio: {e}")

# Cleanup
stream.stop_stream()
stream.close()
p.terminate()
print()
print(f"\nAudio saved to {filename}")