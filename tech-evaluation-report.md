# GenshinGuide 技术路径评估报告 — 从原型到生产

> 评估人：柯知匠（AI产品工程师）  
> 评估对象：`/Users/liucs/WorkBuddy/2026-06-16-21-29-42/pr-site/` 现有原型  
> 日期：2026-06-18

---

## 〇、原型资产现状评估

先说结论：**掌门这个原型做得相当扎实**，不是废铁。

### 资产清单

| 资产 | 文件 | 行数 | 质量评价 |
|------|------|------|----------|
| HTML页面 | 14个 | ~2000行 | 结构清晰，语义化标签，SEO meta + schema.org已到位 |
| CSS设计系统 | `style.css` | 988行 | 完整的暗色游戏主题，7元素视觉系统，CSS变量体系，响应式 |
| i18n引擎 | `i18n.js` | ~900行 | 中英双语，localStorage持久化，data-i18n属性驱动 |
| 计算器逻辑 | `calculator.js` | 203行 | 6角色数据层，武器/圣遗物/配队推荐，分数计算 |
| 图片资源 | `images/` | 1张角色立绘 | raiden-shogun.png |

### 原型做对了什么

1. **SEO基础好**：每个页面都有 `<meta description>`、`<title>`、`schema.org` JSON-LD —— 这对内容站是命根子
2. **设计系统统一**：CSS变量 + 元素配色体系，不是随便堆的，改主题只改 `:root`
3. **i18n已就位**：中英双语切换可用，对面向全球的原神社区是加分项
4. **数据与展示分离**：`calculator.js` 里的 `DATA` 对象就是结构化数据的雏形，可以直接被Pipeline复用
5. **Pro变现钩子设计到位**：TL;DR快速答案 → 免费计算器 → Pro DMG模拟器锁定，转化漏斗清晰

### 原型的局限

1. **内容硬编码**：8个攻略页面是手写HTML，不可批量生成
2. **无后端**：邮箱订阅是假的（`onclick`改文字），支付是 `alert()`，无用户系统
3. **数据量小**：计算器只有6个角色，离"30+"还差24个
4. **无自动化**：新版本发布需手动改所有页面的版本号和内容
5. **无数据同步**：pipeline.html 展示了愿景但没实现

---

## 一、架构决策：迁移 Next.js vs 保留静态HTML

### 两条路径对比

| 维度 | A) 迁移 Next.js + Vercel | B) 保留静态HTML + Python后端 |
|------|--------------------------|------------------------------|
| **迁移成本** | 2-3周重写14个页面为React组件 | 0，现有资产直接用 |
| **学习曲线** | 需掌握React/Next.js/SSG/ISR | 掌门已会HTML/CSS/JS，Python门槛低 |
| **SEO** | SSG模式SEO好，但需要正确配置 | 纯静态HTML，SEO天然满分 |
| **内容Pipeline** | 需要生成MDX/JSX组件 | 直接生成HTML文件，最简单 |
| **交互工具** | React组件开发体验好 | 纯JS也能做，复杂工具稍费力 |
| **部署成本** | Vercel免费版够用 | Cloudflare Pages/Vercel静态都免费 |
| **维护负担** | 一个人维护React项目不轻 | 静态文件 + Python脚本，最轻 |
| **扩展性** | 长期最好 | 够用到50+角色攻略没问题 |
| **Pro功能实现** | 需要API Route + 数据库 | 同样需要，但可后加 |

### 我的决策：**B方案优先，预留Next.js迁移路径**

理由（务实第一）：

1. **现有原型已经能用了**。14个页面、设计系统、i18n、计算器都跑起来了。迁移Next.js意味着推倒重来，对验证商业模式没有任何帮助——用户不关心你用React还是HTML。

2. **内容Pipeline用Python更直接**。Pipeline的核心是"数据→DeepSeek→HTML文件"，Python脚本直接写HTML文件到目录，git push部署。如果用Next.js，得先生成MDX再走构建流程，多一层转换。

3. **SEO是内容站命根子**。纯静态HTML对搜索引擎最友好，加载最快。Next.js的SSG也能做到，但需要正确配置，多一个出错点。

4. **一人公司的核心矛盾是时间**。掌门的时间和精力应该花在"内容质量"和"获客"上，而不是"重构一个能用的网站"。

