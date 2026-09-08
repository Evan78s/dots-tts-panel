import os, json, shutil, time
import gradio as gr
import soundfile as sf
import torch
from dots_tts.runtime import DotsTtsRuntime
from dots_tts.utils.util import seed_everything

# ---------- 本地路径（都在本脚本所在目录） ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRESET_DIR = os.path.join(BASE_DIR, "presets")           # 内置音色参考音频
LIB_DIR = os.path.join(BASE_DIR, "voice_library")        # 音色库（持久化到本地）
os.makedirs(LIB_DIR, exist_ok=True)
os.makedirs(PRESET_DIR, exist_ok=True)
LIB_JSON = os.path.join(LIB_DIR, "voices.json")

# ---------- 设备 & 精度 ----------
if torch.cuda.is_available():
    cap = torch.cuda.get_device_capability(0)
    PRECISION = "bfloat16" if cap[0] >= 8 else "float16"
    DEVICE_NOTE = "CUDA"
elif torch.backends.mps.is_available():
    PRECISION = "float16"
    DEVICE_NOTE = "Apple MPS"
else:
    PRECISION = "float32"
    DEVICE_NOTE = "CPU（无 GPU，会比较慢）"
print("运行设备：", DEVICE_NOTE, "| 精度：", PRECISION, flush=True)

# ---------- 模型：默认自动下载；也可用 DOTS_MODEL_DIR 指向本地已下载目录 ----------
MODEL = os.environ.get("DOTS_MODEL_DIR") or "dots-studio/dots.tts-soar"
print("加载模型...（首次会自动下载约 5GB）", flush=True)
runtime = DotsTtsRuntime.from_pretrained(MODEL, precision=PRECISION, optimize=False)
print("模型加载完成", flush=True)

# ---------- 内置音色预设（本地仓库自带 presets/，缺失时从 GitHub 下载） ----------
# 每项：(key, 标签, 文件名, 参考文本)。参考文本必须与音频实际内容一致。
PRESET_DEFS = [
    ("tingting", "婷婷（温柔女声）", "tingting.wav", "大家好，我是你的专属语音助手。今天天气很不错，我们一起来聊一聊最近发生的趣事吧。"),
    ("eddy", "埃迪（沉稳男声）", "eddy.wav", "各位听众朋友，大家好。欢迎收听今天的节目，希望你能喜欢我的声音，也祝你度过愉快的一天。"),
    ("meijia", "美佳（甜美女声）", "meijia.wav", "你好呀，很高兴认识你。今天想跟你分享一些有趣的事情，希望你听了以后会开心一点。"),
    ("sandy", "桑迪（知性女声）", "sandy.wav", "大家好，我是你的语音助手。无论是工作还是生活，我都愿意随时为你提供帮助和建议。"),
    ("samantha", "Samantha（美式女声）", "samantha.wav", "Hello, I'm your friendly voice assistant. It's a pleasure to meet you, and I'm here to help with whatever you need today."),
    ("daniel", "Daniel（英式男声）", "daniel.wav", "Good day to you, and welcome. I hope you find my voice clear, natural, and pleasant to listen to."),
    ("karen", "Karen（澳洲女声）", "karen.wav", "G'day, I'm your voice assistant. Let's get started and make the most of today, together."),
    ("moira", "Moira（爱尔兰女声）", "moira.wav", "Hello there, lovely to meet you. I'll be guiding you through today, so just relax and enjoy the conversation."),
    ("kyoko", "Kyoko（日语女声）", "kyoko.wav", "こんにちは、あなたの音声アシスタントです。今日もよろしくお願いします。"),
    ("yuna", "Yuna（韩语女声）", "yuna.wav", "안녕하세요, 저는 당신의 음성 비서입니다. 오늘도 좋은 하루 보내세요."),
    ("thomas", "Thomas（法语男声）", "thomas.wav", "Bonjour, je suis votre assistant vocal. C'est un plaisir de vous accompagner aujourd'hui."),
    ("anna", "Anna（德语女声）", "anna.wav", "Hallo, ich bin deine Sprachassistentin. Schön, dich heute begleiten zu dürfen."),
    ("goodnews", "开心·欢快（情绪参考）", "goodnews.wav", "Great news! Everything went perfectly today!"),
    ("badnews", "悲伤·低沉（情绪参考）", "badnews.wav", "I'm afraid I have some difficult news to share with you."),
    ("whisper", "悄悄话·耳语（情绪参考）", "whisper.wav", "Psst, come a little closer. I have a secret to tell you, but just between us, quietly."),
]
PRESET_BASE = "https://raw.githubusercontent.com/Evan78s/dots-tts-panel/main/presets"

