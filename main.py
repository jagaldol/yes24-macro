import enum
import time

import keyboard
import pyautogui


# 상태를 열거형(enum)으로 정의
class TicketingState(enum.Enum):
    INIT = 0
    DATE_SELECTION = 1
    NEXT_PAGE = 2
    STANDING_SELECTION = 3
    FINISH = 4


terminate = False


def on_press_terminate_key(e):
    global terminate
    terminate = True


def locate_and_click(image_path, confidence=0.8):
    """이미지를 찾아서 클릭하는 함수. 없으면 False 반환."""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
    except pyautogui.ImageNotFoundException:
        # 이미지가 발견되지 않으면 False 반환
        return False

    if location:
        center_point = pyautogui.center(location)
        pyautogui.click(center_point)
        return True
    return False


def refresh_and_reset():
    """alert를 닫기 위해 엔터키 누르고, 새로고침(F5) 실행 후 INIT 상태로 리셋"""
    print("대상 이미지를 찾지 못했습니다. alert 처리 후 새로고침(F5) 합니다.")
    pyautogui.press("enter")  # alert 닫기용 엔터키
    time.sleep(0.2)  # alert 처리 시간 대기
    pyautogui.press("f5")  # 새로고침
    time.sleep(1)  # 새로고침 후 안정화를 위한 대기


def main():
    print("티켓팅을 시작하려면 F6 키를 누르세요.")
    print("프로그램을 종료할려면 F7 키를 누르세요.")
    print("화면의 빨간 선안에 창을 위치시켜주세요")
    while True:
        if keyboard.is_pressed("f6"):
            print("프로그램을 시작합니다.")
            break

    state = TicketingState.INIT
    while True:
        if terminate:
            print("프로그램을 종료합니다.")
            break

        if state == TicketingState.INIT:
            # 초기 상태: 예를 들어 날짜 선택 화면을 기다림
            if locate_and_click("targets/date.png", confidence=0.8):
                print("날짜 선택 클릭")
                state = TicketingState.DATE_SELECTION

        elif state == TicketingState.DATE_SELECTION:
            # 날짜 선택 후 다음 단계로 넘어가기
            if locate_and_click("targets/next.png", confidence=0.8):
                print("다음 페이지 클릭")
                state = TicketingState.NEXT_PAGE
            else:
                # alert가 뜰 수도 있으니 엔터키 누르고 새로고침 후 INIT 상태로 복귀
                refresh_and_reset()
                state = TicketingState.INIT

        elif state == TicketingState.NEXT_PAGE:
            # 자리 선택 상태

            # TODO: "targets/info.png" 이미지에 포함되어있는 standing 이미지는 선택하면 안됨
            if locate_and_click("targets/standing.png", confidence=0.9):
                print("좌석(standing) 클릭")
                state = TicketingState.STANDING_SELECTION
            elif locate_and_click("targets/back.png", confidence=0.9):
                print("뒤로가기(back) 클릭")
                state = TicketingState.INIT
            else:
                # alert 처리 및 새로고침 후 초기 상태로 복귀
                refresh_and_reset()
                state = TicketingState.INIT

        elif state == TicketingState.STANDING_SELECTION:
            # 좌석 선택 후 결제 혹은 마무리 상태로 전환
            if locate_and_click("targets/finish.png", confidence=0.9):
                print("마무리(finish) 클릭")
                state = TicketingState.FINISH

        elif state == TicketingState.FINISH:
            print("티켓팅 완료")
            break

        time.sleep(0.1)


if __name__ == "__main__":
    # 화면이 준비될 시간을 주기 위해 잠시 대기 (예: 2초)
    time.sleep(2)
    main()
