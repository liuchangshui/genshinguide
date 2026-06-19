# GenshinGuide — 2026-06-18 会话总结

> 从评估到执行，一天之内从原型推进到可部署状态。

---

## 一、项目起点

收到 `genshinguide-deliverables/` 目录，内含：
- 14 页静态 HTML 原型（index、guides、calculator、pricing、pipeline、9 个攻略页）
- 988 行 CSS 设计系统（暗色主题 + 7 元素视觉）
- 398 行 i18n 中英双语引擎
- 203 行计算器逻辑（6 个角色硬编码）
- 3 份参谋团报告（battle-manual.html、tech-evaluation-report.md、overview.md）

---

## 二、关键决策

| # | 决策 | 原因 |
|---|------|------|
| 1 | 不迁移 Next.js | 静态 HTML 原型质量扎实，迁移 = 推倒重来 2-3 周，对验证零帮助 |
| 2 | Freemium 模式 | 攻略免费引流，Pro $5/月锁工具功能（DMG 模拟器、AI Copilot） |
| 3 | 收入预期下调 5-10 倍 | M12 $40-100/月（非 $185-530），新域名 SEO 第一年爬坡慢 |
| 4 | 去掉 DeepSeek API | 成本转嫁用户，改为纯数据驱动 + 人工写内容 |
| 5 | 攻略永远免费，Pro 只锁工具 | HoYoverse 法律合规——Fan Content Policy 不覆盖数字服务但需谨慎 |
| 6 | 图片从 genshin.jmp.blue 获取 | 免费、开源、结构化、无 API Key |

---

## 三、遇到的问题与解决方法

### 问题 1：占位攻略全是雷神内容 🔴
**现象**：7 个攻略页（hutao/ayaka/yelan/nahida/kazuha/zhongli/albedo）的正文是复制 `guide-raiden.html` 的。标题写"胡桃"但武器推荐"薙草之稻光"、配队写"雷神国家队"。

**根因**：快速原型阶段只改了名字，正文完全没动。`i18n.js` 中 `guide.*` 共享翻译键全部写的是雷神文本。

**解决**：
- 专家 Agent 逐篇修复正文（武器表/圣遗物/配队/天赋/手法/误区）
- 从 8 个攻略中移除 185 个指向共享 `guide.*` 的 `data-i18n` 属性
- 添加角色专属翻译键（`hutao.*`、`ayaka.*` 等）到 `i18n.js`
- 流水线生成 Bennett/Kazuha/Nahida 3 篇全新攻略

**教训**：永不复制攻略页做新角色。共享翻译键只放 UI 文本（标题/表头），角色内容用专属键。

### 问题 2：i18n.js 语法错误导致中英文切换失效 🔴
**现象**：切换中英文按钮无反应，中文内容不显示。

**根因**：两次——
1. 翻译文本中 `Gladiator's` 的单引号未转义（`'Gladiator's Finale'`）
2. 新加翻译中 `don't`/`won't` 未转义（`'...won't be ready'`）
3. Bash heredoc 中 `$5` 被 shell 吃掉变成 `/month`

**解决**：
- `"Gladiator's Finale"` 用双引号包裹
- `won\'t` 加反斜杠转义
- 用 `node -e "new Function(code)"` 做 JS 语法验证

**教训**：每次编辑 `i18n.js` 后必须跑 JS 语法验证。单引号字符串中的缩写词必须转义。不在 bash heredoc 中放 `$` 符号。

### 问题 3：Workflow Agent 无法写入文件 🟡
**现象**：7 个 Agent 消耗 300K+ token、77 次工具调用，零文件写入磁盘。

**根因**：Workflow 子 Agent 运行在沙箱环境，文件变更不持久化到项目目录。

**解决**：改用直接 `Write`/`Edit`/`Bash` 操作，后台 `Agent` 做独立的分析/审计任务。

**教训**：Workflow 适合分析决策，不适合文件产出。文件产出用主会话直接操作。

### 问题 4：Python 3.9 类型注解兼容 🟡
**现象**：`sync_wiki.py` 和 `generate.py` 语法报错 `dict | list`。

**根因**：`X | Y` 联合类型语法是 Python 3.10+ 特性，系统运行 3.9.7。

**解决**：用 `typing.Optional`/`Union` 替换或移除注解。

**教训**：写代码前检查 `python3 --version`。

### 问题 5：卡片用元素 emoji 代替角色立绘 🟡
**现象**：攻略列表卡片和关联攻略卡片用 `💧🔥🍃` 等 emoji 占位，没有角色形象。

**根因**：原型阶段优先结构，忽略视觉。

