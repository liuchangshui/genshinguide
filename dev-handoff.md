# GenshinGuide 开发任务交付清单（修正版 v2）

> **修正说明**：本版基于五方会审（夜兰·凝光·阿贝多·钟离·琴）的评估结果，对原版 dev-handoff 做了系统修正。主要变化：新增 Phase 0 法律+内容验证、工时预估上调 2-3 倍、收入预期下调至务实区间、增加法律风险和 AI 内容风险应对。
>
> 致开发人员：本文档是一人公司作战手册的开发任务拆解版，配合 PR 原型和架构设计文档使用。
> 项目代号：GenshinGuide · 定位：原神 Build 攻略 + AI 数据工具站
> 技术栈：静态 HTML + Python Pipeline + DeepSeek V3.2

---

## 修正要点速览

| 维度 | 原版 | 修正版 | 原因 |
|------|------|--------|------|
| 市场可触达用户 | 210-315万 | **~42万**（海外主动搜索 build guide 的玩家） | 2100万 MAU 含 60% 中国用户、大量非搜索型玩家 |
| M12 月访问预期 | 5-20万 | **5千-1万** | 新域名第一年 SEO 现实；竞品三年才到百万级 |
| M12 月收入 | $185-530 | **$50-150** | 访问量 × 转化率 × 定价 的务实推算 |
| 盈亏平衡点 | M12-M18 | **M18-M24** | 流量爬坡更慢 |
| Phase 1 工时 | 23h / 3-4天 | **50-60h / 约2周** | Prompt engineering、调试、审核工作量被低估 |
| 最大风险 | AI 内容惩罚 | **HoYoverse 法律风险** > AI 内容惩罚 > 单点故障 |

---

## 项目背景速览

- **产品**：原神角色 Build 攻略站 + AI 驱动的伤害计算/配队工具
- **商业模式**：Freemium（免费引流 + Pro $5/月增值）
- **核心护城河**：AI Build Copilot（自然语言配队推荐）
- **目标市场**：英文市场为主，中文仅 SEO 引流
- **修正时间预期**：12 个月 $50-150/月，18-24 个月 $300-600/月
- **⚠️ 前置条件**：需确认 HoYoverse Fan Content Policy 允许付费订阅（见 Phase 0）

完整商业分析见 `battle-manual.html`，技术架构见 `tech-evaluation-report.md`，修正备忘录见 `corrections-memo.md`。

---

## PR 原型资产清单（`pr-site/` 目录）

| 资产 | 文件 | 状态 | 说明 |
|------|------|------|------|
| 首页 | `index.html` | ✅ 完成 | 品牌展示 + 快速搜索 + 热门攻略入口 |
| 攻略列表页 | `guides.html` | ✅ 完成 | 元素筛选 + 攻略卡片 |
| 计算器页 | `calculator.html` | ✅ 完成 | 选角色+武器→推荐圣遗物+配队 |
| 定价页 | `pricing.html` | ✅ 完成 | Free vs Pro 对比 + CTA |
| Pipeline 展示页 | `pipeline.html` | ✅ 完成 | 内容生产流程可视化 |
| 角色攻略页 ×8 | `guide-{raiden,hutao,yelan,nahida,kazuha,zhongli,ayaka,albedo}.html` | 🟡 占位 | 模板已定，内容待 Pipeline 批量生成 |
| 香菱攻略页 | `guide-xiangling.html` | ✅ 完成 | 含完整 Build 内容，**可作为内容质量基准线** |
| CSS 设计系统 | `css/style.css`（988 行） | ✅ 完成 | 暗色主题 + 7 元素视觉系统 + 响应式 |
| i18n 引擎 | `js/i18n.js`（900 行） | ✅ 完成 | 中英双语 + localStorage 持久化 |
| 计算器逻辑 | `js/calculator.js`（203 行） | 🟡 需重构 | 当前是查表工具，非真实伤害计算；需升级为 DMG 模拟器 |
| 角色立绘 | `images/raiden-shogun.png` | ✅ 完成 | Character Showcase 组件示例 |

### ⚠️ calculator.js 的局限性（重要）