PRESET_LABELS = {}
PRESET_TEXTS = {}
for _key, _label, _file, _text in PRESET_DEFS:
    PRESET_LABELS[_key] = _label
    PRESET_TEXTS[_key] = _text

def _ensure_presets():
    import urllib.request
    for _key, _label, _file, _text in PRESET_DEFS:
        _path = os.path.join(PRESET_DIR, _file)
        if os.path.exists(_path) and os.path.getsize(_path) > 1000:
            continue
        try:
            urllib.request.urlretrieve(PRESET_BASE + "/" + _file, _path)
            print("下载预设音色：%s" % _label, flush=True)
        except Exception as _e:
            print("⚠️ 预设音色「%s」下载失败（仍可上传参考音频使用）：%s" % (_label, _e), flush=True)

_ensure_presets()
print("内置音色预设：", list(PRESET_LABELS.values()), flush=True)

PRESET_CHOICES = [("默认音色（不克隆）", "")] + [(lbl, key) for key, lbl in PRESET_LABELS.items()]

# ---------- 语言（全部中文显示） ----------
LANG_CHOICES = [
    ("自动检测", "auto_detect"),
    ("中文（普通话）", "ZH"),
    ("英语", "EN"),
    ("粤语", "Cantonese"),
    ("日语", "JA"),
    ("韩语", "KO"),
    ("法语", "FR"),
    ("德语", "DE"),
    ("西班牙语", "ES"),
    ("俄语", "RU"),
    ("阿拉伯语", "AR"),
    ("印地语", "HI"),
    ("葡萄牙语", "PT"),
    ("意大利语", "IT"),
    ("泰语", "TH"),
    ("越南语", "VI"),
    ("印尼语", "ID"),
    ("捷克语", "CS"),
    ("荷兰语", "NL"),
    ("芬兰语", "FI"),
    ("希腊语", "EL"),
    ("波兰语", "PL"),
    ("罗马尼亚语", "RO"),
    ("土耳其语", "TR"),
    ("乌克兰语", "UK"),
    ("口音：北京官话", "口音:北京官话"),
    ("口音：东北话", "口音:东北话"),
    ("口音：四川话", "口音:四川话"),
    ("口音：闽南话", "口音:闽南话"),
    ("口音：吴语", "口音:吴语"),
]

