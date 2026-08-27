# Discord Bot Auto Clicker - Đi Bí Cảnh (Uyên Sư Muội)

Tool tự động hóa thao tác click trên giao diện Discord để tự động đi **Bí Cảnh** khi chơi cùng bot **Uyên Sư Muội**.

Công cụ sử dụng thị giác máy tính (**Computer Vision - OpenCV**) kết hợp điều khiển chuột (**PyAutoGUI**) để nhận diện các nút bấm trên màn hình, tự động hoàn thành từng vòng bí cảnh và lặp lại liên tục cho đến khi gặp lỗi hoặc hết thể lực.

---

## 🌟 Tính năng nổi bật

- 🤖 **Máy trạng thái tự thích ứng (Smart State Machine)**: Không chạy cứng theo bước, tự động nhận diện màn hình Discord đang ở trạng thái nào (Cổng, Kỳ ngộ, Khai chiến, Tiếp tục, Chiến tiếp...) để hành động ngay lập tức mà không bao giờ bị lệch nhịp.
- 🛡️ **Cơ chế chống Lag & Tự phục hồi**:
  - **Dynamic State Polling**: Quét động liên tục, bot phản hồi nhanh thì đi tiếp nhanh, bot lag thì kiên nhẫn chờ mà không bị đơ.
  - **Anti-Hover**: Tự động dời chuột sang vùng trống sau khi click để tránh nút bị đổi màu sáng (hover effect), giúp OpenCV nhận diện chính xác 100%.
  - **Auto-Scroll**: Tự động cuộn màn hình xuống dưới nếu tin nhắn mới bị trôi khỏi tầm nhìn.
  - **Xử lý lỗi tự động (`loi.png`)**: Tự động phát hiện và tắt thông báo lỗi của Discord.
- 🚪 **Chọn cổng thông minh (Bát Môn)**: Tự động nhận diện 3 cổng xuất hiện trên Discord và chọn 1 cổng theo thứ tự ưu tiên:
  $$\text{Sinh} \rightarrow \text{Khai} \rightarrow \text{Hưu} \rightarrow \text{Cảnh} \rightarrow \text{Kinh} \rightarrow \text{Đỗ} \rightarrow \text{Thương} \rightarrow \text{Tử}$$
- ⚔️ **Tự động xử lý trọn vẹn 5 Ải Bí Cảnh**:
  - **Ải 1 (Kỳ Ngộ)**: Chọn cổng $\rightarrow$ Chọn Kỳ Ngộ (*"Lắng nghe tiếng sấm"* / *"Cẩn thận thu hái"* / *"Hứng lấy linh nhũ"*) $\rightarrow$ Ấn *Tiếp Tục*.
  - **Ải 2 (Chiến Đấu)**: Chọn cổng $\rightarrow$ Ấn *Khai Chiến* $\rightarrow$ Chờ chiến đấu (5-10s) $\rightarrow$ Ấn *Tiếp Tục Khai Phá*.
  - **Ải 3 (Kỳ Ngộ)**: Chọn cổng $\rightarrow$ Chọn Kỳ Ngộ $\rightarrow$ Ấn *Tiếp Tục*.
  - **Ải 4 (Chiến Đấu)**: Chọn cổng $\rightarrow$ Ấn *Khai Chiến* $\rightarrow$ Chờ chiến đấu (5-10s) $\rightarrow$ Ấn *Tiếp Tục Khai Phá*.
  - **Ải 5 (Chiến Đấu Cuối)**: Chọn cổng $\rightarrow$ Ấn *Khai Chiến* $\rightarrow$ Chờ chiến đấu $\rightarrow$ Ấn *Chiến Tiếp* kết thúc vòng.
- 🔄 **Tự động lặp lại vòng bí cảnh (`auto_repeat`)**: Hoàn thành ải 5 và tự động chuyển sang vòng tiếp theo.
- ⏹️ **Phím tắt dừng khẩn cấp**: Nhấn phím `q` bất kỳ lúc nào để dừng tool ngay lập tức.

---

## 📁 Cấu trúc thư mục

