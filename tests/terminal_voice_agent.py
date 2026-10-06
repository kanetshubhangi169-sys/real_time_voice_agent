import asyncio
import base64
import json
import threading
from pathlib import Path

import pygame
import sounddevice as sd
import soundfile as sf
import websockets


# ============================================================
# CONFIGURATION
# ============================================================

SAMPLE_RATE = 16000
CHANNELS = 1

SESSION_ID = "terminal-session"

WEBSOCKET_URL = (
    f"ws://127.0.0.1:8000/api/v1/ws/voice/{SESSION_ID}"
)

AUDIO_DIR = Path("test_audio")

INPUT_AUDIO_FILE = (
    AUDIO_DIR / "terminal_microphone.wav"
)

OUTPUT_AUDIO_FILE = (
    AUDIO_DIR / "terminal_response.mp3"
)


# ============================================================
# MICROPHONE RECORDER
# ============================================================

class MicrophoneRecorder:
    """
    Records microphone audio until the user presses ENTER.
    """

    def __init__(self):
        self.audio_data = []
        self.recording = False
        self.stream = None

    def audio_callback(
        self,
        indata,
        frames,
        time,
        status
    ):
        if status:
            print(
                f"\n⚠️ Microphone status: {status}"
            )

        if self.recording:
            self.audio_data.append(
                indata.copy()
            )

    def start(self):
        """
        Start microphone recording.
        """

        self.audio_data = []
        self.recording = True

        print()
        print("🎤 Recording...")
        print("Press ENTER to stop recording.")
        print()

        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            callback=self.audio_callback
        )

        self.stream.start()

    def stop(self):
        """
        Stop recording and return audio data.
        """

        self.recording = False

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if not self.audio_data:
            return None

        import numpy as np

        return np.concatenate(
            self.audio_data,
            axis=0
        )

    def save(self, audio):
        """
        Save recorded audio as WAV.
        """

        AUDIO_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        sf.write(
            INPUT_AUDIO_FILE,
            audio,
            SAMPLE_RATE
        )

        return INPUT_AUDIO_FILE


# ============================================================
# RECORD MICROPHONE
# ============================================================

def record_audio():
    """
    Record until ENTER is pressed.
    """

    recorder = MicrophoneRecorder()

    try:
        recorder.start()

        input()

        audio = recorder.stop()

        if audio is None:
            print(
                "❌ No audio was recorded."
            )
            return False

        output_path = recorder.save(
            audio
        )

        print()
        print("🛑 Recording stopped.")

        print(
            f"Audio saved to: {output_path}"
        )

        return True

    except Exception as exc:

        try:
            recorder.stop()
        except Exception:
            pass

        print()
        print(
            f"❌ Recording failed: {exc}"
        )

        return False


# ============================================================
# PLAY AI AUDIO
# ============================================================

def play_audio(audio_path):
    """
    Play AI-generated MP3 through speakers.
    """

    try:

        pygame.mixer.init()

        pygame.mixer.music.load(
            str(audio_path)
        )

        print()
        print("🔊 AI is speaking...")

        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(20)

        pygame.mixer.music.stop()
        pygame.mixer.quit()

        print(
            "✅ Voice response completed."
        )

    except Exception as exc:

        print()
        print(
            f"⚠️ Audio playback failed: {exc}"
        )

        try:
            pygame.mixer.quit()
        except Exception:
            pass


# ============================================================
# WEBSOCKET VOICE PIPELINE
# ============================================================

