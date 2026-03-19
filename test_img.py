import sys
import os
os.chdir('C:/Users/13321/ai-coach')
sys.path.insert(0, '.')

import cv2
img = cv2.imread('C:/Users/13321/ai-coach/data/uploads/Snipaste_2026-03-17_19-10-29.png')
print(f'图片加载成功: {img.shape}')

import numpy as np
h, w = img.shape[:2]
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print(f'灰度图尺寸: {gray.shape}')

print(f'\n区域检查:')
print(f'左侧队伍区域: 0-{int(w*0.45)}')
print(f'右侧队伍区域: {int(w*0.55)}-{w}')