当前 `calculator.js` 的本质是**查表推荐**，不是真正的伤害计算。`scoreBuild()` 公式为 `wpn.rarity * 10 + char.atk / 20`——这是拍脑袋的加权，与游戏内实际伤害公式无关。

真正的 DMG 模拟器需要实现：
```
伤害 = 技能倍率 × 攻击力 × (1 + 伤害加成%) × (1 + 暴击伤害%) × 反应系数 × 敌人抗性系数 × 防御减免系数
```

这些数据 current codebase 里完全没有。在 Phase 2 做 Pro DMG 模拟器时，需要从 genshin.jmp.blue 或 Genshin Data JSON 获取完整的技能倍率、反应系数和敌人数据。

---

## Phase 0：前置验证（第 0 周，**在写任何 Pipeline 代码之前**）

> **这是修正版新增的阶段。** 目的：用最小成本验证两个决定性前提——法律可行 + Google 愿意收录。
>
> **2026-06-18 更新**：法律调研已完成（见 corrections-memo.md 第 9 条）。结论：**HoYoverse 的 Fan Content Policy 不覆盖数字服务，且已有竞品在跑付费订阅。法律风险评级为🟡中低。** Phase 0 的主要验证目标现在聚焦于 Google SEO。

### 任务 0.1：法律合规落地（1h）✅ 调研已完成，只需执行

**背景**：已完成系统调研。HoYoverse 所有法律行动（HomDGCat 诉讼、外挂诉讼、GitHub DMCA）均针对泄露内容/外挂/盗版，**无一起针对合法粉丝攻略站**。Fan Content Policy 覆盖实体周边，不覆盖数字服务。竞品 Genshin Mastery Hub 已在跑 $20/月付费订阅，未被追诉。

**执行清单（三铁律 + 七措施）**：

铁律（不可违反）：
- [ ] **只用正式服公开数据**（genshin.jmp.blue），绝不碰泄露/beta 内容
- [ ] **攻略永远免费**，Pro 只锁工具功能（DMG 模拟器、AI Copilot）
- [ ] **每页 footer 标注**："Fan-made project. Not affiliated with HoYoverse. Game data © Cognosphere."

措施（上线前完成）：
- [ ] 域名使用独立品牌名，避免 `genshin` 作为主域名（如用 `buildguide.gg`）
- [ ] 不使用官方角色立绘做商业用途，角色展示用 SVG 图标或粉丝自制素材
- [ ] AI 生成攻略标注"AI 辅助生成 + 人工审核"
- [ ] Pro 产品描述用"Pro Tools"而非"Genshin Pro"
- [ ] Lemon Squeezy 支付，MoR 模式自动处理税务
- [ ] 攻略内容增加原创分析性内容（配队逻辑、伤害原理），而非单纯数据罗列
- [ ] 不在域名/商标中注册任何含 HoYoverse 知识产权的标识

**验收标准**：上述三项铁律已落实，七项措施在上线前 checklist 中

### 任务 0.2：手动内容验证（Google SEO 最小可行性测试）

**目标**：验证 Google 是否会收录和排名一个新域名的原创攻略内容

- [ ] 注册域名 → Cloudflare Pages 部署现有 `pr-site/`
- [ ] 手动撰写 3 篇高质量攻略（不依赖 AI，确保 EEAT）：
  1. 芙宁娜 (Furina) — Build Guide
  2. 阿蕾奇诺 (Arlecchino) — Build Guide
  3. 那维莱特 (Neuvillette) — Build Guide
- [ ] 每篇攻略标准：TL;DR + 武器排名（含理由） + 圣遗物（含替代） + 配队（3-4 个） + 输出手法 + 常见误区 + 有实际游戏截图
- [ ] 提交 Google Search Console → 请求索引
- [ ] 配置 GA4 追踪：页面浏览、计算器使用、Pro CTA 点击
- [ ] 观察 7-14 天：是否被收录？是否有自然搜索展示？
- [ ] 以 guide-xiangling.html 为质量基准线——AI 生成的攻略不能比它差

**验收标准**：
- Search Console 显示至少 2/3 篇被索引
- 至少出现 3-5 个搜索展示（即使排名很低）
- 确认"手动写的攻略能被 Google 收录"这一基本前提成立

