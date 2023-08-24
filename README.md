### 이미지를 M x N 으로 자른후에 random rotation, flip, mirroring을 각 grid에 적용하고 원본 이미지로 다시 복원합니다.

실행환경 ubuntu 18.04

1. git clone 

2. 라이브러리 설치
```commandline
pip install -r requirements.txt
```

3. 이미지 준비

4. 쉘스크립트 변경 후 코드 실행
```commandline
# run.sh
INPUT_FILE='test11.jpg'
OUTPUT_FOLDER='./output'
ROW_NUM=3
COL_NUM=4
```
   
```commandline
sh run.sh
```
