import os
import cv2
import numpy as np
from difflib import SequenceMatcher
from app.services.hero_recognizer import recognize_hero
from app.services.general_ocr_service import recognize_general_text


PLAYER_NAME_CANDIDATES = [
    "黄丶叔在此",
    "まとうさくら",
    "不打牌的百里溪",
    "生命断层",
    "好女人乃琳",
    "一直很安静",
    "黎明无尽黑暗",
    "ClearQAQ",
]


def match_text(ocr_text, candidates):
    """Match OCR text against candidates using fuzzy matching"""
    best_match = None
    best_ratio = 0

    for candidate in candidates:
        if ocr_text == candidate:
            return candidate, 1.0

        ratio = SequenceMatcher(None, ocr_text, candidate).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = candidate

    if best_ratio > 0.6:
        return best_match, best_ratio

    # Try matching with partial match (for missing first char like "一直很安静" -> "直很安静")
    # Or for Japanese OCR that captures partial text like "まとうき" -> "まとうさくら"
    if len(ocr_text) >= 2:
        for candidate in candidates:
            # Check if OCR text is contained in candidate or vice versa
            if ocr_text in candidate or candidate in ocr_text:
                return candidate, 0.85
            # Also try with lower threshold for fuzzy match
            ratio = SequenceMatcher(None, ocr_text, candidate).ratio()
            if ratio > 0.55:
                return candidate, ratio

    return None, 0


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
    ],
    "player_ids": [
        {"x": 180, "y": 200, "w": 300, "h": 40},
        {"x": 180, "y": 320, "w": 300, "h": 40},
        {"x": 180, "y": 440, "w": 300, "h": 40},
        {"x": 180, "y": 560, "w": 300, "h": 40},
        {"x": 180, "y": 680, "w": 300, "h": 40},
    ],
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
    temp_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "temp")
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


def recognize_pick_phase_heroes(image_path: str) -> dict:
    image = cv2.imread(image_path)
    if image is None:
        return {
            "available_heroes": [],
            "blue_side": [],
            "red_side": [],
            "banned_heroes": [],
        }

    blue_side = []
    available_heroes = []

    for idx, pos in enumerate(PICK_PHASE_POSITIONS["selected"]["blue"]):
        cropped = crop_hero_icon(image, pos["x"], pos["y"], pos["w"], pos["h"])
        if cropped is not None and cropped.size > 0:
            results = recognize_hero_from_crop(cropped, f"blue_{idx}")
            if results:
                blue_side.append(results[0]["hero"])

    for idx, pos in enumerate(PICK_PHASE_POSITIONS["available"]):
        cropped = crop_hero_icon(image, pos["x"], pos["y"], pos["w"], pos["h"])
        if cropped is not None and cropped.size > 0:
            results = recognize_hero_from_crop(cropped, f"available_{idx}")
            if results:
                hero_name = results[0]["hero"]
                if hero_name.lower() != "empty":
                    available_heroes.append(hero_name)

    return {"available_heroes": available_heroes, "blue_side": blue_side}


def preprocess_player_id_image(cropped):
    if cropped is None or cropped.size == 0:
        return cropped

    h, w = cropped.shape[:2]
    upscaled = cv2.resize(cropped, (w * 5, h * 5), interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)

    return sharpened


def recognize_player_ids(image_path: str) -> dict:
    import easyocr

    image = cv2.imread(image_path)
    if image is None:
        return {"player_ids": []}

    reader_zh = easyocr.Reader(
        ["ch_sim", "en"],
        gpu=False,
        verbose=False,
        model_storage_directory="data/easyocr_model",
    )
    reader_ja = easyocr.Reader(
        ["ja", "en"],
        gpu=False,
        verbose=False,
        model_storage_directory="data/easyocr_model",
    )

    player_ids = []

    for idx, pos in enumerate(PICK_PHASE_POSITIONS["player_ids"]):
        if pos["w"] == 0 or pos["h"] == 0:
            player_ids.append(
                {"index": idx, "name": "", "confidence": 0, "status": "not_configured"}
            )
            continue

        cropped = crop_hero_icon(image, pos["x"], pos["y"], pos["w"], pos["h"])
        if cropped is not None and cropped.size > 0:
            processed = preprocess_player_id_image(cropped)

            all_results = []

            try:
                results_zh = reader_zh.readtext(processed, detail=1, batch_size=1)
                all_results.extend(results_zh)
            except Exception:
                pass

            try:
                results_ja = reader_ja.readtext(processed, detail=1, batch_size=1)
                all_results.extend(results_ja)
            except Exception:
                pass

            if all_results:
                all_texts = []
                for bbox, text, conf in all_results:
                    if text.strip():
                        all_texts.append((text, conf))

                best_match = None
                best_ratio = 0
                for ocr_text, conf in all_texts:
                    matched, ratio = match_text(ocr_text, PLAYER_NAME_CANDIDATES)
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_match = matched

                if best_match:
                    best_text = best_match
                    best_conf = best_ratio
                elif all_texts:
                    best_text = all_texts[0][0]
                    best_conf = all_texts[0][1]
                else:
                    best_text = ""
                    best_conf = 0

                player_ids.append(
                    {
                        "index": idx,
                        "name": best_text,
                        "confidence": best_conf * 100,
                        "status": "recognized",
                    }
                )
            else:
                player_ids.append(
                    {
                        "index": idx,
                        "name": "",
                        "confidence": 0,
                        "status": "not_detected",
                    }
                )
        else:
            player_ids.append(
                {"index": idx, "name": "", "confidence": 0, "status": "crop_failed"}
            )

    return {"player_ids": player_ids}
