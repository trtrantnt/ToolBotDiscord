import time
import ctypes
import keyboard
import threading
from src.vision import VisionManager
from src.clicker import ClickerManager

# Danh sách 8 cổng và thứ tự ưu tiên mặc định:
# 1. Sinh -> 2. Khai -> 3. Hưu -> 4. Cảnh -> 5. Kinh -> 6. Đỗ -> 7. Thương -> 8. Tử
DEFAULT_GATE_PRIORITY = [
    {
        "id": "sinh",
        "name": "Sinh Môn",
        "templates": ["gates/sinh.png", "sinh.png", "gate_sinh.png", "cong_sinh.png", "Sinh.png", "Sinh Môn.png"]
    },
    {
        "id": "khai",
        "name": "Khai Môn",
        "templates": ["gates/khai.png", "khai.png", "gate_khai.png", "cong_khai.png", "Khai.png", "Khai Môn.png"]
    },
    {
        "id": "huu",
        "name": "Hưu Môn",
        "templates": ["gates/huu.png", "huu.png", "gate_huu.png", "cong_huu.png", "Hưu.png", "Hưu Môn.png"]
    },
    {
        "id": "canh",
        "name": "Cảnh Môn",
        "templates": ["gates/canh.png", "canh.png", "gate_canh.png", "cong_canh.png", "Cảnh.png", "Cảnh Môn.png"]
    },
    {
        "id": "kinh",
        "name": "Kinh Môn",
        "templates": ["gates/kinh.png", "kinh.png", "gate_kinh.png", "cong_kinh.png", "Kinh.png", "Kinh Môn.png"]
    },
    {
        "id": "do",
        "name": "Đỗ Môn",
        "templates": ["gates/do.png", "do.png", "gate_do.png", "cong_do.png", "Đỗ.png", "Đỗ Môn.png"]
    },
    {
        "id": "thuong",
        "name": "Thương Môn",
        "templates": ["gates/thuong.png", "thuong.png", "gate_thuong.png", "cong_thuong.png", "Thương.png", "Thương Môn.png"]
    },
    {
        "id": "tu",
        "name": "Tử Môn",
        "templates": ["gates/tu.png", "tu.png", "gate_tu.png", "cong_tu.png", "Tử.png", "Tử Môn.png"]
    }
]

# Các lựa chọn Kỳ Ngộ (Ải 1 và Ải 3)
DEFAULT_KI_NGO_CHOICES = [
    {
        "id": "lang_nghe_tieng_sam",
        "name": "Lắng nghe tiếng sấm",
        "templates": ["ki_ngo/lang_nghe_tieng_sam.png", "lang_nghe_tieng_sam.png", "tieng_sam.png"]
    },
    {
        "id": "can_than_thu_hai",
        "name": "Cẩn thận thu hái",
        "templates": ["ki_ngo/can_than_thu_hai.png", "can_than_thu_hai.png", "thu_hai.png"]
    },
    {
        "id": "hung_lay_linh_nhu",
        "name": "Hứng lấy linh nhũ",
        "templates": ["ki_ngo/hung_lay_linh_nhu.png", "hung_lay_linh_nhu.png", "linh_nhu.png"]
    }
]

# Các nút hành động chính
DEFAULT_ACTION_TEMPLATES = {
    "start": ["start.png", "bat_dau.png", "Start.png"],
    "khai_chien": ["khai_chien.png", "KhaiChien.png", "actions/khai_chien.png"],
    "tiep_tuc": ["tiep_tuc.png", "TiepTuc.png", "actions/tiep_tuc.png"],
    "tiep_tuc_khai_pha": [
        "tiep_tuc_khai_pha.png", 
        "tiep_tuc_kham_pha.png", 
        "TiepTucKhaiPha.png", 
        "TiepTucKhamPha.png", 
        "actions/tiep_tuc_khai_pha.png",
        "actions/tiep_tuc_kham_pha.png"
    ],
    "chien_tiep": ["chien_tiep.png", "ChienTiep.png", "actions/chien_tiep.png"]
}

# Các mẫu phát hiện thông báo lỗi
DEFAULT_ERROR_TEMPLATES = ["loi.png", "error.png", "actions/loi.png"]

