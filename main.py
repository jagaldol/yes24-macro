import enum
import json
import time
import winsound

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


# 종료키 F7 등록
keyboard.on_press_key("f7", on_press_terminate_key)


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
        location = pyautogui.locateOnScreen(image_path, region=select_box_region, confidence=confidence)
    except pyautogui.ImageNotFoundException:
        return False

    if location:
        center_point = pyautogui.center(location)
        pyautogui.click(center_point)
        return True
    return False


def refresh_and_reset():
    """alert를 닫기 위해 엔터키 누르고, 새로고침(F5) 실행 후 초기 상태로 리셋"""
    print("대상 이미지를 찾지 못했거나 info 영역 내의 target은 무시합니다.")
    print("alert 처리 후 새로고침(F5) 합니다.")
    pyautogui.press("enter")  # alert 닫기용 엔터키
    time.sleep(0.2)  # alert 처리 시간 대기
    pyautogui.click()
    pyautogui.press("f5")  # 새로고침
    time.sleep(1)  # 새로고침 후 안정화를 위한 대기


def main():
    print("티켓팅을 시작하려면 F6 키를 누르세요.")
    print("프로그램을 종료하려면 F7 키를 누르세요.")

    # F6를 누를 때까지 대기
    while True:
        if keyboard.is_pressed("f6"):
            print("프로그램을 시작합니다.")
            break

    state = TicketingState.INIT
    retry = 0
    while True:
        if terminate:
            print("프로그램을 종료합니다.")
            break
        if locate_and_click("targets/alert_confirm.png", confidence=0.8):
            print("alert 확인 클릭")
            time.sleep(0.5)

        if state == TicketingState.INIT:
            # 초기 상태: 날짜 선택 화면 대기
            if locate_and_click("targets/date.png", confidence=0.8):
                print("날짜 선택 클릭")
                state = TicketingState.DATE_SELECTION
            else:
                refresh_and_reset()

        elif state == TicketingState.DATE_SELECTION:
            # 날짜 선택 후 다음 단계로
            if locate_and_click("targets/next.png", confidence=0.8):
                print("다음 페이지 클릭")
                state = TicketingState.LOADING
            else:
                # alert가 뜰 수도 있으니 alert 처리 후 새로고침 후 INIT 상태로 복귀
                refresh_and_reset()
                state = TicketingState.INIT

        elif state == TicketingState.LOADING:
            if retry >= 200:
                print("로딩이 너무 오래 걸려서 새로고침합니다.")
                refresh_and_reset()
                state = TicketingState.INIT
                retry = 0
            if locate_and_click("targets/load_fin.png", confidence=0.8):
                state = TicketingState.NEXT_PAGE
                retry = 0
            else:
                time.sleep(0.005)
                retry += 1

        elif state == TicketingState.NEXT_PAGE:
            # 자리 선택 단계
            # info 영역은 항상 나타나므로 먼저 info 영역을 감지합니다.
            # info 영역 안에 포함된 standing 이미지는 무시하고,
            # info 영역 밖에 있는 standing 이미지를 클릭합니다.
            if locate_and_click_standing("targets/standing.png", confidence=0.9):
                print("좌석(standing) 클릭")
                state = TicketingState.STANDING_SELECTION
            else:
                state = TicketingState.NEED_REFRESH

        elif state == TicketingState.NEED_REFRESH:
            if locate_and_click("targets/date_selector.png", confidence=0.8):
                pyautogui.click()
                print("회차 포커스")
                keyboard.press_and_release("left")
                keyboard.press_and_release("right")
                print("새로고침")
                state = TicketingState.LOADING
            else:
                refresh_and_reset()

        elif state == TicketingState.STANDING_SELECTION:
            # 좌석 선택 후 결제 혹은 마무리 단계로 전환
            if locate_and_click("targets/finish.png", confidence=0.9):
                print("마무리(finish) 클릭")
                state = TicketingState.FINISH

        elif state == TicketingState.FINISH:
            print("티켓팅 완료")
            winsound.Beep(1000, 3000)
            break


if __name__ == "__main__":
    main()
