import json
import os
import sys

# Đảm bảo hiển thị tốt tiếng Việt có dấu trên Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from src.controller import AutoClickerController

def load_config(config_path="config.json"):
    if not os.path.exists(config_path):
        print(f"Không tìm thấy file cấu hình {config_path}. Đang sử dụng cấu hình mặc định.")
        return {
            "scan_interval": 0.8,
            "ocr_min_score": 0.6,
            "stop_hotkey": "q"
        }
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("=== Discord Auto-Clicker Đi Bí Cảnh (OCR Edition) ===")
    
    # Load configuration
    config = load_config()
    
    # Initialize controller
    controller = AutoClickerController(config)
    
    # Start the application
    controller.start()

if __name__ == "__main__":
    main()