# ---------- 音色库（持久化到本地） ----------
def load_library():
    if os.path.exists(LIB_JSON):
        try:
            return json.load(open(LIB_JSON, encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_library(lib):
    json.dump(lib, open(LIB_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- 参考音频转写（ASR） ----------
_whisper = None
def get_whisper():
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        _whisper = WhisperModel(
            "small",
            device="cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu"),
            compute_type="float16" if (torch.cuda.is_available() or torch.backends.mps.is_available()) else "int8",
        )
    return _whisper

def do_transcribe(ref_audio):
    if not ref_audio:
        return "", "⚠️ 请先上传参考音频。"
    try:
        model = get_whisper()
        segments, _ = model.transcribe(ref_audio, beam_size=1)
        text = "".join(s.text for s in segments).strip()
        return text, "✅ 识别完成，请核对并更正下方文字（文字越准，克隆越像）。"
    except Exception as e:
        return "", "⚠️ 识别失败：" + str(e) + "（可手动填写参考音频说了什么）"

# ---------- 音色库操作 ----------
def do_save_voice(name, ref_audio, ref_text):
    if not name or not name.strip():
        raise gr.Error("请先填写音色名称。")
    if not ref_audio:
        raise gr.Error("请先上传参考音频。")
    name = name.strip()
    lib = load_library()
    ext = os.path.splitext(ref_audio)[1].lower() or ".wav"
    dst = os.path.join(LIB_DIR, "%02d_%d%s" % (len(lib) + 1, int(time.time()), ext))
    shutil.copy(ref_audio, dst)
    lib[name] = {"file": os.path.basename(dst), "prompt_text": (ref_text or "").strip()}
    save_library(lib)
    choices = list(lib.keys())
    return gr.update(choices=choices, value=name), "✅ 已保存音色「%s」到音色库（共 %d 个）。" % (name, len(choices))

def do_delete_voice(lib_voice):
    lib = load_library()
    if lib_voice in lib:
        _f = lib.pop(lib_voice)
        try:
            os.remove(os.path.join(LIB_DIR, _f["file"]))
        except Exception:
            pass
        save_library(lib)
    choices = list(lib.keys())
    return gr.update(choices=choices, value=None), "已删除音色「%s」。" % lib_voice

def preview_preset(preset):
    if not preset:
        return None, "默认音色无需试听，直接合成即可。"
    path = os.path.join(PRESET_DIR, preset + ".wav")
    if not os.path.exists(path):
        return None, "⚠️ 预设音频不存在。"
    data, sr = sf.read(path)
    return (sr, data), "试听预设音色：%s" % PRESET_LABELS.get(preset, preset)

# ---------- 合成 ----------
def synth(source, preset, ref_audio, ref_text, lib_voice, synth_text, synth_lang, speaker_scale,
          seed=0, num_steps=10, guidance_scale=1.2, normalize_text=False):
    prompt_path = None
    prompt_text = None
    info = []
    if source == "音色预设":
        if preset:
            prompt_path = os.path.join(PRESET_DIR, preset + ".wav")
            prompt_text = PRESET_TEXTS.get(preset, "")
            info.append("音色预设：" + PRESET_LABELS.get(preset, preset))
    elif source == "上传参考音频":
        if ref_audio:
            prompt_path = ref_audio
            prompt_text = (ref_text or "").strip() or None
            info.append("音色：上传参考音频")
    else:
        if lib_voice:
            _e = load_library().get(lib_voice)
            if _e:
                prompt_path = os.path.join(LIB_DIR, _e["file"])
                prompt_text = _e.get("prompt_text") or None
                info.append("音色库：" + lib_voice)
    if not synth_text or not synth_text.strip():
        raise gr.Error("请先输入要合成的文字。")
    lang = synth_lang or "auto_detect"
    if seed and int(seed) > 0:
        seed_everything(int(seed))
        info.append("音色种子 %d" % int(seed))
    res = runtime.generate(text=synth_text.strip(), language=lang,
                           prompt_audio_path=prompt_path, prompt_text=prompt_text,
                           speaker_scale=speaker_scale,
                           num_steps=int(num_steps), guidance_scale=float(guidance_scale),
                           normalize_text=bool(normalize_text))
    audio = res["audio"].float().cpu().squeeze().numpy()
    sr = res["sample_rate"]
    dur = round(len(audio) / sr, 2)
    info.append("语言：" + lang)
    info.append("%d 秒 · %d Hz" % (round(dur), sr))
    if prompt_path:
        info.append("音色相似度 %.1f" % speaker_scale)
    else:
        info.append("未用参考音色（模型默认声音）")
    return (sr, audio), " · ".join(info)

# ---------- 音色来源切换 ----------
def on_source_change(src):
    if src == "音色预设":
        return (gr.update(visible=True), gr.update(visible=True), gr.update(visible=True),
                gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                gr.update(visible=False))
    if src == "上传参考音频":
        return (gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
                gr.update(visible=True), gr.update(visible=True), gr.update(visible=True),
                gr.update(visible=True), gr.update(visible=True), gr.update(visible=False),
                gr.update(visible=False))
    return (gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
            gr.update(visible=False), gr.update(visible=False), gr.update(visible=False),
            gr.update(visible=False), gr.update(visible=False), gr.update(visible=True),
            gr.update(visible=True))

# ---------- 顶部 Banner ----------
BILIBILI_URL = "https://space.bilibili.com/380877309"
DAOYAKE_URL = "https://www.daoyanke.cn"
_BANNER_HTML = (
    '<div style="text-align:center;padding:20px 14px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:14px;margin-bottom:14px;">'
    '<h1 style="color:#fff;margin:0 0 6px;font-size:28px;">🎙️ dots.tts 语音合成面板</h1>'
    '<p style="color:#eaeaff;margin:0 0 14px;font-size:15px;">输入文字 → 选音色（预设 / 上传克隆 / 音色库）→ 选语言 → 一键合成<br>支持声音克隆 · 20+ 语言 · 中文方言口音</p>'
    '<p style="margin:0;">'
    '<a href="' + BILIBILI_URL + '" target="_blank" rel="noopener" style="display:inline-block;color:#fff;background:rgba(255,255,255,0.22);padding:5px 16px;border-radius:18px;text-decoration:none;margin:0 6px;font-weight:600;">📺 B站</a>'
    '<a href="' + DAOYAKE_URL + '" target="_blank" rel="noopener" style="display:inline-block;color:#fff;background:rgba(255,255,255,0.22);padding:5px 16px;border-radius:18px;text-decoration:none;margin:0 6px;font-weight:600;">🎬 导演课</a>'
    '</p></div>'
)

# ---------- 界面 ----------
with gr.Blocks(title="dots.tts 语音合成面板") as demo:
    gr.HTML(_BANNER_HTML)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## ① 音色设置")
            source = gr.Radio(["音色预设", "上传参考音频", "音色库"], value="音色预设", label="音色来源")
            preset_dd = gr.Dropdown(PRESET_CHOICES, value="", label="音色预设")
            preview_btn = gr.Button("试听预设音色")
            gr.Markdown("💡 **调情绪/语气**：情绪来自参考音频的韵律——选「情绪参考」预设，或上传带目标情绪的人声（3-10 秒）；再用下方「音色种子」换韵律。")
            preview_audio = gr.Audio(label="预设试听")
            ref_audio = gr.Audio(label="参考音频（3-10 秒清晰人声）", type="filepath", visible=False)
            transcribe_btn = gr.Button("识别转写", visible=False)
            ref_text = gr.Textbox(label="参考音频文字（自动识别，可手动更正）", lines=3, visible=False,
                                  placeholder="上传音频后点「识别转写」自动填写；也可直接手填。文字越准，克隆越像。")
            voice_name = gr.Textbox(label="音色名称（保存到音色库）", visible=False, placeholder="例如：我的声音")
            save_btn = gr.Button("保存到音色库", visible=False)
            lib_dd = gr.Dropdown(choices=list(load_library().keys()), value=None,
                                 label="音色库（已保存的音色）", visible=False)
            delete_btn = gr.Button("删除选中音色", visible=False)
            voice_status = gr.Textbox(label="提示", interactive=False)

        with gr.Column(scale=1):
            gr.Markdown("## ② 合成")
            synth_text = gr.Textbox(label="要合成的文字", lines=4, value="你好，欢迎使用 dots.tts 语音合成面板。")
            synth_lang = gr.Dropdown(LANG_CHOICES, value="ZH", label="语言")
            speaker_scale = gr.Slider(minimum=0.5, maximum=3.0, value=1.5, step=0.1,
                                      label="音色相似度（使用参考音色时生效，越高越像）")
            with gr.Accordion("⚙️ 高级设置（可选）", open=False):
                seed = gr.Slider(minimum=0, maximum=9999, value=0, step=1,
                                 label="音色种子（0=随机；固定数字=每次生成同一个声音）")
                num_steps = gr.Slider(minimum=10, maximum=32, value=10, step=1,
                                      label="生成质量·采样步数（越大越细腻，但更慢）")
                guidance_scale = gr.Slider(minimum=0.5, maximum=3.0, value=1.2, step=0.1,
                                           label="引导强度（越大越贴合文字与参考音色）")
                normalize_text = gr.Checkbox(value=False, label="文本规范化（数字/符号自动转口语读法）")
            synth_btn = gr.Button("开始合成", variant="primary")
            result_audio = gr.Audio(label="合成结果")
            result_info = gr.Textbox(label="结果信息", interactive=False)

    _voice_components = [preset_dd, preview_btn, preview_audio, ref_audio, transcribe_btn,
                         ref_text, voice_name, save_btn, lib_dd, delete_btn]
    source.change(on_source_change, source, _voice_components)
    preview_btn.click(preview_preset, preset_dd, [preview_audio, voice_status])
    transcribe_btn.click(do_transcribe, ref_audio, [ref_text, voice_status])
    save_btn.click(do_save_voice, [voice_name, ref_audio, ref_text], [lib_dd, voice_status])
    delete_btn.click(do_delete_voice, lib_dd, [lib_dd, voice_status])
    synth_btn.click(synth, [source, preset_dd, ref_audio, ref_text, lib_dd, synth_text, synth_lang,
                            speaker_scale, seed, num_steps, guidance_scale, normalize_text],
                    [result_audio, result_info])

# 本地默认只开 localhost；想开公网隧道设 GRADIO_SHARE=1
_SHARE = os.environ.get("GRADIO_SHARE", "0") == "1"
print("启动 Gradio 面板（share=%s）..." % _SHARE, flush=True)
demo.launch(share=_SHARE, debug=False, server_name="0.0.0.0", server_port=7860)