**🚩 关键决策点**：如果手写的都收不到自然搜索流量，AI 生成的更收不到。这时需要重新评估整个 SEO 驱动策略。

---

## Phase 1：上线 + 内容生产（第 1-2 周，～50-60h）

> **修正**：原版预估 23h/3-4天。实际需要约 2 周全职投入。

### 任务 1.1：部署上线 + SEO 基础设施（6h）

**目标**：站点可被全球访问，可被 Google 正确索引

- [ ] 确认域名注册（建议 `.com` 或 `.gg`）
- [ ] Cloudflare Pages 连接 Git 仓库 + 自动部署
- [ ] 生成 `sitemap.xml`（覆盖所有现有页面 + 攻略页）
- [ ] 配置 `robots.txt`（允许全部爬取）
- [ ] 为每个页面的 `<title>` 和 `<meta description>` 做差异化（避免重复）
- [ ] 完善 schema.org JSON-LD（所有攻略页含 Article + HowTo）
- [ ] 添加 `og:image` 和 `twitter:card` 标签
- [ ] 建立内链网络：攻略页底部的"相关攻略"交叉引用
- [ ] 提交 `sitemap.xml` 到 Google Search Console
- [ ] 配置 Google Analytics 4（事件追踪：页面浏览、计算器使用、Pro CTA 点击、邮件订阅）

**验收标准**：域名可访问，Search Console 显示"已提交"，GA4 有数据流入

### 任务 1.2：内容 Pipeline 搭建（20-30h）⚠️ 工时大幅上调

**目标**：用 AI 批量生成角色攻略，但有人工审核关卡

- [ ] 注册 DeepSeek API（`platform.deepseek.com`），获取 API Key
- [ ] 编写 `pipeline/config.py`：API Key、模型名（`deepseek-chat` / V3.2）、数据源 URL
- [ ] 编写 `pipeline/sync_wiki.py`：从 `genshin.jmp.blue` 拉取角色/武器/圣遗物数据，本地缓存为 JSON
  - 缓存策略：所有 API 数据本地缓存，API 挂了用缓存继续
  - 增量检测：对比版本号，只更新有变化的数据
- [ ] 编写 `pipeline/generate.py`（核心生成脚本）：
  - 输入：角色 ID
  - Step 1：从缓存读取角色数据（不每次调 API）
  - Step 2：构建 Prompt（结构化数据 + 模板指令 + 角色 lore/背景）
  - Step 3：调用 DeepSeek V3.2（`deepseek-chat`，temperature=0.3，`response_format={"type": "json_object"}`）
  - Step 4：输出结构化 JSON（tldr + weapons + artifacts + teams + talents + rotation + mistakes + seo）
  - Step 5：调用 DeepSeek V3.2 自检验证（数值核对：ATK、稀有度、套装名、元素属性、角色存在性）
  - Step 6：用 Jinja2 模板渲染为 HTML
  - Step 7：写入 `pr-site/guide-{character}.html`
  - 异常处理：验证失败最多重试 2 次；API 超时 30s 自动重试
- [ ] 编写 `pipeline/templates/guide_template.html`：基于 `guide-xiangling.html` 抽取模板
- [ ] 编写 `pipeline/verify.py`：LLM 二次校验
  - 武器基础 ATK 是否正确
  - 武器稀有度是否正确
  - 圣遗物套装名是否是游戏中真实存在的
  - 角色元素属性是否正确
  - 配队成员是否是游戏中真实存在的角色
- [ ] 编写 `pipeline/publish.py`：更新 `guides.html` 索引 + `sitemap.xml` + git commit
- [ ] **人工审核流程**（这是被原版遗漏的关键环节）：
  - 每个 AI 生成的攻略标记为 `status: draft`
  - 人工审核者（掌门）逐篇检查：
    - 配队推荐是否在实战中可行（不是纯数据最优）
    - 武器排名逻辑是否合理
    - 没有 AI 编造的虚假角色/武器/圣遗物
    - 输出手法描述是否准确
  - 通过后标记为 `status: published` → git push 部署
  - **预估审核时间：20-30 分钟/篇**
