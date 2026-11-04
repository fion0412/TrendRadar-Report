import base64
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import yunzhou_tts


class SpeechStreamingTests(unittest.TestCase):
    def test_completion_code_20000000_is_success(self):
        chunk = base64.b64encode(b"ID3test-audio").decode("ascii")
        response = io.BytesIO(
            ('{"code":0,"data":"' + chunk + '"}\n'
             '{"code":20000000,"message":"OK","data":null}\n').encode()
        )
        with tempfile.TemporaryDirectory() as directory:
            old = Path.cwd()
            os.chdir(directory)
            try:
                with patch.dict(os.environ, {"VOLCENGINE_TTS_API_KEY": "test-key", "TTS_TEXT": "你好"}):
                    with patch.object(yunzhou_tts, "urlopen", return_value=response):
                        self.assertEqual(yunzhou_tts.main(), 0)
                self.assertEqual(Path("output/tts/yunzhou2.mp3").read_bytes(), b"ID3test-audio")
            finally:
                os.chdir(old)


if __name__ == "__main__":
    unittest.main()
