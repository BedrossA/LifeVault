# Development server run script

cd "$(dirname "$0")/.."
source venv1/bin/activate

echo "?? Starting LifeVault Development Server..."
echo "============================================"
echo "API Documentation: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000