- [ ] 配置 `.github/workflows/daily-sync.yml`：GitHub Actions 每日 00:00 自动同步数据

**验收标准**：
- `python generate.py --character xiangling` 生成的攻略质量不低于现有手写版
- 自检验证能正确标记已知的错误数据（用故意错误的数据做一次边界测试）
- Pipeline 部署在 GitHub Actions（海外网络），避免国内访问 DeepSeek 需代理的问题

### 任务 1.3：批量生成首批攻略（生成 4h + 审核 5-8h）

**目标**：5 篇 P0 角色攻略上线（经过人工审核）

按搜索热度优先：
1. `python generate.py --character furina` → 人工审核 → publish
2. `python generate.py --character arlecchino` → 人工审核 → publish
3. `python generate.py --character neuvillette` → 人工审核 → publish
4. `python generate.py --character raiden` → 覆盖现有占位 → 人工审核 → publish
5. `python generate.py --character bennett` → 人工审核 → publish

**验收标准**：5 篇攻略全部通过人工审核上线，内容包含 TL;DR + 武器排名 + 圣遗物 + 配队 + 手法 + 误区。每篇审核不通过的重试成本计入工时。

### 任务 1.4：Reddit 养号启动（每天 30min，持续 2 个月）

**目标**：养一个可信的社区账号，为后续推广做准备

- [ ] 注册 Reddit 账号（不要用与网站相同的用户名，避免被识别为推广号）
- [ ] 订阅 r/Genshin_Impact + r/GenshinImpactTips + r/RaidenMains 等角色主 Sub
- [ ] **前 2 周只点赞和浏览**，不发言（潜伏期）
- [ ] **第 3-8 周**：每天回答 2-3 个 build 相关问题（只提供价值，不提网站）
  - 目标：积累 karma 到 500+，建立"这个人懂原神"的信誉
  - 90/10 规则：90% 纯价值回复，10% 可以提"我还写了个工具"
- [ ] **第 9 周起**：发布第一条原创内容（如"我测试了 5 个 Raiden 配队，伤害数据出乎意料"），以工具价值吸引，不提 Pro

**验收标准**：第 8 周末 karma ≥ 500，已建立 r/GenshinImpactTips 的活跃贡献者身份

---

## Phase 2：支付 + Pro 功能（第 3-5 周，～40-50h）

> **修正**：原版预估 28h/4-5天。实际需要约 3 周（含 DMG 模拟器的技术攻坚）。

### 任务 2.1：Lemon Squeezy 支付接入（6h）

**目标**：用户能真实付费订阅 Pro

- [ ] 注册 Lemon Squeezy 账号，创建 Pro 订阅产品（$5/月，$40/年）
- [ ] 创建 Checkout 链接，嵌入 `pricing.html` 的 CTA 按钮
- [ ] 配置 Webhook 接收支付成功通知
- [ ] 部署 Cloudflare Worker 处理 Webhook
- [ ] Webhook 验证逻辑：签名验证 → 确认支付成功 → 生成 JWT → 通过 Resend 发送含 magic link 的邮件

**验收标准**：完整支付流程跑通（测试卡支付 → webhook → 邮件），至少测试 3 次

### 任务 2.2：Pro 鉴权系统（6h）

**目标**：区分免费/付费用户，gating Pro 功能

- [ ] 用户点击邮件 magic link → 前端存 JWT 到 `localStorage`
- [ ] 前端 JS 读取 JWT → 判断 Pro 状态
- [ ] Cloudflare Worker `/api/auth`：接收 JWT → 查询 Lemon Squeezy API 验证订阅有效性
- [ ] 订阅过期处理：定时检查（每天一次），过期则清除前端 Pro 标记
- [ ] Pro 功能 gating：DMG 模拟器、圣遗物优化器等模块检查 Pro 状态

**验收标准**：付费用户能访问 Pro 功能，免费用户看到"Unlock Pro"提示并被限制每日 3 次使用

### 任务 2.3：Pro DMG 模拟器（16-20h）⚠️ 工时上调 + 技术复杂度上调

**目标**：Pro 核心功能可用，伤害计算误差 < 5%

这是**整个项目技术难度最高的模块**。需要从"查表推荐"升级为"真实伤害模拟"。

