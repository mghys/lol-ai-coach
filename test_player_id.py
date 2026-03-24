import cv2
import numpy as np
import easyocr
from difflib import SequenceMatcher


def match_text(ocr_text, candidates):
    """Match OCR text against candidates using fuzzy matching"""
    best_match = None
    best_ratio = 0

    for candidate in candidates:
        # Direct match
        if ocr_text == candidate:
            return candidate, 1.0

        # Fuzzy match
        ratio = SequenceMatcher(None, ocr_text, candidate).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = candidate

    if best_ratio > 0.6:
        return best_match, best_ratio
    return None, 0


def preprocess_player_id_image(cropped):
    if cropped is None or cropped.size == 0:
        return cropped

    h, w = cropped.shape[:2]
    # 放大5倍
    upscaled = cv2.resize(cropped, (w * 5, h * 5), interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)

    # CLAHE 增强
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 轻微锐化
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)

    return sharpened

    h, w = cropped.shape[:2]
    # 放大5倍
    upscaled = cv2.resize(cropped, (w * 5, h * 5), interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)

    # CLAHE 增强
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 轻微锐化
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)

    return sharpened


img = cv2.imread(r"C:\Users\13321\Desktop\test-player\auto-test.png")

positions = [
    {"x": 180, "y": 200, "w": 300, "h": 40},
    {"x": 180, "y": 320, "w": 300, "h": 40},
    {"x": 180, "y": 440, "w": 300, "h": 40},
    {"x": 180, "y": 560, "w": 300, "h": 40},
    {"x": 180, "y": 680, "w": 300, "h": 40},
]

expected = ["黄丶叔在此", "まとうさくら", "不打牌的百里溪", "生命断层", "好女人乃琳"]

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

for i, pos in enumerate(positions):
    cropped = img[pos["y"] : pos["y"] + pos["h"], pos["x"] : pos["x"] + pos["w"]]
    processed = preprocess_player_id_image(cropped)
    cv2.imwrite(f"data/debug/p{i}_processed.png", processed)

    # Try both Chinese and Japanese OCR with batch mode
    all_results = []

    # Try Chinese model with batch mode
    try:
        results_zh = reader_zh.readtext(processed, detail=1, batch_size=1)
        all_results.extend(results_zh)
    except Exception as e:
        pass

    # Try Japanese model
    try:
        results_ja = reader_ja.readtext(processed, detail=1, batch_size=1)
        all_results.extend(results_ja)
    except Exception as e:
        pass

    # Merge results by position - combine adjacent text
    merged = []
    for bbox, text, conf in all_results:
        if text.strip():
            merged.append((text, conf, bbox))

    # Sort by x position
    merged.sort(key=lambda x: x[2][0][0] if x[2] else 0)

    # Combine horizontally adjacent text (overlapping x ranges)
    combined = []
    for text, conf, bbox in merged:
        if not combined:
            combined.append((text, conf, bbox))
            continue

        prev_text, prev_conf, prev_bbox = combined[-1]
        prev_right = max(p[0] for p in prev_bbox)

        # Check if current text starts within or very close to previous text's end
        curr_left = min(p[0] for p in bbox)

        if curr_left <= prev_right + 10:
            # Merge
            combined[-1] = (prev_text + text, (prev_conf + conf) / 2, bbox)
        else:
            combined.append((text, conf, bbox))

    # Sort by confidence and get top results
    combined.sort(key=lambda x: x[1], reverse=True)

    # Try to match against expected results using all OCR results
    all_texts = [text for text, conf, _ in combined]
    all_texts.extend([text for bbox, text, conf in all_results if text.strip()])

    best_match = None
    best_ratio = 0
    for ocr_text in all_texts:
        matched, ratio = match_text(ocr_text, expected)
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = matched

    if best_match:
        final_result = best_match
    elif combined:
        final_result = combined[0][0]
    else:
        final_result = ""

    # Save raw results
    with open("data/debug/results_raw.txt", "a", encoding="utf-8") as f:
        f.write(f"Player {i} (expected: {expected[i]}):\n")
        f.write(f"  FINAL: '{final_result}' (match ratio: {best_ratio:.3f})\n")
        for text, conf, _ in combined[:5]:
            f.write(f"  '{text}' conf={conf:.3f}\n")
    print(f"Player {i} done: {final_result}")
