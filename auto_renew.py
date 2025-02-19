import enum
import json
import time

import keyboard
import pyautogui


# 상태를 열거형(enum)으로 정의
class TicketingState(enum.Enum):
    INIT = 0
    DATE_SELECTION = 1
    LOADING = 2
    NEXT_PAGE = 3
    NEED_REFRESH = 4
    FOCUS_DATE = 5
    STANDING_SELECTION = 6
    FINISH = 7


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

    state = TicketingState.NEED_REFRESH
    retry = 0
    last_check_time = time.time()  # 마지막 확인 시각 기록

    while True:
        if terminate:
            print("프로그램을 종료합니다.")
            break

        if state == TicketingState.LOADING:
            # 좌석이 완전 없는거를 찾음(화면에 텅 빈 좌석이 보여야 새로고침 시도)
            retry += 1
            if locate_find("targets/select_box.png", confidence=0.8):
                state = TicketingState.NEED_REFRESH

            if retry > 20:
                current_time = time.time()
                elapsed = current_time - last_check_time
                print(f"좌석 선택 화면인지 확인 - {elapsed:.2f}초")
                last_check_time = current_time  # 확인 후 시각 업데이트
                retry = 0
                if locate_find("targets/finish.png", confidence=0.8):
                    state = TicketingState.NEED_REFRESH

        elif state == TicketingState.NEED_REFRESH:
            keyboard.press_and_release("enter")
            pyautogui.doubleClick()
            keyboard.press_and_release("left")
            keyboard.press_and_release("right")

            state = TicketingState.LOADING
            retry = 0
            time.sleep(0.01)


if __name__ == "__main__":
    main()