5. **迁移路径保留**。当Pro功能（DMG模拟器、圣遗物优化器）需要复杂前端交互时，可以把计算器页面单独用React/Vue做，嵌入静态站。不用全站迁移。

### 什么时候该迁移Next.js？

- Pro工具有3个以上需要复杂状态管理的交互组件
- 需要用户登录态影响页面渲染（SSR需求）
- 角色攻略超过100个，手动管理HTML文件变得痛苦
- 月收入稳定在 $500+，值得投入工程化

**在那之前，静态HTML + Python Pipeline 是最快见效的路径。**

---

## 二、内容Pipeline架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     Content Pipeline                             │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ 1.数据源  │───▶│ 2.变更检测│───▶│ 3.DeepSeek│───▶│ 4.自检验证│  │
│  │ genshin.  │    │ diff对比  │    │ 生成攻略  │    │ LLM二次校验│  │
│  │ jmp.blue  │    │ 版本号    │    │ 结构化输出│    │ 数值核对  │  │
│  │ API       │    │ 属性变化  │    │           │    │           │  │
│  └──────────┘    └──────────┘    └──────────┘    └─────┬─────┘  │
│                                                         │        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐         │        │
│  │ 8.部署    │◀───│ 7.更新索引│◀───│ 6.写HTML  │◀────────┘        │
│  │ git push  │    │ guides.   │    │ 模板填充  │    ┌──────────┐│
│  │ →自动触发 │    │ html列表  │    │ +i18n键值 │    │ 5.SEO生成 ││
│  │ Cloudflare│    │ sitemap   │    │           │    │ meta/schema││
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

触发方式：
  - Cron定时（每日0点同步检测）
  - 手动触发（python generate.py --character xxx）
  - Webhook（新版本发布时手动跑一次全量）
```

### 2.2 数据源选择：Honey Impact API → 改用 genshin.jmp.blue

**v3方案提到的 "Honey Impact API" 存在问题：**

| 问题 | 说明 |
|------|------|
| HoneyHunterWorld没有公开API | 它是网站，不是API服务。要用得爬页面，脆弱且可能违反ToS |
| 数据更新滞后 | 非官方维护，版本更新后数据同步时间不确定 |
| 无结构化保证 | HTML结构可能随时变，爬虫会断 |

**推荐数据源：genshin.jmp.blue（genshin.dev API）**

| 数据源 | 类型 | 端点示例 | 评价 |
|--------|------|----------|------|
| **genshin.jmp.blue** ✅推荐 | 开源REST API | `https://genshin.jmp.blue/characters` | 免费、开源、结构化JSON、社区维护 |
| genshin.dev API | 同上（同一项目） | `https://genshin.dev/api` | 同上，备用镜像 |
| Genshin Data JSON (GitHub) | 静态JSON包 | GitHub仓库clone | 数据最全（含技能倍率），但需手动更新 |
| ambr.top | 网站API | 非公开 | 数据全但无官方API授权 |
| HoYoverse官方 | 官方API | 无公开游戏数据API | 不存在面向开发者的游戏数据API |

**混合策略（最稳）：**
- 主数据源：genshin.jmp.blue（角色/武器/圣遗物基础数据）
- 补充数据：Genshin Data JSON GitHub包（技能倍率、详细数值）
- 人工维护：Meta推荐、配队策略（这部分AI生成 + 人工审核）

### 2.3 DeepSeek生成流程详细设计

**重要修正：v3方案中提到的 "DeepSeek V4 Flash" 目前不存在。** 当前可用的是 DeepSeek V3.2（2025年9月发布），这是目前最强的DeepSeek对话模型。Pipeline应基于 V3.2 设计。

#### 生成一个角色攻略的完整流程