**前置准备**：
- [ ] 从 genshin.jmp.blue + Genshin Data JSON 获取完整技能倍率数据
- [ ] 建立伤害计算公式所需的数据模型：
  - 角色基础属性（ATK/HP/DEF）+ 突破加成
  - 技能倍率（每级，含 E/Q/NA）
  - 反应系数（蒸发 1.5× / 融化 2.0× / 激化加成等）
  - 敌人抗性默认值（10% 通用抗性）
  - 防御减免公式：`(角色等级 + 100) / ((角色等级 + 100) + (敌人等级 + 100))`

**开发任务**：
- [ ] 实现伤害计算核心函数：
  ```
  DMG = 技能倍率 × 攻击力 × (1 + 伤害加成%) × (1 + 暴击伤害% × 暴击率%) × 反应系数 × 抗性系数 × 防御系数
  ```
- [ ] 输入界面：角色等级、武器（含精炼）、圣遗物主词条、圣遗物套装、敌人等级、队伍 Buff
- [ ] 输出：精确伤害数字 + 伤害构成饼图（用 Chart.js）
- [ ] 配队对比：同时模拟 3 套配队，输出 DPS 对比柱状图
- [ ] 免费用户：每日 3 次模拟（前端 `localStorage` 计数）
- [ ] Pro 用户：无限模拟 + 保存方案到 Supabase

**验收标准**：
- 选择 Raiden 满配数据（2000 ATK, 70/140 CRIT, 270% ER, R1 Engulfing, 4pc Emblem）
- 输出 Q 首刀伤害数字
- 与 Genshin Optimizer 同等配置对比，误差 < 5%
- **如果误差 > 5%，先修复再上线 Pro，不降低标准**

### 任务 2.4：邮箱订阅 + AI 内容审核流程（4h）

**目标**：收集邮箱 + 建立内容质量保证体系

- [ ] 注册 Resend 账号，获取 API Key
- [ ] 首页 + 攻略页底部添加邮箱订阅框
- [ ] Cloudflare Worker `/api/subscribe`：接收邮箱 → 存入 Supabase → Resend 发送欢迎邮件
- [ ] 建立内容审核清单（Checklist）：
  - 配队推荐在实战中可行？（Y/N）
  - 武器排名逻辑合理？（Y/N）
  - 无 AI 编造内容？（Y/N）
  - 输出手法描述准确？（Y/N）
  - 数值与源数据一致？（Y/N，此项由 verify.py 自动检查）
- [ ] 周报邮件模板（版本更新 Build 变化 + 新攻略通知）

**验收标准**：输入邮箱能收到欢迎邮件；每篇 AI 攻略发布前完成审核 Checklist

---

## Phase 3：增长放大（第 6 周起，持续投入）

### 任务 3.1：批量扩展攻略（持续）

- [ ] 用 Pipeline 生成剩余 25 个角色的攻略
- [ ] **12 周发布节奏**（不是一次性全放）：
  - W1-2：首批 5 篇 P0 角色
  - W3-6：每周 3 篇（12 篇）
  - W7-12：每周 2 篇（12 篇）
  - 总计 12 周 30 篇 + Pipeline 随时补新角色
- [ ] 每篇攻略发布前完成人工审核 Checklist
- [ ] 攻略发布时同步更新 sitemap.xml + 提交 GSC 索引

### 任务 3.2：程序化 SEO 页面（8h）

**目标**：用 DMG 模拟器产出真实对比数据，生成有价值的 SEO 内容

- [ ] 先做配队对比页（搜索量最大）：
  - `/teams/raiden-national.html`
  - `/teams/raiden-hypercarry.html`
  - `/teams/hutao-double-hydro.html`
  - 首批 10-15 个高价值配队
- [ ] 每个页面内容：配队说明 + 角色分工 + DPS 模拟数据 + 圣遗物推荐 + 适用场景
- [ ] **不做模板页面**（Google 会判定 thin content 惩罚）

### 任务 3.3：AI Build Copilot（核心护城河，16-20h）

**目标**：自然语言配队推荐，验证这个功能是否真的"不可替代"

