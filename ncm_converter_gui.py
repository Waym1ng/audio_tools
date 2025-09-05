import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import subprocess
import shutil

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


def convert_ncm_file(ncm_path: str, output_dir: str):
    try:
        # 使用 ncmdump/ncm2mp3 等命令行工具（你也可以用 Python 实现）
        result = subprocess.run(
            ["ncmdump", ncm_path, "-o", output_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())
        return True, result.stdout.strip()
    except FileNotFoundError:
        return False, "ncmdump' command not found. Please ensure it is installed and in your PATH."
    except Exception as e:
        return False, str(e)


class NCMConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🎵 NCM 转换器")
        self.geometry("600x450")
        self.resizable(False, False)

        self.ncm_path = ctk.StringVar()
        self.output_dir = ctk.StringVar()
        self.status_text = ctk.StringVar(value="请选择 .ncm 文件或包含 .ncm 的目录")

        ctk.CTkLabel(self, text="📂 NCM 文件或目录：").pack(pady=(20, 5))
        ctk.CTkEntry(self, textvariable=self.ncm_path, width=480).pack()
        
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=5)
        ctk.CTkButton(button_frame, text="选择文件", command=self.select_ncm_file).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="选择目录", command=self.select_ncm_dir).pack(side="left", padx=5)

        ctk.CTkLabel(self, text="💾 输出目录：").pack(pady=(15, 5))
        ctk.CTkEntry(self, textvariable=self.output_dir, width=480).pack()
        ctk.CTkButton(self, text="选择输出目录", command=self.select_output).pack(
            pady=5
        )

        self.convert_button = ctk.CTkButton(self, text="🚀 开始转换", command=self.start_conversion)
        self.convert_button.pack(pady=20)

        self.status_label = ctk.CTkLabel(
            self,
            textvariable=self.status_text,
            wraplength=520,
            justify="left",
            text_color="green",
        )
        self.status_label.pack(pady=10)
        
        self.check_ncmdump()

    def check_ncmdump(self):
        if not shutil.which("ncmdump"):
            self.status_text.set("错误: 'ncmdump' 未找到. 请确保它已安装并在您的 PATH 中.")
            self.convert_button.configure(state="disabled")
            messagebox.showerror("错误", "'ncmdump' 未找到. 请确保它已安装并在您的 PATH 中.")

    def select_ncm_file(self):
        path = filedialog.askopenfilename(
            title="选择单个 .ncm 文件", filetypes=[("NCM 文件", "*.ncm")]
        )
        if path:
            self.ncm_path.set(path)

    def select_ncm_dir(self):
        path = filedialog.askdirectory(title="选择包含 NCM 的目录")
        if path:
            self.ncm_path.set(path)

    def select_output(self):
        folder = filedialog.askdirectory(title="选择输出目录")
        if folder:
            self.output_dir.set(folder)

    def start_conversion(self):
        src = self.ncm_path.get()
        out = self.output_dir.get()

        if not src or not out:
            messagebox.showwarning("⚠️ 缺少路径", "请指定 NCM 文件或目录 和 输出目录")
            return

        ncm_files = []

        if os.path.isfile(src) and src.endswith(".ncm"):
            ncm_files = [src]
        elif os.path.isdir(src):
            ncm_files = [str(f) for f in Path(src).rglob("*.ncm")]
        else:
            messagebox.showerror("无效路径", "请选择 .ncm 文件或包含 .ncm 的目录")
            return

        if not ncm_files:
            messagebox.showinfo("提示", "未找到任何 .ncm 文件")
            return

        self.status_text.set(f"开始转换 {len(ncm_files)} 个文件...\n")
        self.update()

        success_count = 0
        fail_count = 0

        for i, file in enumerate(ncm_files, 1):
            self.status_text.set(
                f"正在转换 ({i}/{len(ncm_files)}): {os.path.basename(file)}"
            )
            self.update()

            success, msg = convert_ncm_file(file, out)
            if success:
                success_count += 1
            else:
                fail_count += 1
                self.status_text.set(f"❌ {os.path.basename(file)} 转换失败：{msg}")
                self.update()

        self.status_text.set(
            f"🎉 转换完成！成功：{success_count} 个，失败：{fail_count} 个。"
        )


if __name__ == "__main__":
    app = NCMConverterApp()
    app.mainloop()