class AutoClickerController:
    def __init__(self, config):
        self.config = config
        self.vision = VisionManager(templates_dir=config.get("templates_dir", "templates"))
        self.clicker = ClickerManager()
        self.running = False
        
        self.scan_interval = config.get("scan_interval", 0.8)
        self.threshold = config.get("confidence_threshold", 0.8)
        self.stop_hotkey = config.get("stop_hotkey", "q")
        self.total_stages = config.get("total_stages", 5)
        self.retry_limit = config.get("retry_limit", 4)
        self.auto_scroll_after_seconds = config.get("auto_scroll_after_seconds", 6.0)
        self.max_idle_timeout = config.get("max_idle_timeout", 45.0)
        self.anti_hover = config.get("anti_hover", True)
        self.auto_repeat = config.get("auto_repeat", True)
        self.delay_between_stages = config.get("delay_between_stages", 2.5)
        self.delay_between_runs = config.get("delay_between_runs", 4.0)

        # Cấu hình danh sách cổng ưu tiên & mẫu ảnh
        self.gate_priority = config.get("gate_priority", DEFAULT_GATE_PRIORITY)
        self.ki_ngo_choices = config.get("ki_ngo_choices", DEFAULT_KI_NGO_CHOICES)
        self.action_templates = config.get("action_templates", DEFAULT_ACTION_TEMPLATES)
        self.error_templates = config.get("error_templates", DEFAULT_ERROR_TEMPLATES)
        
        self._build_candidates()

    def _build_candidates(self):
        """
        Chuẩn hóa danh sách các cổng và kỳ ngộ để tìm kiếm hình ảnh nhanh.
        """
        self.gate_candidates = []
        for gate in self.gate_priority:
            gate_id = gate.get("id", gate.get("name", "unknown"))
            gate_name = gate.get("name", gate_id)
            templates = gate.get("templates", [f"gates/{gate_id}.png", f"{gate_id}.png"])
            if isinstance(templates, str):
                templates = [templates]
            self.gate_candidates.append({
                "id": gate_id,
                "name": gate_name,
                "templates": templates
            })

        self.ki_ngo_candidates = []
        for choice in self.ki_ngo_choices:
            c_id = choice.get("id", choice.get("name", "unknown"))
            c_name = choice.get("name", c_id)
            templates = choice.get("templates", [f"ki_ngo/{c_id}.png", f"{c_id}.png"])
            if isinstance(templates, str):
                templates = [templates]
            self.ki_ngo_candidates.append({
                "id": c_id,
                "name": c_name,
                "templates": templates
            })

    def sleep_check(self, seconds, step=0.1):
        """
        Sleep có thể bị ngắt ngay lập tức khi self.running = False (người dùng bấm phím tắt dừng).
        """
        elapsed = 0.0
        while elapsed < seconds and self.running:
            time.sleep(min(step, seconds - elapsed))
            elapsed += step
        return self.running

    def show_alert(self, message, title="Cảnh báo Bí Cảnh", is_error=True):
        """
        Hiển thị hộp thoại cảnh báo trên Windows (MessageBoxW).
        """
        print(f"\n[ALERT] {title}: {message}")
        flags = 0x10 if is_error else 0x40  # 0x10 = MB_ICONERROR, 0x40 = MB_ICONINFORMATION
        try:
            ctypes.windll.user32.MessageBoxW(0, message, title, flags | 0x10000)
        except Exception as e:
            print(f"Không thể hiển thị MessageBox: {e}")

    def start(self):
        print("\n" + "="*60)
        print("🚀 BẮT ĐẦU CHẠY AUTO ĐI BÍ CẢNH - PHIÊN BẢN CHỐNG LAG TỰ THÍCH ỨNG")
        print(f"👉 Số ải mỗi vòng: {self.total_stages}")
        print(f"👉 Thứ tự ưu tiên cổng: Sinh > Khai > Hưu > Cảnh > Kinh > Đỗ > Thương > Tử")
        print(f"🛡️ Tính năng: Anti-Hover, Auto-Scroll khi trôi tin nhắn, Xử lý lỗi tự động")
        print(f"👉 Nhấn '{self.stop_hotkey}' bất kỳ lúc nào để DỪNG tool.")
        print("="*60 + "\n")
        
        self.running = True
        threading.Thread(target=self._hotkey_listener, daemon=True).start()
        self._run_smart_state_loop()

    def stop(self):
        if self.running:
            print("\n🛑 Đang dừng Bot...")
            self.running = False

    def _hotkey_listener(self):
        try:
            keyboard.wait(self.stop_hotkey)
            self.stop()
        except Exception as e:
            print(f"Lỗi listener phím tắt: {e}")

    def _get_template_list(self, key):
        """Lấy danh sách file ảnh mẫu từ action_templates hoặc trả về danh sách chứa key"""
        tpls = self.action_templates.get(key, [key])
        if isinstance(tpls, str):
            tpls = [tpls]
        return tpls

    def _detect_screen_state(self):
        """
        Quét toàn diện màn hình và nhận diện trạng thái hiện tại.
        Trả về tuple: (state_type, coords, display_name, templates_matched)
        """
        # 1. Kiểm tra bảng báo lỗi Discord (loi.png)
        for err_tpl in self.error_templates:
            center, conf = self.vision.find_template_on_screen(err_tpl, threshold=self.threshold)
            if center:
                return ("ERROR", center, "Thông báo lỗi Discord", [err_tpl])

        # 2. Kiểm tra nút Chiến Tiếp (Ưu tiên cao - kết thúc vòng)
        for tpl in self._get_template_list("chien_tiep"):
            center, conf = self.vision.find_template_on_screen(tpl, threshold=self.threshold)
            if center:
                return ("CHIEN_TIEP", center, "Chiến Tiếp", [tpl])

        # 3. Kiểm tra nút Tiếp Tục Khai Phá (Ải 2 & Ải 4)
        for tpl in self._get_template_list("tiep_tuc_khai_pha"):
            center, conf = self.vision.find_template_on_screen(tpl, threshold=self.threshold)
            if center:
                return ("TIEP_TUC_KHAI_PHA", center, "Tiếp Tục Khai Phá", [tpl])

        # 4. Kiểm tra nút Tiếp Tục (Ải 1 & Ải 3 sau Kỳ Ngộ)
        for tpl in self._get_template_list("tiep_tuc"):
            center, conf = self.vision.find_template_on_screen(tpl, threshold=self.threshold)
            if center:
                return ("TIEP_TUC", center, "Tiếp Tục", [tpl])

        # 5. Kiểm tra nút Khai Chiến (Ải 2, 4, 5)
        for tpl in self._get_template_list("khai_chien"):
            center, conf = self.vision.find_template_on_screen(tpl, threshold=self.threshold)
            if center:
                return ("KHAI_CHIEN", center, "Khai Chiến", [tpl])

        # 6. Kiểm tra các nút Kỳ Ngộ (Lắng nghe tiếng sấm / Cẩn thận thu hái / Hứng lấy linh nhũ)
        ki_ngo_search_list = [(c, c["templates"]) for c in self.ki_ngo_candidates]
        matched_choice, coords, conf = self.vision.find_first_matching_template(ki_ngo_search_list, threshold=self.threshold)
        if matched_choice and coords:
            return ("KI_NGO", coords, matched_choice["name"], matched_choice["templates"])

        # 7. Kiểm tra các Cổng Bát Môn theo thứ tự ưu tiên (Sinh > Khai > Hưu > Cảnh > Kinh > Đỗ > Thương > Tử)
        gate_search_list = [(g, g["templates"]) for g in self.gate_candidates]
        matched_gate, coords, conf = self.vision.find_first_matching_template(gate_search_list, threshold=self.threshold)
        if matched_gate and coords:
            return ("GATE", coords, matched_gate["name"], matched_gate["templates"])

        # 8. Kiểm tra nút Bắt Đầu
        for tpl in self._get_template_list("start"):
            center, conf = self.vision.find_template_on_screen(tpl, threshold=self.threshold)
            if center:
                return ("START", center, "Bắt Đầu", [tpl])

        return (None, None, None, None)

    def _run_smart_state_loop(self):
        """
        Vòng lặp Máy Trạng Thái Tự Thích Ứng (Smart State Machine).
        Tự động nhận diện trạng thái, tự cuộn trang khi bị trôi tin nhắn và tự phục hồi khi bot lag.
        """
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
                state, coords, name, templates = self._detect_screen_state()

                if state is not None:
                    # Đã phát hiện thấy trạng thái hợp lệ trên màn hình
                    last_action_time = time.time()
                    last_scroll_time = time.time()

                    # Xử lý kiểm tra trùng lặp thao tác (Backoff khi Discord đang xử lý)
                    if state == last_clicked_state:
                        consecutive_same_state_count += 1
                        if consecutive_same_state_count > self.retry_limit:
                            self.show_alert(
                                f"Đã click {self.retry_limit} lần nút [{name}] nhưng giao diện không chuyển đổi.\n"
                                f"Có thể do hết thể lực hoặc Discord bị mất kết nối.",
                                f"Cảnh báo kẹt giao diện"
                            )
                            self.stop()
                            break

                        # Khi Discord lag, tăng nhẹ thời gian chờ trước khi click lại (Backoff)
                        backoff_wait = min(4.0, 1.8 + consecutive_same_state_count * 0.6)
                        print(f"⏳ Giao diện chưa chuyển sau khi bấm [{name}], đang chờ Discord xử lý ({backoff_wait:.1f}s)...")
                        if not self.sleep_check(backoff_wait):
                            break
                    else:
                        consecutive_same_state_count = 0

                    last_clicked_state = state

                    # Thực hiện click hành động tương ứng với trạng thái
                    stage_str = f"[Ải {current_stage}/{self.total_stages}]"
                    
                    if state == "ERROR":
                        print(f"\n⚠️ {stage_str} Phát hiện thông báo lỗi của Discord. Đang click đóng lỗi...")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        self.sleep_check(1.5)
                        continue

                    elif state == "START":
                        print(f"\n🚀 Bấm nút [Bắt Đầu] để vào Bí Cảnh...")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        current_stage = 1
                        self.sleep_check(self.delay_between_stages)

                    elif state == "GATE":
                        print(f"\n🚪 {stage_str} Đã chọn cổng ưu tiên: [{name}]")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        self.sleep_check(self.delay_between_stages)

                    elif state == "KI_NGO":
                        print(f"\n🔮 {stage_str} [Kỳ Ngộ] Đã chọn: [{name}]")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        self.sleep_check(self.delay_between_stages)

                    elif state == "KHAI_CHIEN":
                        print(f"\n⚔️ {stage_str} Đã bấm [Khai Chiến]. Đang chờ kết quả trận đấu...")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        # Đợi bot xử lý chiến đấu (dynamic check)
                        self.sleep_check(3.0)

                    elif state == "TIEP_TUC":
                        print(f"\n➡️ {stage_str} Đã bấm [Tiếp Tục]. Chuẩn bị sang Ải tiếp theo...")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        current_stage = min(self.total_stages, current_stage + 1)
                        self.sleep_check(self.delay_between_stages)

                    elif state == "TIEP_TUC_KHAI_PHA":
                        print(f"\n➡️ {stage_str} Đã bấm [Tiếp Tục Khai Phá]. Chuẩn bị sang Ải tiếp theo...")
                        self.clicker.move_and_click(coords[0], coords[1], human_like=True, move_away=self.anti_hover)
                        current_stage = min(self.total_stages, current_stage + 1)
                        self.sleep_check(self.delay_between_stages)

                    elif state == "CHIEN_TIEP":
                        print(f"\n🏆 [Ải 5/5] Đã bấm [Chiến Tiếp] - HOÀN THÀNH XUẤT SẮC VÒNG {run_count}!")
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
                    # Không tìm thấy trạng thái nào trên màn hình hiện tại
                    idle_time = time.time() - last_action_time
                    scroll_idle_time = time.time() - last_scroll_time

                    # Tự động cuộn trang xuống dưới nếu quá auto_scroll_after_seconds (trôi tin nhắn)
                    if scroll_idle_time >= self.auto_scroll_after_seconds:
                        print("📜 Đang quét tìm nút... (Tự động cuộn màn hình xuống tin nhắn mới nhất)")
                        self.clicker.scroll_down(300)
                        last_scroll_time = time.time()

                    # Báo lỗi nếu quá max_idle_timeout mà không thấy bất kỳ nút nào
                    if idle_time >= self.max_idle_timeout:
                        self.show_alert(
                            f"Không nhận diện được nút nào sau {self.max_idle_timeout:.0f}s.\n"
                            f"Vui lòng kiểm tra lại cửa sổ Discord và ảnh mẫu trong thư mục templates.",
                            "Hết thời gian chờ"
                        )
                        self.stop()
                        break

                    # Nghỉ ngắn giữa các lần quét
                    if not self.sleep_check(self.scan_interval):
                        break

        except Exception as e:
            print(f"❌ Đã xảy ra lỗi ngoại lệ: {e}")
            self.show_alert(f"Đã xảy ra lỗi ngoại lệ trong quá trình chạy:\n{e}", "Lỗi ngoại lệ")
        finally:
            self.running = False
            print("\nBot đã dừng hoạt động hoàn toàn.")



