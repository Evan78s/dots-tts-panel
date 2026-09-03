# dots.tts 语音合成面板（小红书 · Colab 一键安装）

一键在 Google Colab 启动**公网可访问**的语音合成面板。支持多语言合成、零样本声音克隆、中文方言口音。

模型：[dots.tts](https://github.com/dots-studio/dots.tts)（小红书 HiLab 开源，Apache-2.0 许可）

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

- 文本转语音：中文 / 英文 / 日韩 / 法语等 20+ 语言
- 零样本声音克隆：上传 3-10 秒清晰人声即可模仿音色
- 中文方言口音：粤语 / 四川话 / 东北话 / 北京官话 / 吴语等
- 模型缓存到你的 Google Drive，下次启动免重下 5GB

## 常见问题

| 问题 | 解决 |
|---|---|
| 首次很慢 | 正常，装环境 + 下 5GB 模型，约 5-8 分钟 |
| 面板地址打不开 | 大陆用户需挂梯子（跟访问 Colab 同一个）；或换「全局模式」 |
| 会话断了 / 环境没了 | 重跑「第 1 步」；若 Colab 还开着只是面板挂了，跑「🔄 重启面板」cell |
| 提示 GPU 不可用 | Colab 免费版配额动态，过几小时再试 |

## 许可

本仓库仅提供使用脚本。模型 dots.tts 遵循 [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0) 许可，可商用。
