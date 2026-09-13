import os, json, shutil, time
import gradio as gr
import soundfile as sf
import torch
from dots_tts.runtime import DotsTtsRuntime
from dots_tts.utils.util import seed_everything

# ---------- 加载模型 ----------
print("HF_HOME =", os.environ.get("HF_HOME"), flush=True)
cap = torch.cuda.get_device_capability(0) if torch.cuda.is_available() else (0, 0)
PRECISION = "bfloat16" if cap[0] >= 8 else "float16"
print("加载模型...", flush=True)
runtime = DotsTtsRuntime.from_pretrained("dots-studio/dots.tts-soar", precision=PRECISION, optimize=False)
print("模型加载完成", flush=True)

# ---------- 目录 ----------
# 音色库必须固定放 Google Drive，不能跟着 HF_HOME 走：
#   HF_HOME 只用于模型缓存，第二次运行会被指到本地 SSD（/content/dots_hf_cache，临时盘），
#   若音色库跟着它走，断连重开后音色就会「消失」。所以这里单独固定到 Drive。
DRIVE_CACHE = "/content/drive/MyDrive/dots_cache"
LIB_DIR = os.path.join(DRIVE_CACHE, "voice_library") if os.path.isdir("/content/drive/MyDrive") else "/content/voice_library"
PRESET_DIR = "/content/presets"
os.makedirs(LIB_DIR, exist_ok=True)
os.makedirs(PRESET_DIR, exist_ok=True)
LIB_JSON = os.path.join(LIB_DIR, "voices.json")

# ---------- 内置音色预设（运行时从 GitHub 仓库下载参考音频，避免内嵌 base64 拖慢代码页） ----------
# 每项：(key, 标签, 文件名, 参考文本)。参考文本必须与音频实际内容一致。
PRESET_DEFS = [
    # ---- 普通话：自然真人录音（来自开源项目 F5-TTS / CosyVoice / IndexTTS，MIT / Apache-2.0 许可）----
    ("f5_zh", "普通话·自然女声", "f5_zh.wav", "对，这就是我万人敬仰的太乙真人。"),
    ("cosy_zh", "普通话·温柔女声", "cosy_zh.wav", "希望你以后能够做的比我还好呦。"),
    ("cn_shuoshu", "普通话·评书男声", "cn_shuoshu.wav", "今天咱们开一部新书，叫《赛博朋克二零七七》。"),
    ("cn_nanyou", "普通话·男声", "cn_nanyou.wav", "当然，我是你前男友。"),
    ("cn_dianying", "普通话·电影腔男声", "cn_dianying.wav", "翻译翻译，什么叫惊喜？"),
    # ---- 英语：自然真人录音（F5-TTS / OpenVoice，MIT 许可）----
    ("f5_en", "英语·自然男声", "f5_en.wav", "Some call me nature, others call me mother nature."),
    ("en_teacher", "英语·讲解男声", "en_teacher.wav", "Have you become an expert in deep learning algorithms?"),
    ("en_kid", "英语·活泼少女声", "en_kid.wav", "Oh! Get him, Timmer's! You can't come to Timmer's Tea Party!"),
    ("en_science", "英语·沉稳男声", "en_science.wav", "You know, there's this scientific method which I very much believe in, where something is true to the degree that it is, testably so."),
    ("en_story", "英语·讲述男声", "en_story.wav", "When I was a wanted man, the resistance gave me a lot of help."),
    # ---- 粤语：自然真人录音（FLEURS，CC-BY-4.0 许可）----
    ("yue_f1", "粤语·温柔女声", "yue_f1.wav", "他在 1945 年加入該隊，並一直待到 1958 年。"),
    ("yue_f2", "粤语·自然女声", "yue_f2.wav", "該主管到場時，公寓已發生爆炸。"),
    ("yue_f3", "粤语·清亮女声", "yue_f3.wav", "首先，必須關閉燈具開關，或拔掉電源線。"),
    ("yue_m1", "粤语·沉稳男声", "yue_m1.wav", "畢竟，領袖終究得對團隊的成敗負責。"),
    ("yue_m2", "粤语·自然男声", "yue_m2.wav", "直升機救出了十二名船員，只有一人鼻骨骨折。"),
]
PRESET_BASE = "https://raw.githubusercontent.com/Evan78s/dots-tts-panel/main/presets"

