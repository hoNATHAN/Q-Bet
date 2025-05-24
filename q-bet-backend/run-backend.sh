set -e 

if [ ! -d ".venv" ]; then
    echo "creating virtual environment..."
    python3 -m venv .venv
fi

echo "activating virtual environment..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "running backend..."
uvicorn app:app --reload --host 127.0.0.1 --port 8000