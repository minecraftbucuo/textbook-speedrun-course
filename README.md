# 📚 Textbook Speedrun Course Skill

> **放进任意一本数学/理工科教材 PDF，让 AI 助手用 Manim 帮你全自动打造一套影院级速通视频课。**

一个基于 **Agent Skills** 规范的开源技能包，沉淀了从「教材 PDF 解析 → 互动偏好定制 → 速通笔记 → `edge-tts` 配音与 100% 逐字字幕 → `Manim` 音画帧级同步动画 → 自动抽帧视觉质检 → 1080p60 成片」的完整工业化制作流水线。

### 🎯 适用学科说明

由于底层动画引擎采用 **Manim + XeLaTeX**，本技能**最适合数学类及强公式推导的理工科教材**，能够充分发挥公式逐行推导、矩阵变换、几何可视化与坐标系动画的优势：
- **核心推荐**：线性代数、高等数学 / 微积分、概率论与数理统计、数学分析、离散数学、复变函数、常微分方程
- **同样适用**：大学物理、信号与系统、自动控制原理、数值分析、算法与数据结构、机器学习数学基础等重公式/图解类教材
- *(注：对于几乎不含公式与几何图示的纯文科/叙事类书籍，Manim 并非最省力的工具，建议优先考虑 PPT/图文类视频方案。)*

适用于 **Antigravity** 等支持 `SKILL.md` 规范的 AI Agent，换一本新教材即可直接复用。

---

## 🎬 实战成品案例（Showcase）

本技能的全部流水线与规范均由真实课程项目实战提炼并验证：

