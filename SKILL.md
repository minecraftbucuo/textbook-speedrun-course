---
name: textbook-speedrun-course
description: >-
  Turn any textbook PDF into a complete, studio-quality Manim + edge-tts speedrun
  video course series (with 100% verbatim burned-in subtitles, zero-drift audio sync,
  standalone study notes, and automated frame-by-frame visual QA). Use this skill
  whenever the user wants to bootstrap a new book's crash-course repo from a PDF,
  plan a textbook's episode roadmap, or produce/revise an episode in an existing
  speedrun course project (e.g., "把这本书做成速通课", "用速通课流程做新一集",
  "create a textbook speedrun video course").
---

# Textbook Speedrun Course Production Skill

本技能将「教材 PDF → 速通笔记 → `edge-tts` 配音与逐字字幕 → `Manim` 音画帧级同步动画 → 480p 全帧质检 → 1080p60 成片」的完整工作流标准化，放进任意一本新教材 PDF 即可直接复用。

## 环境依赖

开始前确保本机具备：Python 3.10+、`manim`、`edge-tts`、`pymupdf` (`fitz`)、`ffmpeg`/`ffprobe`、`xelatex`（TeX Live / MiKTeX）以及中文字体 `Noto Sans SC`。

---

## Phase 0：新书项目初始化（每本新书首次执行）

当用户提供一本新教材 PDF（或在一个尚未初始化的目录中启动新课程）时，**切勿直接套用默认偏好开干**，必须先完成以下引导式初始化：

### Step 0：初始化偏好问答 + 自定义要求采集（必做！）
1. **选择题快速定调**：使用 `ask_question` 工具（若环境不支持则用编号选择题形式）向用户一次性确认以下 5 项偏好（每题默认把经典最佳实践标为 `(Recommended)`）：
   - **教学风格与比例**：
     - `(Recommended) 直觉 4 : 应试 6（平衡理解与例题实战，适合期末/考研速通）`
     - `硬核应试（直觉 2 : 应试 8，重题型归纳、计算套路与考场避坑）`
     - `概念直觉优先（直觉 7 : 应试 3，重原理可视化与几何/物理图像）`
     - `零基础保姆级（放慢节奏，补充前置知识，每步拆得更细）`
   - **口播语气与配音音色**：
     - `(Recommended) 平实干练讲师风 · 男声云希 zh-CN-YunxiNeural（+8% 语速）`
     - `亲切清晰讲师风 · 女声晓晓 zh-CN-XiaoxiaoNeural（+5% 语速）`
     - `沉稳学术/纪录片风 · 男声云扬 zh-CN-YunyangNeural（+0% 语速）`
     - `活泼轻快风格（允许适度类比与趣味互动，可选配音）`
   - **分集粒度与单集时长**：
     - `(Recommended) 按教材一节一集（常规 4~6 分钟，短节 3 分钟精华版）`
     - `按章节合集（每章 1 集，8~15 分钟总览）`
     - `短视频切片（每个核心知识点/定理 1 集，2~3 分钟）`
   - **教材依赖与题干呈现**：
     - `(Recommended) 独立成课 + 保留原书题号（画面写全完整原题干，不翻书也能看懂）`
     - `纯独立课程（不标原书题号，自编或改编典型例题）`
     - `精简伴学模式（假设观众手边有书，画面侧重推导步骤）`
   - **出片画质与视觉风格**：
     - `(Recommended) 深空影院蓝（#0B1120）· 1080p 60fps + 逐字内嵌字幕`
     - `快速轻量出片 · 深空影院蓝 · 720p 30fps + 逐字内嵌字幕`
     - `自定义视觉配色/风格（在下一步补充说明）`

2. **开放式个性化需求补充**：在收到选择题答案后，**再明确询问用户一次**：
   > “基础偏好已确认！在正式初始化项目前，您还有哪些**自己的个性化要求**吗？（例如：目标受众是考研/期末/高中/自学、哪些章节重点讲或跳过、特定符号或双语术语习惯、片头片尾固定话术、配套笔记风格、自定义配色等；如果没有，回复「无」或「直接开始」即可。）”

3. 等待用户回复后，将所有选项与个性化要求完整写入后续脚手架初始化命令。

### Step 1：一键脚手架初始化
运行 [init_course_project.py](./scripts/init_course_project.py)，把用户选择的偏好与自定义要求固化到新项目的 `GEMINI.md` 中：
```powershell
python "<SKILL_DIR>\scripts\init_course_project.py" "<目标项目目录>" `
  --course-name "<课程名>" --pdf "<教材文件名.pdf>" --offset 0 `
  --voice "<选定音色>" --rate "<选定语速>" `
  --style "<教学风格>" --tone "<口播语气>" `
  --pacing "<分集粒度>" --standalone "<题干模式>" `
  --quality "<h|m|l>" --custom-reqs "<用户个性化要求>"