- [ ] 集成 DeepSeek API 到 Cloudflare Worker（前端不直接暴露 API Key）
- [ ] 用户输入：自然语言问题 + 手动选择角色 box
- [ ] AI 分析 box → 推荐 Top 3 配队 + 理由 + 伤害预估
- [ ] 追问支持："如果换成如雷套呢？"→ AI 重新分析
- [ ] 上线后密切追踪：Pro 转化率是否因为这个功能有明显提升？

**关键验证指标**：AI Build Copilot 上线前 vs 上线后，Pro 转化率的变化。
- 如果转化率 > 2%（访问→付费）→ 加大投入，这是真正的护城河
- 如果转化率 < 1% → 重新评估 Pro 价值主张，考虑转向一次性付费

### 任务 3.4：新角色自动跟进（4h）

- [ ] 监控 genshin.jmp.blue 数据更新
- [ ] 新角色上线当天自动触发 Pipeline 生成
- [ ] 人工审核（新角色攻略质量要求更高，因为是时效性内容）
- [ ] 自动 git commit + 部署 + 邮件通知订阅者

---

## 技术架构速查

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | 静态 HTML + CSS + 原生 JS | 现有原型，不迁框架 |
| 内容 Pipeline | Python 3.10+ + Jinja2 + DeepSeek V3.2 | `pipeline/` 目录 |
| 数据源 | `genshin.jmp.blue` REST API | 免费、开源、结构化 JSON |
| 补充数据源 | Genshin Data JSON (GitHub) | 技能倍率等详细数值 |
| 部署 | Cloudflare Pages | 免费、全球 CDN、自动部署 |
| 支付 | Lemon Squeezy | MoR 模式，自动处理全球税务 |
| 邮件 | Resend | 3000 封/月免费 |
| 后端 | Cloudflare Workers（按需） | 处理 webhook、JWT 验证、邮件订阅、AI API 代理 |
| 数据库 | 暂不需要 → Supabase（Pro 功能上线后） | PostgreSQL + Auth + API |
| AI 生成 | DeepSeek V3.2（`deepseek-chat`） | OpenAI 兼容接口，$0.14/百万 token |
| AI 备用 | OpenAI GPT-4o-mini | DeepSeek 服务中断时的 fallback |
| 分析 | Google Analytics 4 + Search Console | 流量追踪 + SEO 监控 |

---

## Pipeline 目录结构

```
genshinguide/
├── pr-site/                 # 静态站点（现有原型）
│   ├── index.html
│   ├── guides.html
│   ├── calculator.html
│   ├── pricing.html
│   ├── guides/
│   │   └── guide-{character}.html
│   ├── css/
│   ├── js/
│   └── images/
├── pipeline/                # 内容 Pipeline
│   ├── generate.py          # 生成单个攻略
│   ├── sync_wiki.py         # 数据同步
│   ├── verify.py            # 自检验证
│   ├── publish.py           # 写文件 + 更新索引
│   ├── templates/
│   │   └── guide_template.html
│   ├── data/
│   │   └── cache/           # 本地数据缓存（所有 API 数据本地存一份）
│   ├── review_checklist.md  # 人工审核清单
│   └── config.py            # API keys, 配置
├── workers/                 # Cloudflare Workers 后端
│   ├── webhook.js           # Lemon Squeezy webhook
│   ├── auth.js              # JWT 验证
│   ├── subscribe.js         # 邮箱订阅
│   └── ai-proxy.js          # DeepSeek API 代理（前端不暴露 Key）
├── .github/workflows/
│   └── daily-sync.yml       # GitHub Actions 定时任务
└── README.md
```

---

## 关键 API 端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `https://genshin.jmp.blue/characters` | GET | 获取所有角色列表 |
| `https://genshin.jmp.blue/characters/{id}` | GET | 获取单个角色详情 |
| `https://genshin.jmp.blue/weapons` | GET | 获取武器列表 |
| `https://genshin.jmp.blue/artifacts` | GET | 获取圣遗物套装 |
| `https://api.deepseek.com/v1/chat/completions` | POST | DeepSeek 生成/验证 |
| `https://api.openai.com/v1/chat/completions` | POST | 备用 AI（DeepSeek 服务中断时） |

