# dots.tts 语音合成面板（小红书 · Colab 一键安装）

一键在 Google Colab 启动**公网可访问**的语音合成面板。支持 24 种官方语言合成、零样本声音克隆、粤语口音。

模型：[dots.tts](https://github.com/studio-dots-ai/dots.tts)（小红书 HiLab 开源，Apache-2.0 许可）

## 🚀 一键打开

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Evan78s/dots-tts-panel/blob/main/dots_tts_panel.ipynb)

> 点上面按钮即可直接在自己的 Colab 打开。

## 使用步骤

1. 点上面的「Open In Colab」按钮
2. 菜单「**运行时 → 更改运行时类型 → 硬件加速器：GPU**」
3. **首次使用**：从上到下跑「第 0 步 → 第 4 步」（约 5-8 分钟，会自动安装依赖 + 缓存到 Drive）
4. **以后每次 / 断连重开**：**重跑全部**（Runtime → Run all / 全部运行，约 2-4 分钟，**免重装环境、模型秒加载**）
5. 浏览器打开打印出来的 `https://xxx.gradio.live` 公网地址

> 想复制到自己的 Colab：打开后点顶部「**复制到云端硬盘**」（File → Save a copy in Drive）。

### 为什么断连后不用重装了

- **环境**（Python + torch + dots.tts）首次装好后会**打包成 `py311.tar.gz` 存到 Drive**，断连重开直接解包恢复，不再重跑安装。
- **模型**缓存到 Drive（`dots_cache/hub/`），每次启动自动**复制到本地 SSD** 再加载，比直接从 Drive 慢读快数倍。
- **音色库**存到 Drive（`dots_cache/voice_library/`），保存的音色下次还在。

## 功能

- **全中文界面**：所有按钮、标签、语言选项都是中文（如「普通话」「粤语」「英语」「日语」等）
- **选择音色（统一）**：内置 20 个**自然真人录音**音色（普通话 5 个 + 英语 5 个 + 粤语 10 个，粤语 5男5女）和你的「我的音色」合并成**一个下拉**，点「试听」可预览
- **➕ 添加我的音色（傻瓜三步）**：上传 3-10 秒人声 → 自动识别文字（可更正）→ 起名保存，以后直接在「选择音色」里选
- **音色库持久化**：保存的音色存到你的 Google Drive（`dots_cache/voice_library/`），断连重开还在
- **音色相似度**：滑块调节克隆相似程度（0.5–3.0，默认 1.5）
- **高级设置**：音色种子（固定数字=每次同一个声音）/ 生成质量·采样步数 / 引导强度 / 文本规范化（数字、符号自动转口语读法）
- 文本转语音：普通话 / 粤语 / 英语 / 日韩法德等 24 种官方语言（dots.tts 的 MiniMax 多语言基准覆盖的语言）
- 零样本声音克隆：上传清晰人声即可模仿音色
- 粤语方言口音：粤语（官方标签 `口音:粤语`）
- **情绪/语气**：情绪来自参考音频的韵律——上传带目标情绪的人声（3-10 秒），再用「音色种子」换韵律/停顿
- 模型与音色库缓存到你的 Google Drive，下次启动免重下 5GB

## 音色预设说明（重要）

**为什么以前的内置音色质量差？** 旧版内置音色是用 macOS `say` 机器合成的，韵律扁平、音色机械，用来做克隆参考时会把这种「机器感」一起学进去。

**对标开源原文件：** dots.tts 是**零样本克隆模型**，官方（studio-dots-ai/dots.tts）**不提供任何内置音色**，HF 模型仓库里也没有示例人声（只有权重文件）。所以音色预设只能自己准备参考音频——必须用**干净的自然人声录音**（3-10 秒、单一人声、无背景噪音）。

现在内置的 20 个音色取自开源项目的人声示例（**自然真人录音**，非机器合成）：

