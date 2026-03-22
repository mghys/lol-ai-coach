import re
import cv2
from rapidocr_onnxruntime import RapidOCR
from config import CHAMPION_LIST


class OCRService:
    def __init__(self):
        self.reader = RapidOCR()
        self.champions = {
            c.lower().replace("'", "").replace(" ", ""): c for c in CHAMPION_LIST
        }

    def extract_game_data(self, image_path):
        results = {
            "win": None,
            "ally_team": [],
            "enemy_team": [],
            "detected_champions": [],
        }

        if self.reader is None:
            return results

        img = cv2.imread(image_path)
        if img is None:
            return results

        h, w = img.shape[:2]

        try:
            win_result = self._detect_victory_defeat(img, h, w)
            results["win"] = win_result
        except:
            pass

        try:
            results["ally_team"] = self._extract_team(
                img, 0, int(w * 0.45), is_ally=True
            )
            results["enemy_team"] = self._extract_team(
                img, int(w * 0.55), w, is_ally=False
            )
        except:
            pass

        for player in results["ally_team"]:
            if player.get("champion"):
                results["detected_champions"].append(player["champion"])
        for player in results["enemy_team"]:
            if player.get("champion"):
                results["detected_champions"].append(player["champion"])

        return results

    def _detect_victory_defeat(self, img, h, w):
        region = img[int(h * 0.02) : int(h * 0.08), int(w * 0.35) : int(w * 0.65)]

        result, _ = self.reader(region)
        text = " ".join([str(r[1]) for r in result]).lower() if result else ""

        if "victory" in text:
            return True
        elif "defeat" in text:
            return False
        return None

    def _extract_team(self, img, x_start, x_end, is_ally):
        team_data = []
        h, w_img = img.shape[:2]

        for i in range(5):
            y_start = int(h * (0.28 + i * 0.09))
            y_end = int(h * (0.28 + (i + 1) * 0.09))

            if y_end > h:
                y_end = h
            if y_start >= h:
                break

            region = img[y_start:y_end, x_start:x_end]

            if region.size == 0:
                continue

            try:
                text = self._read_text(region)

                player = {
                    "name": "",
                    "champion": "",
                    "kills": 0,
                    "deaths": 0,
                    "assists": 0,
                    "win": None,
                }

                kda = self._extract_kda(text)
                player["kills"] = kda.get("kills", 0)
                player["deaths"] = kda.get("deaths", 0)
                player["assists"] = kda.get("assists", 0)

                champion = self._extract_champion(text)
                player["champion"] = champion if champion else ""

                player["win"] = True if is_ally else False

                team_data.append(player)
            except:
                continue

        return team_data

    def _read_text(self, region):
        try:
            result, _ = self.reader(region)
            if result:
                return " ".join([str(r[1]) for r in result if r])
            return ""
        except:
            return ""

    def _extract_kda(self, text):
        numbers = re.findall(r"\d+", text)
        if len(numbers) >= 3:
            return {
                "kills": int(numbers[0]),
                "deaths": int(numbers[1]),
                "assists": int(numbers[2]),
            }
        elif len(numbers) == 2:
            return {"kills": int(numbers[0]), "deaths": int(numbers[1]), "assists": 0}
        return {}

    def _extract_champion(self, text):
        text_clean = text.lower().replace("'", "").replace(" ", "").replace("-", "")

        for key, champion in self.champions.items():
            if key in text_clean or text_clean in key:
                return champion

        return None


ocr_service = None


def get_ocr_service():
    global ocr_service
    if ocr_service is None:
        print("初始化OCR服务 (RapidOCR)...")
        ocr_service = OCRService()
        print("OCR服务初始化完成")
    return ocr_service


def process_screenshot(image_path):
    service = get_ocr_service()
    return service.extract_game_data(image_path)
