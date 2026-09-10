import time
import ctypes
import keyboard
import threading
from src.vision import VisionManager
from src.clicker import ClickerManager
from src.overlay import FloatingStopButton

# Danh sách 8 cổng và thứ tự ưu tiên mặc định:
# 1. Sinh -> 2. Khai -> 3. Hưu -> 4. Cảnh -> 5. Kinh -> 6. Đỗ -> 7. Thương -> 8. Tử
DEFAULT_GATE_PRIORITY = [
    {"id": "sinh", "name": "Sinh Môn", "keywords": ["sinh mon", "sinh"]},
    {"id": "khai", "name": "Khai Môn", "keywords": ["khai mon", "khai"]},
    {"id": "huu", "name": "Hưu Môn", "keywords": ["huu mon", "huu"]},
    {"id": "canh", "name": "Cảnh Môn", "keywords": ["canh mon", "canh"]},
    {"id": "kinh", "name": "Kinh Môn", "keywords": ["kinh mon", "kinh"]},
    {"id": "do", "name": "Đỗ Môn", "keywords": ["do mon", "d mon", "do"]},
    {"id": "thuong", "name": "Thương Môn", "keywords": ["thuong mon", "thudng mon", "thuong"]},
    {"id": "tu", "name": "Tử Môn", "keywords": ["tu mon", "tu"]}
]

# Các lựa chọn Kỳ Ngộ (Ải 1 và Ải 3)
DEFAULT_KI_NGO_CHOICES = [
    {
        "id": "lang_nghe_tieng_sam",
        "name": "Lắng nghe tiếng sấm",
        "keywords": ["lang nghe tieng sam", "tieng sam", "lang nghe"]
    },
    {
        "id": "can_than_thu_hai",
        "name": "Cẩn thận thu hái",
        "keywords": ["can than thu hai", "thu hai", "can than"]
    },
    {
        "id": "hung_lay_linh_nhu",
        "name": "Hứng lấy linh nhũ",
        "keywords": ["hung lay linh nhu", "hing lay linh nhu", "linh nhu"]
    }
]

# Các nút hành động chính cho Chức năng 1 (Đi Bí Cảnh)
DEFAULT_ACTION_KEYWORDS = {
    "start": ["bat dau", "start"],
    "khai_chien": ["khai chien"],
    "tiep_tuc_khai_pha": ["tiep tuc khai pha", "tiep tuc kham pha", "khai pha", "kham pha"],
    "tiep_tuc": ["tiep tuc"],
    "chien_tiep": ["chien tiep"]
}

# Các mẫu phát hiện thông báo lỗi
DEFAULT_ERROR_KEYWORDS = [
    "tuong tac nay khong thanh cong",
    "khong thanh cong",
    "that bai",
    "het the luc",
    "khong the"
]

def show_windows_alert(message, title="Cảnh báo Bot Discord", is_error=True):
    """Hiển thị hộp thoại cảnh báo trên Windows (MessageBoxW)"""
    print(f"\n[ALERT] {title}: {message}")
    flags = 0x10 if is_error else 0x40  # 0x10 = MB_ICONERROR, 0x40 = MB_ICONINFORMATION
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, flags | 0x10000)
    except Exception as e:
        print(f"Không thể hiển thị MessageBox: {e}")

