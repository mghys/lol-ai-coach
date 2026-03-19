# AI Coach - Agent Guidelines

This is a FastAPI-based web application for League of Legends game analysis and hero recognition.

## Project Overview

- **Framework**: FastAPI with Jinja2 templates
- **Database**: SQLite via SQLAlchemy ORM
- **Image Processing**: OpenCV, PaddleOCR, EasyOCR
- **Python Version**: 3.9+

## Project Structure

```
ai-coach/
├── app/
│   ├── main.py              # FastAPI app and routes
│   ├── models/models.py     # SQLAlchemy models (Player, Game, ChampionStats)
│   └── services/
│       ├── hero_recognizer.py   # Hero image recognition using CV
│       ├── ocr_service.py        # Screenshot OCR processing
│       ├── data_service.py       # Database operations
│       └── recommend_service.py   # Champion recommendations
├── config.py                # Configuration and constants
├── main.py                  # Entry point (uvicorn)
├── requirements.txt         # Dependencies
└── data/                    # Runtime data (uploads, database)
```

## Build/Lint/Test Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Application
```bash
python main.py
```
Server starts on `http://0.0.0.0:8000`

### Run Single Test
Since no formal test framework exists, test individual modules by importing:
```bash
python -c "from app.services.hero_recognizer import recognize_hero; print(recognize_hero('path/to/image.png'))"
python -c "from app.services.ocr_service import process_screenshot; print(process_screenshot('path/to/screenshot.png'))"
```

### Manual Testing
```bash
python test_img.py        # Test image loading
python analyze.py         # Run analysis scripts
python import_data.py     # Import data
```

### Verify FastAPI Routes
```bash
uvicorn app.main:app --reload
```

## Code Style Guidelines

### General Conventions
- Follow PEP 8 style guide
- Use 4 spaces for indentation
- Maximum line length: 120 characters
- Use `True`/`False`/`None` instead of `true`/`false`/`null`

### Imports
```python
# Standard library first
import os
import re
import uuid

# Third-party libraries
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile

# Local imports (use absolute imports)
from app.services.hero_recognizer import recognize_hero
from app.models.models import Player, Game
from config import DATABASE_URL
```

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `hero_recognizer.py` |
| Classes | PascalCase | `HeroRecognizer` |
| Functions | snake_case | `recognize_hero()` |
| Methods | snake_case | `_compute_phash()` |
| Variables | snake_case | `file_path`, `hero_name` |
| Constants | UPPER_SNAKE | `DATABASE_URL`, `CHAMPION_LIST` |
| Private methods | leading underscore | `_load_templates()` |

### Type Annotations
Use type hints for function parameters and return values:
```python
def recognize_hero(image_path: str) -> list[dict]:
    ...

def save_game_data(db: Session, player_riot_id: str, game_data: dict) -> Optional[Player]:
    ...
```

### Class Structure
```python
class HeroRecognizer:
    def __init__(self):
        self.heros_dir = os.path.join(...)  # Instance attributes
    
    def _private_method(self):  # Private methods with underscore
        ...
    
    def public_method(self):    # Public methods
        ...
```

### Error Handling
```python
# Use try/except sparingly and specifically
try:
    img = cv2.imread(filepath)
    if img is None:
        return []
except Exception as e:
    print(f"Error loading {filename}: {e}")
    return []

# Return sensible defaults on failure
if input_img is None:
    return []
```

### Database Models (SQLAlchemy)
```python
class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True)
    riot_id = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    games = relationship("Game", back_populates="player")
```

### FastAPI Routes
```python
@app.post("/hero-recognize")
async def recognize_hero_image(file: UploadFile = File(...)):
    # Always validate input
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"hero_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Return structured responses
    return {
        "success": True,
        "hero": results[0]["hero"] if results else None,
        "similarity": results[0]["similarity"] if results else 0
    }
```

### File Paths
Use `os.path` for cross-platform compatibility:
```python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
```

### Image Processing Patterns
```python
# Read image safely
img = cv2.imread(image_path)
if img is None:
    return []

# Check dimensions before processing
h, w = img.shape[:2]

# Resize with dimension preservation
resized = cv2.resize(img, (target_width, target_height))
```

### Avoid
- Bare `except:` clauses without specific handling
- Global mutable state (use singletons with lazy initialization)
- Hardcoded paths (use config.py constants)
- `print()` statements in production code (use logging)
- Modifying `sys.path` manually

## Key Dependencies

| Package | Purpose |
|---------|---------|
| fastapi | Web framework |
| uvicorn | ASGI server |
| sqlalchemy | ORM |
| opencv-python | Image processing |
| paddleocr/easyocr | OCR |
| pillow | Image handling |
| numpy | Array operations |

## Database

- Location: `data/coach.db` (SQLite)
- Initialize: `from app.models.models import init_db; init_db()`
- Session pattern: Use `with SessionLocal() as session:` or dependency injection

## Common Tasks

### Adding a New Route
1. Add endpoint in `app/main.py`
2. Create service function in `app/services/`
3. Update imports

### Adding a New Model
1. Add class to `app/models/models.py`
2. Run `init_db()` to create tables

### Debugging OCR Issues
```python
# Test specific image region
img = cv2.imread('path/to/screenshot.png')
region = img[y1:y2, x1:x2]
cv2.imwrite('debug_region.png', region)
```
