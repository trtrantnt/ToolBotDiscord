# Discord Bot Auto Clicker (Uyên Sư Muội) - OCR Edition

Tool tự động hóa thao tác click trên giao diện Discord khi chơi cùng bot **Uyên Sư Muội** (hoặc Thiên Đạo Nhân Tử).

Công cụ sử dụng công nghệ nhận diện ký tự quang học **OCR Tiếng Việt siêu tốc (RapidOCR - ONNX Runtime)** kết hợp thuật toán **Smart Button Filtering** và điều khiển chuột qua **Windows Native API** để đảm bảo độ chính xác tuyệt đối 100% khi click nút bấm.

---

## 🌟 3 Chức năng hoạt động độc lập

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

### 🎯 [Chức năng 3] Tự động bấm nút tùy chọn (Nhập chữ trên nút & thời gian chờ)
*Chế độ tự do theo nhu cầu cá nhân.*
- ✍️ Cho phép bạn nhập bất kỳ **chữ hiển thị trên nút** nào bạn muốn click (ví dụ: `Luyện Đan`, `Chiến Lại`, `Trồng Cây`, `Thu Hoạch`...).
- ⏳ Cho phép bạn nhập **thời gian chờ giữa 2 lần bấm** (tính bằng giây).
- 🔄 Tool sẽ liên tục tìm đúng nút đó trên màn hình, click chính xác và chờ đúng số giây bạn đã đặt rồi mới lặp lại.

---

## 🎯 Các điểm mạnh công nghệ

1. **Pixel-Perfect Accuracy (Windows Native API):** Sử dụng trực tiếp `SetCursorPos` và `mouse_event` ở cấp độ hệ điều hành Windows, triệt tiêu hoàn toàn độ trễ lướt chuột và lỗi lệch tọa độ do phóng to màn hình (DPI Scaling).
2. **Không cần chụp ảnh mẫu:** Sử dụng OCR để đọc trực tiếp chữ trên nút, không phụ thuộc vào màu nền, theme sáng/tối hay kích thước nút.
3. **Smart Button Filtering:** Loại bỏ các đoạn văn bản trong tin nhắn chat để tránh click nhầm vào chữ hiển thị không bấm được.

---

## 🛑 Nút Dừng Tool Siêu Tiện Lợi (Stop Controls)

Khi tool đang hoạt động, bạn có thể dừng bất cứ lúc nào bằng một trong hai cách:
1. **Nút bấm nổi trên màn hình (`Floating Stop Button`):** Một nút đỏ **`🛑 DỪNG TOOL [ESC / Q]`** luôn hiển thị nổi ở góc màn hình (có thể kéo thả di chuyển tùy ý). Chỉ cần click chuột vào nút này là tool dừng ngay lập tức.
2. **Phím tắt bàn phím:** Nhấn phím **`ESC`** hoặc phím **`Q`** trên bàn phím.

---

## 📁 Cấu trúc thư mục

```text
ToolBotDiscord/
├── config.json               # File cấu hình từ khóa OCR & thông số hoạt động
├── main.py                   # File khởi chạy chính (kèm Menu chọn 3 chế độ)
├── requirements.txt          # Danh sách thư viện Python cần thiết
├── README.md                 # Tài liệu hướng dẫn sử dụng
└── src/
    ├── __init__.py
    ├── clicker.py            # Module điều khiển chuột chính xác (Windows API)
    ├── controller.py         # Chứa DungeonController, Fast10xController & CustomButtonController
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
Giao diện Menu sẽ xuất hiện trên Terminal:
```text
==============================================================
🤖 DISCORD BOT AUTO CLICKER (UYÊN SƯ MUỘI) - OCR EDITION
==============================================================
 [1] 🏰 Tự động đi Bí Cảnh (5 Ải Bát Môn, Kỳ Ngộ, Chiến Đấu)
 [2] ⚡ Tự động bấm nút 'Nhanh x10' (Tăng tốc chiến đấu)
 [3] 🎯 Tự động bấm nút tùy chọn (Nhập chữ trên nút & thời gian)
 [0] 🛑 Thoát chương trình
==============================================================
👉 Vui lòng nhập lựa chọn của bạn (1 / 2 / 3 / 0): 
```

### 3. Khởi chạy nhanh bằng lệnh trực tiếp:
- **Đi Bí Cảnh:** `python main.py 1`
- **Auto Nhanh x10:** `python main.py 2`
- **Nút tùy chọn:** `python main.py 3 "Luyện Đan" 5` *(Ví dụ: tìm nút "Luyện Đan" và chờ 5 giây)*