# ==============================================================================
# CHỨC NĂNG 1: TỰ ĐỘNG ĐI BÍ CẢNH (5 ẢI BÁT MÔN & KỲ NGỘ) - HOÀN TOÀN KHÔNG CÓ X10
# ==============================================================================
class DungeonController:
    def __init__(self, config, vision=None):
        self.config = config
        self.vision = vision if vision is not None else VisionManager()
        self.clicker = ClickerManager()
        self.running = False
        self.overlay = FloatingStopButton(on_stop_callback=self.stop)
        
        self.scan_interval = config.get("scan_interval", 0.8)
        self.ocr_min_score = config.get("ocr_min_score", 0.6)
        self.stop_hotkey = config.get("stop_hotkey", "q")
        self.total_stages = config.get("total_stages", 5)
        self.retry_limit = config.get("retry_limit", 4)
        self.enable_auto_scroll = config.get("enable_auto_scroll", False)
        self.auto_scroll_after_seconds = config.get("auto_scroll_after_seconds", 15.0)
        self.max_idle_timeout = config.get("max_idle_timeout", 45.0)
        self.anti_hover = config.get("anti_hover", True)
        self.auto_repeat = config.get("auto_repeat", True)
        self.delay_between_stages = config.get("delay_between_stages", 2.5)
        self.delay_between_runs = config.get("delay_between_runs", 4.0)

        # Cấu hình danh sách cổng ưu tiên & từ khóa OCR
        self.gate_priority = config.get("gate_priority", DEFAULT_GATE_PRIORITY)
        self.ki_ngo_choices = config.get("ki_ngo_choices", DEFAULT_KI_NGO_CHOICES)
        self.action_keywords = config.get("action_keywords", DEFAULT_ACTION_KEYWORDS)
        self.error_keywords = config.get("error_keywords", DEFAULT_ERROR_KEYWORDS)

    def sleep_check(self, seconds, step=0.1):
        elapsed = 0.0
        while elapsed < seconds and self.running:
            time.sleep(min(step, seconds - elapsed))
            elapsed += step
        return self.running

    def start(self):
        print("\n" + "="*60)
        print("🚀 [CHỨC NĂNG 1] BẮT ĐẦU AUTO ĐI BÍ CẢNH (BOT UYÊN SƯ MUỘI)")
        print(f"👉 Số ải mỗi vòng: {self.total_stages}")
        print(f"👉 Thứ tự ưu tiên cổng: Sinh > Khai > Hưu > Cảnh > Kinh > Đỗ > Thương > Tử")
        print(f"🛡️ Công nghệ: Quét chữ OCR Tiếng Việt (RapidOCR), Anti-Hover, Auto-Scroll")
        print(f"👉 Dừng tool: Bấm nút đỏ '🛑 DỪNG TOOL' trên màn hình hoặc nhấn phím 'q' / 'ESC'.")
        print("="*60 + "\n")
        
        self.running = True
        self.overlay.show()
        threading.Thread(target=self._hotkey_listener, daemon=True).start()
        self._run_smart_state_loop()

    def stop(self):
        if self.running:
            print("\n🛑 Đang dừng Bot...")
            self.running = False
            self.overlay.close()

    def _hotkey_listener(self):
        try:
            keyboard.add_hotkey(self.stop_hotkey, self.stop)
            keyboard.add_hotkey("esc", self.stop)
            while self.running:
                time.sleep(0.2)
        except Exception as e:
            print(f"Lỗi listener phím tắt: {e}")

    def _detect_screen_state(self):
        """
        Quét toàn diện màn hình bằng OCR và nhận diện trạng thái Bí Cảnh.
        Trả về tuple: (state_type, coords, display_name, raw_text)
        """
        detected_items = self.vision.scan_screen_text(min_score=self.ocr_min_score)
        if not detected_items:
            return None, None, None, None

        # 1. Kiểm tra thông báo lỗi Discord (chỉ xét trong vùng chat x >= 280, bỏ qua thanh kênh sidebar)
        chat_items = [it for it in detected_items if it.get("center", (0, 0))[0] >= 280 and "#" not in it.get("text_raw", "")]
        center, score, text_raw = self.vision.find_matching_text(chat_items, self.error_keywords)
        if center:
            return ("ERROR", center, f"Lỗi Discord: {text_raw}", text_raw)

        # 2. Kiểm tra nút Chiến Tiếp (Ưu tiên cao - kết thúc vòng)
        center, score, text_raw = self.vision.find_matching_button(detected_items, self.action_keywords.get("chien_tiep", ["chien tiep"]))
        if center:
            return ("CHIEN_TIEP", center, "Chiến Tiếp", text_raw)

        # 3. Kiểm tra nút Tiếp Tục Khai Phá / Khám Phá (Ải 2 & Ải 4)
        center, score, text_raw = self.vision.find_matching_button(detected_items, self.action_keywords.get("tiep_tuc_khai_pha", ["tiep tuc khai pha", "tiep tuc kham pha"]))
        if center:
            return ("TIEP_TUC_KHAI_PHA", center, "Tiếp Tục Khai Phá", text_raw)

        # 4. Kiểm tra nút Tiếp Tục (Ải 1 & Ải 3 sau Kỳ Ngộ)
        center, score, text_raw = self.vision.find_matching_button(detected_items, self.action_keywords.get("tiep_tuc", ["tiep tuc"]))
        if center:
            return ("TIEP_TUC", center, "Tiếp Tục", text_raw)

        # 5. Kiểm tra nút Khai Chiến (Ải 2, 4, 5)
        center, score, text_raw = self.vision.find_matching_button(detected_items, self.action_keywords.get("khai_chien", ["khai chien"]))
        if center:
            return ("KHAI_CHIEN", center, "Khai Chiến", text_raw)

        # 6. Kiểm tra các nút Kỳ Ngộ (Lắng nghe tiếng sấm / Cẩn thận thu hái / Hứng lấy linh nhũ)
        choice, center, text_raw, score = self.vision.find_ki_ngo(detected_items, self.ki_ngo_choices)
        if center and choice:
            return ("KI_NGO", center, choice["name"], text_raw)

        # 7. Kiểm tra các Cổng Bát Môn theo thứ tự ưu tiên (Sinh > Khai > Hưu > Cảnh > Kinh > Đỗ > Thương > Tử)
        gate, center, text_raw, score = self.vision.find_gate_by_priority(detected_items, self.gate_priority)
        if center and gate:
            return ("GATE", center, gate["name"], text_raw)

        # 8. Kiểm tra nút Bắt Đầu
        center, score, text_raw = self.vision.find_matching_button(detected_items, self.action_keywords.get("start", ["bat dau", "start"]))
        if center:
            return ("START", center, "Bắt Đầu", text_raw)

        return None, None, None, None

    def _run_smart_state_loop(self):
        run_count = 1
        current_stage = 1
        last_action_time = time.time()
        last_scroll_time = time.time()
        last_clicked_state = None
        consecutive_same_state_count = 0

        print(f"\n{'#'*60}")
        print(f"👉 BẮT ĐẦU VÒNG BÍ CẢNH SỐ {run_count}")
        print(f"{'#'*60}")

        try:
            while self.running:
                state, coords, name, raw_text = self._detect_screen_state()

                if state is not None:
                    last_action_time = time.time()
                    last_scroll_time = time.time()

                    if state == last_clicked_state:
                        consecutive_same_state_count += 1
                        if consecutive_same_state_count > self.retry_limit:
                            if state == "ERROR":
                                show_windows_alert(
                                    f"Phát hiện thông báo lỗi từ Discord lặp lại {self.retry_limit} lần liên tiếp.\n"
                                    f"Có thể do hết thể lực, hết lượt đi Bí Cảnh hoặc Discord bị mất kết nối.",
                                    "Lỗi Discord Bot"
                                )
                            else:
                                show_windows_alert(
                                    f"Đã click {self.retry_limit} lần nút [{name}] nhưng giao diện không chuyển đổi.\n"
                                    f"Có thể do hết thể lực hoặc Discord bị mất kết nối.",
                                    "Cảnh báo kẹt giao diện"
                                )
                            self.stop()
                            break

                        backoff_wait = min(4.5, 2.0 + consecutive_same_state_count * 0.8)
                        if state == "ERROR":
                            print(f"⏳ Đang xử lý lỗi Discord (Lần {consecutive_same_state_count}/{self.retry_limit}), chờ {backoff_wait:.1f}s...")
                        else:
                            print(f"⏳ Giao diện chưa chuyển sau khi bấm [{name}] (Lần {consecutive_same_state_count}/{self.retry_limit}), đang chờ Discord xử lý ({backoff_wait:.1f}s)...")
                        
                        if not self.sleep_check(backoff_wait):
                            break
                    else:
                        consecutive_same_state_count = 0

                    last_clicked_state = state
                    stage_str = f"[Ải {current_stage}/{self.total_stages}]"
                    
                    if state == "ERROR":
                        print(f"\n⚠️ {stage_str} Phát hiện thông báo lỗi Discord: '{raw_text}'. Đang click đóng lỗi...")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        self.sleep_check(self.delay_between_stages)
                        continue

                    elif state == "START":
                        print(f"\n🚀 OCR tìm thấy nút: '{raw_text}' -> Bấm nút [Bắt Đầu] để vào Bí Cảnh...")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        current_stage = 1
                        self.sleep_check(self.delay_between_stages)

                    elif state == "GATE":
                        print(f"\n🚪 {stage_str} OCR nhận diện cổng: '{raw_text}' -> Chọn cổng ưu tiên: [{name}]")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        self.sleep_check(self.delay_between_stages)

                    elif state == "KI_NGO":
                        print(f"\n🔮 {stage_str} OCR nhận diện Kỳ Ngộ: '{raw_text}' -> Đã chọn: [{name}]")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        self.sleep_check(self.delay_between_stages)

                    elif state == "KHAI_CHIEN":
                        print(f"\n⚔️ {stage_str} OCR tìm thấy nút: '{raw_text}' -> Đã bấm [Khai Chiến]. Đang chờ kết quả trận đấu...")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        self.sleep_check(3.0)

                    elif state == "TIEP_TUC":
                        print(f"\n➡️ {stage_str} OCR tìm thấy nút: '{raw_text}' -> Đã bấm [Tiếp Tục]. Chuẩn bị sang Ải tiếp theo...")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        current_stage = min(self.total_stages, current_stage + 1)
                        self.sleep_check(self.delay_between_stages)

                    elif state == "TIEP_TUC_KHAI_PHA":
                        print(f"\n➡️ {stage_str} OCR tìm thấy nút: '{raw_text}' -> Đã bấm [Tiếp Tục Khai Phá]. Chuẩn bị sang Ải tiếp theo...")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        current_stage = min(self.total_stages, current_stage + 1)
                        self.sleep_check(self.delay_between_stages)

                    elif state == "CHIEN_TIEP":
                        print(f"\n🏆 [Ải 5/5] OCR tìm thấy nút: '{raw_text}' -> Đã bấm [Chiến Tiếp] - HOÀN THÀNH XUẤT SẮC VÒNG {run_count}!")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        
                        run_count += 1
                        current_stage = 1
                        last_clicked_state = None

                        if not self.auto_repeat:
                            print("Chế độ tự động lặp tắt. Kết thúc chương trình.")
                            self.stop()
                            break

                        print(f"⏳ Đang nghỉ {self.delay_between_runs}s trước khi bước vào vòng bí cảnh tiếp theo...")
                        if not self.sleep_check(self.delay_between_runs):
                            break

                        print(f"\n{'#'*60}")
                        print(f"👉 BẮT ĐẦU VÒNG BÍ CẢNH SỐ {run_count}")
                        print(f"{'#'*60}")

                else:
                    idle_time = time.time() - last_action_time
                    scroll_idle_time = time.time() - last_scroll_time

                    if self.enable_auto_scroll and scroll_idle_time >= self.auto_scroll_after_seconds:
                        print("📜 Đang quét tìm nút trên màn hình... (Tự động cuộn màn hình xuống tin nhắn mới nhất)")
                        self.clicker.scroll_down(300)
                        last_scroll_time = time.time()

                    if idle_time >= self.max_idle_timeout:
                        show_windows_alert(
                            f"Không nhận diện được nội dung chữ của nút nào sau {self.max_idle_timeout:.0f}s.\n"
                            f"Vui lòng kiểm tra lại cửa sổ Discord và tin nhắn của bot Uyên Sư Muội.",
                            "Hết thời gian chờ"
                        )
                        self.stop()
                        break

                    if not self.sleep_check(self.scan_interval):
                        break

        except Exception as e:
            print(f"❌ Đã xảy ra lỗi ngoại lệ: {e}")
            show_windows_alert(f"Đã xảy ra lỗi ngoại lệ trong quá trình chạy:\n{e}", "Lỗi ngoại lệ")
        finally:
            self.running = False
            self.overlay.close()
            print("\nBot đã dừng hoạt động hoàn toàn.")

