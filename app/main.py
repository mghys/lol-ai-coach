from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import os
import uuid
import tempfile

from app.services.hero_recognizer import recognize_hero
from app.services.general_ocr_service import recognize_general_text

app = FastAPI(title="英雄识别")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


def save_temp_file(file: UploadFile) -> str:
    content = file.file.read()
    suffix = os.path.splitext(file.filename or "")[1] or ".tmp"
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.write(fd, content)
    os.close(fd)
    return path


def cleanup_temp_file(path: str):
    if os.path.exists(path):
        os.remove(path)


@app.post("/hero-recognize")
async def recognize_hero_image(file: UploadFile = File(...)):
    file_path = save_temp_file(file)
    try:
        results = recognize_hero(file_path)
        return {
            "success": True,
            "hero": results[0]["hero"] if results else None,
            "similarity": results[0]["similarity"] if results else 0,
        }
    finally:
        cleanup_temp_file(file_path)


@app.post("/pick-phase-recognize")
async def recognize_pick_phase(file: UploadFile = File(...)):
    file_path = save_temp_file(file)
    try:
        from app.services.pick_phase_service import recognize_pick_phase_heroes

        results = recognize_pick_phase_heroes(file_path)
        return {
            "success": True,
            "available_heroes": results.get("available_heroes", []),
            "blue_side": results.get("blue_side", []),
        }
    finally:
        cleanup_temp_file(file_path)


@app.post("/ocr-recognize")
async def recognize_text_from_image(file: UploadFile = File(...)):
    file_path = save_temp_file(file)
    try:
        results = recognize_general_text(file_path)
        return results
    finally:
        cleanup_temp_file(file_path)


@app.post("/player-id-recognize")
async def recognize_player_id(file: UploadFile = File(...)):
    file_path = save_temp_file(file)
    try:
        from app.services.pick_phase_service import recognize_player_ids

        results = recognize_player_ids(file_path)
        return {"success": True, "player_ids": results.get("player_ids", [])}
    finally:
        cleanup_temp_file(file_path)