```python
# 伪代码 — generate_guide.py

def generate_character_guide(character_id):
    # Step 1: 获取结构化数据
    char_data = fetch_from_api(f"genshin.jmp.blue/characters/{character_id}")
    weapons_data = fetch_relevant_weapons(char_data)
    artifacts_data = fetch_artifacts()
    
    # Step 2: 构建Prompt（结构化数据 + 模板指令）
    prompt = f"""
    你是原神攻略专家。根据以下游戏数据，生成{char_data['name']}的Build攻略。
    
    ## 角色数据（JSON）
    {json.dumps(char_data, ensure_ascii=False)}
    
    ## 可用武器（JSON）
    {json.dumps(weapons_data, ensure_ascii=False)}
    
    ## 输出要求
    - 按以下JSON结构输出，不要输出其他内容
    - 所有推荐必须基于提供的游戏数据，不要编造数值
    - 武器排名需说明理由
    - 配队推荐需考虑元素反应机制
    
    ## 输出结构
    {{
      "tldr": {{"weapon": "...", "artifact": "...", "team": "...", "key_stats": "..."}},
      "intro": "一段引言",
      "weapons": [{{"rank": 1, "name": "...", "rarity": 5, "atk": 608, "substat": "...", "notes": "..."}}],
      "artifacts": {{"best": "...", "why": "...", "alt": "...", "main_stats": {{"sands": "...", "goblet": "...", "circlet": "..."}}, "sub_priority": ["..."]}},
      "teams": [{{"name": "...", "members": "...", "desc": "..."}}],
      "talents": {{"priority": ["burst", "skill", "normal"], "note": "..."}},
      "rotation": "输出手法",
      "mistakes": ["常见错误1", "常见错误2"],
      "seo": {{"title": "...", "description": "..."}}
    }}
    """
    
    # Step 3: 调用DeepSeek V3.2
    response = deepseek.chat.completions.create(
        model="deepseek-chat",  # V3.2
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3  # 低温度，保证一致性
    )
    
    guide_data = json.loads(response.choices[0].message.content)
    
    # Step 4: 自检验证（第二次LLM调用）
    verification = verify_guide(guide_data, char_data)
    if verification["errors"]:
        log_errors(verification["errors"])
        # 有错误则重新生成（最多重试2次）
        if retry_count < 2:
            return generate_character_guide(character_id, retry_count + 1)
    
    # Step 5: 渲染HTML（Jinja2模板）
    html = render_template("guide_template.html", 
                          char=char_data, 
                          guide=guide_data,
                          version=current_game_version)
    
    # Step 6: 写文件 + 更新索引
    write_file(f"guides/guide-{character_id}.html", html)
    update_guides_index(character_id, guide_data["seo"])
    update_sitemap()
    
    # Step 7: Git commit
    git_commit(f"auto: update {character_id} guide for v{current_game_version}")
```

#### 自检验证机制

```python
def verify_guide(guide_data, source_data):
    """用第二次LLM调用校验攻略数据的数值准确性"""
    
    verify_prompt = f"""
    你是数据验证员。以下是AI生成的攻略和原始游戏数据。
    检查攻略中引用的所有数值是否与源数据一致。
    
    ## 生成的攻略
    {json.dumps(guide_data)}
    
    ## 源数据
    {json.dumps(source_data)}
    
    ## 检查项
    1. 武器基础ATK是否正确
    2. 武器稀有度是否正确
    3. 圣遗物套装名是否是游戏中真实存在的
    4. 角色元素属性是否正确
    5. 角色武器类型是否正确
    6. 配队成员是否是游戏中真实存在的角色
    
    输出JSON: {{"errors": ["错误描述"], "passed": true/false}}
    """
    
    result = deepseek.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": verify_prompt}],
        response_format={"type": "json_object"},
        temperature=0.0  # 确定性输出
    )
    return json.loads(result.choices[0].message.content)
```

#### 成本估算

| 项目 | 单次成本 | 说明 |
|------|----------|------|
| 生成1篇攻略（V3.2） | ~$0.003 | 输入~2000 tokens + 输出~1500 tokens |
| 验证1篇攻略 | ~$0.001 | 输入~3000 tokens + 输出~200 tokens |
| 全量更新（30角色） | ~$0.12 | 30 × $0.004 |
| 月度成本（每日同步+每周全量） | ~$1-2/月 | 绝大多数日子是增量检测，不触发生成 |

**结论：DeepSeek成本可忽略不计。** 免费100万tokens/月额度就能覆盖大部分需求。

### 2.4 程序化SEO页面自动生成

除了角色攻略，还可以程序化生成以下SEO页面：

