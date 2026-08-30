import pyautogui
import time
import random
import ctypes
import sys

# Bật chế độ DPI Awareness để tọa độ click khớp 100% với độ phân giải màn hình
if sys.platform.startswith('win'):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # PROCESS_PER_MONITOR_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

class ClickerManager:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05
        self._is_win = sys.platform.startswith('win')

    def move_and_click(self, x, y, human_like=False, move_away=True):
        """
        Click chính xác 100% vào tâm tọa độ (x, y) bằng Windows Native API để triệt tiêu độ trễ
        và lỗi lệch tọa độ do DPI Scaling hoặc chuột lướt chậm.
        """
        target_x = int(round(x))
        target_y = int(round(y))

        if self._is_win:
            try:
                # 1. Đặt con trỏ chuột trực tiếp và chính xác vào tâm nút
                ctypes.windll.user32.SetCursorPos(target_x, target_y)
                time.sleep(0.04)
                
                # 2. Phát tín hiệu Mouse Down & Mouse Up tại đúng điểm
                # MOUSEEVENTF_LEFTDOWN = 0x0002, MOUSEEVENTF_LEFTUP = 0x0004
                ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)
                time.sleep(0.04)
                ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)
                
                # 3. Anti-Hover: Dời chuột sang vùng an toàn bên cạnh nút (tránh đổi màu giao diện)
                if move_away:
                    time.sleep(0.06)
                    # Dời chuột sang phải 120px và giữ nguyên Y để không kích hoạt hover nút khác
                    away_x = target_x + 120
                    away_y = target_y
                    ctypes.windll.user32.SetCursorPos(away_x, away_y)
                return
            except Exception as e:
                pass

        # Fallback sang PyAutoGUI nếu không dùng Windows API
        pyautogui.moveTo(target_x, target_y, duration=0.05)
        pyautogui.click(target_x, target_y)
        if move_away:
            pyautogui.moveTo(target_x + 120, target_y, duration=0.05)

    def scroll_down(self, clicks=300):
        """Cuộn màn hình xuống dưới để kéo tin nhắn mới nhất vào tầm nhìn"""
        try:
            pyautogui.scroll(-clicks)
            time.sleep(0.2)
        except Exception as e:
            print(f"Không thể cuộn màn hình: {e}")

    def click_center(self):
        """Click tại vị trí chuột hiện tại"""
        pyautogui.click()
