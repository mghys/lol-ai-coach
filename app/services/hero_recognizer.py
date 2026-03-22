import os
import cv2
import numpy as np

class HeroRecognizer:
    def __init__(self):
        self.heros_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hero_identification_data', 'heros')
        self.checked_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'hero_identification_data', 'heros_checked')
        
        self.normal_templates = {}
        self.checked_templates = {}
        
        self._load_templates()
    
    def _load_templates(self):
        self._load_from_directory(self.heros_dir, self.normal_templates)
        self._load_from_directory(self.checked_dir, self.checked_templates)
        
        print(f"加载普通头像: {len(self.normal_templates)} 个")
        print(f"加载选中头像: {len(self.checked_templates)} 个")
    
    def _load_from_directory(self, directory, target_dict):
        if not os.path.exists(directory):
            print(f"目录不存在: {directory}")
            return
        
        for filename in os.listdir(directory):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                hero_name = os.path.splitext(filename)[0]
                filepath = os.path.join(directory, filename)
                try:
                    img = cv2.imread(filepath)
                    if img is not None:
                        template = self._prepare_template(img)
                        target_dict[hero_name] = template
                except Exception as e:
                    print(f"加载失败 {filename}: {e}")
    
    def _prepare_template(self, img, target_size=100):
        h, w = img.shape[:2]
        size = min(h, w)
        
        center_x, center_y = w // 2, h // 2
        half = size // 2
        
        cropped = img[center_y-half:center_y+half, center_x-half:center_x+half]
        
        if cropped.size == 0:
            cropped = img
        
        return cv2.resize(cropped, (target_size, target_size))
    
    def _compute_phash(self, gray_img, hash_size=12):
        resized = cv2.resize(gray_img, (hash_size * 4, hash_size * 4))
        avg = resized.mean()
        binary = (resized > avg).astype(int)
        hash_str = ''.join(str(b) for row in binary for b in row)
        return hash_str
    
    def _hamming_distance(self, hash1, hash2):
        if len(hash1) != len(hash2):
            return float('inf')
        return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
    
    def _extract_circle(self, img):
        h, w = img.shape[:2]
        size = min(h, w)
        
        center_x, center_y = w // 2, h // 2
        radius = size // 2
        
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), radius, 255, -1)
        
        result = np.zeros_like(img)
        for i in range(3):
            result[:,:,i] = cv2.bitwise_and(img[:,:,i], img[:,:,i], mask=mask)
        
        x1 = max(0, center_x - radius)
        x2 = min(w, center_x + radius)
        y1 = max(0, center_y - radius)
        y2 = min(h, center_y + radius)
        
        cropped = result[y1:y2, x1:x2]
        
        if cropped.size == 0:
            return None
        
        return cv2.resize(cropped, (100, 100))
    
    def _compute_similarity(self, img1, img2):
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        phash1 = self._compute_phash(gray1)
        phash2 = self._compute_phash(gray2)
        phash_sim = 1 - (self._hamming_distance(phash1, phash2) / len(phash1))
        
        hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
        cv2.normalize(hist1, hist1)
        cv2.normalize(hist2, hist2)
        hist_sim = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        hist_sim = max(0, hist_sim)
        
        orb = cv2.ORB_create(nfeatures=100)
        kp1, des1 = orb.detectAndCompute(gray1, None)
        kp2, des2 = orb.detectAndCompute(gray2, None)
        
        if des1 is not None and des2 is not None and len(des1) > 5 and len(des2) > 5:
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)
            if len(matches) > 0:
                orb_sim = len(matches) / max(len(kp1), len(kp2), 1)
            else:
                orb_sim = 0
        else:
            orb_sim = 0
        
        similarity = phash_sim * 0.4 + hist_sim * 0.2 + orb_sim * 0.4
        
        return similarity
    
    def _extract_80px_circle(self, img):
        h, w = img.shape[:2]
        
        center_x, center_y = w // 2, h // 2
        radius = 40
        
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), radius, 255, -1)
        
        result = img.copy()
        result[np.where(mask == 0)] = [0, 0, 0]
        
        x1 = max(0, center_x - radius)
        x2 = min(w, center_x + radius)
        y1 = max(0, center_y - radius)
        y2 = min(h, center_y + radius)
        
        cropped = result[y1:y2, x1:x2]
        
        if cropped.size == 0:
            return None
        
        return cv2.resize(cropped, (100, 100))
    
    def recognize(self, image_path, top_n=1, zone_type="normal"):
        input_img = cv2.imread(image_path)
        if input_img is None:
            return []
        
        template_normal = self._prepare_template(input_img)
        results = {}
        
        if zone_type == "normal":
            for hero_name, template in self.normal_templates.items():
                similarity = self._compute_similarity(template_normal, template)
                results[hero_name] = similarity
        elif zone_type == "selected":
            for hero_name, template in self.normal_templates.items():
                similarity = self._compute_similarity(template_normal, template)
                results[hero_name] = similarity
            
            processed_img = self._extract_80px_circle(input_img)
            if processed_img is not None:
                for hero_name, template in self.checked_templates.items():
                    similarity = self._compute_similarity(processed_img, template)
                    if hero_name in results:
                        results[hero_name] = max(results[hero_name], similarity)
                    else:
                        results[hero_name] = similarity
        
        sorted_results = [
            {"hero": name, "similarity": round(sim * 100, 1)}
            for name, sim in results.items()
        ]
        
        sorted_results.sort(key=lambda x: x["similarity"], reverse=True)
        
        if zone_type == "normal" and sorted_results:
            max_similarity = sorted_results[0]["similarity"]
            if max_similarity < 50:
                return [{"hero": "empty", "similarity": 0}]
        
        return sorted_results[:top_n]

hero_recognizer = None

def get_hero_recognizer():
    global hero_recognizer
    if hero_recognizer is None:
        print("初始化英雄识别器...")
        hero_recognizer = HeroRecognizer()
        print("英雄识别器初始化完成")
    return hero_recognizer

def recognize_hero(image_path, zone_type="normal"):
    recognizer = get_hero_recognizer()
    return recognizer.recognize(image_path, zone_type=zone_type)