---

## 成本估算

| 项目 | 成本 | 说明 |
|------|------|------|
| 域名 | ~$10/年 | .com 或 .gg |
| Cloudflare Pages | $0 | 免费额度足够 |
| DeepSeek API | ~$2/月 | 生成+验证 |
| OpenAI API（备用） | ~$5/月（偶尔使用） | 仅 DeepSeek 中断时启用 |
| Lemon Squeezy | 5% + $0.50/笔 | 有交易才扣 |
| Resend | $0 → $20/月 | 3000 封/月免费 |
| Supabase | $0 → $25/月 | 免费额度够初期 |
| 法律咨询（一次性） | ~$200-500 | Phase 0，值这个钱 |
| **月固定成本** | **~$2-5** | 不计交易费 |
| **一次性成本** | **$210-510** | 域名+法律咨询 |

---

## 收入预期（修正版）

| 时间 | 月访问 | Pro 用户 | Pro 收入 | AdSense | **月总收入** |
|------|--------|----------|----------|---------|-------------|
| M3 | 500-2K | 0-3 | $0-15 | $0 | **$0-15** |
| M6 | 2K-5K | 3-10 | $15-50 | $5-15 | **$20-65** |
| M9 | 3K-8K | 5-15 | $25-75 | $10-30 | **$35-105** |
| M12 | 5K-10K | 5-10 | $25-50 | $15-50 | **$40-100** |
| M18 | 10K-30K | 15-40 | $75-200 | $50-150 | **$125-350** |
| M24 | 20K-60K | 30-70 | $150-350 | $100-300 | **$250-650** |

> **修正说明**（相比原版 battle-manual.html 的预期下调了多少）：
> - M12 收入从 $185-530 下调至 $40-100（约 1/5）
> - M24 收入从 $550-1100 下调至 $250-650（约 1/2）
> - 核心原因：新域名 SEO 爬坡比预期慢、付费转化率被 Genshin Optimizer 免费压制、竞品流量在萎缩不是扩大
> - **月成本只有 $2-5，所以即使是 M12 的 $40-100/月，也已经是正的现金流。活着很容易，赚大钱很难。**

---

## 风险管理

### 风险一：HoYoverse 法律合规 🟡 中低严重度（已完成调研）

- **风险**：Fan Content Policy 不覆盖数字服务（仅覆盖实体周边），但付费订阅处于灰色地带
- **调研结论**：HoYoverse 所有已知法律行动（HomDGCat、外挂、DMCA）均针对泄露内容/外挂/盗版。**零起针对合法粉丝攻略站。** 竞品 Genshin Mastery Hub 已跑 $20/月订阅无追诉。
- **应对**：
  - 三铁律：只用正式服数据 + 攻略永远免费 + 明确非官方声明
  - 域名用独立品牌，Pro 只锁工具不锁内容
- **触发条件**：HoYoverse 更新 Fan Content Policy 明确覆盖数字服务（届时需重新评估）
- **如果发生**：如果收到停止函 → 立即下架 Pro 付费，转为纯免费+捐赠模式

### 风险二：Google AI 内容惩罚（EEAT）🟡 中高严重度

- **风险**：Google 检测到 AI 生成内容，整站被降权
- **应对**：
  - 每篇攻略经过人工审核和修改（不能纯 AI 生成直接发布）
  - 融入"第一手经验"：实际游戏截图、实测伤害数据
  - **必须靠工具（计算器/DMG 模拟器/Copilot）建立差异化**——纯内容站必死
  - AI 内容标注审核者（"Reviewed by [掌门]"），增加信任信号
  - 策略上，AI 生成是第一稿，人工编辑是必需步骤，不是可选项
- **触发条件**：Search Console 显示展示量突然下降 > 50%
- **如果发生**：暂停 AI 内容生成，转为人工原创为主，修复已有内容

### 风险三：genshin.jmp.blue 数据源中断 🟡 中严重度

- **风险**：社区项目停止维护，数据不更新
- **应对**：
  - 所有 API 数据本地缓存一份（已设计到 Pipeline 中）
  - 维护 Genshin Data JSON (GitHub) 作为备用数据源
  - 降级策略：数据不更新时，用缓存数据 + 标记"数据可能非最新"
