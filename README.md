# audio_tools

一个实用的音频与视频处理工具集，包含多种常用的音频剪辑、混音、提取与格式转换脚本，适用于日常音视频处理自动化任务。

## 功能简介

- **audio_cutter.py**  
  支持音频文件的剪切、分割等操作，可批量处理音频片段。

- **mix_audio.py**  
  实现多音频文件的混音功能，可自定义音量、时长等参数，适合制作混音音轨。

- **video_audio_extractor.py**  
  从视频文件中提取音频流，支持多种视频格式，便于音频素材的获取。

- **ncm_converter_gui.py**  
  提供图形界面，支持将网易云音乐的.ncm格式文件批量转换为常见音频格式（如mp3、flac等）。

## 使用方法

1. 克隆本仓库到本地：

   ```bash
   git clone https://github.com/Waym1ng/audio_tools.git
   cd audio_tools
   ```

2. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

3. 运行脚本：

   所有脚本均为可视化界面，直接运行对应脚本即可启动GUI工具。例如：

   ```bash
   python audio_cutter.py
   python mix_audio.py
   python video_audio_extractor.py
   python ncm_converter_gui.py
   ```

## 依赖环境

- Python 3.7+
- 主要依赖库：`pydub`, `moviepy`, `tkinter` 等