PRESET_LABELS = {}
PRESET_TEXTS = {}
for _key, _label, _file, _text in PRESET_DEFS:
    PRESET_LABELS[_key] = _label
    PRESET_TEXTS[_key] = _text

def _ensure_presets():
    import urllib.request
    from concurrent.futures import ThreadPoolExecutor

    def _dl(_file):
        _path = os.path.join(PRESET_DIR, _file)
        if os.path.exists(_path) and os.path.getsize(_path) > 1000:
            return True
        try:
            urllib.request.urlretrieve(PRESET_BASE + "/" + _file, _path)
            return True
        except Exception as _e:
            print("⚠️ 预设音色「%s」下载失败（仍可上传参考音频使用）：%s" % (_file, _e), flush=True)
            return False

    _files = [_f for _, _, _f, _ in PRESET_DEFS]
    with ThreadPoolExecutor(max_workers=6) as _ex:
        _results = list(_ex.map(_dl, _files))
    print("内置音色预设就绪：%d/%d" % (sum(_results), len(_files)), flush=True)

_ensure_presets()
print("内置音色预设：", list(PRESET_LABELS.values()), flush=True)

# ---------- 统一「选择音色」下拉：内置预设 + 我的音色合并，选起来最省心 ----------
def build_voice_choices():
    choices = [("🎤 默认音色（不克隆）", "")]
    for key, lbl in PRESET_LABELS.items():
        choices.append(("内置 · " + lbl, "preset:" + key))
    for name in load_library():
        choices.append(("我的 · " + name, "lib:" + name))
    return choices

# ---------- 语言（全部中文显示） ----------
LANG_CHOICES = [
    ("自动检测", "auto_detect"),
    # ---- dots.tts 官方支持语言（MiniMax 多语言基准的 24 种语言）----
    ("普通话", "ZH"),
    ("粤语", "口音:粤语"),
    ("英语", "EN"),
    ("西班牙语", "ES"),
    ("法语", "FR"),
    ("德语", "DE"),
    ("意大利语", "IT"),
    ("葡萄牙语", "PT"),
    ("俄语", "RU"),
    ("日语", "JA"),
    ("韩语", "KO"),
    ("阿拉伯语", "AR"),
    ("印地语", "HI"),
    ("印尼语", "ID"),
    ("泰语", "TH"),
    ("越南语", "VI"),
    ("土耳其语", "TR"),
    ("乌克兰语", "UK"),
    ("波兰语", "PL"),
    ("捷克语", "CS"),
    ("罗马尼亚语", "RO"),
    ("希腊语", "EL"),
    ("芬兰语", "FI"),
    ("荷兰语", "NL"),
]

# ---------- 音色库（持久化到 Drive） ----------
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
            device="cuda" if torch.cuda.is_available() else "cpu",
            compute_type="float16" if torch.cuda.is_available() else "int8",
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
def _save_as_wav(src, dst):
    """把任意音频（wav/mp3/m4a/flac 等）转成 16kHz 单声道 WAV 写入 dst。成功返回 True。"""
    try:
        import librosa
        y, _sr = librosa.load(src, sr=16000, mono=True)
        sf.write(dst, y, 16000)
        return True
    except Exception as e:
        print("⚠️ 转 WAV 失败，退回直接复制：%s" % e, flush=True)
        return False

