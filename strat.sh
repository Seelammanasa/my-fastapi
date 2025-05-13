#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
uvicorn pizza:app --host=0.0.0.0 --workers=4
