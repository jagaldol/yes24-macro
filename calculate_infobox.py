import json

import keyboard
import pyautogui


def main():
    print("준비되면 F6 키를 누르세요.")

    # F6를 누를 때까지 대기
    while True:
        if keyboard.is_pressed("f6"):
            print("프로그램을 시작합니다.")
            break

    try:
        location = pyautogui.locateOnScreen("targets/info.png", confidence=0.8)
    except pyautogui.ImageNotFoundException:
        print("이미지를 찾지 못했습니다.")
        return

    if location:
        print(f"top-left: {location[0]}, {location[1]}")
        print(f"w, h: {location[2]}, {location[3]}")

        data = {
            "x": int(location[0]),
            "y": int(location[1]),
            "width": int(location[2]),
            "height": int(location[3]),
        }
        with open("info_location.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
