import asyncio
import base64
import json
from pathlib import Path

import websockets


AUDIO_FILE = Path("test_audio/microphone_test.wav")
WEBSOCKET_URL = "ws://127.0.0.1:8000/api/v1/ws/voice/demo-session"

async def main():
    print("=" * 60)
    print("MICROPHONE → WEBSOCKET VOICE TEST")
    print("=" * 60)

    if not AUDIO_FILE.exists():
        print(f"Audio file not found: {AUDIO_FILE}")
        return

    audio_data = AUDIO_FILE.read_bytes()

    print()
    print(f"Audio file: {AUDIO_FILE}")
    print(f"Audio size: {len(audio_data)} bytes")
    print()

    async with websockets.connect(
        WEBSOCKET_URL
    ) as websocket:

        # Receive connected event
        message = await websocket.recv()

        print("Server:")
        print(message)

        # Send metadata
        await websocket.send(
            json.dumps(
                {
                    "filename": AUDIO_FILE.name
                }
            )
        )

        # Send microphone audio
        print()
        print("Sending microphone audio...")
        await websocket.send(audio_data)

        # Receive server events
        while True:
            message = await websocket.recv()

            data = json.loads(message)

            event_type = data.get("type")

            if event_type == "processing":
                print("Event: processing")
                print(data.get("message"))

            elif event_type == "transcription":
                print("Event: transcription")
                print("You:", data.get("text"))

            elif event_type == "response":
                print("Event: response")
                print("AI:", data.get("text"))

            elif event_type == "audio":
                print("Event: audio")

                audio_bytes = base64.b64decode(
                    data["data"]
                )

                output_file = Path(
                    "test_audio/microphone_websocket_response.mp3"
                )

                output_file.write_bytes(audio_bytes)

                print(
                    f"Audio saved to: {output_file}"
                )
                print(
                    f"Audio size: {len(audio_bytes)} bytes"
                )

            elif event_type == "complete":
                print("Event: complete")
                print(
                    "Session:",
                    data.get("session_id")
                )
                break

            elif event_type == "error":
                print("Event: error")
                print(data.get("message"))
                break

    print()
    print("=" * 60)
    print("MICROPHONE WEBSOCKET TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())