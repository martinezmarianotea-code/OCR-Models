"""python -m src.api  →  API y frontend compilado en http://127.0.0.1:8000"""

import argparse

import uvicorn

parser = argparse.ArgumentParser(description="Servidor local de OCR-Models")
parser.add_argument("--port", type=int, default=8000)
args = parser.parse_args()

uvicorn.run("src.api.app:app", host="127.0.0.1", port=args.port)
