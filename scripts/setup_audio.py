"""Download the multilingual model once: python scripts/setup_audio.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from grievance.speech import download_model


def main():
    print("Downloading the multilingual speech model into the project.", flush=True)
    download_model()
    print("Urdu/English speech model is ready.", flush=True)


if __name__ == "__main__":
    main()