# Alias để tương thích
AutoClickerController = DungeonController

# ==============================================================================
# CHỨC NĂNG 2: AUTO CLICK "⚡ NHANH X10" (TÁCH BIỆT ĐỘC LẬP)
# ==============================================================================
class Fast10xController:
    def __init__(self, config, vision=None):
        self.config = config
        self.vision = vision if vision is not None else VisionManager()
        self.clicker = ClickerManager()
        self.running = False
        self.overlay = FloatingStopButton(on_stop_callback=self.stop)
        
        fast_cfg = config.get("fast_10x", {})
        self.scan_interval = fast_cfg.get("scan_interval", 0.5)
        self.keywords = fast_cfg.get("keywords", ["nhanh x10", "nhanhx10", "nhanh 10"])
        self.delay_after_click = fast_cfg.get("delay_after_click", 1.2)
        
        self.stop_hotkey = config.get("stop_hotkey", "q")
        self.ocr_min_score = config.get("ocr_min_score", 0.6)
        self.anti_hover = config.get("anti_hover", True)
        self.enable_auto_scroll = config.get("enable_auto_scroll", False)
        self.auto_scroll_after_seconds = config.get("auto_scroll_after_seconds", 15.0)

    def sleep_check(self, seconds, step=0.1):
        elapsed = 0.0
        while elapsed < seconds and self.running:
            time.sleep(min(step, seconds - elapsed))
            elapsed += step
        return self.running

    def start(self):
        print("\n" + "="*60)
        print("⚡ [CHỨC NĂNG 2] BẮT ĐẦU AUTO CLICK 'NHANH X10' (TĂNG TỐC CHIẾN ĐẤU)")
        print(f"👉 Từ khóa nút: {self.keywords}")
        print(f"🛡️ Phân biệt nút bấm: Tự động bỏ qua thanh kênh sidebar (#) và tiêu đề kết quả")
        print(f"👉 Dừng tool: Bấm nút đỏ '🛑 DỪNG TOOL' trên màn hình hoặc nhấn phím 'q' / 'ESC'.")
        print("="*60 + "\n")
        
        self.running = True
        self.overlay.show()
        threading.Thread(target=self._hotkey_listener, daemon=True).start()
        self._run_fast_loop()

    def stop(self):
        if self.running:
            print("\n🛑 Đang dừng chức năng Nhanh x10...")
            self.running = False
            self.overlay.close()

    def _hotkey_listener(self):
        try:
            keyboard.add_hotkey(self.stop_hotkey, self.stop)
            keyboard.add_hotkey("esc", self.stop)
            while self.running:
                time.sleep(0.2)
        except Exception as e:
            print(f"Lỗi listener phím tắt: {e}")

    def _run_fast_loop(self):
        click_count = 0
        last_click_time = time.time()
        last_scroll_time = time.time()
        last_disabled_log = 0.0

        try:
            while self.running:
                detected_items = self.vision.scan_screen_text(min_score=self.ocr_min_score)

                if detected_items:
                    # 1. Tìm nút Nhanh x10 ĐANG HOẠT ĐỘNG (only_enabled=True, loại trừ thanh kênh x < 280 và ký tự '#')
                    pos, score, text_raw = self.vision.find_matching_button(
                        detected_items, 
                        self.keywords,
                        exclude_words=["lich", "luyen", "hoan tat", "ket qua", "thong bao", "doi thu", "da thuc hien", "the luc", "tong phan thuong", "luan dao", "van dap"],
                        prioritize_bottom=True,
                        min_x=280,
                        only_enabled=True
                    )
                    if pos:
                        click_count += 1
                        last_click_time = time.time()
                        last_scroll_time = time.time()
                        print(f"⚡ [Lần {click_count}] OCR phát hiện đúng NÚT BẤM (Sáng/Kích hoạt): '{text_raw}' tại {pos} -> ĐÃ CLICK [NHANH X10]!")
                        self.clicker.move_and_click(pos[0], pos[1], human_like=True, move_away=self.anti_hover)
                        if not self.sleep_check(self.delay_after_click):
                            break
                        continue
                    else:
                        # Kiểm tra xem có nút Nhanh x10 nhưng đang bị mờ/vô hiệu hóa không
                        dis_pos, _, dis_raw = self.vision.find_matching_button(
                            detected_items, 
                            self.keywords,
                            exclude_words=["lich", "luyen", "hoan tat", "ket qua", "thong bao", "doi thu", "da thuc hien", "the luc", "tong phan thuong", "luan dao", "van dap"],
                            prioritize_bottom=True,
                            min_x=280,
                            only_enabled=False
                        )
                        if dis_pos and (time.time() - last_disabled_log >= 3.0):
                            print(f"⏳ Phát hiện nút '{dis_raw}' nhưng đang ở trạng thái MỜ / VÔ HIỆU HÓA (Disabled). Đang chờ bot kích hoạt lại...")
                            last_disabled_log = time.time()

                # Nếu chưa thấy nút Nhanh x10
                scroll_idle = time.time() - last_scroll_time
                if self.enable_auto_scroll and scroll_idle >= self.auto_scroll_after_seconds:
                    print("📜 Đang tìm nút [Nhanh x10]... (Tự động cuộn màn hình xuống dưới)")
                    self.clicker.scroll_down(300)
                    last_scroll_time = time.time()

                if not self.sleep_check(self.scan_interval):
                    break

        except Exception as e:
            print(f"❌ Đã xảy ra lỗi ngoại lệ: {e}")
            show_windows_alert(f"Đã xảy ra lỗi ngoại lệ:\n{e}", "Lỗi ngoại lệ")
        finally:
            self.running = False
            self.overlay.close()
            print(f"\nĐã dừng chức năng Nhanh x10. Tổng số lần bấm thành công: {click_count}")

