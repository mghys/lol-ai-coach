import os
import cv2
import numpy as np

def create_checked_heroes():
    heros_dir = 'C:/Users/13321/ai-coach/data/hero_identification_data/heros'
    checked_dir = 'C:/Users/13321/ai-coach/data/hero_identification_data/heros_checked'
    
    if not os.path.exists(checked_dir):
        os.makedirs(checked_dir)
    
    files = [f for f in os.listdir(heros_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    print(f"开始处理 {len(files)} 个英雄头像...")
    
    for i, filename in enumerate(files):
        filepath = os.path.join(heros_dir, filename)
        img = cv2.imread(filepath)
        
        if img is None:
            print(f"跳过: {filename} (无法读取)")
            continue
        
        h, w = img.shape[:2]
        
        center_x, center_y = w // 2, h // 2
        radius = 40
        
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), radius, 255, -1)
        
        result = img.copy()
        
        result[np.where(mask == 0)] = [0, 0, 0]
        
        output_path = os.path.join(checked_dir, filename)
        cv2.imwrite(output_path, result)
        
        if (i + 1) % 20 == 0:
            print(f"已处理 {i + 1}/{len(files)}")
    
    print(f"完成! 共处理 {len(files)} 个英雄")
    print(f"输出目录: {checked_dir}")

if __name__ == '__main__':
    create_checked_heroes()
