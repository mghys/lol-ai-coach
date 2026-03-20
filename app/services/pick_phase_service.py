import os
import cv2
import numpy as np
from app.services.hero_recognizer import recognize_hero

PICK_PHASE_POSITIONS = {
    "selected": {
        "blue": [
            {"x": 79, "y": 152, "w": 100, "h": 100},
            {"x": 79, "y": 272, "w": 100, "h": 100},
            {"x": 79, "y": 392, "w": 100, "h": 100},
            {"x": 79, "y": 512, "w": 100, "h": 100},
            {"x": 79, "y": 632, "w": 100, "h": 100},
        ]
    },
    "available": [
        {"x": 527, "y": 15, "w": 75, "h": 75},
        {"x": 615, "y": 15, "w": 75, "h": 75},
        {"x": 703, "y": 15, "w": 75, "h": 75},
        {"x": 791, "y": 15, "w": 75, "h": 75},
        {"x": 879, "y": 15, "w": 75, "h": 75},
        {"x": 967, "y": 15, "w": 75, "h": 75},
        {"x": 1055, "y": 15, "w": 75, "h": 75},
        {"x": 1143, "y": 15, "w": 75, "h": 75},
        {"x": 1231, "y": 15, "w": 75, "h": 75},
        {"x": 1319, "y": 15, "w": 75, "h": 75},
    ]
}

def update_pick_phase_positions(positions: dict):
    global PICK_PHASE_POSITIONS
    PICK_PHASE_POSITIONS = positions

def crop_hero_icon(image, x: int, y: int, w: int, h: int):
    h_img, w_img = image.shape[:2]
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(w_img, x + w)
    y2 = min(h_img, y + h)
    
    if x2 <= x1 or y2 <= y1:
        return None
    
    cropped = image[y1:y2, x1:x2]
    return cropped

def save_temp_crop(cropped, hero_idx) -> str:
    temp_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_path = os.path.join(temp_dir, f"crop_{hero_idx}.png")
    cv2.imwrite(temp_path, cropped)
    return temp_path

def recognize_hero_from_crop(cropped, hero_idx: str) -> list:
    temp_path = save_temp_crop(cropped, hero_idx)
    results = recognize_hero(temp_path)
    
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    return results

DEBUG_MODE = True
DEBUG_SELECTED_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'debug_selected')
DEBUG_AVAILABLE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'debug_available')

def recognize_pick_phase_heroes(image_path: str) -> dict:
    image = cv2.imread(image_path)
    if image is None:
        return {
            "available_heroes": [],
            "blue_side": [],
            "red_side": [],
            "banned_heroes": []
        }
    
    if DEBUG_MODE:
        os.makedirs(DEBUG_SELECTED_DIR, exist_ok=True)
        os.makedirs(DEBUG_AVAILABLE_DIR, exist_ok=True)
    
    blue_side = []
    available_heroes = []
    
    for idx, pos in enumerate(PICK_PHASE_POSITIONS["selected"]["blue"]):
        cropped = crop_hero_icon(image, pos["x"], pos["y"], pos["w"], pos["h"])
        if cropped is not None and cropped.size > 0:
            if DEBUG_MODE:
                debug_path = os.path.join(DEBUG_SELECTED_DIR, f"blue_{idx}.png")
                cv2.imwrite(debug_path, cropped)
            
            results = recognize_hero_from_crop(cropped, f"blue_{idx}")
            if results:
                blue_side.append(results[0]["hero"])
    
    for idx, pos in enumerate(PICK_PHASE_POSITIONS["available"]):
        cropped = crop_hero_icon(image, pos["x"], pos["y"], pos["w"], pos["h"])
        if cropped is not None and cropped.size > 0:
            if DEBUG_MODE:
                debug_path = os.path.join(DEBUG_AVAILABLE_DIR, f"available_{idx}.png")
                cv2.imwrite(debug_path, cropped)
            
            results = recognize_hero_from_crop(cropped, f"available_{idx}")
            if results:
                hero_name = results[0]["hero"]
                if hero_name.lower() != "empty":
                    available_heroes.append(hero_name)
    
    return {
        "available_heroes": available_heroes,
        "blue_side": blue_side
    }