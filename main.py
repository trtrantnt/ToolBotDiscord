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
        print(f"Config file not found at {config_path}. Using defaults.")
        return {
            "scan_interval": 1.0,
            "confidence_threshold": 0.8,
            "stop_hotkey": "q",
            "templates_dir": "templates"
        }
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("=== Discord Auto-Clicker ===")
    
    # Load configuration
    config = load_config()
    
    # Initialize controller
    controller = AutoClickerController(config)
    
    # Ensure templates directory exists
    templates_dir = config.get("templates_dir", "templates")
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        print(f"Created '{templates_dir}' directory.")
        print("Please use Snipping Tool to take screenshots of the buttons you want to click,")
        print(f"save them as .png in the '{templates_dir}' directory, and run the script again.")
        sys.exit(0)
        
    if not os.listdir(templates_dir):
        print(f"Directory '{templates_dir}' is empty.")
        print("Please add image templates (e.g. claim_button.png) to this directory first.")
        sys.exit(0)

    # Start the application
    controller.start()

if __name__ == "__main__":
    main()
