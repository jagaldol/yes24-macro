import enum
import json
import time

import keyboard
import pyautogui


# 상태를 열거형(enum)으로 정의
class TicketingState(enum.Enum):
    INIT = 0
    LOADING = 2
    NEED_REFRESH = 4


terminate = False

try:
    with open("select_location.json", "r", encoding="utf-8") as f:
        data = json.load(f)

except FileNotFoundError:
    print("저장된 위치 정보가 없습니다.")
    exit()

select_box_region = (
    data["x"],  # left
    data["y"],  # top
    data["width"],  # width
    data["height"],  # height
)


def on_press_terminate_key(e):
    global terminate
    terminate = True


# 종료키 F9 등록
keyboard.on_press_key("f9", on_press_terminate_key)


def locate_and_click(image_path, confidence=0.8):
    """이미지를 찾아서 클릭하는 함수. 없으면 False 반환."""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
    except pyautogui.ImageNotFoundException:
        return False

    if location:
        center_point = pyautogui.center(location)
        pyautogui.click(center_point)
        return True
    return False


def locate_find(image_path, confidence=0.8):
    """이미지를 찾아서 클릭하는 함수. 없으면 False 반환."""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
    except pyautogui.ImageNotFoundException:
        return False

    if location:
        return True
    return False


def main():
    print("공연장이 감지되면 새로고침합니다.")
    print("프로그램을 종료하려면 F9 키를 누르세요.")

    state = TicketingState.INIT
    retry = 0
    last_check_time = time.time()  # 마지막 확인 시각 기록

    while True:
        if terminate:
            print("프로그램을 종료합니다.")
            break

        if state == TicketingState.INIT:
            if locate_and_click("targets/alert_confirm.png", confidence=0.8):
                print("alert 확인 클릭")
            if locate_and_click("targets/date_selector.png", confidence=0.9):
                pyautogui.click()
                state = TicketingState.NEED_REFRESH
            elif locate_find("targets/selected_date_selector.png", confidence=0.9):
                state = TicketingState.NEED_REFRESH

        if state == TicketingState.LOADING:
            # 좌석이 완전 없는거를 찾음(화면에 텅 빈 좌석이 보여야 새로고침 시도)
            retry += 1
            if locate_find("targets/select_box.png", confidence=0.9):
                state = TicketingState.NEED_REFRESH

            if retry > 20:
                retry = 0
                current_time = time.time()
                elapsed = current_time - last_check_time
                print(f"초기상태로 회귀 - {elapsed:.2f}초")
                last_check_time = current_time  # 확인 후 시각 업데이트
                state = TicketingState.INIT

        elif state == TicketingState.NEED_REFRESH:
            current_mouse_x, current_mouse_y = pyautogui.position()
            pyautogui.click(600, 600)
            pyautogui.doubleClick(current_mouse_x, current_mouse_y)
            keyboard.press_and_release("left")
            keyboard.press_and_release("right")
            state = TicketingState.LOADING
            retry = 0


if __name__ == "__main__":
    main()
