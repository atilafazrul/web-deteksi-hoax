import os
import sys

# CRITICAL FIX for Windows Winsock:
# When spawned from PHP/proc_open, SystemRoot might not be inherited.
# Without SystemRoot, Windows Winsock (_overlapped / asyncio / sockets) fails with [WinError 10106].
if sys.platform == "win32":
    system_root = os.environ.get("SystemRoot") or os.environ.get("SYSTEMROOT") or "C:\\Windows"
    os.environ["SystemRoot"] = system_root
    os.environ["SYSTEMROOT"] = system_root
    if "windir" not in os.environ:
        os.environ["windir"] = system_root

import json

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.detector_service import HoaxDetectionService

def main():
    try:
        # Read request payload from stdin
        input_data = sys.stdin.read()
        if not input_data:
            print(json.dumps({"status": "error", "error_msg": "No input provided via stdin."}))
            return

        payload = json.loads(input_data)
        mode = payload.get("mode", "text")

        if mode == "gemini":
            from src.models.generative_reasoner import GenerativeFactChecker
            text = payload.get("text", "").strip()
            label = payload.get("label", "HOAX")
            confidence = float(payload.get("confidence", 95.0))
            api_key = payload.get("api_key") or os.environ.get("GEMINI_API_KEY")
            checker = GenerativeFactChecker(api_key=api_key)
            explanation = checker.explain(text, predicted_label=label, confidence=confidence / 100.0)
            print(json.dumps({"status": "success", "explanation": explanation}))
            return

        service = HoaxDetectionService()

        if mode == "url":
            url = payload.get("url", "").strip()
            api_key = payload.get("api_key") or os.environ.get("GEMINI_API_KEY")
            if not url:
                print(json.dumps({"status": "error", "error_msg": "URL tidak boleh kosong."}))
                return
            result = service.analyze_url(url, api_key=api_key)
            print(json.dumps(result))

        elif mode == "text":
            text = payload.get("text", "").strip()
            title = payload.get("title", "").strip()
            api_key = payload.get("api_key") or os.environ.get("GEMINI_API_KEY")
            if not text:
                print(json.dumps({"status": "error", "error_msg": "Teks tidak boleh kosong."}))
                return
            result = service.analyze_text(text, title=title, api_key=api_key)
            print(json.dumps(result))

        else:
            print(json.dumps({"status": "error", "error_msg": f"Mode '{mode}' tidak dikenal."}))

    except Exception as e:
        print(json.dumps({"status": "error", "error_msg": f"Python Bridge Error: {str(e)}"}))

if __name__ == "__main__":
    main()
