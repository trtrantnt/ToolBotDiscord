import tkinter as tk
import threading
import time

class FloatingStopButton:
    """
    Cửa sổ nút bấm nổi '🛑 DỪNG TOOL (ESC / Q)' luôn nằm trên cùng màn hình.
    Người dùng có thể click chuột trực tiếp vào nút này hoặc nhấn phím ESC/Q để dừng tool.
    """
    def __init__(self, on_stop_callback=None):
        self.on_stop_callback = on_stop_callback
        self.root = None
        self._thread = None
        self._is_alive = False

    def show(self):
        self._is_alive = True
        self._thread = threading.Thread(target=self._run_ui, daemon=True)
        self._thread.start()

    def _run_ui(self):
        try:
            self.root = tk.Tk()
            self.root.title("Stop Tool")
            
            # Cấu hình cửa sổ không viền, luôn nổi trên cùng (TopMost)
            self.root.attributes("-topmost", True)
            self.root.overrideredirect(True)
            
            # Vị trí mặc định: góc trên bên phải màn hình
            screen_w = self.root.winfo_screenwidth()
            pos_x = max(10, screen_w - 220)
            pos_y = 30
            self.root.geometry(f"190x42+{pos_x}+{pos_y}")

            # Tạo khung viền và nút bấm
            frame = tk.Frame(self.root, bg="#2c3e50", bd=2)
            frame.pack(fill="both", expand=True)

            self.btn = tk.Button(
                frame,
                text="🛑 DỪNG TOOL [ESC / Q]",
                font=("Arial", 9, "bold"),
                bg="#e74c3c",
                fg="white",
                activebackground="#c0392b",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                command=self._on_stop_clicked
            )
            self.btn.pack(fill="both", expand=True, padx=2, pady=2)

            # Cho phép kéo thả nút bấm nổi đến vị trí khác nếu che khuất tầm nhìn
            self.btn.bind("<ButtonPress-1>", self._start_move)
            self.btn.bind("<B1-Motion>", self._do_move)

            self.root.mainloop()
        except Exception as e:
            pass

    def _start_move(self, event):
        self._x = event.x
        self._y = event.y

    def _do_move(self, event):
        if self.root:
            deltax = event.x - self._x
            deltay = event.y - self._y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

    def _on_stop_clicked(self):
        if self.on_stop_callback:
            self.on_stop_callback()
        self.close()

    def close(self):
        if self.root and self._is_alive:
            self._is_alive = False
            try:
                self.root.after(0, self._destroy_safe)
            except Exception:
                pass

    def _destroy_safe(self):
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
                self.root = None
        except Exception:
            pass

