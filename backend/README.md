# LifeVault Backend

Privacy-first personal analytics platform with face recognition running on Raspberry Pi 5.

## Technology Stack

- **Python**: 3.13.5
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Face Recognition**: dlib 20.0.0 + face_recognition
- **Camera**: Picamera2 (RPi5 official)

## Setup

### Prerequisites
- Raspberry Pi 5
- Python 3.13.5
- PostgreSQL database
- 5MP Camera Module

### Installation

1. Clone repository:
```bash
git clone https://github.com/BedrossA/LifeVault.git
cd LifeVault/backend
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Initialize database:
```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE lifevault_db;
CREATE USER lifevault WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE lifevault_db TO lifevault;
\q
```

6. Run application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure
## Testing

```bash
pytest
```

## Development

- All commits follow Conventional Commits
- Code follows PEP 8 style guide
- Type hints are required
- Tests required for new features

## License

MIT License