**解决**：从 `genshin.jmp.blue/characters/{id}/card` 下载角色卡片图（WebP）。

**教训**：角色页面必须有真实立绘，不用 emoji 或纯色块占位。

### 问题 6：i18n 翻译键污染 🟡
见问题 1。

---

## 四、当前项目状态

### 站点文件
```
pr-site/
  index.html             ✅ 首页（6 张精选卡片，3×2 居中网格）
  guides.html            ✅ 攻略列表（13 张角色卡片，全部真实立绘）
  calculator.html        ✅ 交互式计算器
  pricing.html           ✅ Pro 定价页
  pipeline.html          ✅ 流水线说明
  guide-raiden.html      ✅ 雷电将军
  guide-xiangling.html   ✅ 香菱
  guide-furina.html      ✅ 芙宁娜（手写）
  guide-arlecchino.html  ✅ 阿蕾奇诺（手写）
  guide-neuvillette.html ✅ 那维莱特（手写）
  guide-bennett.html     ✅ 班尼特（流水线生成）
  guide-kazuha.html      ✅ 万叶（流水线生成）
  guide-nahida.html      ✅ 纳西妲（流水线生成）
  guide-hutao.html       ✅ 胡桃（专家修复）
  guide-ayaka.html       ✅ 神里绫华（专家修复）
  guide-yelan.html       ✅ 夜兰（专家修复）
  guide-zhongli.html     ✅ 钟离（专家修复）
  guide-albedo.html      ✅ 阿贝多（专家修复）
  sitemap.xml            ✅
  robots.txt             ✅
  images/                ✅ 18 个角色图片（card + icon）
  js/i18n.js             ✅ 12 个角色翻译键 + 通用 UI 键
  js/calculator.js       ✅ 6 角色数据（已修正武器类型错误）
  css/style.css          ✅ 988 行设计系统
```

### 流水线文件
```
pipeline/
  config.py          ✅ 零 API 配置
  sync_wiki.py       ✅ 数据同步（12 角色已缓存）
  generate.py        ✅ scaffold + render（无 AI）
  verify.py          ✅ 确定性验证
  publish.py         ✅ 发布 + 更新索引
  make.py            ✅ 主控脚本
  templates/
    guide_template.html ✅ Jinja2 模板
  data/
    cache/           ✅ 12 角色 + 武器 + 圣遗物
    guides/          ✅ Bennett/Kazuha/Nahida JSON
  CONTENT_STANDARDS.md ✅ 内容质量标准
  PIPELINE_README.md ✅ 使用说明
  requirements.txt   ✅ requests + jinja2

.github/workflows/
  daily-sync.yml     ✅ 每日数据同步
```

### 文档
```
DEPLOY.md            ✅ 部署指南
LESSONS_LEARNED.md   ✅ 问题与教训
corrections-memo.md  ✅ 五方会审修正记录
overview.md          ✅ 项目概览
dev-handoff.md       ✅ 开发任务清单
tech-evaluation-report.md ✅ 技术评估
battle-manual.html   ✅ 作战手册
```

---

## 五、流水线操作速查

```bash
cd pipeline/

# 每日数据同步（CI 自动跑）
python make.py sync

# 加新角色
python make.py new {id}        # 生成 scaffold
# 编辑 data/guides/{id}.json   # 人工填写
python make.py render {id}     # 渲染 HTML
# 浏览器审核
python make.py publish {id}    # 发布

# 版本更新
python make.py sync            # 拉最新数据
python make.py update-all      # 重渲染全部

# 状态
python make.py status
```

---

## 六、部署

```bash
# 1. 推到 GitHub
git init && git add . && git commit -m "GenshinGuide v1" && git push

# 2. Cloudflare Pages 连接仓库
#    输出目录: pr-site/
#    自定义域名: buildguide.gg（推荐）

# 3. Google Search Console 提交 sitemap.xml

# 月成本: ~$0.83（仅域名费）
```

---

## 七、内容质量标准速查

每篇攻略上线前检查：
- [ ] 武器 ATK 数值与官方一致
- [ ] 圣遗物套装名真实存在
- [ ] 配队成员全部可玩
- [ ] 角色元素/武器类型正确
- [ ] HP 角色不推 ATK，ATK 角色不推 HP
- [ ] 天赋优先级符合 meta
- [ ] 输出手法可实际执行
- [ ] 角色图片加载正常
- [ ] JS 语法验证通过
- [ ] 中英文切换正常

详见 `pipeline/CONTENT_STANDARDS.md`

---

*会话日期：2026-06-18*
*下次继续：内容生产（补充剩余角色）、部署上线、Reddit 养号*
