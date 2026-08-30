# Discord Bot Auto Clicker - Đi Bí Cảnh & Auto Nhanh x10 (Uyên Sư Muội)

Tool tự động hóa thao tác click trên giao diện Discord khi chơi cùng bot **Uyên Sư Muội**.

Công cụ sử dụng công nghệ nhận diện chữ **OCR Tiếng Việt siêu tốc (RapidOCR - ONNX Runtime)** kết hợp điều khiển chuột (**PyAutoGUI**), chia thành **2 chức năng hoàn toàn độc lập** phục vụ từng nhu cầu khác nhau.

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
- 🔍 Quét màn hình liên tục chu kỳ nhanh (0.5s).
- 🎯 Tự động phát hiện nút **"⚡ Nhanh x10"** và click ngay lập tức kèm cơ chế **Anti-Hover** (nhấc chuột ra vùng trống để tránh đổi màu giao diện).
- 📜 **Auto-Scroll:** Tự động cuộn trang nếu tin nhắn bị trôi khỏi màn hình.
- 📊 Đếm số lần click thành công theo thời gian thực.

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
    ├── controller.py         # Chứa DungeonController (Chức năng 1) & Fast10xController (Chức năng 2)
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

## 🚀 Hướng dẫn vận hành

### 1. Khởi chạy với Menu tương tác:
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
 [0] 🛑 Thoát chương trình
==============================================================
👉 Vui lòng nhập lựa chọn của bạn (1 / 2 / 0): 
```

### 2. Khởi chạy nhanh bằng tham số dòng lệnh (Tùy chọn):
- **Chạy trực tiếp Đi Bí Cảnh:**
  ```powershell
  python main.py 1
  ```
- **Chạy trực tiếp Auto Nhanh x10:**
  ```powershell
  python main.py 2
  ```

### 3. Dừng tool bất kỳ lúc nào:
- Nhấn phím **`q`** trên bàn phím để dừng ngay lập tức.
