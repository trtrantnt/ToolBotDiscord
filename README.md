# Discord Bot Auto Clicker - Đi Bí Cảnh (Uyên Sư Muội) - OCR Edition

Tool tự động hóa thao tác click trên giao diện Discord để tự động đi **Bí Cảnh** khi chơi cùng bot **Uyên Sư Muội**.

Công cụ sử dụng công nghệ nhận diện chữ **OCR Tiếng Việt siêu tốc (RapidOCR - ONNX Runtime)** kết hợp điều khiển chuột (**PyAutoGUI**) để đọc trực tiếp chữ trên các nút bấm của Discord, loại bỏ hoàn toàn 100% lỗi chọn nhầm nút do trùng màu nền hoặc thay đổi giao diện.

---

## 🌟 Tính năng nổi bật

- 🔤 **Nhận diện chữ OCR siêu chính xác (RapidOCR)**: Đọc trực tiếp nội dung văn bản trên nút bấm (`[Sinh Môn]`, `[Kinh Môn]`, `Lắng nghe tiếng sấm`, `Khai Chiến`, `Tiếp Tục`...). Không còn tình trạng click nhầm nút do cùng màu xám/xanh trên Discord!
- 🤖 **Máy trạng thái tự thích ứng (Smart State Machine)**: Tự động nhận diện trạng thái trên màn hình Discord để điều hướng linh hoạt mà không bị lệch nhịp.
- 🛡️ **Cơ chế chống Lag & Tự phục hồi**:
  - **Dynamic State Polling**: Quét động liên tục, bot Discord phản hồi nhanh thì đi nhanh, lag thì chờ tự động.
  - **Anti-Hover**: Tự động dời chuột sang vùng trống sau khi click.
  - **Auto-Scroll**: Tự động cuộn màn hình xuống dưới nếu tin nhắn mới bị trôi khỏi tầm nhìn.
  - **Xử lý lỗi tự động**: Tự động phát hiện thông báo lỗi của Discord (*"Tương tác này không thành công"*, *"Hết thể lực"*...).
- 🚪 **Chọn cổng thông minh (Bát Môn)**: Tự động nhận diện các cổng xuất hiện và chọn 1 cổng theo thứ tự ưu tiên:
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
├── config.json               # File cấu hình từ khóa OCR & thông số hoạt động
├── main.py                   # File khởi chạy chính của chương trình
├── requirements.txt          # Danh sách các thư viện Python cần thiết
├── README.md                 # Tài liệu hướng dẫn sử dụng
└── src/
    ├── __init__.py
    ├── clicker.py            # Module điều khiển chuột, Anti-Hover và Scroll
    ├── controller.py         # Module điều khiển luồng 5 ải, xử lý lỗi & vòng lặp
    └── vision.py             # Module nhận diện chữ OCR (RapidOCR + mss)
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
    "scan_interval": 0.8,
    "ocr_min_score": 0.6,
    "stop_hotkey": "q",
    "total_stages": 5,
    "retry_limit": 4,
    "auto_scroll_after_seconds": 6.0,
    "max_idle_timeout": 45.0,
    "anti_hover": true,
    "auto_repeat": true,
    "delay_between_stages": 2.5,
    "delay_between_runs": 4.0
}
```

---

## 🚀 Hướng dẫn vận hành

1. Mở Discord đến khung chat của bot **Uyên Sư Muội** (đảm bảo cửa sổ Discord hiển thị rõ ràng trên màn hình).
2. Mở Terminal và chạy lệnh:
   ```powershell
   python main.py
   ```
3. Tool sẽ tự động quét chữ trên màn hình và click tuần tự các nút chính xác 100%.
4. **Dừng bot:** Nhấn phím `q` trên bàn phím bất cứ lúc nào.

---

## ⚠️ Lưu ý quan trọng

- **Scale màn hình:** Khuyến nghị đặt Windows Display Scaling ở mức **100%** hoặc **125%** để chữ hiển thị rõ nét nhất.
- **Quyền Administrator:** Khuyến nghị chạy Terminal dưới quyền **Run as Administrator** để phím tắt dừng `q` luôn nhận diện được.
