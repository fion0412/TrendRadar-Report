"""Generate an MP3 using Volcengine Doubao Speech 2.0 (Yunzhou 2.0)."""

import base64
import json
import os
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ENDPOINT = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"
VOICE = "zh_female_qingxinnvsheng_uranus_bigtts"


def main() -> int:
    key = os.environ.get("VOLCENGINE_TTS_API_KEY", "").strip()
    if not key:
        print("Missing VOLCENGINE_TTS_API_KEY in GitHub Actions Secrets", file=sys.stderr)
        return 2

    message = os.environ.get("TTS_TEXT", "").strip()
    if not message or len(message) > 1000:
        print("Provide TTS_TEXT between 1 and 1000 characters", file=sys.stderr)
        return 2

    body = {
        "req_params": {
            "text": message,
            "speaker": VOICE,
            "audio_params": {"format": "mp3", "sample_rate": 24000},
        }
    }
    request = Request(
        ENDPOINT,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "X-Api-Key": key,
            "X-Api-Resource-Id": "seed-tts-2.0",
            "X-Api-Request-Id": str(uuid.uuid4()),
            "Content-Type": "application/json",
        },
        method="POST",
    )

    audio = bytearray()
    try:
        with urlopen(request, timeout=120) as response:
            for line in response:
                if not line.strip():
                    continue
                item = json.loads(line)
                # 20000000 is the documented successful stream-completion frame.
                if item.get("code", 0) not in (0, 20000000):
                    raise RuntimeError(
                        f"Speech API error {item.get('code')}: {item.get('message', 'unknown')}"
                    )
                if item.get("data"):
                    audio.extend(base64.b64decode(item["data"], validate=True))
    except HTTPError as exc:
        print(f"Speech API HTTP error: {exc.code}", file=sys.stderr)
        return 1
    except (URLError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Speech API request failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    if not audio:
        print("Speech API returned no audio", file=sys.stderr)
        return 1

    dest = Path("output/tts/yunzhou2.mp3")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(audio)
    print(f"Generated {dest} ({len(audio)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