```text
ToolBotDiscord/
├── config.json               # File cấu hình thông số hoạt động của tool
├── main.py                   # File khởi chạy chính của chương trình
├── requirements.txt          # Danh sách các thư viện Python cần thiết
├── README.md                 # Tài liệu hướng dẫn sử dụng
├── src/
│   ├── __init__.py
│   ├── clicker.py            # Module điều khiển chuột và mô phỏng click
│   ├── controller.py         # Module điều khiển luồng 5 ải, xử lý lỗi & vòng lặp
│   └── vision.py             # Module nhận diện hình ảnh OpenCV
└── templates/                # Thư mục chứa các ảnh mẫu nút bấm
    ├── start.png             # Nút "Bắt Đầu"
    ├── khai_chien.png        # Nút "Khai Chiến" (Ải 2, 4, 5)
    ├── tiep_tuc.png          # Nút "Tiếp Tục" (Ải 1, 3 sau khi chọn kỳ ngộ)
    ├── tiep_tuc_khai_pha.png # Nút "Tiếp Tục Khai Phá" (Ải 2, 4)
    ├── chien_tiep.png        # Nút "Chiến Tiếp" (Ải 5 kết thúc vòng)
    ├── gates/                # Thư mục 8 Cổng Bát Môn
    │   ├── sinh.png          # Cổng Sinh Môn (Ưu tiên 1)
    │   ├── khai.png          # Cổng Khai Môn (Ưu tiên 2)
    │   ├── huu.png           # Cổng Hưu Môn  (Ưu tiên 3)
    │   ├── canh.png          # Cổng Cảnh Môn (Ưu tiên 4)
    │   ├── kinh.png          # Cổng Kinh Môn (Ưu tiên 5)
    │   ├── do.png            # Cổng Đỗ Môn   (Ưu tiên 6)
    │   ├── thuong.png        # Cổng Thương Môn (Ưu tiên 7)
    │   └── tu.png            # Cổng Tử Môn   (Ưu tiên 8)
    └── ki_ngo/               # Thư mục các lựa chọn Kỳ Ngộ
        ├── lang_nghe_tieng_sam.png # Nút "Lắng nghe tiếng sấm"
        ├── can_than_thu_hai.png    # Nút "Cẩn thận thu hái"
        └── hung_lay_linh_nhu.png   # Nút "Hứng lấy linh nhũ"
```

---

## ⚙️ Cài đặt

### Yêu cầu hệ thống
- Hệ điều hành: **Windows 10 / 11**
- **Python 3.10+** đã được cài đặt trên máy.

### Các bước cài đặt

1. **Mở Terminal / PowerShell** tại thư mục dự án:
   ```powershell
   cd d:\ToolBotDiscord
   ```
2. **Cài đặt các thư viện phụ thuộc:**
   ```powershell
   pip install -r requirements.txt
   ```

---

## 🔧 Cấu hình (`config.json`)

```json
{
    "scan_interval": 1.0,
    "confidence_threshold": 0.8,
    "stop_hotkey": "q",
    "templates_dir": "templates",
    "total_stages": 5,
    "retry_limit": 3,
    "gate_wait_timeout": 25.0,
    "action_wait_timeout": 25.0,
    "combat_wait_seconds": 7.0,
    "auto_repeat": true,
    "delay_between_stages": 3.0,
    "delay_between_runs": 5.0
}
```

---

## 📸 Danh sách ảnh mẫu cần chụp (Templates)

Dùng **Snipping Tool** (`Win + Shift + S`) cắt sát viền các nút bấm trên Discord và lưu vào đúng vị trí:

### 1. Các nút hành động chính (Lưu tại `templates/`):
- `templates/start.png`: Nút **Bắt Đầu** vào bí cảnh.
- `templates/khai_chien.png`: Nút **Khai Chiến** (khi vào ải 2, 4, 5).
- `templates/tiep_tuc.png`: Nút **Tiếp Tục** (sau khi chọn Kỳ Ngộ ở ải 1, 3).
- `templates/tiep_tuc_khai_pha.png`: Nút **Tiếp Tục Khai Phá** (sau khi thắng ải 2, 4).
- `templates/chien_tiep.png`: Nút **Chiến Tiếp** (sau khi thắng ải 5).

### 2. Các nút Kỳ Ngộ (Lưu tại `templates/ki_ngo/`):
- `templates/ki_ngo/lang_nghe_tieng_sam.png`: Nút **Lắng nghe tiếng sấm**.
- `templates/ki_ngo/can_than_thu_hai.png`: Nút **Cẩn thận thu hái**.
- `templates/ki_ngo/hung_lay_linh_nhu.png`: Nút **Hứng lấy linh nhũ**.

### 3. Ảnh 8 Cổng Bát Môn (Lưu tại `templates/gates/`):
- `templates/gates/sinh.png` (Sinh Môn - Ưu tiên 1)
- `templates/gates/khai.png` (Khai Môn - Ưu tiên 2)
- `templates/gates/huu.png` (Hưu Môn - Ưu tiên 3)
- `templates/gates/canh.png` (Cảnh Môn - Ưu tiên 4)
- `templates/gates/kinh.png` (Kinh Môn - Ưu tiên 5)
- `templates/gates/do.png` (Đỗ Môn - Ưu tiên 6)
- `templates/gates/thuong.png` (Thương Môn - Ưu tiên 7)
- `templates/gates/tu.png` (Tử Môn - Ưu tiên 8)

---

## 🚀 Hướng dẫn vận hành

1. Mở Discord đến khung chat của bot **Uyên Sư Muội** (đảm bảo cửa sổ Discord hiển thị rõ ràng).
2. Mở Terminal và chạy lệnh:
   ```powershell
   python main.py
   ```
3. Bot sẽ tự động thực hiện trọn vẹn chu trình 5 ải và lặp lại liên tục.
4. **Dừng bot:** Nhấn phím `q` trên bàn phím bất cứ lúc nào.

---

## ⚠️ Lưu ý quan trọng

- **Scale màn hình:** Đặt Windows Display Scaling ở mức **100%** để click chính xác nhất.
- **Quyền Administrator:** Khuyến nghị chạy Terminal dưới quyền **Run as Administrator** để phím tắt dừng `q` luôn nhận diện được.

