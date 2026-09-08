#!/usr/bin/env python3
# 生成 dots.tts 面板的内置音色预设参考音频（macOS `say` 生成）
# 用法：python3 gen_presets.py
# 输出：presets/*.wav（48kHz 单声道 16bit）
import subprocess, os

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "presets")
os.makedirs(OUT, exist_ok=True)

# (key, say 语音名, 参考文本, 显示标签)
PRESETS = [
    # ---- 中文 ----
    ("tingting", "Tingting",
     "大家好，我是你的专属语音助手。今天天气很不错，我们一起来聊一聊最近发生的趣事吧。",
     "婷婷（温柔女声）"),
    ("eddy", "Eddy (中文（中国大陆）)",
     "各位听众朋友，大家好。欢迎收听今天的节目，希望你能喜欢我的声音，也祝你度过愉快的一天。",
     "埃迪（沉稳男声）"),
    ("meijia", "Meijia",
     "你好呀，很高兴认识你。今天想跟你分享一些有趣的事情，希望你听了以后会开心一点。",
     "美佳（甜美女声）"),
    ("sandy", "Sandy (中文（中国大陆）)",
     "大家好，我是你的语音助手。无论是工作还是生活，我都愿意随时为你提供帮助和建议。",
     "桑迪（知性女声）"),

    # ---- 英语 ----
    ("samantha", "Samantha",
     "Hello, I'm your friendly voice assistant. It's a pleasure to meet you, and I'm here to help with whatever you need today.",
     "Samantha（美式女声）"),
    ("daniel", "Daniel",
     "Good day to you, and welcome. I hope you find my voice clear, natural, and pleasant to listen to.",
     "Daniel（英式男声）"),
    ("karen", "Karen",
     "G'day, I'm your voice assistant. Let's get started and make the most of today, together.",
     "Karen（澳洲女声）"),
    ("moira", "Moira",
     "Hello there, lovely to meet you. I'll be guiding you through today, so just relax and enjoy the conversation.",
     "Moira（爱尔兰女声）"),

    # ---- 其他语言 ----
    ("kyoko", "Kyoko",
     "こんにちは、あなたの音声アシスタントです。今日もよろしくお願いします。",
     "Kyoko（日语女声）"),
    ("yuna", "Yuna",
     "안녕하세요, 저는 당신의 음성 비서입니다. 오늘도 좋은 하루 보내세요.",
     "Yuna（韩语女声）"),
    ("thomas", "Thomas",
     "Bonjour, je suis votre assistant vocal. C'est un plaisir de vous accompagner aujourd'hui.",
     "Thomas（法语男声）"),
    ("anna", "Anna",
     "Hallo, ich bin deine Sprachassistentin. Schön, dich heute begleiten zu dürfen.",
     "Anna（德语女声）"),

    # ---- 情绪参考（英语，用于把情绪/语气转移到合成结果） ----
    ("goodnews", "Good News",
     "Great news! Everything went perfectly today!",
     "开心·欢快（情绪参考）"),
    ("badnews", "Bad News",
     "I'm afraid I have some difficult news to share with you.",
     "悲伤·低沉（情绪参考）"),
    ("whisper", "Whisper",
     "Psst, come a little closer. I have a secret to tell you, but just between us, quietly.",
     "悄悄话·耳语（情绪参考）"),
]


def main():
    ok = 0
    for key, voice, text, label in PRESETS:
        aiff = f"/tmp/{key}.aiff"
        wav = os.path.join(OUT, key + ".wav")
        r = subprocess.run(["say", "-v", voice, "-o", aiff, text],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"❌ say 失败 [{key}] {voice}: {r.stderr.strip()}")
            continue
        r2 = subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@48000", aiff, wav],
                            capture_output=True, text=True)
        if r2.returncode != 0:
            print(f"❌ 转换失败 [{key}]: {r2.stderr.strip()}")
            continue
        ok += 1
        print(f"✅ {key:<10} {os.path.getsize(wav)/1024:6.1f} KB  {label}")
    print(f"\n完成：{ok}/{len(PRESETS)}")


if __name__ == "__main__":
    main()
