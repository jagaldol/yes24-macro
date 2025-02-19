import enum
import json
import random
import threading
import winsound

import keyboard
import pyautogui
import pyscreeze


class State(enum.Enum):
    STOPPED = 0
    RUNNING = 1
    SETUP = 2


state = State.STOPPED

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


def on_press_run_key(e):
    global state
    state = State.RUNNING
    print("프로그램을 실행합니다.")


def on_press_stop_key(e):
    global state
    state = State.STOPPED
    print("프로그램을 멈춥니다.")


def on_press_setup_key(e):
    global state
    state = State.SETUP
    print("새로고침을 위한 설정에 진입합니다.")


keyboard.on_press_key("f6", on_press_run_key)
keyboard.on_press_key("f7", on_press_stop_key)
keyboard.on_press_key("f8", on_press_setup_key)


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


def locate_and_click_standing(image_path, confidence=0.9):
    """
    standing 이미지를 모두 찾은 후,
    고정된 exclusion zone (left=57, top=746, width=224, height=636) 안에
    완전히 포함된 후보는 무시하고, 영역 밖의 첫 번째 후보를 클릭하는 함수.
    """
    try:
        locations = list(pyautogui.locateAllOnScreen(image_path, region=select_box_region, confidence=confidence))
    except pyscreeze.ImageNotFoundException:
        return False

    if locations:
        location = random.choice(locations)
        center_point = pyautogui.center(location)
        pyautogui.click(center_point)
        return True
    return False


def beep_async():
    winsound.Beep(1000, 3000)


def main():
    print("진행하려면 F6 키를 누르세요.")
    print("멈추려면 F7 키를 누르세요.")
    print("새로고침을 위해 회차 선택창에 focus를 하기 위해서는 F8 키를 누르세요.")
    print("방향키 <-, ->를 연속적으로 누르면 새로고침됩니다.")
    global state
    while True:
        if state == State.STOPPED:
            continue
        elif state == State.SETUP:
            if locate_and_click("targets/date_selector.png", confidence=0.9):
                pyautogui.click()
                state = State.RUNNING
        elif state == State.RUNNING:
            if locate_and_click_standing("targets/standing.png", confidence=0.9):
                print("좌석(standing) 클릭")
                if locate_and_click("targets/finish.png", confidence=0.9):
                    print("마무리(finish) 클릭")
                    pyautogui.press("enter")
                    threading.Thread(target=beep_async).start()
                    print("비프음 발생")
                    state = State.SETUP


if __name__ == "__main__":
    main()
