import asyncio
import base64
import json
from pathlib import Path

import websockets


WS_URL = (
    "ws://127.0.0.1:8000"
    "/api/v1/ws/voice/demo-session"
)

AUDIO_FILE = Path("test_audio/hello.wav")


async def main():
    print("=" * 60)
    print("REAL WEBSOCKET VOICE TEST")
    print("=" * 60)

    if not AUDIO_FILE.exists():
        print(f"Audio file not found: {AUDIO_FILE}")
        return

    audio_data = AUDIO_FILE.read_bytes()

    print(f"Audio file: {AUDIO_FILE}")
    print(f"Audio size: {len(audio_data)} bytes")
    print()

    async with websockets.connect(
        WS_URL
    ) as websocket:

        # ---------------------------------------------
        # Connection message
        # ---------------------------------------------

        message = await websocket.recv()

        print("Server:")
        print(message)
        print()

        # ---------------------------------------------
        # Send metadata
        # ---------------------------------------------

        await websocket.send(
            json.dumps(
                {
                    "filename": AUDIO_FILE.name
                }
            )
        )

        # ---------------------------------------------
        # Send audio
        # ---------------------------------------------

        print("Sending audio...")
        await websocket.send(audio_data)

        # ---------------------------------------------
        # Receive server events
        # ---------------------------------------------

        while True:

            message = await websocket.recv()

            data = json.loads(message)

            event_type = data.get("type")

            print(f"Event: {event_type}")

            if event_type == "processing":
                print(
                    data.get("message")
                )

            elif event_type == "transcription":
                print(
                    "Transcription:",
                    data.get("text")
                )

            elif event_type == "response":
                print(
                    "AI Response:",
                    data.get("text")
                )

            elif event_type == "audio":

                audio_base64 = data.get(
                    "data"
                )

                audio_bytes = base64.b64decode(
                    audio_base64
                )

                output_path = Path(
                    "test_audio/websocket_response.mp3"
                )

                output_path.write_bytes(
                    audio_bytes
                )

                print(
                    "Audio saved to:",
                    output_path
                )

                print(
                    "Audio size:",
                    len(audio_bytes),
                    "bytes"
                )

            elif event_type == "complete":

                print(
                    "Session:",
                    data.get("session_id")
                )

                print()
                print("=" * 60)
                print("WEBSOCKET TEST COMPLETED")
                print("=" * 60)

                break

            elif event_type == "error":

                print(
                    "ERROR:",
                    data.get("message")
                )

                break


if __name__ == "__main__":
    asyncio.run(main())