def do_save_voice(name, ref_audio, ref_text):
    if not name or not name.strip():
        raise gr.Error("请先给音色起个名字。")
    if not ref_audio:
        raise gr.Error("请先上传参考音频。")
    name = name.strip()
    lib = load_library()
    base = "%02d_%d" % (len(lib) + 1, int(time.time()))
    dst = os.path.join(LIB_DIR, base + ".wav")
    if not _save_as_wav(ref_audio, dst):
        # 兜底：librosa 也读不了，直接复制原文件并保留原扩展名
        ext = os.path.splitext(ref_audio)[1].lower() or ".wav"
        dst = os.path.join(LIB_DIR, base + ext)
        shutil.copy(ref_audio, dst)
    # 校验保存的文件确实可读、非空
    try:
        import librosa
        _y, _sr = librosa.load(dst, sr=None, mono=True)
        if _y.size == 0:
            raise ValueError("音频为空")
    except Exception as e:
        try:
            os.remove(dst)
        except Exception:
            pass
        raise gr.Error("保存失败：音频无法读取（%s）。请上传 wav/mp3/m4a 格式的清晰人声。" % e)
    lib[name] = {"file": os.path.basename(dst), "prompt_text": (ref_text or "").strip()}
    save_library(lib)
    return (gr.update(choices=build_voice_choices(), value="lib:" + name),
            "✅ 已保存「%s」（已转为 16kHz WAV）。以后在「选择音色」里直接选它即可（现在共 %d 个我的音色）。" % (name, len(lib)))

def do_delete_voice(voice_dd):
    if not voice_dd or not voice_dd.startswith("lib:"):
        return gr.update(choices=build_voice_choices()), "⚠️ 只能删除「我的 · xxx」里的音色（先在上方选中它）。"
    name = voice_dd[len("lib:"):]
    lib = load_library()
    if name in lib:
        _f = lib.pop(name)
        try:
            os.remove(os.path.join(LIB_DIR, _f["file"]))
        except Exception:
            pass
        save_library(lib)
    return gr.update(choices=build_voice_choices(), value=""), "已删除「%s」。" % name

def _read_audio(path):
    """读音频返回 (sr, data)。优先 soundfile（快），失败退回 librosa（兼容 mp3/m4a）。"""
    try:
        data, sr = sf.read(path)
        return sr, data
    except Exception:
        import librosa
        y, sr = librosa.load(path, sr=None, mono=True)
        return sr, y

def preview_voice(voice_dd):
    if not voice_dd:
        return None, "默认音色无需试听，直接合成即可。"
    if voice_dd.startswith("preset:"):
        key = voice_dd[len("preset:"):]
        path = os.path.join(PRESET_DIR, key + ".wav")
        label = PRESET_LABELS.get(key, key)
    elif voice_dd.startswith("lib:"):
        name = voice_dd[len("lib:"):]
        _e = load_library().get(name)
        if not _e:
            return None, "⚠️ 该音色不存在（可能已被删除）。"
        path = os.path.join(LIB_DIR, _e["file"])
        label = name
    else:
        return None, "未知音色。"
    if not os.path.exists(path):
        return None, "⚠️ 音频文件不存在：" + path
    return path, "试听：%s" % label

# ---------- 合成 ----------
def synth(voice_dd, ref_audio, ref_text, synth_text, synth_lang, speaker_scale,
          seed=0, num_steps=10, guidance_scale=1.2, normalize_text=False):
    prompt_path = None
    prompt_text = None
    info = []
    if voice_dd and voice_dd.startswith("preset:"):
        key = voice_dd[len("preset:"):]
        prompt_path = os.path.join(PRESET_DIR, key + ".wav")
        prompt_text = PRESET_TEXTS.get(key, "")
        info.append("音色：" + PRESET_LABELS.get(key, key))
    elif voice_dd and voice_dd.startswith("lib:"):
        name = voice_dd[len("lib:"):]
        _e = load_library().get(name)
        if _e:
            prompt_path = os.path.join(LIB_DIR, _e["file"])
            prompt_text = _e.get("prompt_text") or None
            info.append("音色：" + name)
    elif ref_audio:
        # 没选音色但上传了参考音频 -> 直接用刚上传的（一次性克隆，无需保存）
        prompt_path = ref_audio
        prompt_text = (ref_text or "").strip() or None
        info.append("音色：刚上传的参考音频")
    if not synth_text or not synth_text.strip():
        raise gr.Error("请先输入要合成的文字。")
    if prompt_path and not os.path.exists(prompt_path):
        raise gr.Error("⚠️ 音色音频文件不存在，请重新保存或换个音色。")
    lang = synth_lang or "auto_detect"
    if seed and int(seed) > 0:
        seed_everything(int(seed))
        info.append("音色种子 %d" % int(seed))
    try:
        res = runtime.generate(text=synth_text.strip(), language=lang,
                               prompt_audio_path=prompt_path, prompt_text=prompt_text,
                               speaker_scale=speaker_scale,
                               num_steps=int(num_steps), guidance_scale=float(guidance_scale),
                               normalize_text=bool(normalize_text))
    except Exception as e:
        raise gr.Error("合成失败：" + str(e))
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

