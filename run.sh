#!/bin/bash

INPUT_FILE='test11.jpg'
OUTPUT_FOLDER='./output'
ROW_NUM=3
COL_NUM=4

python cut_image.py --image_file_name $INPUT_FILE --column_num $COL_NUM --row_num $ROW_NUM --prefix_output_file_name $OUTPUT_FOLDER
python merge_image.py --prefix_output_file_name $OUTPUT_FOLDER --column_num $COL_NUM --row_num $ROW_NUM