| 页面类型 | URL模式 | 搜索意图 | 生成方式 |
|----------|---------|----------|----------|
| 角色攻略 | `/guides/{character}.html` | "raiden shogun build" | 已设计 |
| 武器对比 | `/weapons/{weapon}.html` | "engulfing lightning stats" | 从API数据直接生成 |
| 圣遗物指南 | `/artifacts/{set}.html` | "emblem of severed fate guide" | 从API数据+AI生成 |
| 配队推荐 | `/teams/{team-name}.html` | "raiden national team guide" | AI生成 |
| 元素反应 | `/elements/{element}.html` | "electro reactions genshin" | 半自动 |
| 版本更新 | `/patches/{version}.html` | "genshin 4.8 patch notes" | AI从patch notes生成 |

**优先级**：角色攻略 > 配队推荐 > 武器对比 > 其他。前两个搜索量最大。

### 2.5 Pipeline触发机制

```
┌─────────────┐     每日 00:00      ┌──────────────┐
│  Cron定时器  │───────────────────▶│ sync_wiki.py │
└─────────────┘                     └──────┬───────┘
                                           │
              ┌────────────────────────────┤
              ▼                            ▼
     ┌──────────────┐           ┌──────────────┐
     │ 有数据变更？  │───是─────▶│ generate.py  │
     └──────┬───────┘           └──────┬───────┘
            │否                         │
            ▼                           ▼
     ┌──────────────┐         ┌──────────────┐
     │ 静默退出      │         │ verify +     │
     │ 等明天        │         │ publish +    │
     └──────────────┘         │ git push     │
                               └──────────────┘

手动触发：
  python generate.py --character arlecchino    # 生成单个
  python generate.py --all                      # 全量重新生成
  python generate.py --patch 4.9                # 版本更新触发
```

---

## 三、关键系统选型

### 决策总表

| 系统 | 推荐方案 | 备选 | 理由 |
|------|----------|------|------|
| **支付** | Lemon Squeezy | Stripe（后期切换） | MoR模式自动处理全球税务，一人公司不用操心VAT/GST |
| **账号** | Lemon Squeezy内置 + JWT | Clerk（如果用户量大） | MVP不需要独立账号系统，LS的订阅管理够用 |
| **邮件** | Resend | ConvertKit（如需营销自动化） | Resend简单便宜，3000封/月免费，API集成方便 |
| **部署** | Cloudflare Pages | Vercel | CF Pages免费额度大，全球CDN快，静态站首选 |
| **数据库** | SQLite（Pipeline用）→ Supabase（Pro功能用） | 不需要时不用上 | Pipeline只需要本地文件操作；Pro功能需要用户状态时上Supabase |
| **内容生成** | DeepSeek V3.2 | OpenAI GPT-4o-mini（备用） | V3.2便宜10倍，中文质量好，OpenAI兼容接口 |
| **数据源** | genshin.jmp.blue | Genshin Data JSON（补充） | 免费、开源、结构化 |

### 3.1 支付系统：Lemon Squeezy

**为什么选Lemon Squeezy而不是Stripe：**

| 维度 | Lemon Squeezy | Stripe |
|------|---------------|--------|
| 商户记录(MoR) | ✅ 是MoR，替你收税缴税 | ❌ 不是MoR，你自己处理全球税务 |
| 税务合规 | 自动计算+收取+缴纳全球VAT/GST | 需自己注册税务、计算、申报 |
| 接入难度 | 简单，checkout链接即可 | 中等，需要后端webhook处理 |
| 手续费 | 5% + $0.50/笔 | 2.9% + $0.30/笔 |
| 月$5订阅实际到手 | ~$4.20 | ~$4.36（但需自己处理税务） |
| 适合阶段 | MVP到月入$10K | 月入$10K+后考虑切换 |

**关键点**：对于面向全球的原神社区（用户可能在任何国家），税务合规是大坑。Lemon Squeezy作为MoR帮你搞定，虽然手续费高1%，但省了一个人的税务管理成本。等月收入过$5000再考虑切Stripe。

**微信支付**：原神用户中有大量中国玩家，但微信支付需要企业资质 + ICP备案，对一人公司门槛太高。MVP阶段用Lemon Squeezy（支持支付宝），后续如果中国市场用户多再考虑。