# ---------- 顶部 Banner（标题 + 说明 + 联系链接） ----------
BILIBILI_URL = "https://space.bilibili.com/380877309"
DAOYAKE_URL = "https://www.daoyanke.cn"

_BANNER_HTML = (
    '<div style="text-align:center;padding:20px 14px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:14px;margin-bottom:14px;">'
    '<h1 style="color:#fff;margin:0 0 6px;font-size:28px;">🎙️ dots.tts 语音合成面板</h1>'
    '<p style="color:#eaeaff;margin:0 0 14px;font-size:15px;">输入文字 → 选音色（内置 / 我的音色 / 直接上传）→ 选语言 → 一键合成<br>支持声音克隆 · 24 种官方语言（普通话/粤语/英语等）</p>'
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
            gr.Markdown("## ① 选择音色")
            voice_dd = gr.Dropdown(build_voice_choices(), value="", label="选择音色",
                                   info="内置音色 + 你保存的「我的音色」都在这一个下拉里")
            with gr.Row():
                preview_btn = gr.Button("试听选中音色")
                delete_btn = gr.Button("删除选中的「我的音色」")
            preview_audio = gr.Audio(label="试听", type="filepath")

            gr.Markdown("## ➕ 添加我的音色（傻瓜三步）")
            gr.Markdown("上传一段 **3-10 秒的清晰人声**（无背景噪音、单一说话人），会自动识别文字；核对后起个名字保存，以后在「选择音色」里直接选。")
            ref_audio = gr.Audio(label="① 上传参考音频", type="filepath")
            ref_text = gr.Textbox(label="② 参考音频文字（自动识别，可手动更正）", lines=3,
                                  placeholder="上传后自动识别填写；文字越准，克隆越像。")
            with gr.Row():
                transcribe_btn = gr.Button("重新识别文字")
                voice_name = gr.Textbox(label="③ 给它起个名字", placeholder="例如：我的声音")
            save_btn = gr.Button("💾 保存为我的音色", variant="primary")
            voice_status = gr.Textbox(label="提示", interactive=False)

        with gr.Column(scale=1):
            gr.Markdown("## ② 合成")
            synth_text = gr.Textbox(label="要合成的文字", lines=4, value="你好，欢迎使用 dots.tts 语音合成面板。")
            synth_lang = gr.Dropdown(LANG_CHOICES, value="auto_detect", label="语言")
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

    # 上传音频后自动识别转写文字（无需手动点按钮）
    ref_audio.change(do_transcribe, ref_audio, [ref_text, voice_status])
    transcribe_btn.click(do_transcribe, ref_audio, [ref_text, voice_status])
    preview_btn.click(preview_voice, voice_dd, [preview_audio, voice_status])
    save_btn.click(do_save_voice, [voice_name, ref_audio, ref_text], [voice_dd, voice_status])
    delete_btn.click(do_delete_voice, voice_dd, [voice_dd, voice_status])
    synth_btn.click(synth, [voice_dd, ref_audio, ref_text, synth_text, synth_lang,
                            speaker_scale, seed, num_steps, guidance_scale, normalize_text],
                    [result_audio, result_info])

print("启动 Gradio 面板（share=True，正在建立公网隧道）...", flush=True)
demo.launch(share=True, debug=False)
