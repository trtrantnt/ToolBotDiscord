# Discord Bot Auto Clicker - Đi Bí Cảnh & Auto Nhanh x10 (Uyên Sư Muội)

Tool tự động hóa thao tác click trên giao diện Discord khi chơi cùng bot **Uyên Sư Muội**.

Công cụ sử dụng công nghệ nhận diện chữ **OCR Tiếng Việt siêu tốc (RapidOCR - ONNX Runtime)** kết hợp thuật toán **Smart Button Filtering** để phân biệt chính xác giữa nút bấm thật và chữ trong tin nhắn chat.

---

## 🌟 2 Chức năng độc lập

### 🏰 [Chức năng 1] Tự động đi Bí Cảnh (5 Ải Bát Môn & Kỳ Ngộ)
*Hoàn toàn độc lập, không chứa nút Nhanh x10.*
- 🚪 **Chọn cổng Bát Môn thông minh theo thứ tự ưu tiên:**
  $$\text{Sinh} \rightarrow \text{Khai} \rightarrow \text{Hưu} \rightarrow \text{Cảnh} \rightarrow \text{Kinh} \rightarrow \text{Đỗ} \rightarrow \text{Thương} \rightarrow \text{Tử}$$
- 🔮 **Tự động xử lý Kỳ Ngộ (Ải 1 & Ải 3):** Nhận diện và chọn các lựa chọn (*"Lắng nghe tiếng sấm"*, *"Cẩn thận thu hái"*, *"Hứng lấy linh nhũ"*) $\rightarrow$ Ấn *Tiếp Tục*.
- ⚔️ **Tự động xử lý Chiến Đấu (Ải 2, Ải 4, Ải 5):** Bấm *Khai Chiến* $\rightarrow$ Chờ kết quả $\rightarrow$ Ấn *Tiếp Tục Khai Phá* / *Chiến Tiếp*.
- 🔄 **Tự động lặp lại vòng bí cảnh (`auto_repeat`)** liên tục.

### ⚡ [Chức năng 2] Tự động click nút "⚡ Nhanh x10" (Tăng tốc chiến đấu)
*Chế độ chuyên dụng độc lập.*
- 🎯 **Smart Button Filtering:** Tự động phân biệt chính xác giữa **nút bấm thật `[⚡ Nhanh x10]`** ở đáy tin nhắn và **chữ tiêu đề hiển thị `Lịch Luyện Nhanh x10 Hoàn Tất!`** trong nội dung tin nhắn chat để click đúng nút 100%.
- 🔍 Quét màn hình liên tục chu kỳ nhanh (0.5s).
- 🛡️ **Anti-Hover:** Tự động dời chuột sang vùng an toàn sau khi click.
- 📜 **Auto-Scroll:** Tự động cuộn trang nếu tin nhắn bị trôi khỏi màn hình.

---

## 🛑 Nút Dừng Tool Siêu Tiện Lợi (Stop Controls)

Khi tool hoạt động, bạn có thể dừng bất cứ lúc nào bằng một trong các cách sau:
1. **Nút bấm nổi trên màn hình (`Floating Stop Button`):** Một nút đỏ **`🛑 DỪNG TOOL [ESC / Q]`** luôn hiển thị nổi ở góc màn hình (có thể kéo thả di chuyển tùy ý). Chỉ cần click chuột vào nút này là tool dừng ngay lập tức.
2. **Phím tắt bàn phím:** Nhấn phím **`ESC`** hoặc phím **`q`** trên bàn phím.

---

## 📁 Cấu trúc thư mục

```text
ToolBotDiscord/
├── config.json               # File cấu hình từ khóa OCR & thông số cho 2 chức năng
├── main.py                   # File khởi chạy chính (kèm Menu chọn chế độ)
├── requirements.txt          # Danh sách thư viện Python cần thiết
├── README.md                 # Tài liệu hướng dẫn sử dụng
└── src/
    ├── __init__.py
    ├── clicker.py            # Module điều khiển chuột, Anti-Hover và Scroll
    ├── controller.py         # Chứa DungeonController & Fast10xController
    ├── overlay.py            # Nút bấm nổi dừng tool trên màn hình (Floating Stop Button)
    └── vision.py             # Module nhận diện chữ OCR & Smart Button Filtering
```

---

## ⚙️ Cài đặt & Vận hành

### 1. Cài đặt các thư viện cần thiết:
```powershell
pip install -r requirements.txt
```

### 2. Khởi chạy tool:
```powershell
python main.py
```
Menu tương tác sẽ xuất hiện để bạn chọn:
- Nhập `1`: Chạy tự động đi Bí Cảnh
- Nhập `2`: Chạy tự động bấm Nhanh x10
- Nhập `0`: Thoát

Hoặc chạy nhanh bằng lệnh:
- `python main.py 1` (Đi Bí Cảnh)
- `python main.py 2` (Auto Nhanh x10)
