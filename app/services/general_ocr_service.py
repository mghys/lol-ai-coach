import warnings

warnings.filterwarnings("ignore", message=".*pin_memory.*")

import cv2
import easyocr


class GeneralOCRService:
    def __init__(self):
        print("加载 EasyOCR 中英文模型...")
        self.reader_zh_en = easyocr.Reader(
            ["ch_sim", "en"],
            gpu=False,
            verbose=False,
            model_storage_directory="data/easyocr_model",
        )
        print("加载 EasyOCR 日文模型...")
        self.reader_ja = easyocr.Reader(
            ["ja", "en"],
            gpu=False,
            verbose=False,
            model_storage_directory="data/easyocr_model",
        )
        print("OCR 引擎加载完成")

    def recognize_text(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            return {"success": False, "error": "无法读取图片", "texts": []}

        try:
            all_texts = []

            try:
                results = self.reader_zh_en.readtext(image_path, detail=1)
                for bbox, text, confidence in results:
                    if text and str(text).strip():
                        x_min = int(min(point[0] for point in bbox))
                        y_min = int(min(point[1] for point in bbox))
                        x_max = int(max(point[0] for point in bbox))
                        y_max = int(max(point[1] for point in bbox))

                        all_texts.append(
                            {
                                "text": str(text).strip(),
                                "confidence": round(float(confidence) * 100, 2),
                                "bbox": {
                                    "x1": x_min,
                                    "y1": y_min,
                                    "x2": x_max,
                                    "y2": y_max,
                                },
                                "engine": "easyocr-zh-en",
                            }
                        )
            except Exception as e:
                print(f"EasyOCR zh-en error: {e}")

            try:
                results = self.reader_ja.readtext(image_path, detail=1)
                for bbox, text, confidence in results:
                    if text and str(text).strip():
                        x_min = int(min(point[0] for point in bbox))
                        y_min = int(min(point[1] for point in bbox))
                        x_max = int(max(point[0] for point in bbox))
                        y_max = int(max(point[1] for point in bbox))

                        all_texts.append(
                            {
                                "text": str(text).strip(),
                                "confidence": round(float(confidence) * 100, 2),
                                "bbox": {
                                    "x1": x_min,
                                    "y1": y_min,
                                    "x2": x_max,
                                    "y2": y_max,
                                },
                                "engine": "easyocr-ja",
                            }
                        )
            except Exception as e:
                print(f"EasyOCR ja error: {e}")

            merged = self._merge_results(all_texts)
            full_text = " ".join([t["text"] for t in merged])

            return {
                "success": True,
                "texts": merged,
                "full_text": full_text,
                "count": len(merged),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "texts": []}

    def _merge_results(self, texts):
        if not texts:
            return []

        texts.sort(key=lambda x: (x["bbox"]["y1"], x["bbox"]["x1"]))

        merged = []
        for item in texts:
            text = item["text"]
            is_dup = False
            for m in merged:
                if self._is_similar(text, m["text"]):
                    if item["confidence"] > m["confidence"]:
                        merged.remove(m)
                        merged.append(item)
                    is_dup = True
                    break

            if not is_dup:
                merged.append(item)

        return merged

    def _is_similar(self, text1, text2):
        if text1 == text2:
            return True
        if text1 in text2 or text2 in text1:
            return True
        return False


general_ocr_service = None


def get_general_ocr_service():
    global general_ocr_service
    if general_ocr_service is None:
        print("初始化通用OCR服务...")
        general_ocr_service = GeneralOCRService()
    return general_ocr_service


def recognize_general_text(image_path):
    service = get_general_ocr_service()
    return service.recognize_text(image_path)