| 文件 | 来源 | 许可 |
|---|---|---|
| `f5_zh.wav` | [F5-TTS](https://github.com/SWivid/F5-TTS) 示例人声 | MIT |
| `cosy_zh.wav` | [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) 示例人声 | Apache-2.0 |
| `cn_shuoshu.wav` | [IndexTTS](https://github.com/index-tts/index-tts) 示例音频 | 见 IndexTTS 仓库 |
| `cn_nanyou.wav` | [IndexTTS](https://github.com/index-tts/index-tts) 示例音频 | 见 IndexTTS 仓库 |
| `cn_dianying.wav` | [IndexTTS](https://github.com/index-tts/index-tts) 示例音频 | 见 IndexTTS 仓库 |
| `f5_en.wav` | [F5-TTS](https://github.com/SWivid/F5-TTS) 示例人声 | MIT |
| `en_teacher.wav` | [OpenVoice](https://github.com/myshell-ai/OpenVoice) 示例音频 | MIT |
| `en_kid.wav` | [OpenVoice](https://github.com/myshell-ai/OpenVoice) 示例音频 | MIT |
| `en_science.wav` | [OpenVoice](https://github.com/myshell-ai/OpenVoice) 示例音频 | MIT |
| `en_story.wav` | [OpenVoice](https://github.com/myshell-ai/OpenVoice) 示例音频 | MIT |
| `yue_f1.wav` | [FLEURS](https://huggingface.co/datasets/google/fleurs) 粤语人声 | CC-BY-4.0 |
| `yue_f2.wav` | [FLEURS](https://huggingface.co/datasets/google/fleurs) 粤语人声 | CC-BY-4.0 |
| `yue_f3.wav` | [FLEURS](https://huggingface.co/datasets/google/fleurs) 粤语人声 | CC-BY-4.0 |
| `yue_f4.wav` | [FLEURS](https://huggingface.co/datasets/google/fleurs) 粤语人声 | CC-BY-4.0 |
| `yue_f5.wav` | [FLEURS](https://huggingface.co/datasets/google/fleurs) 粤语人声 | CC-BY-4.0 |
| `yue_m1.wav` | [FLEURS](https://huggingface.co/datasets/google/fleurs) 粤语人声 | CC-BY-4.0 |
| `yue_m2.wav` | [FLEURS](https://huggingface.co/datasets/google/fleurs) 粤语人声 | CC-BY-4.0 |
| `yue_m3.wav` | [FLEURS](https://huggingface.co/datasets/google/fleurs) 粤语人声 | CC-BY-4.0 |
| `yue_m4.wav` | [FLEURS](https://huggingface.co/datasets/google/fleurs) 粤语人声 | CC-BY-4.0 |
| `yue_m5.wav` | [FLEURS](https://huggingface.co/datasets/google/fleurs) 粤语人声 | CC-BY-4.0 |

**想加更多音色（普通话 / 粤语等）：** 把任意干净人声 wav 放进 `presets/`，然后在 `panel_src.py` 的 `PRESET_DEFS` 里加一行 `(key, 标签, 文件名, 参考文字)`，重跑 `python3 gen_dots_tts_panel.py` 即可。**粤语音色**同理：找一个讲粤语的人声录音（3-10 秒）放进去就行。

## 关于「粤语」语言

- 面板里选「粤语」用的是官方标签 `口音:粤语`（= **用粤语口音朗读你输入的文字**）。
- 如果你输入的是**普通话文字**，出来的就是「普通话 + 粤语口音」，听起来像普通话，这是正常的。
- 想要**真正的粤语**，请在文字输入框里直接写**粤语白话**（例如「你食咗饭未呀？」），再选「粤语」。

## 常见问题

| 问题 | 解决 |
|---|---|
| 首次很慢 | 正常，装环境 + 下 5GB 模型，约 5-8 分钟 |
| 面板地址打不开 | 大陆用户需挂梯子（跟访问 Colab 同一个）；或换「全局模式」 |
| 断连后还要重装吗 | 不用了，环境已缓存到 Drive，重跑全部约 2-4 分钟 |
| 等了很久没地址 | 最多等 20 分钟；若进程崩了会打印日志末尾，照着修 |
| 转写报错 / 组件缺失 | 环境已内置 `faster-whisper`；仍报错可删 Drive 的 `py311.tar.gz` 重装一次 |
| 保存的音色下次不见了 | 需挂载了 Google Drive（音色库存在 `dots_cache/voice_library/`） |
| 想彻底重装 | 删除 Drive 的 `dots_cache/py311.tar.gz`，再重跑全部会自动重装 |
| 提示 GPU 不可用 | Colab 免费版配额动态，过几小时再试 |

## 目录说明

| 文件 | 作用 |
|---|---|
| `dots_tts_panel.ipynb` | 主 notebook（音色预设运行时从本仓库 `presets/` 下载，代码轻量不卡顿） |
| `panel_src.py` | 面板源码（Gradio Blocks，被 notebook 内嵌，本地可读改） |
| `presets/*.wav` | 内置音色预设的参考音频（自然真人录音，来自 F5-TTS / CosyVoice / IndexTTS / OpenVoice / FLEURS） |
| `gen_dots_tts_panel.py` | 生成脚本：读取 `panel_src.py` + `presets/` 重新生成 notebook |

> 重新生成 notebook：`python3 gen_dots_tts_panel.py`

## 版本历史

| 版本 | 说明 | Colab 链接 |
|---|---|---|
| **v2.5.0**（最新） | 粤语音色扩至 10 个（5 男 5 女）：重新精选 FLEURS 粤语真人录音，按音高分层 + SNR 筛选出更干净、音色各异的参考音频 → 内置音色扩至 20 个（普通话 5 + 英语 5 + 粤语 10） | [打开](https://colab.research.google.com/github/Evan78s/dots-tts-panel/blob/main/dots_tts_panel.ipynb) |
| **v2.4.2** | 修正语言列表：对齐 dots.tts 官方 MiniMax 24 种语言（移除不支持的「北京官话/东北话」等假方言标签，修复切语言不生效）；试听改为直接返回音频文件（更快）+ 预设音色并行下载 | [打开](https://colab.research.google.com/github/Evan78s/dots-tts-panel/blob/v2.4.2/dots_tts_panel.ipynb) |
| **v2.4.1** | 移除冗余的「🚀 一键启动」格（与第 1-4 步重复，断连重开直接「重跑全部」即可）+ 修正 notebook 内置音色数文案 | [打开](https://colab.research.google.com/github/Evan78s/dots-tts-panel/blob/v2.4.1/dots_tts_panel.ipynb) |
| **v2.4.0** | 新增 5 个粤语音色（3 女声 + 2 男声，取自 FLEURS 粤语真人录音）→ 内置音色扩至 15 个（普通话 5 + 英语 5 + 粤语 5） | [打开](https://colab.research.google.com/github/Evan78s/dots-tts-panel/blob/v2.4.0/dots_tts_panel.ipynb) |
| **v2.3.0** | 新增 7 个自然真人音色（3 普通话男声 + 4 英语，取自 IndexTTS / OpenVoice）→ 内置音色扩至 10 个 | [打开](https://colab.research.google.com/github/Evan78s/dots-tts-panel/blob/v2.3.0/dots_tts_panel.ipynb) |
| **v2.2.0** | 修复「选粤语出普通话」（粤语改用官方标签 `口音:粤语`）+ 语言列表对齐官方 100+ 语言 + 音色预设换成自然真人录音（替换 macOS say 机器声）+ **傻瓜式加音色**（统一下拉/上传自动转写/一键保存）+ **修复音色库断连后消失**（固定存 Drive，不再跟模型缓存路径走） | [打开](https://colab.research.google.com/github/Evan78s/dots-tts-panel/blob/v2.2.0/dots_tts_panel.ipynb) |
| **v2.1.0** | 环境打包缓存到 Drive（断连免重装）+ 模型复制本地 SSD（加载快）+ 启动前杀旧进程 + 智能等待地址（20 分钟）+ 代码块拆分 + 「🚀 一键启动」 | [打开](https://colab.research.google.com/github/Evan78s/dots-tts-panel/blob/v2.1.0/dots_tts_panel.ipynb) |
| **v2.0.0** | 音色预设（4 个）+ 参考音频转写 + 音色库（持久化到 Drive）+ 音色相似度 + 高级设置（音色种子 / 生成质量 / 引导强度 / 文本规范化）+ 顶部 Banner 联系链接 | [打开](https://colab.research.google.com/github/Evan78s/dots-tts-panel/blob/v2.0.0/dots_tts_panel.ipynb) |
| **v1.0.0** | 基础版：多语言 TTS + 零样本声音克隆 + 公网面板 | [打开](https://colab.research.google.com/github/Evan78s/dots-tts-panel/blob/v1.0.0/dots_tts_panel.ipynb) |

> 想打开旧版：把链接里的 `v2.0.0` 换成 `v1.0.0` 即可。

## 许可

本仓库仅提供使用脚本。模型 dots.tts 遵循 [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) 许可，可商用。
