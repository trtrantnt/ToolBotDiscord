import pyautogui
import time
import random

class ClickerManager:
    def __init__(self):
        # Configure pyautogui safety settings
        pyautogui.FAILSAFE = True  # Move mouse to a corner to abort
        pyautogui.PAUSE = 0.1      # Small pause after every pyautogui call

    def move_and_click(self, x, y, human_like=True, move_away=True):
        """
        Moves the mouse to the specified coordinates and clicks.
        If human_like is True, adds slight random delays and offsets.
        If move_away is True, moves the mouse cursor away to avoid Discord hover effect.
        """
        if human_like:
            # Thêm độ lệch ngẫu nhiên nhỏ tránh click đúng 1 pixel cố định
            offset_x = random.randint(-4, 4)
            offset_y = random.randint(-4, 4)
            target_x = x + offset_x
            target_y = y + offset_y
            
            # Thời gian di chuyển mượt mà
            duration = random.uniform(0.12, 0.35)
            pyautogui.moveTo(target_x, target_y, duration, pyautogui.easeOutQuad)
            
            # Nghỉ ngắn trước khi click
            time.sleep(random.uniform(0.06, 0.14))
            pyautogui.click()
            
            # Anti-Hover: Dời chuột sang vùng trống bên cạnh (tránh nút bị đổi màu hover)
            if move_away:
                time.sleep(random.uniform(0.05, 0.10))
                # Di chuột sang phải hoặc trái 80-120px
                screen_w, screen_h = pyautogui.size()
                away_x = min(screen_w - 20, max(20, target_x + random.choice([100, 130, -100, -130])))
                away_y = min(screen_h - 20, max(20, target_y + random.randint(-20, 20)))
                pyautogui.moveTo(away_x, away_y, random.uniform(0.08, 0.18), pyautogui.easeOutQuad)
        else:
            pyautogui.click(x, y)
            if move_away:
                pyautogui.moveRel(100, 0, duration=0.1)

    def scroll_down(self, clicks=300):
        """Cuộn màn hình xuống dưới để kéo tin nhắn mới nhất vào tầm nhìn"""
        try:
            pyautogui.scroll(-clicks)
            time.sleep(0.3)
        except Exception as e:
            print(f"Không thể cuộn màn hình: {e}")

    def click_center(self):
        """Clicks at the current mouse position"""
        pyautogui.click()

