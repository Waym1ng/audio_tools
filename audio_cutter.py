import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pydub import AudioSegment

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AudioCutterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("✂️ 音频剪切工具")
        self.geometry("640x500")
        self.resizable(False, False)

        self.audio_path = None
        self.audio = None
        self.duration_sec = 0
        self.output_dir = None

        # 新增：模式选择和分段数
        self.mode = ctk.StringVar(value="自由选择时间")
        self.n_segments = ctk.IntVar(value=2)

        # 状态文本
        self.status_text = ctk.StringVar(value="未加载音频")

        # --- 界面部分 ---
        ctk.CTkButton(self, text="📂 选择音频文件", command=self.load_audio).pack(pady=10)
        ctk.CTkLabel(self, textvariable=self.status_text, wraplength=500).pack(pady=5)

        # 模式选择
        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(pady=5)
        ctk.CTkLabel(mode_frame, text="模式选择：").pack(side="left")
        ctk.CTkRadioButton(mode_frame, text="自由选择时间", variable=self.mode, value="自由选择时间", command=self.update_mode).pack(side="left")
        ctk.CTkRadioButton(mode_frame, text="平均分段", variable=self.mode, value="平均分段", command=self.update_mode).pack(side="left")

        # 平均分段输入框
        self.n_frame = ctk.CTkFrame(self)
        ctk.CTkLabel(self.n_frame, text="分段数 n：").pack(side="left")
        self.n_entry = ctk.CTkEntry(self.n_frame, textvariable=self.n_segments, width=60)
        self.n_entry.pack(side="left")
        # 默认隐藏
        self.n_frame.pack_forget()

        # 起始/结束时间输入框（替换滑块）
        self.time_frame = ctk.CTkFrame(self)
        self.time_frame.pack()
        ctk.CTkLabel(self.time_frame, text="开始时间（秒）").grid(row=0, column=0, padx=5, pady=5)
        self.entry_start = ctk.CTkEntry(self.time_frame, width=80)
        self.entry_start.grid(row=0, column=1, padx=5)
        ctk.CTkLabel(self.time_frame, text="结束时间（秒）").grid(row=1, column=0, padx=5, pady=5)
        self.entry_end = ctk.CTkEntry(self.time_frame, width=80)
        self.entry_end.grid(row=1, column=1, padx=5)
        # 最大时长显示
        self.label_duration = ctk.CTkLabel(self.time_frame, text="音频时长：0.00 秒")
        self.label_duration.grid(row=2, column=0, columnspan=2, pady=5)
        self.time_frame.pack_forget()  # 默认隐藏

        # 输出目录选择
        ctk.CTkButton(self, text="📁 设置输出目录（可选）", command=self.select_output_dir).pack(pady=10)

        # 剪切操作
        ctk.CTkButton(self, text="✂️ 剪切并保存", command=self.cut_audio).pack(pady=20)

    def update_mode(self):
        mode = self.mode.get()
        if mode == "自由选择时间":
            self.n_frame.pack_forget()
            self.time_frame.pack(pady=5)
        else:
            self.time_frame.pack_forget()
            self.n_frame.pack(pady=5)

    def load_audio(self):
        path = filedialog.askopenfilename(filetypes=[("音频文件", "*.wav *.mp3 *.flac")])
        if not path:
            return
        try:
            self.audio = AudioSegment.from_file(path)
            self.audio_path = path
            self.duration_sec = round(len(self.audio) / 1000, 2)
            self.label_duration.configure(text=f"音频时长：{self.duration_sec} 秒")
            self.status_text.set(f"✅ 加载成功：{os.path.basename(path)}\n音频时长：{self.duration_sec} 秒")
        except Exception as e:
            messagebox.showerror("加载失败", str(e))

    def select_output_dir(self):
        folder = filedialog.askdirectory(title="选择输出目录")
        if folder:
            self.output_dir = folder
            messagebox.showinfo("输出目录设置成功", f"保存路径：\n{folder}")

    def cut_audio(self):
        if not self.audio:
            messagebox.showwarning("⚠️", "请先加载音频文件")
            return
        mode = self.mode.get()
        if mode == "自由选择时间":
            try:
                start = float(self.entry_start.get())
                end = float(self.entry_end.get())
            except Exception:
                messagebox.showerror("输入错误", "请输入有效的起始和结束时间（数字）")
                return
            if start < 0 or end <= start or end > self.duration_sec:
                messagebox.showerror("时间范围错误", f"请确认开始 < 结束，且在 0~{self.duration_sec} 秒之间")
                return
            cut_audio = self.audio[start * 1000 : end * 1000]
            duration = int(end - start)
            base_name = os.path.splitext(os.path.basename(self.audio_path))[0]
            output_name = f"{base_name}_{duration}s.wav"
            output_path = os.path.join(self.output_dir or os.path.dirname(self.audio_path), output_name)
            try:
                cut_audio.export(output_path, format="wav")
                messagebox.showinfo("剪切成功", f"已保存为：\n{output_name}")
            except Exception as e:
                messagebox.showerror("保存失败", str(e))
        else:
            # 平均分段
            try:
                n = int(self.n_segments.get())
                if n < 1:
                    raise ValueError
            except Exception:
                messagebox.showerror("输入错误", "请输入有效的分段数（正整数）")
                return
            total_ms = len(self.audio)
            seg_ms = total_ms // n
            base_name = os.path.splitext(os.path.basename(self.audio_path))[0]
            output_dir = self.output_dir or os.path.dirname(self.audio_path)
            saved_files = []
            for i in range(n):
                start_ms = i * seg_ms
                end_ms = (i + 1) * seg_ms if i < n - 1 else total_ms
                seg_audio = self.audio[start_ms:end_ms]
                output_name = f"{base_name}_part{i+1}_{start_ms//1000}_{end_ms//1000}s.wav"
                output_path = os.path.join(output_dir, output_name)
                try:
                    seg_audio.export(output_path, format="wav")
                    saved_files.append(output_name)
                except Exception as e:
                    messagebox.showerror("保存失败", f"第{i+1}段导出失败：{e}")
            if saved_files:
                messagebox.showinfo("分段剪切完成", f"已保存 {len(saved_files)} 段：\n" + "\n".join(saved_files))

if __name__ == "__main__":
    app = AudioCutterApp()
    app.mainloop()
