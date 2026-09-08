# dots.tts 本地部署（Mac / Linux / Windows）

把面板从 Colab 搬到本地。面板程序 + 模型分开下载，模型放默认缓存目录即可（不用手动放，跑的时候会自动下）。

## 一、要下载的东西

### 1. 面板程序（本仓库）

```bash
git clone https://github.com/Evan78s/dots-tts-panel.git
cd dots-tts-panel
```

或直接下 zip：https://github.com/Evan78s/dots-tts-panel/archive/refs/heads/main.zip

### 2. 模型（2 个，会自动下载，也可手动下）

| 模型 | 用途 | 大小 | 官方链接 | 国内镜像 |
|---|---|---|---|---|
| `dots-studio/dots.tts-soar` | 主 TTS 模型 | ~5GB | https://huggingface.co/dots-studio/dots.tts-soar | https://hf-mirror.com/dots-studio/dots.tts-soar |
| `Systran/faster-whisper-small` | 参考音频转文字 | ~500MB | https://huggingface.co/Systran/faster-whisper-small | https://hf-mirror.com/Systran/faster-whisper-small |

> 国内网络推荐用 **hf-mirror.com** 镜像，否则可能连不上 huggingface.co。

## 二、模型「放到哪里」

**推荐做法：不用手动放，让它自动下载。** 程序第一次跑时会自动下到 HuggingFace 默认缓存目录：

```
~/.cache/huggingface/hub/
├── models--dots-studio--dots.tts-soar/      ← 主模型
└── models--Systran--faster-whisper-small/   ← 转写模型
```

- Mac / Linux：`~/.cache/huggingface/hub/`
- Windows：`C:\Users\你的用户名\.cache\huggingface\hub\`

### 想手动下载的话

用 `git clone` 把模型下到任意目录（例如 `~/models/`），然后启动时用环境变量指向它：

```bash
git clone https://hf-mirror.com/dots-studio/dots.tts-soar ~/models/dots.tts-soar
# 启动时指定：
DOTS_MODEL_DIR=~/models/dots.tts-soar python3 panel_local.py
```

不设置 `DOTS_MODEL_DIR` 时，程序自动按仓库 ID 下载到默认缓存目录。

## 三、安装依赖 + 启动

```bash
cd dots-tts-panel

# 建虚拟环境
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 装依赖（CPU 版 torch；有 NVIDIA 显卡再换成 CUDA 版）
pip install torch torchaudio
pip install dots.tts soundfile gradio faster-whisper

# 国内网络加速（走镜像）
export HF_ENDPOINT=https://hf-mirror.com

# 启动（首次会下 5GB 模型，约几分钟）
python3 panel_local.py
```

启动后浏览器打开 **http://127.0.0.1:7860**

## 四、几点说明

- **本地版** = `panel_local.py`（Colab 用的 `panel_src.py` 里路径是 `/content/...`，本地跑不了，所以单独做了这个）。
- **音色库**存在 `voice_library/`（本地持久化，关掉也不丢）。
- **预设音色**用的是仓库里自带的 `presets/*.wav`。
- **默认只开 localhost**（`share=False`），只有你自己能访问；想开公网隧道：`GRADIO_SHARE=1 python3 panel_local.py`。
- ⚠️ **Intel Mac / 无 NVIDIA 显卡**：只能 CPU 推理，合成会比较慢（一句几十秒到一两分钟）。要快，建议用带 NVIDIA 显卡的机器，或继续用 Colab。

## 五、常见问题

| 问题 | 解决 |
|---|---|
| 下载模型卡住/失败 | 确认 `export HF_ENDPOINT=https://hf-mirror.com` 已设置 |
| 没有 GPU，慢 | 换 NVIDIA 显卡机器，或回 Colab 用免费 GPU |
| 想开公网给手机用 | `GRADIO_SHARE=1 python3 panel_local.py` |
| 手动下了模型但报错 | 删掉 `DOTS_MODEL_DIR` 环境变量，走自动下载最稳 |
