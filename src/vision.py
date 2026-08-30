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

        # Lấy offset của màn hình (nếu có)
        monitor_left = 0
        monitor_top = 0
        if self._sct is not None and len(self._sct.monitors) > 0:
            m = self._sct.monitors[1] if len(self._sct.monitors) > 1 else self._sct.monitors[0]
            monitor_left = m.get("left", 0)
            monitor_top = m.get("top", 0)

        detected_items = []
        for item in ocr_results:
            if not item or len(item) < 3:
                continue
            box, text, score = item[0], item[1], item[2]
            if not text:
                continue

            try:
                score_val = float(score)
            except (ValueError, TypeError):
                score_val = 0.0

            if score_val < min_score:
                continue
            
            # Tính tọa độ tâm của khối chữ từ 4 đỉnh: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            try:
                pts = np.array(box, dtype=np.int32)
                center_x = int(np.mean(pts[:, 0])) + monitor_left
                center_y = int(np.mean(pts[:, 1])) + monitor_top
            except Exception:
                continue
            
            text_norm = normalize_vietnamese_text(text)
            
            detected_items.append({
                "text_raw": text,
                "text_norm": text_norm,
                "center": (center_x, center_y),
                "box": pts,
                "score": score_val
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

    def find_matching_button(self, detected_items, keywords, exclude_words=None, prioritize_bottom=True):
        """
        Tìm nút bấm chính xác, phân biệt giữa 'Nút Bấm' (button) và 'Văn Bản Hiển Thị' (embed/chat text).
        
        Quy tắc lọc thông minh:
        1. Loại trừ các khối chữ chứa từ khóa của tiêu đề tin nhắn (ví dụ: 'lich luyen', 'hoan tat', 'tong phan thuong').
        2. Kiểm tra độ dài: Nút bấm chỉ là nhãn ngắn (1-3 từ), không phải câu văn dài.
        3. Ưu tiên nút ở dưới cùng (bottom-up): Trên Discord, các nút bấm component luôn nằm ở đáy tin nhắn.
        """
        if isinstance(keywords, str):
            keywords = [keywords]

        norm_keywords = [normalize_vietnamese_text(kw) for kw in keywords]
        
        default_excludes = [
            "lich", "luyen", "hoan tat", "ket qua", "thong bao", 
            "doi thu", "da thuc hien", "the luc", "tong phan thuong", 
            "sinh menh", "diem tinh thong", "tu vi", "chien thang"
        ]
        if exclude_words is None:
            exclude_words = default_excludes
        else:
            exclude_words = list(set(default_excludes + [normalize_vietnamese_text(w) for w in exclude_words]))

        candidates = []
        for item in detected_items:
            t = item["text_norm"]
            
            # 1. Bỏ qua nếu là câu văn/nội dung tin nhắn
            if any(ex in t for ex in exclude_words):
                continue
            
            tokens = t.split()
            for kw in norm_keywords:
                kw_tokens = kw.split()
                # Khớp nếu chuỗi chứa từ khóa và không phải câu văn dài (số từ <= số từ của kw + 1)
                if is_keyword_match(t, kw) and len(tokens) <= len(kw_tokens) + 1:
                    candidates.append(item)
                    break

        if not candidates:
            return None, 0, ""

        # Nếu có nhiều kết quả, chọn khối chữ nằm thấp nhất trên màn hình (tọa độ Y lớn nhất)
        if prioritize_bottom:
            candidates.sort(key=lambda c: c["center"][1], reverse=True)

        best = candidates[0]
        return best["center"], best["score"], best["text_raw"]

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

