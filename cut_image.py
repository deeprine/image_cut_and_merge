import argparse
import random
import os

import numpy as np
import shutil
import cv2

def random_transform(img, probability = 0.5):
    if random.random() < probability:
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # 상하반전(flip)
    if random.random() < probability:
        img = cv2.flip(img, 0)

    # 좌우반전(mirroring)
    if random.random() < probability:
        img = cv2.flip(img, 1)

    return img

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='image cut')

    # image_file_name , column_num, row_num, prefix_output_file_name
    parser.add_argument('--image_file_name', type=str, default='input.png')
    parser.add_argument('--column_num', type=int, default=4)
    parser.add_argument('--row_num', type=int, default=3)
    parser.add_argument('--prefix_output_file_name', type=str, default='./output')

    args = parser.parse_args()

    input_path = args.image_file_name
    output_path = args.prefix_output_file_name

    if os.path.isdir(output_path):
        shutil.rmtree(output_path)

    os.makedirs(output_path, exist_ok=True)

    row = args.row_num
    col = args.column_num

    image = cv2.imread(input_path)
    h, w, _ = image.shape

    if (h % 2) != 0:
        image = image[:h-1, :, :]
    elif (w % 2) != 0:
        image = image[:, :w-1, :]

    # 행을 row개로 나눔
    grid_row = np.array_split(image, row, axis=0)
    # 나눈 행을 각각 col개로 나눔
    grid_result = [np.array_split(row_image, col, axis=1) for row_image in grid_row]

    random_number = np.random.choice(range(1, 999), row*col, replace=False)
    count = 0

    for r in range(row):
        for c in range(col):
            save_path = os.path.join(output_path, f'{random_number[count]}.png')
            img = random_transform(grid_result[r][c], probability = 0.5)
            cv2.imwrite(save_path, img)
            count+=1

    print(f'{row} x {col} 자르기 완료')





