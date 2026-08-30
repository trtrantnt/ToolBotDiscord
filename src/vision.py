import cv2
import numpy as np
import pyautogui
import os
import sys
import re
import mss
from rapidocr_onnxruntime import RapidOCR

# Đảm bảo console Windows không bị lỗi Unicode khi in tiếng Việt và emoji
if sys.platform.startswith('win'):
    try:
        if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


def normalize_vietnamese_text(text):
    """
    Chuẩn hóa văn bản Tiếng Việt:
    - Chuyển về chữ thường
    - Bỏ toàn bộ dấu thanh/mũ (á->a, đ->d, ô->o,...)
    - Xóa các ký tự đặc biệt như ngoặc vuông [], ngoặc tròn (), dấu câu
    - Rút gọn khoảng trắng thừa
    """
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', text)
    text = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', text)
    text = re.sub(r'[ìíịỉĩ]', 'i', text)
    text = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', text)
    text = re.sub(r'[ùúụủũưừứựửữ]', 'u', text)
    text = re.sub(r'[ỳýỵỷỹ]', 'y', text)
    text = re.sub(r'[đ]', 'd', text)
    # Xử lý các lỗi OCR ký tự đặc trưng (vd: 'd mon' -> 'do mon', 'thudng' -> 'thuong')
    text = text.replace('thudng', 'thuong')
    text = text.replace('hing', 'hung')
    # Bỏ ký tự đặc biệt
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def is_keyword_match(text_norm, keyword):
    """
    Kiểm tra xem từ khóa có khớp với văn bản không:
    - Nếu từ khóa có nhiều từ (vd: 'sinh mon', 'tieng sam'): kiểm tra chuỗi con
    - Nếu từ khóa là 1 từ đơn (vd: 'tu', 'do', 'sinh'): kiểm tra khớp chính xác từ nguyên vẹn (token), tránh nhầm 'tu' trong 'tiep tuc'
    """
    if not text_norm or not keyword:
        return False
    keyword = keyword.strip()
    if ' ' in keyword:
        return keyword in text_norm
    else:
        tokens = text_norm.split()
        return keyword in tokens

class VisionManager:
    def __init__(self, templates_dir="templates"):
        self.templates_dir = templates_dir
        try:
            self._sct = mss.mss()
        except Exception as e:
            print(f"Không thể khởi tạo mss: {e}")
            self._sct = None
            
        print("🔍 Đang khởi tạo bộ máy nhận diện chữ OCR (RapidOCR)...")
        self.ocr_engine = RapidOCR()
        print("✅ Bộ máy OCR đã sẵn sàng hoạt động!")

    def get_screenshot(self):
        """
        Chụp màn hình siêu tốc (10ms) bằng mss, tránh lỗi OSError: screen grab failed của Windows GDI.
        """
        if self._sct is not None:
            try:
                monitor = self._sct.monitors[1] if len(self._sct.monitors) > 1 else self._sct.monitors[0]
                sct_img = self._sct.grab(monitor)
                img_np = np.array(sct_img)
                return cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
            except Exception:
                pass
        
        # Fallback sang pyautogui
        try:
            shot = pyautogui.screenshot()
            return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Lỗi chụp màn hình: {e}")
            return None

    def scan_screen_text(self, min_score=0.60):
        """
        Quét toàn bộ màn hình và trả về danh sách các khối chữ nhận diện được cùng tọa độ tâm.
        """
        screenshot_bgr = self.get_screenshot()
        if screenshot_bgr is None:
            return []

        try:
            ocr_results, _ = self.ocr_engine(screenshot_bgr)
        except Exception as e:
            print(f"Lỗi OCR Engine: {e}")
            return []

        if not ocr_results:
            return []

        detected_items = []
        for box, text, score in ocr_results:
            if score < min_score:
                continue
            
            # Tính tọa độ tâm của khối chữ từ 4 đỉnh: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            pts = np.array(box, dtype=np.int32)
            center_x = int(np.mean(pts[:, 0]))
            center_y = int(np.mean(pts[:, 1]))
            
            text_norm = normalize_vietnamese_text(text)
            
            detected_items.append({
                "text_raw": text,
                "text_norm": text_norm,
                "center": (center_x, center_y),
                "box": pts,
                "score": float(score)
            })

        return detected_items

    def find_matching_text(self, detected_items, keywords):
        """
        Tìm khối chữ khớp với một trong các từ khóa trong danh sách keywords.
        """
        if isinstance(keywords, str):
            keywords = [keywords]

        norm_keywords = [normalize_vietnamese_text(kw) for kw in keywords]

        for item in detected_items:
            t = item["text_norm"]
            for kw in norm_keywords:
                if is_keyword_match(t, kw):
                    return item["center"], item["score"], item["text_raw"]

        return None, 0, ""

    def find_gate_by_priority(self, detected_items, gate_priority_list):
        """
        Quét danh sách khối chữ và chọn Cổng có độ ưu tiên cao nhất đang có mặt trên màn hình.
        Thứ tự ưu tiên: Sinh > Khai > Hưu > Cảnh > Kinh > Đỗ > Thương > Tử.
        """
        # Thu thập tất cả các cổng thực sự xuất hiện trên màn hình
        detected_gates = {}
        
        # Các từ khóa hành động cần loại trừ khỏi cổng (tránh 'khai' trong 'khai chien')
        excluded_action_words = ["khai chien", "tiep tuc", "chien tiep", "bat dau", "tuong tac"]

        for gate in gate_priority_list:
            gate_id = gate.get("id", gate.get("name", "unknown"))
            keywords = gate.get("keywords", [gate.get("name", ""), gate_id])
            if isinstance(keywords, str):
                keywords = [keywords]
            norm_keywords = [normalize_vietnamese_text(kw) for kw in keywords]

            for item in detected_items:
                t = item["text_norm"]
                # Bỏ qua nếu khối chữ này thuộc về các nút hành động khác
                if any(ex in t for ex in excluded_action_words):
                    continue

                for kw in norm_keywords:
                    if is_keyword_match(t, kw):
                        detected_gates[gate_id] = {
                            "gate": gate,
                            "center": item["center"],
                            "score": item["score"],
                            "text_raw": item["text_raw"]
                        }
                        break
                if gate_id in detected_gates:
                    break

        # Chọn cổng có độ ưu tiên cao nhất trong số các cổng phát hiện được
        for gate in gate_priority_list:
            gate_id = gate.get("id", gate.get("name", "unknown"))
            if gate_id in detected_gates:
                match_info = detected_gates[gate_id]
                return match_info["gate"], match_info["center"], match_info["text_raw"], match_info["score"]

        return None, None, "", 0

    def find_ki_ngo(self, detected_items, ki_ngo_choices):
        """
        Quét tìm các lựa chọn Kỳ Ngộ (Lắng nghe tiếng sấm, Cẩn thận thu hái, Hứng lấy linh nhũ).
        """
        for choice in ki_ngo_choices:
            c_id = choice.get("id", choice.get("name", "unknown"))
            keywords = choice.get("keywords", [choice.get("name", ""), c_id])
            if isinstance(keywords, str):
                keywords = [keywords]
            norm_keywords = [normalize_vietnamese_text(kw) for kw in keywords]

            for item in detected_items:
                t = item["text_norm"]
                for kw in norm_keywords:
                    if is_keyword_match(t, kw):
                        return choice, item["center"], item["text_raw"], item["score"]

        return None, None, "", 0

