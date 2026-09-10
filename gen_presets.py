#!/usr/bin/env python3
# 管理内置音色预设的参考音频（自然真人录音）
#
# 重要说明：
#   dots.tts 是「零样本声音克隆」模型，官方（studio-dots-ai/dots.tts）不提供任何内置音色，
#   HF 模型仓库里也没有示例人声文件（只有模型权重）。所以「音色预设」必须自己准备参考音频。
#
#   参考音频质量直接决定克隆效果：
#   ✅ 用「干净的自然人声录音」（3-10 秒、单一人声、无背景噪音/音乐）→ 克隆自然
#   ❌ 用机器合成的声音（如 macOS `say`、其它 TTS 输出）→ 韵律扁平、克隆出来很机械
#
# 本脚本内置的 3 个音色取自开源项目的人声示例（自然真人录音），来源与许可：
#   f5_zh.wav    F5-TTS（MIT 许可）     src/f5_tts/infer/examples/basic/basic_ref_zh.wav
#   cosy_zh.wav  CosyVoice（Apache-2.0） asset/zero_shot_prompt.wav
#   f5_en.wav    F5-TTS（MIT 许可）     src/f5_tts/infer/examples/basic/basic_ref_en.wav
#
# 用法：
#   1) python3 gen_presets.py            # 重新下载内置 3 个自然音色
#   2) 自己加音色：把任意干净人声 wav 放进 presets/，然后在 panel_src.py 的
#      PRESET_DEFS 里加一行 (key, 标签, 文件名, 参考文字)，重新跑 gen_dots_tts_panel.py 即可。
import os, urllib.request, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "presets")
os.makedirs(OUT, exist_ok=True)

# (文件名, 下载地址, 参考文字, 显示标签)
PRESETS = [
    ("f5_zh.wav",
     "https://raw.githubusercontent.com/SWivid/F5-TTS/main/src/f5_tts/infer/examples/basic/basic_ref_zh.wav",
     "对，这就是我万人敬仰的太乙真人。",
     "普通话·自然女声①"),
    ("cosy_zh.wav",
     "https://raw.githubusercontent.com/FunAudioLLM/CosyVoice/main/asset/zero_shot_prompt.wav",
     "希望你以后能够做的比我还好呦。",
     "普通话·自然女声②"),
    ("f5_en.wav",
     "https://raw.githubusercontent.com/SWivid/F5-TTS/main/src/f5_tts/infer/examples/basic/basic_ref_en.wav",
     "Some call me nature, others call me mother nature.",
     "英语·自然女声"),
]


def to_wav_16k_mono(src, dst):
    """统一转成 16kHz 单声道 WAV（可选，用 ffmpeg 或 macOS afconvert）。
    dots.tts 内部会重采样，所以非必须，但统一格式更稳。"""
    if os.path.exists(src):
        subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@16000", "-c", "1", src, dst],
                       capture_output=True)


def main():
    ok = 0
    for fname, url, text, label in PRESETS:
        dst = os.path.join(OUT, fname)
        if os.path.exists(dst) and os.path.getsize(dst) > 1000:
            print(f"✅ 已存在 {fname:<14} {label}")
            ok += 1
            continue
        try:
            urllib.request.urlretrieve(url, dst)
            print(f"✅ 下载 {fname:<14} {label}  <- {url}")
            ok += 1
        except Exception as e:
            print(f"❌ 下载失败 {fname}: {e}")

    print(f"\n完成：{ok}/{len(PRESETS)}")
    print("提示：想加更多音色，把干净人声 wav 放进 presets/ 并更新 panel_src.py 的 PRESET_DEFS。")


if __name__ == "__main__":
    main()