- **触发条件**：API 连续 3 天无响应
- **如果发生**：切换备用数据源，在网站顶部 banner 告知用户数据更新延迟

### 风险四：DeepSeek API 中断 🟡 中严重度

- **风险**：API 服务不可用，内容生成中断
- **应对**：
  - 准备 OpenAI GPT-4o-mini 作为备用（成本约高 3-5 倍，但仍可接受）
  - Pipeline 中实现 API fallback 逻辑：DeepSeek 超时 30s → 自动切 GPT-4o-mini
  - 攻略不是实时服务，中断 1-2 天不影响用户
- **触发条件**：DeepSeek API 连续 3 次重试失败
- **如果发生**：自动 fallback，成本临时上涨 $5-10/月

### 风险五：一人公司单点故障 🟡 中严重度

- **风险**：生病、倦怠、生活变故导致项目停摆
- **应对**：
  - Pipeline 自动化部署（GitHub Actions 定时触发），人不在也能跑
  - 攻略库作为存量的 SEO 资产，即使停更 1-2 个月流量也不会归零
  - 邮件订阅列表作为私域资产，停更时可以发"暂停维护"通知
  - 关键：前 12 周搭建好自动化体系，之后项目可以在"维护模式"下低功耗运行
- **触发条件**：不可预测
- **如果发生**：项目进入维护模式（只做必要更新，不发新内容），等待恢复

---

## 注意事项

1. **商标合规**：原神是 HoYoverse 商标，站点须标注"非官方粉丝站 · Game data © HoYoverse"，不使用官方 logo 商用。Phase 0 法律评估必须完成。
2. **AI 内容风险**：Google 对纯 AI 内容可能降权。**每篇 AI 攻略必须经过人工审核和修改**。差异化必须靠工具（计算器、DMG 模拟器），不能只靠内容。
3. **数据缓存**：所有 API 数据本地缓存一份，API 挂了用缓存继续。这是被原版忽略的关键策略。
4. **Pipeline 部署位置**：DeepSeek 国内访问需代理，Pipeline 部署在 GitHub Actions（海外网络，免费定时触发）。
5. **不要做的事**：
   - ❌ 不要迁移 Next.js（现在）——推倒重来对验证商业模式零帮助
   - ❌ 不要建数据库（Pro 功能前）——纯静态文件够了
   - ❌ 不要做用户注册系统——邮箱即身份，JWT 够用
   - ❌ 不要等"完美"才上线——Phase 0 验证通过就上
   - ❌ 不要一上来发 Reddit 推广帖——90/10 规则，先养号 2 个月
   - ❌ 不要把 AI 生成的内容直接发布——每篇必须人工审核
   - ❌ 不要碰中文市场变现——被米游社/B站锁死，仅做 SEO 引流

---

## 关键决策检查点

| 时间 | 检查点 | 继续条件 | 转向信号 |
|------|--------|----------|----------|
| **Phase 0 结束**（W1） | Google 收录验证 | 至少 2/3 篇被索引 | Google 不收录 → 重评 SEO 策略或内容形式 |
| **Phase 1 结束**（W2-3） | Pipeline + 首批 5 篇 | 生成质量 ≥ 手写版 + Search Console 有展示 | Pipeline 产出质量不可控 → 转人工原创策略 |
| **Phase 2 结束**（W5-6） | Pro 收入首月 | 至少 1 个付费用户 | 0 付费用户 → 检查定价/价值主张，考虑降价或免费化 |
| **M6** | 中期复盘 | 月访问 > 3K + Pro 用户 > 5 | 月访问 < 1K → 检查 SEO 策略；0 Pro 用户 → 考虑转向纯免费+捐赠 |
| **M12** | 年度决策 | 月收入 $50+ 或在增长趋势中 | 月收入 < $20 且无增长 → 考虑止损或扩展到 HSR/ZZZ |

---

*本文档配合 `battle-manual.html`（作战手册）和 `tech-evaluation-report.md`（技术评估）使用。*
*修正版 v2 — 2026-06-18 — 基于五方会审（夜兰·凝光·阿贝多·钟离·琴）修正。*