### 3.2 账号系统：极简方案

**MVP阶段不需要独立账号系统。** 

方案：Lemon Squeezy的订阅状态通过API查询，用户邮箱就是账号。

```
用户流程：
1. 点击 "Go Pro" → 跳转 Lemon Squeezy Checkout
2. 支付成功 → LS发送含magic link的邮件
3. 用户点链接 → 前端JS存JWT到localStorage
4. 访问Pro功能 → 前端带JWT请求后端验证
5. 后端查LS API确认订阅有效 → 返回Pro数据
```

不需要密码、不需要注册页面、不需要忘记密码流程。邮箱即身份。

**何时升级**：当需要用户保存个人数据（如圣遗物仓库、Build方案）时，再上Supabase Auth。

### 3.3 邮件系统：Resend

| 维度 | Resend | ConvertKit |
|------|--------|------------|
| 定位 | 开发者邮件API | 营销自动化平台 |
| 免费额度 | 3000封/月 + 100封/天 | 1000订阅者免费 |
| 接入方式 | API/SDK，几行代码 | 需要用他们的编辑器 |
| 适合场景 | 交易邮件+简单newsletter | 复杂邮件营销漏斗 |
| 成本（超免费额度） | $20/月 5万封 | $29/月 1000+订阅者 |

**策略**：MVP用Resend发送交易邮件（支付确认、Pro开通）+ 周报newsletter。等订阅者超过1000人，再考虑切ConvertKit做营销自动化。

### 3.4 部署：Cloudflare Pages

| 维度 | Cloudflare Pages | Vercel | Netlify |
|------|------------------|--------|---------|
| 免费额度 | 无限请求 + 500次构建/月 | 100GB带宽 | 100GB带宽 |
| 全球CDN | ✅ Cloudflare全球网络 | ✅ | ✅ |
| 自定义域名 | 免费SSL | 免费SSL | 免费SSL |
| 静态站速度 | 最快之一 | 快 | 快 |
| Git集成 | GitHub/GitLab自动部署 | 同 | 同 |
| 构建时间 | 快 | 快 | 快 |

**选择Cloudflare Pages的理由**：免费额度最大，全球CDN性能强，对纯静态站完美。Pipeline的 `git push` 直接触发部署。

### 3.5 数据库：渐进式

| 阶段 | 需要数据库？ | 用什么 |
|------|-------------|--------|
| MVP（免费攻略+广告） | ❌ 不需要 | 纯静态文件 |
| Pro订阅上线 | ⚠️ 轻量需要 | Lemon Squeezy API查订阅状态 + JWT |
| Pro工具（DMG模拟器） | ✅ 需要 | Supabase（PostgreSQL + Auth + API） |
| 用户存档（圣遗物仓库） | ✅ 需要 | Supabase |

**策略**：不到万不得已不上数据库。Pro功能的"计算"可以纯前端完成（JS计算，不需要后端），只需要一个"用户是否是Pro"的状态查询。

---

## 四、开发优先级排序

按"对验证商业模式贡献最大"排序。时间假设掌门全职投入（每天6-8小时有效开发时间）。

### Phase 1：让站点能被找到（验证流量）

| # | 任务 | 工时 | 产出 | 商业价值 |
|---|------|------|------|----------|
| 1 | 部署到Cloudflare Pages + 绑定域名 | 2h | 站点上线 | 站点可访问 |
| 2 | 生成sitemap.xml + robots.txt + 提交Google Search Console | 2h | SEO可索引 | 搜索引擎收录 |
| 3 | 搭建DeepSeek内容Pipeline（generate.py + verify.py） | 8h | 自动生成攻略 | 内容可批量生产 |
| 4 | 用Pipeline批量生成30个角色攻略 | 4h | 30+攻略页面 | SEO流量入口 |
| 5 | 接入genshin.jmp.blue数据同步（sync_wiki.py） | 6h | 数据自动更新 | "24h更新"承诺可兑现 |
| 6 | 添加Google Analytics / Plausible | 1h | 流量监控 | 验证流量 |

**Phase 1 合计：~23h（3-4天）**  
**目标**：站点上线，30+攻略可被搜索引擎收录，开始获取自然流量。

### Phase 2：验证变现意愿（验证付费）

