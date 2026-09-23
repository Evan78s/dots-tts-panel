#!/usr/bin/env python3
# 生成 dots.tts 面板 Colab notebook（v2.1）
# 核心改进：
#   1) 环境打包缓存到 Drive（断连后免重装，秒恢复）
#   2) 模型复制到本地 SSD（加载快，不用每次从 Drive 慢读 5GB）
#   3) 启动前先杀旧进程 + 智能等待地址（20 分钟 + 检测进程退出）
#   4) 代码块拆分：挂载 / 环境 / 模型 / 启动
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


# ---- 面板源码已改为运行时从 GitHub 下载（notebook 不再内嵌超长代码块）----

# ============================================================
# 第 1 步：挂载 Drive + 定义路径
# ============================================================
STEP_MOUNT = '''# ---- 第 1 步：挂载 Google Drive + 定义路径 ----
import os, subprocess, time, re, shutil, sys

CACHE = "/content/drive/MyDrive/dots_cache"        # Drive 持久化目录（环境 + 模型 + 音色库）
PY = "/content/py311/bin/python"                    # 本地 Python 环境
ENV_TARBALL = os.path.join(CACHE, "py311.tar.gz")   # 环境备份包（首次装好后存到 Drive）
LOCAL_HF = "/content/dots_hf_cache"                 # 本地 SSD 模型缓存（加载快）
PANEL_PY = "/content/panel.py"

try:
    from google.colab import drive
    if not os.path.isdir("/content/drive/MyDrive"):
        drive.mount("/content/drive")
    os.makedirs(CACHE, exist_ok=True)
    DRIVE_OK = True
    print("✅ Drive 已挂载，持久化目录：", CACHE, flush=True)
except Exception as e:
    DRIVE_OK = False
    print("⚠️ Drive 未挂载（断连后需重装环境 + 重下模型）：", e, flush=True)
'''

# ============================================================
# 第 2 步：环境（首次安装并缓存到 Drive；之后秒恢复）
# ============================================================
STEP_ENV = '''# ---- 第 2 步：准备环境（首次安装并缓存到 Drive，之后秒恢复；缺依赖会自动补齐）----
import os, subprocess

_REQ = ["torch", "gradio", "dots_tts", "faster_whisper", "soundfile", "huggingface_hub"]

def _py_runs(p):
    try:
        return subprocess.run([p, "--version"], capture_output=True, text=True, timeout=60).returncode == 0
    except Exception:
        return False

def _deps_ok(p):
    _code = "import importlib.util as u, sys; sys.exit(0 if all(u.find_spec(m) for m in %r) else 1)" % (_REQ,)
    try:
        return subprocess.run([p, "-c", _code], capture_output=True, text=True, timeout=120).returncode == 0
    except Exception:
        return False

def _install_deps():
    subprocess.run("pip install -q uv", shell=True, check=True)
    UV = "uv pip install --python /content/py311/bin/python"
    subprocess.run(UV + " torch==2.11.0 torchaudio==2.11.0", shell=True, check=True)
    subprocess.run(UV + " dots.tts huggingface_hub soundfile 'gradio>=6.17,<7' faster-whisper", shell=True, check=True)

# 1) 确保 python 解释器存在（恢复 / 新建）
if not _py_runs(PY):
    if DRIVE_OK and os.path.exists(ENV_TARBALL):
        print("🔄 从 Drive 恢复环境（约 1-2 分钟，免重装）...", flush=True)
        subprocess.run(["tar", "xzf", ENV_TARBALL, "-C", "/"], check=True)
    if not _py_runs(PY):
        print("🔄 首次安装环境（约 3-5 分钟）...", flush=True)
        subprocess.run("python3 -m venv /content/py311", shell=True, check=True)

# 2) 检查依赖是否齐全，缺哪个补哪个（uv 幂等，已装的秒过）
if not _deps_ok(PY):
    print("🔄 检测到依赖缺失，正在补齐（已装的会自动跳过）...", flush=True)
    _install_deps()

if not _deps_ok(PY):
    _r = subprocess.run([PY, "-c", "import gradio"], capture_output=True, text=True)
    print("❌ 依赖仍缺失：", _r.stderr[-800:], flush=True)
    raise SystemExit("依赖安装失败，请检查上方报错后重跑本格")

# 3) 环境齐了，首次打包缓存到 Drive（之后断连免重装）
if DRIVE_OK and not os.path.exists(ENV_TARBALL):
    print("📦 缓存环境到 Drive（首次稍慢，约 2-4 分钟）...", flush=True)
    subprocess.run(["tar", "czf", ENV_TARBALL, "-C", "/", "content/py311"], check=True)
    print("✅ 环境已缓存：", ENV_TARBALL, flush=True)

print("✅ 环境就绪（含 gradio / torch / dots.tts / faster-whisper）", flush=True)
'''

