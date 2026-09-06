# dots.tts 语音合成面板（小红书 · Colab 一键安装）

一键在 Google Colab 启动**公网可访问**的语音合成面板。支持多语言合成、零样本声音克隆、中文方言口音。

模型：[dots.tts](https://github.com/studio-dots-ai/dots.tts)（小红书 HiLab 开源，Apache-2.0 许可）

## 🚀 一键打开

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Evan78s/dots-tts-panel/blob/main/dots_tts_panel.ipynb)

> 点上面按钮即可直接在自己的 Colab 打开。

## 使用步骤

1. 点上面的「Open In Colab」按钮
2. 菜单「**运行时 → 更改运行时类型 → 硬件加速器：GPU**」
3. 运行「**第 1 步 一键启动面板**」那个 cell（首次约 5-8 分钟）
4. 浏览器打开打印出来的 `https://xxx.gradio.live` 公网地址

> 想复制到自己的 Colab：打开后点顶部「**复制到云端硬盘**」（File → Save a copy in Drive）。

## 功能

- **全中文界面**：所有按钮、标签、语言选项都是中文（如「中文（普通话）」「英语」「口音：东北话」等）
- **音色预设**：内置 4 个中文音色（婷婷/埃迪/美佳/桑迪），点「试听」可预览，无需上传
- **参考音频转写**：上传 3-10 秒人声 → 自动识别成文字（faster-whisper）→ 可手动更正，文字越准克隆越像
- **音色库**：把上传的声音保存下来（存到你的 Google Drive），以后直接选，不用重复上传
- **音色相似度**：滑块调节克隆相似程度（0.5–3.0，默认 1.5）
- **高级设置**：音色种子（固定数字=每次同一个声音）/ 生成质量·采样步数 / 引导强度 / 文本规范化（数字、符号自动转口语读法）
- 文本转语音：中文 / 英文 / 日韩 / 法语等 20+ 语言
- 零样本声音克隆：上传清晰人声即可模仿音色
- 中文方言口音：北京官话 / 东北话 / 四川话 / 闽南话 / 吴语 / 粤语
- 模型与音色库缓存到你的 Google Drive，下次启动免重下 5GB

## 常见问题

| 问题 | 解决 |
|---|---|
| 首次很慢 | 正常，装环境 + 下 5GB 模型，约 5-8 分钟 |
| 面板地址打不开 | 大陆用户需挂梯子（跟访问 Colab 同一个）；或换「全局模式」 |
| 转写报错 / 转写组件缺失 | 重跑「第 1 步」，会自动补齐 `faster-whisper` 转写组件 |
| 保存的音色下次不见了 | 需挂载了 Google Drive（音色库存在 `dots_cache/voice_library/`） |
| 会话断了 / 环境没了 | 重跑「第 1 步」；若 Colab 还开着只是面板挂了，跑「🔄 重启面板」cell |
| 提示 GPU 不可用 | Colab 免费版配额动态，过几小时再试 |

## 目录说明

| 文件 | 作用 |
|---|---|
| `dots_tts_panel.ipynb` | 主 notebook（内置音色已 base64 嵌入，开箱即用） |
| `panel_src.py` | 面板源码（Gradio Blocks，被 notebook 内嵌，本地可读改） |
| `presets/*.wav` | 内置音色预设的参考音频（macOS `say` 生成，用于克隆参考） |
| `gen_dots_tts_panel.py` | 生成脚本：读取 `panel_src.py` + `presets/` 重新生成 notebook |

> 重新生成 notebook：`python3 gen_dots_tts_panel.py`

## 版本历史

| 版本 | 说明 | Colab 链接 |
|---|---|---|
| **v2.0.0**（最新） | 音色预设（4 个）+ 参考音频转写 + 音色库（持久化到 Drive）+ 音色相似度 + 高级设置（音色种子 / 生成质量 / 引导强度 / 文本规范化）+ 顶部 Banner 联系链接 | [打开](https://colab.research.google.com/github/Evan78s/dots-tts-panel/blob/v2.0.0/dots_tts_panel.ipynb) |
| **v1.0.0** | 基础版：多语言 TTS + 零样本声音克隆 + 公网面板 | [打开](https://colab.research.google.com/github/Evan78s/dots-tts-panel/blob/v1.0.0/dots_tts_panel.ipynb) |

> 想打开旧版：把链接里的 `v2.0.0` 换成 `v1.0.0` 即可。

## 许可

本仓库仅提供使用脚本。模型 dots.tts 遵循 [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) 许可，可商用。
