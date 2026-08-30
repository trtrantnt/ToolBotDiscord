import json
import os
import sys
import ctypes

# Bật chế độ DPI Awareness và hỗ trợ UTF-8 cho Windows console
if sys.platform.startswith('win'):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # PROCESS_PER_MONITOR_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    try:
        if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from src.controller import DungeonController, Fast10xController

def load_config(config_path="config.json"):
    if not os.path.exists(config_path):
        print(f"Không tìm thấy file cấu hình {config_path}. Đang sử dụng cấu hình mặc định.")
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def display_menu():
    print("\n" + "="*62)
    print("🤖 DISCORD BOT AUTO CLICKER (UYÊN SƯ MUỘI) - OCR EDITION")
    print("="*62)
    print(" [1] 🏰 Tự động đi Bí Cảnh (5 Ải Bát Môn, Kỳ Ngộ, Chiến Đấu)")
    print(" [2] ⚡ Tự động bấm nút 'Nhanh x10' (Tăng tốc chiến đấu)")
    print(" [0] 🛑 Thoát chương trình")
    print("="*62)

def main():
    config = load_config()
    
    # Kiểm tra nếu có truyền tham số dòng lệnh (vd: python main.py 1 hoặc python main.py 2)
    choice = None
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        if arg in ["1", "2", "0"]:
            choice = arg

    while choice is None:
        display_menu()
        try:
            user_input = input("👉 Vui lòng nhập lựa chọn của bạn (1 / 2 / 0): ").strip()
            if user_input in ["1", "2", "0", "q", "Q"]:
                choice = user_input.lower()
            else:
                print("❌ Lựa chọn không hợp lệ! Vui lòng nhập 1, 2 hoặc 0.")
        except (KeyboardInterrupt, EOFError):
            print("\nĐã hủy.")
            return

    if choice == "1":
        controller = DungeonController(config)
        controller.start()
    elif choice == "2":
        controller = Fast10xController(config)
        controller.start()
    else:
        print("Tạm biệt!")
        sys.exit(0)

if __name__ == "__main__":
    main()