# ============================================================
# 第 3 步：准备模型（Drive -> 本地 SSD）+ 写面板代码
# ============================================================
STEP_PREP = '''# ---- 第 3 步：准备模型（复制到本地 SSD，加载快）+ 下载面板代码 ----
import os, subprocess, urllib.request, json, glob, shutil

PANEL_URL = "https://raw.githubusercontent.com/Evan78s/dots-tts-panel/main/panel_src.py"
try:
    urllib.request.urlretrieve(PANEL_URL, "/content/panel.py")
    print("✅ 面板代码已下载到 /content/panel.py", flush=True)
except Exception as e:
    raise SystemExit("❌ 下载面板代码失败（请检查网络后重跑本格）：" + str(e))

drive_hub = os.path.join(CACHE, "hub") if DRIVE_OK else None
local_hub = os.path.join(LOCAL_HF, "hub")
SENTINEL = os.path.join(LOCAL_HF, ".hub_copied_ok")

def _model_cache_ok(hub):
    """检查 dots.tts 模型的 tokenizer.json 是否完整可解析（= 缓存没损坏）。"""
    if not hub:
        return False
    pat = os.path.join(hub, "models--dots-studio--dots.tts-soar", "snapshots", "*", "tokenizer.json")
    for p in glob.glob(pat):
        try:
            with open(p, encoding="utf-8") as f:
                json.load(f)
            return True
        except Exception:
            return False
    return False

if drive_hub and os.path.isdir(drive_hub):
    # 只有上次「完整复制」过（有标记 + 校验通过）才跳过；否则重新复制，避免复用残缺缓存
    if os.path.exists(SENTINEL) and _model_cache_ok(local_hub):
        print("✅ 模型已在本地 SSD（上次已完整复制，跳过）", flush=True)
        HF_HOME_USE = LOCAL_HF
    else:
        print("📦 复制模型缓存到本地 SSD（含 blobs 软链，约 1-3 分钟）...", flush=True)
        if os.path.isdir(local_hub):
            shutil.rmtree(local_hub, ignore_errors=True)
        os.makedirs(LOCAL_HF, exist_ok=True)
        subprocess.run(["cp", "-a", drive_hub, local_hub], check=True)
        if _model_cache_ok(local_hub):
            open(SENTINEL, "w").write("ok")
            print("✅ 模型已就位本地 SSD", flush=True)
            HF_HOME_USE = LOCAL_HF
        else:
            # Drive 缓存本身损坏 → 删掉后重新下载到 Drive（避免反复复制同一个坏缓存）
            print("⚠️ Drive 模型缓存不完整（tokenizer.json 损坏），自动重新下载...", flush=True)
            shutil.rmtree(local_hub, ignore_errors=True)
            for _d in ["models--dots-studio--dots.tts-soar"]:
                shutil.rmtree(os.path.join(drive_hub, _d), ignore_errors=True)
            HF_HOME_USE = CACHE if DRIVE_OK else None
else:
    # 首次运行：还没有 Drive 缓存，模型将直接下载到 Drive
    HF_HOME_USE = CACHE if DRIVE_OK else None
    print("ℹ️ 首次运行：模型将下载到", HF_HOME_USE or "默认缓存", flush=True)
'''

# ============================================================
# 第 4 步：启动面板 + 智能等待地址
# ============================================================
STEP_LAUNCH = '''# ---- 第 4 步：启动面板 + 智能等待公网地址 ----
import subprocess, os, time, re

# 杀掉可能残留的旧面板进程（避免抢 GPU 导致加载失败）
subprocess.run("pkill -f panel.py || true", shell=True)
time.sleep(2)

env = dict(os.environ)
if 'HF_HOME_USE' in dir() and HF_HOME_USE:
    env["HF_HOME"] = HF_HOME_USE
elif DRIVE_OK and os.path.isdir(CACHE):
    env["HF_HOME"] = CACHE

proc = subprocess.Popen([PY, "-u", "/content/panel.py"],
                        stdout=open("panel.log", "w"),
                        stderr=subprocess.STDOUT, env=env)

URL_RE = re.compile(r"https://[a-z0-9.-]+\\.gradio\\.live")
url = None
t0 = time.time()
i = 0
while time.time() - t0 < 1200:          # 最多等 20 分钟
    if proc.poll() is not None:          # 进程已退出
        break
    if os.path.exists("panel.log"):
        text = open("panel.log", encoding="utf-8", errors="ignore").read()
        m = URL_RE.search(text)
        if m:
            url = m.group(0)
            break
    i += 1
    if i % 15 == 0:
        print("  ... 已等 %d 秒" % (i * 2), flush=True)
    time.sleep(2)

if url:
    open("panel_url.txt", "w").write(url)
    print("🌐 面板公网地址：", url, flush=True)
    print("   用浏览器打开这个地址（保持梯子开启）。", flush=True)
else:
    print("⚠️ 未获取到地址。", flush=True)
    if proc.poll() is not None:
        print("面板进程已退出，退出码：", proc.returncode, flush=True)
    if os.path.exists("panel.log"):
        tail = open("panel.log", encoding="utf-8", errors="ignore").read()[-3000:]
        print("日志末尾：", flush=True)
        print(re.sub(r"\\x1b\\[[0-9;]*m", "", tail), flush=True)
    else:
        print("无日志", flush=True)
'''

