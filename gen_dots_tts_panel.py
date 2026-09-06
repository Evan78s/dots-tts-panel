#!/usr/bin/env python3
# 生成 dots.tts 面板 Colab notebook（升级版）
# 功能：中文界面 + 音色预设 + 参考音频转写(ASR) + 音色库(持久化到 Drive) + 音色相似度
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
# 兼容两种布局：平铺（仓库根）或 dots-tts-panel/ 子目录（本地开发）
REPO_DIR = BASE if os.path.exists(os.path.join(BASE, "panel_src.py")) else os.path.join(BASE, "dots-tts-panel")
PANEL_SRC = os.path.join(REPO_DIR, "panel_src.py")


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": [l + "\n" for l in text.strip("\n").split("\n")]}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": [l + "\n" for l in text.strip("\n").split("\n")]}


# ---- 1. 读取面板脚本 ----
panel_code = open(PANEL_SRC, encoding="utf-8").read()

# ---- 3. 第 1 步 cell 模板 ----
STEP1 = '''import os, subprocess, time, re

PY = "/content/py311/bin/python"

# ---- 0. 挂载 Google Drive（缓存模型，下次免重下 5GB）----
CACHE = "/content/drive/MyDrive/dots_cache"
try:
    from google.colab import drive
    if not os.path.exists("/content/drive/MyDrive"):
        drive.mount("/content/drive")
    os.makedirs(CACHE, exist_ok=True)
    print("✅ Drive 已挂载，模型缓存：", CACHE)
except Exception as e:
    CACHE = None
    print("⚠️ Drive 未挂载（模型缓存在本地，下次需重下）：", e)

# ---- 1. 环境（缺失才重建，约 3-5 分钟）----
if not os.path.exists(PY):
    print("🔄 环境缺失，重建中（约 3-5 分钟）...")
    subprocess.run("pip install -q uv", shell=True)
    subprocess.run("uv python install 3.11", shell=True)
    subprocess.run("uv venv /content/py311 --python 3.11", shell=True)
    subprocess.run("uv pip install --python /content/py311/bin/python torch==2.11.0 torchaudio==2.11.0", shell=True)
    subprocess.run("uv pip install --python /content/py311/bin/python dots.tts huggingface_hub soundfile 'gradio>=6.17,<7' faster-whisper", shell=True)
    print("✅ 环境重建完成")
else:
    # 已有环境：补齐转写组件 + 升级 gradio 到 6.x（修复与新版 huggingface_hub 的冲突）
    subprocess.run("pip install -q uv", shell=True)
    subprocess.run("uv pip install --python /content/py311/bin/python faster-whisper 'gradio>=6.17,<7'", shell=True)
    print("✅ 环境已就绪（含参考音频转写组件）")

# ---- 2. 写面板脚本 ----
panel_code = r"""__PANEL_CODE__"""
open("panel.py", "w", encoding="utf-8").write(panel_code)

# ---- 3. 启动面板 + 拿公网地址 ----
env = dict(os.environ)
if CACHE:
    env["HF_HOME"] = CACHE
subprocess.Popen([PY, "-u", "panel.py"], stdout=open("panel.log", "w"), stderr=subprocess.STDOUT, env=env)

url = None
for i in range(1, 601):
    time.sleep(1)
    if os.path.exists("panel.log"):
        m = re.search("https://[a-z0-9-]+.gradio.live", open("panel.log").read())
        if m:
            url = m.group(0)
            break
    if i % 30 == 0:
        print(f"  ... 已等 {i} 秒（首次加载模型较慢，尤其从 Drive 读取）", flush=True)

if url:
    open("panel_url.txt", "w").write(url)
    print("🌐 面板公网地址：", url)
    print("   用浏览器打开这个地址即可（保持梯子开启）。")
else:
    print("⚠️ 未获取到地址，日志：")
    print(open("panel.log").read()[-2000:] if os.path.exists("panel.log") else "无日志")
'''

STEP1 = STEP1.replace("__PANEL_CODE__", panel_code)

# ---- 4. 组装 notebook ----
cells = []

