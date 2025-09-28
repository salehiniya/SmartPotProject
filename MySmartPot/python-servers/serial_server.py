import serial
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import platform
import winsound  # فقط روی ویندوز کار می‌کند
from PIL import Image, ImageTk  # برای بارگذاری تصویر


# تنظیمات سریال
PORT = 'COM4'
BAUD = 9600

# تابع هشدار صوتی
def play_beep():
    if platform.system() == "Windows":
        winsound.Beep(1000, 500)  # فرکانس 1000Hz به مدت 500ms
    else:
        print("🔔 هشدار! (در این سیستم پخش صدا فعال نیست)")

# راه‌اندازی GUI
root = tk.Tk()
root.title("Smart Flowerpot Dashboard 🌱")

# بارگذاری و نمایش عکس در بالای پنجره
image = Image.open("smartppp.jpg")
image = image.resize((150, 150))  # تغییر اندازه اختیاری
photo = ImageTk.PhotoImage(image)
image_label = tk.Label(root, image=photo)
image_label.pack(pady=10)  # فاصله از بالا


style = ttk.Style()
style.configure("TLabel", font=("Segoe UI", 12))
style.configure("TFrame", padding=10)

frame = ttk.Frame(root)
frame.pack()

# برچسب‌ها
temp_label = ttk.Label(frame, text="🌡 Temp: -- °C")
temp_label.grid(row=0, column=0, sticky="w")

light_label = ttk.Label(frame, text="💡 Light: --")
light_label.grid(row=1, column=0, sticky="w")

moisture_label = ttk.Label(frame, text="💧 Moisture: --")
moisture_label.grid(row=2, column=0, sticky="w")

alert_label = ttk.Label(frame, text="", foreground="red", font=("Segoe UI", 12, "bold"))
alert_label.grid(row=3, column=0, columnspan=2)

# نمودار
fig, ax = plt.subplots(figsize=(5, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

times, temps, lights, moistures = [], [], [], []

def update_plot():
    ax.clear()
    ax.plot(times, temps, label="Temp (°C)", color='red')
    ax.plot(times, lights, label="Light", color='orange')
    ax.plot(times, moistures, label="Moisture", color='blue')
    ax.set_xlabel("Time (s)")
    ax.legend()
    canvas.draw()

def read_serial():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"📡 اتصال به {PORT} برقرار شد.")
    except:
        alert_label.config(text="❌ اتصال سریال برقرار نشد.")
        return

    start_time = time.time()

    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if line:
                parts = line.split(",")
                alerts = []

                if len(parts) >= 3:
                    temp = float(parts[0])
                    light = int(parts[1])
                    moist = int(parts[2])

                    now = round(time.time() - start_time)
                    times.append(now)
                    temps.append(temp)
                    lights.append(light)
                    moistures.append(moist)

                    if len(times) > 30:
                        times.pop(0)
                        temps.pop(0)
                        lights.pop(0)
                        moistures.pop(0)

                    temp_label.config(text=f"Temp: {temp:.1f} °C")
                    light_label.config(text=f"Light: {light}")
                    moisture_label.config(text=f"Moisture: {moist}")

                    # بررسی هشدارهای اضافه‌شده توسط آردوینو
                    if len(parts) > 3:
                        for msg in parts[3:]:
                            msg = msg.strip().upper()
                            if msg == "LOW_TEMP":
                                alerts.append("⚠ دمای پایین!")
                                play_beep()
                            elif msg == "HIGH_TEMP":
                                alerts.append("⚠ دمای بالا!")
                                play_beep()
                            elif msg == "LOW_LIGHT":
                                alerts.append("⚠ نور کم!")
                                play_beep()
                            elif msg == "HIGH_LIGHT":
                                alerts.append("⚠ نور زیاد!")
                                play_beep()
                            elif msg == "LOW_MOISTURE":
                                alerts.append("⚠ رطوبت کم!")
                                play_beep()
                            elif msg == "HIGH_MOISTURE":
                                alerts.append("⚠ رطوبت زیاد!")
                                play_beep()

                    alert_label.config(text=" | ".join(alerts) if alerts else "")

                    update_plot()

        except Exception as e:
            alert_label.config(text=f"خطا: {e}")

# شروع خواندن در نخ جداگانه
threading.Thread(target=read_serial, daemon=True).start()

root.mainloop()

