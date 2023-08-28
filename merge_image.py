import argparse
import natsort
import glob
import cv2
import os

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color

def side_lines(image):
    left_line = image[:, 0, :]
    right_line = image[:, -1, :]
    return [left_line, right_line]

def topdown_lines(image):
    top_line = image[0, :, :]
    down_line = image[-1, :, :]
    return [top_line, down_line]

def edge_equal(sub_img, edge_img, direction = None, transform = None):
    if transform == 'flip':
        edge_img = cv2.flip(edge_img, 0)
    elif transform == 'mirror':
        edge_img = cv2.flip(edge_img, 1)
    elif transform == 'f_m':
        edge_img = cv2.flip(edge_img, 0)
        edge_img = cv2.flip(edge_img, 1)
    else:
        pass

    if direction == 'side':
        sub_lines = side_lines(sub_img)
        edge_lines = list(reversed(side_lines(edge_img)))
    elif direction == 'topdown':
        sub_lines = topdown_lines(sub_img)
        edge_lines = list(reversed(topdown_lines(edge_img)))

    best_diff = float('inf')
    best_idx = 0
    for idx, (subs, edges) in enumerate(zip(sub_lines, edge_lines)):
        color_diff = 0
        for sub, edge in zip(subs, edges):
            sub_color = sRGBColor(sub[0], sub[1], sub[2])
            edge_color = sRGBColor(edge[0], edge[1], edge[2])
            sub_lab = convert_color(sub_color, LabColor)
            edge_lab = convert_color(edge_color, LabColor)

            delta_e = delta_e_cie2000(sub_lab, edge_lab)
            color_diff += delta_e

        if best_diff > color_diff:
            best_diff = color_diff
            best_idx = idx

    return best_idx, best_diff, edge_img

# 12개의 이미지에 대한 모든 가능한 순서를 생성합니다.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='image merge')

    # prefix_output_file_name
    parser.add_argument('--prefix_output_file_name', type=str, default='./output')
    parser.add_argument('--column_num', type=int, default=4)
    parser.add_argument('--row_num', type=int, default=3)

    args = parser.parse_args()

    output_path = args.prefix_output_file_name
    row = args.row_num
    col = args.column_num

    if not os.path.exists(output_path):
        raise FileNotFoundError(f"File '{output_path}' already exists!")

    transformed_images = natsort.natsorted(glob.glob(os.path.join(output_path, '*.png')))

    images = []
    sub = cv2.imread(transformed_images[0])
    sh,sw,_ = sub.shape
    images.append(sub)
    # 첫번째 인덱스 기준으로 shape 맞추기
    for idx, edge in enumerate(transformed_images[1:]):
        edge = cv2.imread(edge)

        while sub.shape != edge.shape:
            eh,ew,_ = edge.shape
            if abs(sh - eh) == 1 or abs(sw - ew) == 1:
                edge = cv2.resize(edge, (sw, sh), interpolation=cv2.INTER_LINEAR)
            else:
                edge = cv2.rotate(edge, cv2.ROTATE_90_COUNTERCLOCKWISE)

        images.append(edge)

    # merge 시작
    images_copy = images.copy()
    concat_imgs = []

    # M x N 형태로 N 개씩 merge
    for t in range(row):
        base_img = images_copy[0]
        for c in range(col-1):
            every_best_diff = float('inf')
            every_best_img = 0
            every_best_loc = 0
            every_best_ind = 0

            for ind, img in enumerate(images_copy[1:]):
                ori_idx, ori_diff, ori_img = edge_equal(base_img, img, direction='side')
                flip_idx, flip_diff, flip_img = edge_equal(base_img, img, direction='side', transform='flip')
                mirr_idx, mirr_diff, mirr_img = edge_equal(base_img, img, direction='side', transform='mirror')
                fm_idx, fm_diff, fm_img = edge_equal(base_img, img, direction='side', transform='f_m')

                # flip, mirror 된 이미지중 베스트 찾기
                diff_values = [ori_diff, flip_diff, mirr_diff, fm_diff]
                diff_imgs = [ori_img, flip_img, mirr_img, fm_img]
                diff_loc = [ori_idx, flip_idx, mirr_idx, fm_idx]

                values = diff_values.copy()
                diff_values = [i for i in diff_values if i != 0]

                if len(diff_values) == 0:
                    diff_values = values

                best_idx = diff_values.index(min(diff_values))
                best_diff = diff_values[best_idx]
                # print(diff_values)
                # print(best_idx)

                if every_best_diff > best_diff:
                    every_best_diff = best_diff
                    every_best_img = diff_imgs[best_idx]
                    every_best_loc = diff_loc[best_idx]
                    every_best_ind = ind+1

            images_copy.pop(every_best_ind)

            if every_best_loc == 0:
                base_img = cv2.hconcat([every_best_img, base_img])
            elif every_best_loc == 1:
                base_img = cv2.hconcat([base_img, every_best_img])
            # cv2.imwrite(f'base_{t}_{c}.png', base_img)

        images_copy.pop(0)
        # cv2.imwrite(f'test_{t}.png', base_img)
        concat_imgs.append(base_img)

    # N개씩 합쳐진 M개의 이미지 merge
    base_cc_img = concat_imgs[0]
    copy_concat = concat_imgs.copy()

    for _ in range(len(copy_concat)-1):
        every_best_diff = float('inf')
        every_best_img = 0
        every_best_loc = 0
        every_best_ind = 0

        for ind, cc_img in enumerate(concat_imgs[1:]):
            ori_idx, ori_diff, ori_img = edge_equal(base_cc_img, cc_img, direction='topdown')
            flip_idx, flip_diff, flip_img = edge_equal(base_cc_img, cc_img, direction='topdown', transform='flip')
            mirr_idx, mirr_diff, mirr_img = edge_equal(base_cc_img, cc_img, direction='topdown', transform='mirror')
            fm_idx, fm_diff, fm_img = edge_equal(base_cc_img, cc_img, direction='topdown', transform='f_m')

            diff_values = [ori_diff, flip_diff, mirr_diff, fm_diff]
            diff_imgs = [ori_img, flip_img, mirr_img, fm_img]
            diff_loc = [ori_idx, flip_idx, mirr_idx, fm_idx]

            print(diff_values)
            best_idx = diff_values.index(min(diff_values))
            best_diff = diff_values[best_idx]

            if every_best_diff > best_diff:
                every_best_diff = best_diff
                every_best_img = diff_imgs[best_idx]
                cv2.imwrite(f'test_{ind}.png', every_best_img)
                every_best_loc = diff_loc[best_idx]
                every_best_ind = ind + 1

        if every_best_loc == 0:
            base_cc_img = cv2.vconcat([every_best_img, base_cc_img])
        elif every_best_loc == 1:
            base_cc_img = cv2.vconcat([base_cc_img, every_best_img])

        concat_imgs.pop(every_best_ind)

    print('merge 완료')
    cv2.imwrite(f'good_result.png', base_cc_img)
    cv2.imshow(f'good_result', base_cc_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