cells.append(md("""# dots.tts 语音合成面板（小红书 · Colab 版）

一键启动**公网面板**：输入文字 → 选音色（预设 / 上传克隆 / 音色库）→ 选语言 → 出语音。

**面板功能：**
- ✅ 界面与语言选项**全中文**
- ✅ **音色预设**：内置 4 个中文音色，点「试听」可预览
- ✅ **参考音频转写**：上传人声 → 自动识别文字 → 可手动更正（文字越准，克隆越像）
- ✅ **音色库**：把上传的声音保存下来，以后直接选，不用重复上传
- ✅ **音色相似度**：调节克隆相似程度
- ✅ 20+ 语言 + 中文方言口音

**模型缓存在你的 Google Drive**，下次启动不用重新下载 5GB。

**每次使用只需 3 步：**
1. 菜单「运行时 → 更改运行时类型 → GPU」
2. 跑「第 1 步」一键启动（首次约 5-8 分钟，之后快）
3. 打开打印出来的 `https://xxx.gradio.live` 公网地址

> ⚠️ 打开面板地址时要**开着梯子**（跟访问 Colab 同一个）。"""))

cells.append(md("""## 第 0 步：确认 GPU（菜单操作，不是代码）

**运行时 → 更改运行时类型 → 硬件加速器选 GPU**，然后跑下面这格确认。"""))

cells.append(code("""!nvidia-smi"""))

cells.append(md("""## 第 1 步：一键启动面板

跑这一格就行：自动挂载 Drive（缓存模型）→ 装环境（缺失才装，含转写组件）→ 启动面板 → 打印公网地址。"""))

cells.append(code(STEP1))

cells.append(md("""## 🔄 重启面板（会话没断、但面板挂了时用）

如果 Colab 还开着、只是面板打不开/地址失效，跑这格快速重启（**不重装环境**，只重新加载模型，约 1 分钟）。"""))

cells.append(code("""import subprocess, os, time, re

PY = "/content/py311/bin/python"
CACHE = "/content/drive/MyDrive/dots_cache"

# 杀掉旧面板进程
subprocess.run("pkill -f panel.py || true", shell=True)
time.sleep(2)

# 重新启动（环境已存在，不重装）
env = dict(os.environ)
if os.path.isdir(CACHE):
    env["HF_HOME"] = CACHE
subprocess.Popen([PY, "-u", "panel.py"], stdout=open("panel.log", "w"), stderr=subprocess.STDOUT, env=env)

url = None
for i in range(1, 601):
    time.sleep(1)
    if os.path.exists("panel.log"):
        m = re.search("https://[a-z0-9-]+.gradio.live", open("panel.log").read())
        if m:
            url = m.group(0)
            break
    if i % 30 == 0:
        print(f"  ... 已等 {i} 秒", flush=True)

if url:
    open("panel_url.txt", "w").write(url)
    print("🌐 新面板地址：", url)
else:
    print("⚠️ 失败，日志：")
    print(open("panel.log").read()[-2000:] if os.path.exists("panel.log") else "无日志")"""))

cells.append(md("""## 📌 下次怎么用（重要）

**把本 notebook 保存到你的 Google Drive**，以后直接从 Drive 打开：

1. 菜单 **文件 → 在 Drive 中保存副本**
2. 下次用：从 Drive 打开这个副本 → 选 GPU → 跑「第 1 步」即可

**为什么快：**
- 模型缓存到了 Drive（`/content/drive/MyDrive/dots_cache`），**下次不重下 5GB**
- 音色库也存到 Drive（`dots_cache/voice_library/`），**保存的音色下次还在**
- 只有 Python 环境需要重装（约 2-3 分钟），这是 Colab 免费版不可避免的

**地址有效期：** 面板地址只要 Colab 会话不断线就有效；断线重连后重跑「第 1 步」会拿到新地址。"""))

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "colab": {"provenance": [], "name": "dots_tts_panel.ipynb"},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
    },
    "cells": cells,
}

out_main = os.path.join(REPO_DIR, "dots_tts_panel.ipynb")
out_root = os.path.join(BASE, "dots_tts_panel.ipynb")
for out in (out_main, out_root):
    with open(out, "w", encoding="utf-8") as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)

print("已生成:", out_main)
print("已生成:", out_root)
print("cells:", len(cells), "| notebook 大小: %.2f KB" % (os.path.getsize(out_main) / 1024))