```
该脚本会自动生成独立的 `common/`（影院深色主题 + `SyncedScene` 音画同步引擎）、`scripts/`（`tts_gen.py`、`build_ep.py`、`read_pdf.py`、`extract_preview.py`）、`.gitignore`、`episodes/` 和写入了用户偏好的项目级 `GEMINI.md`。若用户要求自定义视觉配色，随后同步微调新项目 `common/theme.py` 中的色板常量。

### Step 2：解析教材目录与页码偏移
- 运行 `python scripts\read_pdf.py "<教材.pdf>" --toc` 查看内嵌目录；若无书签，运行 `--pages 1-15 --offset 0` 查看前言/目录页。
- 核对正文第 1 页对应的 PDF 页码，算出 `offset = PDF页码 - 教材页码`，更新根目录 `GEMINI.md` 中的页码偏移量。

### Step 3：规划全书剧集映射表
- 结合用户在 Step 0 选定的**分集粒度**与**重点/跳过章节要求**，在根目录 `GEMINI.md` 中填写完整 `EP01 ~ EPNN` 的目录名（`epXX_c_s_slug`）、章节标题与教材页码范围，并标出每章第一集（开场展示全书路线图 `make_knowledge_map`），请用户确认后再开做 EP01。

---

## Phase 1：单集制作 5 步标准流水线（每集必走）

动手编写前，优先遵守当前项目根目录 `GEMINI.md` 中的**用户偏好与个性化要求**，并参考两份规范手册与样板：
- 教学红线、口播文案、TTS 断句与 `script.json` 规范：[pedagogy-and-script.md](./references/pedagogy-and-script.md)
- 画布安全区、`common/theme.py` API、音画同步与高危踩坑：[manim-visual-and-pitfalls.md](./references/manim-visual-and-pitfalls.md)
- 样板文件：[script_example.json](./examples/script_example.json) 与 [scene_skeleton.py](./examples/scene_skeleton.py)

### Step 1：读教材原页 + 写速通笔记
- 读取对应小节原页（严禁凭记忆编造教材例题数值）：
  ```powershell
  python scripts\read_pdf.py "<教材.pdf>" --pages <起>-<止> --offset <偏移量>
  ```
- 新建 `episodes/epXX_c_s_slug/`，按用户选定的教学比例提炼核心直觉画面、经典例题与高频易错反例，并编写 `output/EPXX_c-s_速通笔记.md`。

### Step 2：编写 `script.json` + 生成配音与时间轴
- 按项目 `GEMINI.md` 的音色/语速/语气及 [pedagogy-and-script.md](./references/pedagogy-and-script.md) 编写 `episodes/epXX_c_s_slug/script.json`：
  - **只写 `text`，不写缩写 `subtitle`**（自动生成 100% 逐字同步字幕）。
  - 数字列举用顿号 `、` 分隔防粘连；长主语后补逗号引导换气。
- 生成配音、`build/timeline.json` 与 `.srt`/`.ass` 字幕（若 `edge-tts` 偶发断连，直接重跑会自动跳过已缓存段落）：
  ```powershell
  python scripts\tts_gen.py episodes\epXX_c_s_slug
  ```

### Step 3：编写 `scene.py`（音画驱动动画）
- 参考 [scene_skeleton.py](./examples/scene_skeleton.py) 与 [manim-visual-and-pitfalls.md](./references/manim-visual-and-pitfalls.md)：
  - 继承 `SyncedScene`，`construct()` 开头固定 `self.add(make_studio_backdrop())`。
  - **每章第一集**开场放 `make_knowledge_map(BOOK_CHAPTERS, highlight_idx=章序号)`；章内其余各集用干净封面标题 + 核心概念对比卡。
  - **分步动态演算**：计算/推导/代入过程必须用 `self.pace_to(seg, frac)` 与口播一一同步展开，严禁静态干读；高阶抽象公式先具体再抽象。
  - **清屏铁律**：每次 `self.clear_stage(...)` 前必须调用 `self.pace_to(seg, 0.995)`。
  - **零缺字与安全区**：含公式/上下标的中英混排一律用 `zh_tex(...)`；所有正文严格留在 `x ∈ [-6.4, +6.4]`、`y ∈ [-2.85, +2.95]`。

### Step 4：480p 预演 + 全帧肉眼质检（不可跳过）
1. 渲染 480p 预览版：
   ```powershell
   python scripts\build_ep.py episodes\epXX_c_s_slug --quality l --skip-tts
   ```
   确认控制台 **0 条 `[SYNC WARNING]`**（若超时则缩短对应段落 `run_time`）。
2. 自动抽取每段 `start + audio_duration * 0.96` 处预览帧：
   ```powershell
   python scripts\extract_preview.py episodes\epXX_c_s_slug
   ```
3. **逐张使用 `read_file` 肉眼检查 `build/preview_frames/*.png`**：
   - [ ] 题干、定义、前提条件是否符合用户选定模式且清晰完整？
   - [ ] 计算/推导是否分步动态展开（非静态铺屏干读）？
   - [ ] 是否有 `□□` 缺字方块、文字/矩阵列重叠、孤字折行或越出安全区？
   发现任何问题立即修改 `scene.py` 并重跑 480p 复查，直到全帧零瑕疵。

### Step 5：最终出片与校验
1. 按项目 `GEMINI.md` 中用户选定的画质（默认 `-q h` 1080p60）渲染成片：
   ```powershell
   python scripts\build_ep.py episodes\epXX_c_s_slug --quality h --skip-tts
   ```
2. 确认 0 条 `[SYNC WARNING]`，用 `ffprobe` 校验分辨率、帧率且总时长与 `build/timeline.json` 误差 `< 0.1s`；对修改过的页面再次抽成片帧复核。
3. **目录隔离与 Git 卫生**：所有缓存/抽帧/成片严格留在当前项目内；Git 仅提交 `script.json`、`scene.py`、`output/*.md`、`output/*.srt` 及规则文档，绝不提交 `.mp4/.wav/.mp3/.png/.pdf` 或 `build/`。