| # | 任务 | 工时 | 产出 | 商业价值 |
|---|------|------|------|----------|
| 7 | 接入Lemon Squeezy支付（Pro订阅） | 6h | 真实支付可用 | 可收钱 |
| 8 | Pro功能后端：JWT验证 + LS订阅状态查询 | 6h | Pro鉴权 | 区分免费/付费 |
| 9 | Pro DMG模拟器前端（基于现有计算器扩展） | 12h | Pro核心功能 | 付费理由 |
| 10 | 邮箱订阅功能（Resend集成） | 4h | 真实邮件订阅 | 邮件列表 |

**Phase 2 合计：~28h（4-5天）**  
**目标**：有人愿意为Pro付$5/月，验证付费意愿。

### Phase 3：增长放大（验证可规模化）

| # | 任务 | 工时 | 产出 | 商业价值 |
|---|------|------|------|----------|
| 11 | 程序化SEO页面（武器/圣遗物/配队） | 8h | 100+额外SEO页面 | 翻倍流量入口 |
| 12 | i18n内容生成（中文攻略） | 6h | 双语内容 | 中国市场流量 |
| 13 | 圣遗物优化器Pro功能 | 16h | 第二个Pro功能 | 提高付费转化 |
| 14 | 版本更新自动化（patch webhook） | 4h | 新版本自动响应 | 时效性优势 |

### 优先级总览（甘特图视角）

```
Week 1 (Day 1-5):  Phase 1 — 上线 + 30攻略 + SEO
                    [ deploy ][ sitemap ][ pipeline ][ 30 guides ][ sync ][ GA ]
                    
Week 2 (Day 6-10): Phase 2 — 支付 + Pro功能
                    [ LS支付 ][ JWT ][ DMG模拟器 ][ 邮件 ]

Week 3+ (Day 11+): Phase 3 — 增长
                    [ SEO页面 ][ i18n ][ 圣遗物优化 ][ 自动化 ]
```

**关键里程碑**：
- Day 5：站点上线 + 30攻略 + 可被Google收录 → 开始等流量
- Day 10：Pro支付可用 + DMG模拟器 → 开始验证付费
- Day 30：Google开始给流量 → 看真实数据决定方向

---

## 五、技术风险评估

### 5.1 DeepSeek API 稳定性风险

| 风险 | 严重度 | 概率 | 应对方案 |
|------|--------|------|----------|
| API服务中断 | 中 | 低 | DeepSeek作为开源模型可本地部署作为fallback；同时准备OpenAI GPT-4o-mini作为备用API |
| 价格上涨 | 低 | 中 | 当前$0.28/1M token已经极低，涨3倍也只多几美元/月。成本可忽略 |
| 模型版本不兼容 | 中 | 中 | "V4 Flash"不存在，用V3.2。API接口OpenAI兼容，换模型只需改model参数 |
| 生成质量不稳定 | 中 | 中 | 低temperature(0.3) + JSON结构化输出 + 自检验证 + 人工抽检5% |
| 国内访问受限 | 高 | 中 | API服务器在海外，国内调用需代理。Pipeline在海外VPS或Cloudflare Workers运行 |

**综合评估**：DeepSeek风险可控。最大问题是"国内访问"——如果Pipeline跑在国内机器上，需要配代理。建议Pipeline部署在海外（Cloudflare Workers / GitHub Actions / 海外VPS）。

### 5.2 数据源依赖风险

| 风险 | 严重度 | 应对方案 |
|------|--------|----------|
| genshin.jmp.blue停止维护 | 中 | 数据是开源JSON，可fork自建。同时维护本地数据副本 |
| 数据更新延迟 | 低 | 不依赖实时性，每日同步够用 |
| API结构变更 | 低 | 加版本检测，异常时报警 |
| 数据不完整（缺技能倍率） | 中 | 补充Genshin Data JSON包 + AI根据已有数据推断 |

**关键策略**：**所有从API获取的数据本地缓存一份**。API挂了用缓存数据继续生成，不阻断Pipeline。

### 5.3 支付合规风险