# ==============================================================================
# CHỨC NĂNG 3: AUTO CLICK NÚT TÙY CHỌN THEO TỪ KHÓA & THỜI GIAN CHỜ
# ==============================================================================
class CustomButtonController:
    def __init__(self, config, button_text, delay_seconds=5.0, vision=None):
        self.config = config
        self.vision = vision if vision is not None else VisionManager()
        self.clicker = ClickerManager()
        self.running = False
        self.overlay = FloatingStopButton(on_stop_callback=self.stop)
        
        self.button_text = button_text.strip()
        try:
            self.delay_seconds = max(0.1, float(delay_seconds))
        except Exception:
            self.delay_seconds = 5.0
        
        self.scan_interval = config.get("scan_interval", 0.6)
        self.stop_hotkey = config.get("stop_hotkey", "q")
        self.ocr_min_score = config.get("ocr_min_score", 0.6)
        self.anti_hover = config.get("anti_hover", True)
        self.enable_auto_scroll = config.get("enable_auto_scroll", False)
        self.auto_scroll_after_seconds = config.get("auto_scroll_after_seconds", 15.0)
        self.error_keywords = config.get("error_keywords", DEFAULT_ERROR_KEYWORDS)

    def sleep_check(self, seconds, step=0.1):
        elapsed = 0.0
        while elapsed < seconds and self.running:
            time.sleep(min(step, seconds - elapsed))
            elapsed += step
        return self.running

    def start(self):
        print("\n" + "="*62)
        print("🎯 [CHỨC NĂNG 3] BẮT ĐẦU AUTO CLICK NÚT TÙY CHỌN")
        print(f"👉 Chữ trên nút cần tìm: '{self.button_text}'")
        print(f"⏳ Thời gian chờ giữa 2 lần bấm: {self.delay_seconds} giây")
        print(f"🛡️ Công nghệ: Quét chữ OCR RapidOCR, Pixel-Perfect Click, Anti-Hover")
        print(f"👉 Dừng tool: Bấm nút đỏ '🛑 DỪNG TOOL' trên màn hình hoặc nhấn phím 'q' / 'ESC'.")
        print("="*62 + "\n")
        
        self.running = True
        self.overlay.show()
        threading.Thread(target=self._hotkey_listener, daemon=True).start()
        self._run_custom_loop()

    def stop(self):
        if self.running:
            print(f"\n🛑 Đang dừng chức năng click nút '{self.button_text}'...")
            self.running = False
            self.overlay.close()

    def _hotkey_listener(self):
        try:
            keyboard.add_hotkey(self.stop_hotkey, self.stop)
            keyboard.add_hotkey("esc", self.stop)
            while self.running:
                time.sleep(0.2)
        except Exception as e:
            print(f"Lỗi listener phím tắt: {e}")

    def _run_custom_loop(self):
        click_count = 0
        last_click_time = time.time()
        last_scroll_time = time.time()
        last_disabled_log = 0.0

        try:
            while self.running:
                detected_items = self.vision.scan_screen_text(min_score=self.ocr_min_score)

                if detected_items:
                    # 1. Tìm nút theo chữ người dùng nhập ĐANG HOẠT ĐỘNG (only_enabled=True, loại trừ thanh kênh x < 280)
                    pos, score, text_raw = self.vision.find_matching_button(
                        detected_items, 
                        [self.button_text],
                        prioritize_bottom=True,
                        min_x=280,
                        only_enabled=True
                    )
                    if pos:
                        click_count += 1
                        last_click_time = time.time()
                        last_scroll_time = time.time()
                        print(f"🎯 [Lần {click_count}] OCR phát hiện nút (Sáng/Kích hoạt): '{text_raw}' tại {pos} -> ĐÃ CLICK THÀNH CÔNG!")
                        self.clicker.move_and_click(pos[0], pos[1], human_like=True, move_away=self.anti_hover)
                        
                        print(f"⏳ Đang chờ {self.delay_seconds}s trước lần bấm tiếp theo...")
                        if not self.sleep_check(self.delay_seconds):
                            break
                        continue
                    else:
                        # Kiểm tra xem có nút nhưng đang bị mờ/vô hiệu hóa không
                        dis_pos, _, dis_raw = self.vision.find_matching_button(
                            detected_items, 
                            [self.button_text],
                            prioritize_bottom=True,
                            min_x=280,
                            only_enabled=False
                        )
                        if dis_pos and (time.time() - last_disabled_log >= 3.0):
                            print(f"⏳ Phát hiện nút '{dis_raw}' nhưng đang ở trạng thái MỜ / VÔ HIỆU HÓA (Disabled). Đang chờ mở lại...")
                            last_disabled_log = time.time()

                # Nếu chưa thấy nút
                scroll_idle = time.time() - last_scroll_time
                if self.enable_auto_scroll and scroll_idle >= self.auto_scroll_after_seconds:
                    print(f"📜 Đang tìm nút [{self.button_text}]... (Tự động cuộn màn hình xuống dưới)")
                    self.clicker.scroll_down(300)
                    last_scroll_time = time.time()

                if not self.sleep_check(self.scan_interval):
                    break

        except Exception as e:
            print(f"❌ Đã xảy ra lỗi ngoại lệ: {e}")
            show_windows_alert(f"Đã xảy ra lỗi ngoại lệ:\n{e}", "Lỗi ngoại lệ")
        finally:
            self.running = False
            self.overlay.close()
            print(f"\nĐã dừng chức năng tùy chọn. Tổng số lần bấm nút '{self.button_text}': {click_count}")