- **线性代数速通课（同济教材）**：👉 [minecraftbucuo/xiandai-sutong](https://github.com/minecraftbucuo/xiandai-sutong)
  - 完整收录了基于本工作流制作的系列剧集工程（每集的 `script.json` 口播分镜、`scene.py` Manim 动画源码、`.srt` 逐字字幕与配套 `速通笔记.md`），可直接参考实际成片组织结构与动画写法。

---

## ✨ 核心特性

- **交互式初始化问答（非硬编码偏好）**：首次为新书建项时，AI 会先通过 **5 项选择题**（教学风格与直觉/应试比例、口播语气与配音音色、分集粒度、独立成课模式、出片画质）+ **1 次开放式个性化需求补充**收集你的要求，并自动写入项目根目录的 `GEMINI.md`，后续每集自动沿用。
- **音频驱动、零累计漂移**：内置 `SyncedScene`（直接对齐 Manim 原生 `renderer.time` 时钟）与 `pace_to(seg, frac)` 节拍器，确保动画与口播严丝合缝，杜绝越往后越不同步。
- **100% 逐字同步内嵌字幕**：`tts_gen.py` 直接基于口播原文生成 `.srt` 与影院描边 `.ass` 字幕并自动烧录，听到什么就看到什么，无需手写两份文案。
- **影院级深色视觉组件库**：`common/theme.py` 提供点阵背景、玻璃卡片、顶栏渐变进度 HUD、自适应任意章节数的全书路线图，以及基于 XeLaTeX 的中英数学公式混排（零缺字方块）。
- **自动化全帧视觉 QA**：`extract_preview.py` 按 `timeline.json` 自动抽取每段末尾预览帧，强制 AI 在 480p 阶段逐帧核查题干完整性、分步动态演算、重叠与越界，通过后再出 1080p60 成片。
- **实战避坑手册**：内置完整教学红线与 9 条 Manim/LaTeX/FFmpeg 高危踩坑指南，大幅降低 AI 写动画的翻车率。

---

## 🔄 完整工作流

```mermaid
flowchart LR
    subgraph P0["Phase 0：新书首次初始化"]
        A["放入教材 PDF"] --> B["5 项偏好问答 + 个性化要求"]
        B --> C["init_course_project.py<br/>生成工程与专属 GEMINI.md"]
        C --> D["read_pdf.py 解析目录<br/>规划 EP01~EPNN 分集表"]
    end

    subgraph P1["Phase 1：单集标准流水线（循环）"]
        E["读教材原页 + 写速通笔记"] --> F["写 script.json<br/>tts_gen.py 生成配音/时间轴/字幕"]
        F --> G["写 scene.py<br/>SyncedScene 音画同步动画"]
        G --> H["480p 预演 + extract_preview.py<br/>逐帧肉眼质检"]
        H -- "有瑕疵" --> G
        H -- "全帧通过" --> I["1080p60 最终出片 + ffprobe 校验"]
    end

    D --> E
```

---

## 🛠️ 环境依赖

使用前请确保本机已安装以下工具：

1. **Python 3.10+** 及核心依赖：
   ```bash
   pip install manim edge-tts pymupdf
   ```
2. **FFmpeg & ffprobe**：确保 `ffmpeg` 和 `ffprobe` 已加入系统 `PATH`。
3. **XeLaTeX**：安装 [TeX Live](https://tug.org/texlive/) 或 [MiKTeX](https://miktex.org/)（用于渲染 `amsmath` / `amssymb` 及 `xeCJK` 中英混排公式）。
4. **中文字体**：系统安装 **Noto Sans SC**（思源黑体，用于字幕与 Manim 文本/XeLaTeX 渲染）。

---

## 📦 安装方式

### 方式一：全局安装（推荐，所有新书项目自动生效）

将本仓库克隆或复制到全局技能目录：

- **Windows (PowerShell)**：
  ```powershell
  git clone https://github.com/minecraftbucuo/textbook-speedrun-course.git "$env:USERPROFILE\.gemini\config\skills\textbook-speedrun-course"
  ```
- **macOS / Linux**：
  ```bash
  git clone https://github.com/minecraftbucuo/textbook-speedrun-course.git ~/.gemini/config/skills/textbook-speedrun-course
  ```

### 方式二：单项目安装

将整个目录放到目标项目的 `.agents/skills/textbook-speedrun-course/` 下即可在当前仓库生效。

---

## 🚀 快速开始

### 1. 用 AI 助手一键启动（推荐）

1. 新建一个空文件夹，把你的教材 `.pdf` 放进去；
2. 用支持该技能的 AI 助手打开该文件夹，直接发送：
   > **“用 textbook-speedrun-course 把这本书做成速通课，先初始化项目并规划全书分集目录。”**
3. AI 会依次：
   - 弹出 **5 道偏好选择题**（教学比例、配音风格、分集粒度、题干模式、画质）；
   - 询问你还有哪些**自己的个性化要求**（如目标受众、重点/跳过章节、特定符号习惯、片头片尾话术等）；
   - 自动初始化工程、解析 PDF 目录与页码偏移、生成全书分集表；
   - 确认分集表后，直接说 **“开始制作 EP01”** 即可全自动产出笔记、配音、字幕与高清成片。

### 2. 手动 CLI 命令速查

你也可以随时直接运行技能内置或初始化后的脚本：

```powershell
# 1. 手动初始化一个新书项目
python scripts\init_course_project.py "E:\Courses\calculus-speedrun" `
  --course-name "高等数学速通课" --pdf "同济高数上册.pdf" --offset 8 `
  --voice "zh-CN-YunxiNeural" --rate "+8%" --quality h

# 2. 查看教材 PDF 书签目录 / 按教材页码读取原页
python scripts\read_pdf.py "同济高数上册.pdf" --toc
python scripts\read_pdf.py "同济高数上册.pdf" --pages 1-8 --offset 8

# 3. 生成配音、timeline.json、SRT 与 ASS 字幕
python scripts\tts_gen.py episodes\ep01_1_1_intro

# 4. 480p 快速预演 + 自动抽取每段预览帧
python scripts\build_ep.py episodes\ep01_1_1_intro --quality l --skip-tts
python scripts\extract_preview.py episodes\ep01_1_1_intro

# 5. 质检通过后导出 1080p60 最终成片
python scripts\build_ep.py episodes\ep01_1_1_intro --quality h --skip-tts
```

---

## 📂 技能目录结构

```text
textbook-speedrun-course/
├── SKILL.md                                # 技能主指令手册（Phase 0 问答初始化 + Phase 1 制作流水线）
├── README.md                               # 项目开源说明文档
├── scripts/                                # 可执行辅助脚本
│   ├── init_course_project.py              # 一键搭建新书速通课工程并写入用户偏好
│   ├── read_pdf.py                         # 教材 PDF 目录解析、偏移读页与关键词检索
│   └── extract_preview.py                  # 按 timeline.json 自动抽取每段预览帧（Visual QA）
├── resources/templates/                    # 新书项目去耦合通用脚手架模板
│   ├── common/
│   │   ├── audio_sync.py                   # SyncedScene 零漂移音画同步引擎
│   │   └── theme.py                        # 影院深色主题、HUD、自适应章节路线图、XeLaTeX 封装
│   ├── scripts/
│   │   ├── tts_gen.py                      # edge-tts 配音 + 48kHz 无缝拼接 + 100% 逐字字幕生成
│   │   └── build_ep.py                     # TTS + Manim + FFmpeg 烧录字幕一键出片脚本
│   ├── GEMINI.md.template                  # 参数化项目规范模板（自动填入用户问答结果）
│   └── gitignore.template                  # 隔离缓存/大体积视频音频的 .gitignore 模板
├── references/                             # 进阶参考文档（按需加载）
│   ├── pedagogy-and-script.md              # 教学设计红线、口播规范、TTS 防粘连断句与 script.json 说明
│   └── manim-visual-and-pitfalls.md        # 画布安全区、组件 API 速查与 9 条高危踩坑红线
└── examples/                               # 最小可运行样板
    ├── script_example.json                 # 标准分镜口播脚本示例
    └── scene_skeleton.py                   # 标准 SyncedScene 动画骨架示例
```

---

## 🤝 欢迎贡献 & 开源协议

- 欢迎提交 Issue / PR 分享更多视觉主题（如浅色黑板风、学术论文风）、配音预设或不同学科的动画组件示例。
- 本项目基于 [MIT License](./LICENSE) 开源，欢迎自由使用、修改与二次分发。
