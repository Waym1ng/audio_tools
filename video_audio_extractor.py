import os
from moviepy.editor import VideoFileClip
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class VideoAudioExtractor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🎬 视频音频提取工具")
        self.geometry("600x400")
        self.resizable(False, False)

        self.video_path = ctk.StringVar()
        self.output_dir = ctk.StringVar()
        self.output_format = ctk.StringVar(value="mp3")
        self.status_text = ctk.StringVar(value="准备就绪")

        # UI 组件
        ctk.CTkLabel(self, text="选择视频文件：").pack(pady=15)
        ctk.CTkEntry(self, textvariable=self.video_path, width=460).pack()
        ctk.CTkButton(self, text="📂 浏览视频文件", command=self.select_video).pack(pady=5)

        ctk.CTkLabel(self, text="选择输出目录 (可选):").pack(pady=10)
        ctk.CTkEntry(self, textvariable=self.output_dir, width=460).pack()
        ctk.CTkButton(self, text="📂 浏览输出目录", command=self.select_output_dir).pack(pady=5)

        ctk.CTkLabel(self, text="选择导出音频格式：").pack(pady=10)
        ctk.CTkOptionMenu(self, values=["mp3", "wav"], variable=self.output_format).pack()

        ctk.CTkButton(self, text="🚀 提取音频", command=self.extract_audio).pack(pady=20)

        ctk.CTkLabel(self, textvariable=self.status_text, text_color="green", wraplength=500).pack(pady=20)

    def select_video(self):
        file = filedialog.askopenfilename(filetypes=[("视频文件", "*.mp4 *.mov *.avi *.mkv")])
        if file:
            self.video_path.set(file)

    def select_output_dir(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir.set(folder)

    def extract_audio(self):
        video_file = self.video_path.get().strip()
        output_dir = self.output_dir.get().strip()
        out_format = self.output_format.get()

        if not os.path.isfile(video_file):
            messagebox.showerror("错误", "请先选择一个有效的视频文件")
            return

        clip = None
        try:
            self.status_text.set("🔄 正在处理，请稍候...")
            self.update()

            clip = VideoFileClip(video_file)
            audio = clip.audio

            base_name = os.path.splitext(os.path.basename(video_file))[0]
            output_filename = f"{base_name}_audio.{out_format}"
            
            if output_dir:
                out_path = os.path.join(output_dir, output_filename)
            else:
                out_path = os.path.join(os.path.dirname(video_file), output_filename)

            audio.write_audiofile(out_path)

            self.status_text.set(f"✅ 提取完成：{os.path.basename(out_path)}")
            messagebox.showinfo("成功", f"音频已提取并保存到:\n{out_path}")
        except Exception as e:
            self.status_text.set(f"❌ 提取失败：{e}")
            messagebox.showerror("错误", f"提取失败:\n{e}")
        finally:
            if clip:
                clip.close()

if __name__ == "__main__":
    app = VideoAudioExtractor()
    app.mainloop()