# ---- 组装 notebook ----
cells = []

cells.append(md("""# dots.tts 语音合成面板（小红书 · Colab 版）

一键启动**公网面板**：输入文字 → 选音色（预设 / 上传克隆 / 音色库）→ 选语言 → 出语音。

**面板功能：**
- ✅ 界面与语言选项**全中文**
- ✅ **音色预设**：内置 20 个**自然真人录音**音色（普通话 5 + 英语 5 + 粤语 10），点「试听」可预览
- ✅ **添加我的音色（傻瓜三步）**：上传人声 → 自动识别文字 → 起名保存，以后与内置音色在**同一个下拉**里选
- ✅ **参考音频转写**：上传后自动识别文字，可手动更正（文字越准克隆越像）
- ✅ **音色相似度** + 高级设置（音色种子 / 生成质量 / 引导强度 / 文本规范化）

**环境 + 模型都缓存到你的 Google Drive**：
- 首次装好后，**断连重开不用再重装环境**（约 1-2 分钟秒恢复）
- 模型复制到本地 SSD 加载，**不用每次从 Drive 慢读 5GB**"""))

cells.append(md("""## 第 0 步：确认 GPU（菜单操作，不是代码）

**运行时 → 更改运行时类型 → 硬件加速器选 GPU**，然后跑下面这格确认。"""))

cells.append(code("""!nvidia-smi"""))

cells.append(md("""## 使用流程（先看清楚，能省不少时间）

**首次使用**：从上到下依次跑「第 0 步 → 第 4 步」（约 5-8 分钟，会自动安装 + 缓存）。

**以后每次 / 断连重开**：**重跑全部（Runtime → Run all / 全部运行）** 即可（约 2-4 分钟，免重装、模型秒加载）。"""))

cells.append(md("""## 第 1 步：挂载 Google Drive + 定义路径

把环境备份、模型、音色库都放在你的 Drive 上，这样断连后不丢。"""))

cells.append(code(STEP_MOUNT))

cells.append(md("""## 第 2 步：准备环境（首次安装 / 之后秒恢复）

- **第一次**：安装全部依赖（约 3-5 分钟），然后**打包缓存到 Drive**。
- **之后每次**：直接从 Drive 解包恢复（约 1-2 分钟），**不再重装**。
- **自愈**：每次都会校验 gradio / torch / dots.tts 等依赖是否齐全，**缺哪个自动补哪个**（不会出现「环境在但缺包」的情况）。"""))

cells.append(code(STEP_ENV))

cells.append(md("""## 第 3 步：准备模型 + 下载面板代码

把 Drive 上的模型缓存**复制到本地 SSD**（加载比直接从 Drive 读快数倍），并从 GitHub 下载最新面板源码（面板代码不再内嵌在本 notebook 里，更新音色 / 功能时无需重下 notebook）。

> 首次运行时 Drive 还没有模型，会直接下载到 Drive；若缓存损坏（下载/复制中断），也会自动重新下载或重新复制（自愈）。"""))

cells.append(code(STEP_PREP))

cells.append(md("""## 第 4 步：启动面板 + 等待公网地址

启动前会**先杀掉旧面板进程**（避免抢 GPU 导致加载失败），然后智能等待地址：最多等 **20 分钟**，期间若进程崩了会立即停下并打印日志末尾，方便定位。"""))

cells.append(code(STEP_LAUNCH))

cells.append(md("""## ❓ 常见问题

| 问题 | 解决 |
|---|---|
| 首次很慢 | 正常：装环境 + 下 5GB 模型，约 5-8 分钟 |
| 断连后还要重装吗 | 不用了。环境已打包到 Drive，重开重跑全部约 2-4 分钟 |
| 面板地址打不开 | 大陆用户需挂梯子（跟访问 Colab 同一个）；或换「全局模式」 |
| 等了很久没地址 | 最多等 20 分钟；若进程报错会打印日志末尾，照着修 |
| 转写报错 / 组件缺失 | 环境已内置 faster-whisper；仍报错可删 Drive 的 `py311.tar.gz` 重装一次 |
| 音色下次不见了 | 需挂载 Drive（音色库存 `dots_cache/voice_library/`） |
| 想彻底重装 | 删除 Drive 的 `dots_cache/py311.tar.gz`，再重跑全部会自动重装 |"""))

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
