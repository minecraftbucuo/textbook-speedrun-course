# Manim 视觉布局、音画同步与高危踩坑手册

---

## 一、画布安全区与统一配色（`common/theme.py`）

1. **持久背景**：`construct()` 开头固定 `self.add(make_studio_backdrop())`（深空点阵 `#0B1120`，无发光圆）。
2. **三段式安全区**（Manim 默认 16:9 画布 `x ∈ [-7.11, 7.11]`、`y ∈ [-4.0, 4.0]`）：
   - 顶栏 HUD：`y ∈ [3.24, 3.95]`（禁放正文）
   - **主画布安全区**：`x ∈ [-6.4, +6.4]`，`y ∈ [-2.85, +2.95]`（所有卡片、公式、图形严禁越出此范围）
   - 底部字幕区：`y ∈ [-4.0, -3.10]`（禁放正文）
3. **语义配色**：
   - `ACCENT_BLUE` (`#38BDF8`)：核心概念 / 输入 / 主角 A
   - `ACCENT_GOLD` (`#FBBF24`)：重点强调 / 关键结论 / 主角 B / 口诀
   - `ACCENT_GREEN` (`#34D399`)：运算结果 / 正确结论 / 已验证
   - `ACCENT_RED` (`#F87171`)：考场雷区 / 反例警示 / 易错点
   - `ACCENT_PURPLE` (`#A78BFA`)：几何直觉 / 空间变换 / 抽象视角
   - `ACCENT_CYAN` (`#22D3EE`)：进度条 / 辅助高亮

---

## 二、`common/theme.py` 核心组件速查

| 函数 | 常用调用方式 | 注意事项 |
| :--- | :--- | :--- |
| `make_studio_backdrop()` | `self.add(make_studio_backdrop())` | 放在 `construct()` 第一行 |
| `make_top_hud(ep_tag, ep_title, chapters, active_idx)` | `make_top_hud("1-1", "标题", CHAPTERS, active_idx=0)` | 切幕用 `ReplacementTransform` 平滑更新 |
| `make_knowledge_map(chapters_all, highlight_idx)` | `make_knowledge_map([("第一章", "..."), ...], highlight_idx=0)` | 仅每章第一集使用；自动适配任意章节数宽度 |
| `make_section_header(title, color, y=2.55)` | `make_section_header("核心定义", color=ACCENT_BLUE, y=2.55)` | 距顶栏留足呼吸感 |
| `make_card(content, width, height, border_color)` | `make_card(VGroup(), width=5.6, height=3.0, border_color=ACCENT_BLUE)` | 第一参是内容 Mobject，关键字是 `border_color` |
| `make_badge(label, color, font_size=20)` | `make_badge("教材例 1", color=ACCENT_GOLD)` | 内部用 `zh_text`，禁放 Unicode 上下标 |
| `zh_text(text, font_size, color, weight)` | `zh_text("纯中文标题", font_size=24, weight=BOLD)` | 仅用于纯中文/ASCII，禁放数学上下标与生僻符号 |
| `zh_tex(tex_str, font_size, color)` | `zh_tex(r"当 $x \to 0$ 时，有 $\sin x \sim x$", font_size=22)` | XeLaTeX 文本模式：中文直写，加粗用 `\textbf{...}`，公式包 `$...$` |
| `math_tex(*parts, font_size, color)` | `math_tex(r"f'(x)=", r"2x", font_size=34)` | 纯数学公式（可分段着色）；若含中文改用 `zh_tex` |

---

## 三、音画同步与清屏铁律（`SyncedScene`）

1. 必须继承 `SyncedScene`，并设置类属性 `TIMELINE_PATH = EP_DIR / "build" / "timeline.json"`。
2. 每段口播用 `with self.segment("s01_intro") as seg:` 包裹。
3. **节点对齐**：在每个关键视觉变化前调用 `self.pace_to(seg, frac)`（`frac ∈ [0.0, 0.98]`），把动画均匀铺满整段口播的 85%~92%，避免提前播完干等。
4. **清屏铁律**：每次 `self.clear_stage(...)` 之前，**必须先调用 `self.pace_to(seg, 0.995)`**，确保清屏发生在 `pause_after` 静音段内，绝不提前清空画面。
5. **零超时校验**：渲染日志中必须 **0 条 `[SYNC WARNING]`**；若某段超时，缩短该段 `run_time` 或精简过渡动画。

---

## 四、高危踩坑红线（实战沉淀）

| # | 踩坑现象 | 根因 | 正确做法 |
| :--- | :--- | :--- | :--- |
| **1** | 画面出现白色缺字方块 `□□` | `Noto Sans SC` 缺失 Unicode 数学上下标与圆圈序号（`₀₁₂₃ₘᵀ ⇏ ①②③`） | **严禁在 `zh_text()` / `make_badge()` 中写数学上下标或生僻符号**；含公式/上下标的中英混排一律用 `zh_tex(...)`，步骤编号用 `1. / 2. / 3.` |
| **2** | LaTeX 编译报错（未定义命令或中文乱码） | 仅加载了 `amsmath` 与 `amssymb`；`math_tex` 不加载 `xeCJK` | 严禁使用 `\xRightarrow`、`\iddots`（统一用 `\xrightarrow`）；含中文的箭头或公式（如 `\xrightarrow{\text{行变换}}`）必须用 `zh_tex` |
| **3** | 公式里的 `\color{#HEX}` 全变白 | Manim `MathTex(..., color=TEXT_PRIMARY)` 会在加载 SVG 后全局覆盖颜色 | 用分段 `math_tex(r"c_{11}=", r"3", ...)` 后在 Python 中调用 `tex[i].set_color(ACCENT_BLUE)`，或用 `Matrix.get_entries()[i].set_color(...)` |
| **4** | 矩阵相邻两列重叠/贴在一起 | Manim `Matrix` 的 `h_buff` 是**列中心距**，不是列间距 | 经验下限：纯正整数 `≥ 0.85`；含负数 `≥ 0.95`；含 `ka_{11}` `≥ 1.60`；含 `a_{11} ± b_{11}` `≥ 2.75` 并配合 `scale(0.76)` |
| **5** | `TransformFromCopy` 目标消失或闪烁 | 同一 `self.play()` 对同一目标施加了两个动画（如 `Write(grp)` + `TransformFromCopy(..., grp[i])`） | 确保每个目标对象在同一 `self.play()` 中只被一个动画控制；多源汇合时改用光点 `Dot` 飞入再 `FadeIn` |
| **6** | 2D 坐标系/函数图像溢出遮挡 HUD 或字幕 | `NumberPlane` / `Axes` 经变换后外扩 | 控制 `x_length`/`y_length` 并放入暗色 `RoundedRectangle` 视口框内，变换时底层叠一张静止参考网格 |
| **7** | 末尾 1~2 个孤字折行或贴边 | `zh_tex` 单行过长超出卡片宽度 | 严控单行字数，必要时拆成两行 `VGroup` 排版，或用 `.scale_to_fit_width(card_w - 0.5)` 兜底 |
| **8** | 音画累计漂移几十秒 | Manim `wait()` 内部调用 `play(Wait(...))`，手动累加时间会重复计入 | 始终继承 `SyncedScene`（直接读取 `self.renderer.time`），切勿重写 `play()` / `wait()` |
| **9** | 字幕背景偏色 | ASS 颜色是 `&HAABBGGRR`（BGR 倒序）而非 RGB | 保持 `scripts/tts_gen.py` 已调好的 ASS 样式，勿手改十六进制顺序 |
