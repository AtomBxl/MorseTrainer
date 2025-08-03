import tkinter as tk
from tkinter import messagebox
import numpy as np
from scipy.io.wavfile import write
import datetime
import os
import re 

MORSE_CODE_DICT = {
    'A': '.-',    'B': '-...',  'C': '-.-.', 'D': '-..',   'E': '.',
    'F': '..-.',  'G': '--.',   'H': '....', 'I': '..',    'J': '.---',
    'K': '-.-',   'L': '.-..',  'M': '--',   'N': '-.',    'O': '---',
    'P': '.--.',  'Q': '--.-',  'R': '.-.',  'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',  'X': '-..-',  'Y': '-.--',
    'Z': '--..',  '0': '-----', '1': '.----','2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....','7': '--...', '8': '---..',
    '9': '----.', ' ': ' '
}

SAMPLE_RATE = 44100  # 采样率
FREQ = 700           # 声音频率

# 生成一个音符
def tone(duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    waveform = 0.5 * np.sin(2 * np.pi * FREQ * t)
    return waveform

# 生成静音
def silence(duration):
    return np.zeros(int(SAMPLE_RATE * duration))

# 将文本转换为莫尔斯音频波形
def morse_to_wave(text, unit=0.1):
    audio = np.array([], dtype=np.float32)
    for char in text.upper():
        if char not in MORSE_CODE_DICT:
            continue
        code = MORSE_CODE_DICT[char]
        if code == ' ':
            audio = np.concatenate((audio, silence(unit * 7)))  # 单词间隔
        else:
            for symbol in code:
                if symbol == '.':
                    audio = np.concatenate((audio, tone(unit)))
                elif symbol == '-':
                    audio = np.concatenate((audio, tone(unit * 3)))
                audio = np.concatenate((audio, silence(unit)))  # 符号间隔
            audio = np.concatenate((audio, silence(unit * 2)))  # 字符间隔
    return audio

# 生成最终音频文件
def generate_audio(text, repeat=1, filename="output.wav", unit=0.1):
    total_wave = np.array([], dtype=np.float32)
    for _ in range(repeat):
        total_wave = np.concatenate((total_wave, morse_to_wave(text, unit), silence(unit * 7)))
    int_wave = np.int16(total_wave * 32767)
    write(filename, SAMPLE_RATE, int_wave)

def generate_file():
    phrase = entry_phrase.get().strip()
    repeat_str = entry_repeat.get().strip()
    filename_input = entry_filename.get().strip()

    if not re.fullmatch(r'[A-Za-z0-9 ]+', phrase):
        messagebox.showerror("错误", "输入内容只能为字母、数字、空格")
        return
    if not repeat_str.isdigit():
        messagebox.showerror("错误", "重复次数必须是一个整数")
        return
    repeat = int(repeat_str)

    # 获取程序路径
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 获取播放速度
    unit_ms = scale_speed.get()  # 单位：毫秒
    unit_sec = unit_ms / 1000.0  # 转换为秒

    # 文件名处理
    if not filename_input:
        now = datetime.datetime.now().strftime("%Y%m%d%H%M")
        filename = f"Morse_{now}.wav"
    else:
        if not filename_input.lower().endswith(".wav"):
            filename_input += ".wav"
        filename = filename_input

    full_path = os.path.join(script_dir, filename)

    try:
        generate_audio(phrase, repeat, full_path, unit_sec)
        messagebox.showinfo("成功", f"音频文件已生成：\n{full_path}")
    except Exception as e:
        messagebox.showerror("错误", f"生成失败：{e}")

window = tk.Tk()
window.title("莫尔斯电码训练音频生成器")
window.geometry("420x330")

# 输入框
tk.Label(window, text="电码内容（支持字母、数字、空格）：").pack(pady=(15, 5))
entry_phrase = tk.Entry(window, width=40)
entry_phrase.pack()

tk.Label(window, text="重复次数：").pack(pady=(10, 5))
entry_repeat = tk.Entry(window, width=10)
entry_repeat.insert(0, "1")
entry_repeat.pack()

tk.Label(window, text="导出文件名（可选）：").pack(pady=(10, 5))
entry_filename = tk.Entry(window, width=40)
entry_filename.insert(0, "")
entry_filename.pack()

# 播放速度滑块
tk.Label(window, text="播放速度（单位毫秒，越大越慢）：").pack(pady=(10, 0))
scale_speed = tk.Scale(window, from_=50, to=300, orient=tk.HORIZONTAL, length=250)
scale_speed.set(100)  # 默认 100 毫秒
scale_speed.pack()

tk.Button(window, text="生成音频", command=generate_file).pack(pady=20)

window.mainloop()
