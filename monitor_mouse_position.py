import time

import pyautogui

try:
    while True:
        # 현재 마우스 위치의 x, y 좌표를 가져옴
        x, y = pyautogui.position()
        # 출력 시 매번 덮어쓰도록 end='\r' 사용
        print(f"현재 마우스 좌표: ({x}, {y})", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n프로그램 종료")