| 风险 | 严重度 | 应对方案 |
|------|--------|----------|
| 全球税务合规 | 高 | 用Lemon Squeezy（MoR模式），它替你处理全球VAT/GST |
| 中国用户支付 | 中 | LS支持支付宝。微信支付需企业资质，MVP阶段不做 |
| 退款纠纷 | 低 | LS有内置退款流程，$5金额低纠纷率低 |
| 欺诈支付 | 低 | LS有风控，$5/月订阅不是欺诈高发场景 |
| 虚拟商品合规 | 低 | 数字内容订阅，无特殊许可证要求 |

**注意**：原神是HoYoverse的商标。站点要明确标注"非官方粉丝站 · Game data © HoYoverse"，不使用官方logo/素材做商业用途。现有原型已做到这一点。

### 5.4 SEO技术债务风险

| 风险 | 严重度 | 应对方案 |
|------|--------|----------|
| 重复内容惩罚 | 中 | 每个攻略页面确保unique content，不照搬Wiki原文 |
| AI内容质量惩罚 | 高 | Google对纯AI生成内容可能降权。必须有unique value（计算器、工具、人工审核的Meta推荐） |
| 页面加载速度 | 低 | 纯静态HTML，加载快。注意图片优化 |
| 结构化数据错误 | 低 | schema.org已正确配置，Pipeline生成时保持 |
| 内链结构 | 中 | 相关攻略推荐（已有），需扩展为完整的内链网络 |

**最重要的一条**：Google的EEAT原则（Experience, Expertise, Authoritativeness, Trustworthiness）对AI生成内容越来越严格。纯AI攻略站可能被降权。**差异化必须靠"工具"**——计算器、DMG模拟器、圣遗物优化器是纯内容站做不到的，这是核心护城河。

---

## 六、总结：务实行动清单

### 立即该做的（本周）

1. **部署上线**：把现有原型推到Cloudflare Pages，绑域名，提交Google Search Console
2. **搭Pipeline**：写 `generate.py`，用DeepSeek V3.2生成30个角色攻略
3. **接数据源**：写 `sync_wiki.py`，从genshin.jmp.blue同步数据

### 这周能验证的

- Pipeline能否自动生成质量过关的攻略？
- 生成的攻略SEO是否合格？
- 站点是否被Google收录？

### 下周该做的

- 接Lemon Squeezy支付
- 扩展计算器为DMG模拟器Pro功能
- 接Resend做邮件订阅

### 不要做的

- ❌ 不要迁移Next.js（现在）
- ❌ 不要建数据库（现在）
- ❌ 不要做用户注册系统（现在）
- ❌ 不要等"完美"才上线（现在就上）

**一人公司的核心优势是速度。先用现有原型 + Python Pipeline跑起来，用真实流量和付费数据验证方向，再决定往哪投入工程化。**

---

## 附录A：Pipeline目录结构建议

```
genshinguide/
├── site/                    # 静态站点（现有原型）
│   ├── index.html
│   ├── guides/
│   │   ├── guide-raiden.html
│   │   └── ...
│   ├── css/
│   ├── js/
│   └── images/
├── pipeline/                # 内容Pipeline
│   ├── generate.py          # 生成单个攻略
│   ├── sync_wiki.py         # 数据同步
│   ├── verify.py            # 自检验证
│   ├── publish.py           # 写文件+更新索引
│   ├── templates/           # HTML模板
│   │   └── guide_template.html
│   ├── data/                # 本地数据缓存
│   │   └── cache/
│   └── config.py            # API keys, 配置
├── .github/workflows/       # GitHub Actions定时任务
│   └── daily-sync.yml
└── README.md
```

## 附录B：关键技术参数速查

| 参数 | 值 | 说明 |
|------|-----|------|
| DeepSeek模型 | `deepseek-chat` (V3.2) | OpenAI兼容接口 |
| DeepSeek成本 | ~$0.004/篇攻略 | 生成+验证 |
| 数据源API | `https://genshin.jmp.blue` | 免费、开源 |
| 部署平台 | Cloudflare Pages | 免费、全球CDN |
| 支付平台 | Lemon Squeezy | 5%+$0.50/笔，MoR模式 |
| 邮件服务 | Resend | 3000封/月免费 |
| Pipeline运行环境 | GitHub Actions | 免费、定时触发、海外网络 |

---

*报告结束。如有技术细节需要深入讨论，随时找我。*
