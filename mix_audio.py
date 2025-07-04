import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pydub import AudioSegment

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class BatchMixerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🎧 批量音频混音工具")
        self.geometry("600x460")
        self.resizable(False, False)

        self.vocal_dir = ctk.StringVar()
        self.vocal_file = ctk.StringVar()
        self.instr_file = ctk.StringVar()
        self.status_text = ctk.StringVar(value="准备就绪")

        # --- UI 部分 ---
        ctk.CTkLabel(self, text="人声音频文件夹路径：").pack(pady=(15, 5))
        ctk.CTkEntry(self, textvariable=self.vocal_dir, width=450).pack()
        ctk.CTkButton(self, text="📁 浏览目录", command=self.select_vocal_dir).pack(pady=5)

        ctk.CTkLabel(self, text="或选择单个人声音频文件：").pack(pady=(15, 5))
        ctk.CTkEntry(self, textvariable=self.vocal_file, width=450).pack()
        ctk.CTkButton(self, text="📄 浏览文件", command=self.select_vocal_file).pack(pady=5)

        ctk.CTkLabel(self, text="伴奏音频文件：").pack(pady=(15, 5))
        ctk.CTkEntry(self, textvariable=self.instr_file, width=450).pack()
        ctk.CTkButton(self, text="🎼 选择伴奏文件", command=self.select_instr_file).pack(pady=5)

        ctk.CTkButton(self, text="🚀 开始混音", command=self.start_batch_mix).pack(pady=(20, 10))
        ctk.CTkButton(self, text="🗑️ 清空所有_mix文件", fg_color="red", command=self.clean_mix_files).pack(pady=5)

        self.status_label = ctk.CTkLabel(self, textvariable=self.status_text, text_color="green", wraplength=500, justify="left")
        self.status_label.pack(pady=15)

    def select_vocal_dir(self):
        folder = filedialog.askdirectory(title="选择人声音频文件夹")
        if folder:
            self.vocal_dir.set(folder)
            self.vocal_file.set("")  # 清空单文件选择

    def select_vocal_file(self):
        file = filedialog.askopenfilename(title="选择单个人声音频", filetypes=[("音频文件", "*.wav *.mp3 *.flac")])
        if file:
            self.vocal_file.set(file)
            self.vocal_dir.set("")  # 清空文件夹选择

    def select_instr_file(self):
        path = filedialog.askopenfilename(filetypes=[("音频文件", "*.wav *.mp3 *.flac")])
        if path:
            self.instr_file.set(path)

    def start_batch_mix(self):
        instr = self.instr_file.get().strip()
        folder = self.vocal_dir.get().strip()
        vocal_file = self.vocal_file.get().strip()

        if not os.path.isfile(instr):
            messagebox.showerror("错误", "请选择有效的伴奏音频文件")
            return

        # 决定混音模式：文件 or 目录
        if vocal_file:
            files = [vocal_file]
            base_folder = os.path.dirname(vocal_file)
        elif os.path.isdir(folder):
            supported_ext = [".wav", ".mp3", ".flac"]
            files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in supported_ext]
            base_folder = folder
        else:
            messagebox.showerror("错误", "请选择人声音频文件或文件夹")
            return

        if not files:
            messagebox.showinfo("提示", "未找到任何人声音频文件")
            return

        # 加载伴奏音频
        try:
            instr_audio = AudioSegment.from_file(instr).set_frame_rate(44100).set_channels(2)
        except Exception as e:
            self.status_text.set(f"❌ 加载伴奏失败：{e}")
            return

        total = len(files)
        success = 0
        for i, f in enumerate(files, 1):
            name, ext = os.path.splitext(os.path.basename(f))
            if name.endswith("_mix"):
                continue  # 跳过已处理文件

            try:
                self.status_text.set(f"🔄 [{i}/{total}] 正在处理：{os.path.basename(f)}")
                self.update()

                vocal = AudioSegment.from_file(f).set_frame_rate(44100).set_channels(2)
                min_len = min(len(vocal), len(instr_audio))
                vocal = vocal[:min_len] + 2  # 提升人声音量
                instr_trim = instr_audio[:min_len] - 2  # 降低伴奏音量

                mixed = instr_trim.overlay(vocal)
                output_path = os.path.join(base_folder, f"{name}_mix.wav")
                mixed.export(output_path, format="wav")

                self.status_text.set(f"✅ 已完成：{name}_mix.wav")
                self.update()
                success += 1
                # 如果是单文件，弹窗提示
                if len(files) == 1:
                    messagebox.showinfo("混音完成", f"混音已完成，输出文件：\n{output_path}")
            except Exception as e:
                self.status_text.set(f"❌ 错误处理 {f}：{e}")
                self.update()

        self.status_text.set(f"🎉 处理完成，共混音：{success} 个")
        self.update()

    def clean_mix_files(self):
        folder = self.vocal_dir.get().strip()
        if not os.path.isdir(folder):
            messagebox.showerror("错误", "请先选择有效的文件夹用于清理")
            return

        deleted = 0
        for f in os.listdir(folder):
            if f.endswith("_mix.wav"):
                try:
                    os.remove(os.path.join(folder, f))
                    deleted += 1
                except:
                    pass

        self.status_text.set(f"🗑️ 已清除 {deleted} 个 *_mix.wav 文件")
        self.update()


if __name__ == "__main__":
    app = BatchMixerApp()
    app.mainloop()