async def process_voice():
    """
    Send microphone audio to the WebSocket server.
    """

    if not INPUT_AUDIO_FILE.exists():

        print(
            "❌ Microphone audio file not found."
        )

        return False

    audio_data = (
        INPUT_AUDIO_FILE.read_bytes()
    )

    print()
    print("Connecting to voice agent...")

    try:

        async with websockets.connect(
            WEBSOCKET_URL,
            max_size=10 * 1024 * 1024
        ) as websocket:

            # ------------------------------------------------
            # Connected
            # ------------------------------------------------

            message = await websocket.recv()

            data = json.loads(message)

            if data.get("type") == "connected":

                print(
                    "Server: "
                    f"{data.get('message')}"
                )

            # ------------------------------------------------
            # Send metadata
            # ------------------------------------------------

            await websocket.send(
                json.dumps(
                    {
                        "filename": (
                            INPUT_AUDIO_FILE.name
                        )
                    }
                )
            )

            # ------------------------------------------------
            # Send audio
            # ------------------------------------------------

            print(
                "Sending microphone audio..."
            )

            await websocket.send(
                audio_data
            )

            # ------------------------------------------------
            # Receive events
            # ------------------------------------------------

            while True:

                message = await websocket.recv()

                data = json.loads(message)

                event_type = data.get("type")

                # --------------------------------------------
                # Processing
                # --------------------------------------------

                if event_type == "processing":

                    print()
                    print(
                        "⏳ Processing..."
                    )

                # --------------------------------------------
                # Transcription
                # --------------------------------------------

                elif event_type == "transcription":

                    print()
                    print(
                        "🗣️ You:",
                        data.get("text")
                    )

                # --------------------------------------------
                # AI response
                # --------------------------------------------

                elif event_type == "response":

                    print()
                    print(
                        "🤖 AI:",
                        data.get("text")
                    )

                # --------------------------------------------
                # Audio response
                # --------------------------------------------

                elif event_type == "audio":

                    audio_base64 = data.get(
                        "data"
                    )

                    if not audio_base64:
                        print(
                            "⚠️ Empty audio response."
                        )
                        continue

                    audio_bytes = (
                        base64.b64decode(
                            audio_base64
                        )
                    )

                    AUDIO_DIR.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    OUTPUT_AUDIO_FILE.write_bytes(
                        audio_bytes
                    )

                    print()
                    print(
                        "🔊 Voice response saved:"
                    )

                    print(
                        OUTPUT_AUDIO_FILE
                    )

                    print(
                        "Audio size:",
                        len(audio_bytes),
                        "bytes"
                    )

                    play_audio(
                        OUTPUT_AUDIO_FILE
                    )

                # --------------------------------------------
                # Complete
                # --------------------------------------------

                elif event_type == "complete":

                    print()
                    print(
                        "✅ Voice interaction completed."
                    )

                    return True

                # --------------------------------------------
                # Error
                # --------------------------------------------

                elif event_type == "error":

                    print()
                    print(
                        "❌ Voice agent error:"
                    )

                    print(
                        data.get(
                            "message",
                            "Unknown error"
                        )
                    )

                    return False

    except ConnectionRefusedError:

        print()
        print(
            "❌ Could not connect to server."
        )

        print()
        print(
            "Start the server with:"
        )

        print(
            "uvicorn app.main:app --reload"
        )

        return False

    except websockets.exceptions.ConnectionClosedError as exc:

        print()
        print(
            "❌ WebSocket connection closed:"
        )

        print(exc)

        return False

    except Exception as exc:

        print()
        print(
            f"❌ Voice agent error: {exc}"
        )

        return False


# ============================================================
# MAIN
# ============================================================

async def main():

    print("=" * 60)
    print("REAL-TIME AI VOICE AGENT")
    print("=" * 60)

    print()
    print(
        f"Session: {SESSION_ID}"
    )

    print()
    print(
        "Press ENTER to start recording."
    )

    print(
        "Press Ctrl+C to exit."
    )

    print()

    try:

        while True:

            input(
                "Press ENTER to speak..."
            )

            # ----------------------------------------------
            # Record until ENTER
            # ----------------------------------------------

            success = record_audio()

            if not success:
                continue

            # ----------------------------------------------
            # Send to voice agent
            # ----------------------------------------------

            await process_voice()

            print()
            print("-" * 60)

    except KeyboardInterrupt:

        print()
        print()
        print(
            "👋 Exiting voice agent..."
        )

    finally:

        try:
            pygame.mixer.quit()
        except Exception:
            pass


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )