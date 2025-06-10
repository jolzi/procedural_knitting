import numpy as np
from knitout import Writer
from primitives import *
from process_image import process_image_to_height_map  # your image processing function
from k_to_kc import k_to_kc   # your subprocess wrapper
from wrappers import cast_on, cast_off # borrow from knitout-kniterate-3D

# 0. parameters
W, H   = 50, 50              # stitches × rows
CARR   = '3'

# 1. budgets
budgetV = process_image_to_height_map("test_textures/AlligatorNoise.1.bmp", target_width=W, target_height=H)
budgetH = np.zeros((H, W), dtype=int)
# ...fill with noise or image...

# 2. knitout writer
w = Writer('1 2 3 4 5 6')  # Initialize with all carriers
w.addHeader('Machine', 'Kniterate')
w.addHeader('Gauge', '7')
w.addHeader('Position', 'Center')

# Set stitch size before starting
w.addRawOperation('x-stitch-number 5')

# Make sure carrier 3 is active before using it
w.incarrier('3')

cast_on(w, left=0, right=119, carrier="3", style="closed")

latency = np.zeros(W, dtype=int)   # delay counter for cables

for y in range(H):
    direction = '+' if y % 2 == 0 else '-'
    needle_range = range(W) if direction == '+' else range(W-1, -1, -1)

    for x in needle_range:
        if latency[x]:
            latency[x] -= 1
            continue

        if abs(budgetH[y, x]) >= 2:
            cable_2x2_RC(w, x)           # consume ±2 horiz
            budgetH[y, x:x+4] -= 2*np.sign(budgetH[y, x])
            latency[x:x+4] = 4           # 4 plain rows until next cable
        elif budgetV[y, x] > 0:
            tuck_on_empty(w, x, direction)  # +1 loop
            budgetV[y, x] -= 1
        elif budgetV[y, x] < 0:
            gather_back_to_front(w, x)           # −2 loops in one shot
            budgetV[y, x] += 2
        else:
            w.knit(direction, ('f', x), CARR)

    w.comment(f'row {y}')

cast_off(w, left=0, right=119, carrier="3", side="l")

# Make sure carrier 3 is taken out at the end
w.outcarrier('3')

w.write('fabric.k')
#sk_to_kc('fabric.k')
