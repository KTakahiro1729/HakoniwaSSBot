import cv2
from matplotlib import pyplot as plt
import os
import numpy as np

def imread(*vars, **kwargs):
  return cv2.imread(*vars, **kwargs)[...,::-1].astype(np.uint8)

img_dir = "img"

xbar_path = os.path.join(img_dir, "mapchips/Hakoniwa_X_axis.png")

mapchip_names = [f"land{i}" for i in range(17)] + [f"monster{i}" for i in range(9)] + ["monument0", "f02"]
mapchip_paths = {f: os.path.join(img_dir, f"mapchips/{f}.png")  for f in mapchip_names}
mapchip_int = {k:i for i, k in enumerate(mapchip_names)}
mapchip_jp = {k:"海荒草村町都森農工ミ防山底痕瀬鉱油緑赤黒王硬三九メ霊礎巨"[i] 
              for i, k in enumerate(mapchip_names)}
mapchip_sim_int = {k:[0,2,4,5,6,7,9,11,14,18,19,20,23,3,1,21,24,33,36,37,41,35,34,39,32,38,25,32][i] for i,k in enumerate(mapchip_names)}
mapchip_size = 60
mapchip_half = mapchip_size // 2
map_w = mapchip_size*12 + mapchip_half
map_h = mapchip_size*12

mapchip_dict = {i: cv2.resize(imread(mapchip_paths[i]),(mapchip_size,mapchip_size)) for i in mapchip_paths}

def crop_area(map_path, xbar_path):
  # read and resize input img
  map_img = imread(map_path)
  h, w, *_ = map_img.shape
  ratio = map_w / w
  map_img = cv2.resize(map_img, dsize=None, fx = ratio, fy = ratio)

  # find x axis
  xbar_img = imread(xbar_path)
  result = cv2.matchTemplate(map_img, xbar_img, cv2.TM_CCOEFF_NORMED)
  *_, maxLoc = cv2.minMaxLoc(result)

  # crop area
  top = maxLoc[1] + xbar_img.shape[0]
  left = 0
  bottom = top + map_h
  right = map_w
  return map_img[top:bottom, left:right]

def convert_coord_to_img_coord(x,y):
  left = mapchip_size * x
  if y % 2 == 0: # has offset when evens
    left += mapchip_half
  top = mapchip_size * y
  return top, left

def crop_coord(img, x,y, *vars, **kwargs):
  t,l = convert_coord_to_img_coord(x,y, *vars, **kwargs)
  return img[t:t+mapchip_size,l:l+mapchip_size]

def img_diff(img1, img2):
  return ((img1 - img2)**2).mean()**0.5

def decide_mapchip(map_img):
  result = []
  for x in range(12):
    result_x = []
    for y in range(12):
      img = crop_coord(map_img, x,y)
      diffs = [(k, img_diff(img, v)) for k,v in mapchip_dict.items()] # compare with each mapchip
      closesest = sorted(diffs, key = lambda x:x[1])[0]
      result_x.append(closesest[0])
    result.append(result_x)
  return result

def gen_map_from_arr(arr):
  newmap = np.zeros((map_h + mapchip_half, map_w, 3)).astype(int)
  fpath = os.path.join(img_dir, f"mapchips/xbar.png")
  newmap[0:mapchip_half] = cv2.resize(imread(fpath), dsize=(map_w,mapchip_half))
  for i in range(12):
    t,l = i*mapchip_size+mapchip_half,0
    if i % 2 == 1:
      l = 720
    fpath = os.path.join(img_dir, f"mapchips/space{i}.png")
    newmap[t:t+mapchip_size,l:l+mapchip_half] = cv2.resize(imread(fpath), (mapchip_half,h))
  for x in range(12):
    for y in range(12):
      t,l = convert_coord_to_img_coord(x,y)
      t += mapchip_half
      newmap[t:t+mapchip_size,l:l+mapchip_size] = mapchip_dict[arr[x][y]]
  return newmap

def convert_to_sim(arr):
  arr_t = list(zip(*arr))
  result = []
  arr_t += [["land0"]*16]*4
  for row in arr_t:
    row = list(row)
    row += ["land0"]*4
    for x in row:
        result.append(mapchip_sim_int[x])
  return ",".join(map(str,result))
  
