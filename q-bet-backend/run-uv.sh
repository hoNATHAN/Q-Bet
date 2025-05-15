set -e

if [ ! -d ".venv" ]; then
  echo "creating virtual environment..."
  uv venv
fi

echo "activating virtual environment..."
source .venv/bin/activate
uv pip install --upgrade pip
uv pip install -r requirements.txt

echo "running backend..."
uvicorn app:app --reload --host 127.0.0.1 --port 8000
