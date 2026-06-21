# GenshinGuide — 支付打通完整方案

> 版本 v2 · 2026-06-21
> 状态：PM 审查完成，方案完备

---

## 〇、PM 审查发现与修复

审查中发现 3 个流程断点，已修复：

| # | 断点 | 修复 |
|---|------|------|
| 1 | 付完钱 JWT 怎么到浏览器？webhook 是服务器间的，不经过用户 | LS checkout 设 `redirect_url` → thanks.html → 调 Worker `/lookup` → 拿到 JWT |
| 2 | LS 没收集邮箱，webhook 里没邮箱 | LS 产品启用「Collect email address」 |
| 3 | Worker 挂了，用户付了钱但 KV 没记录 | Worker `/verify` 加 LS API 降级查询 |

---

## 一、架构

```
用户付 $5
  → LS checkout → 填邮箱 → 支付成功
    → LS webhook → Worker → KV 写 order_id → email
    → LS 跳转 redirect_url → /support/thanks.html?order=xxx
      → thanks.html 调 Worker /lookup?order=xxx
      → Worker 查 KV → 返回 email + 日期
      → 展示感谢卡 + localStorage 存 JWT
        → 导航栏 ☕ Support → ❤️ Supporter
        → 广告位隐藏

换设备恢复：
  定价页输入邮箱 → Worker /verify?email=xxx
    → 查 KV → 找到 → 返回 JWT
    → 查 KV → 没找到 → 调 LS API 降级查询 → 找到 → 补写 KV → 返回 JWT
    → 都没找到 → 返回「无购买记录」
```

**组件**：

| 组件 | 用途 | 成本 |
|------|------|------|
| Lemon Squeezy | 收钱 + webhook | 5% + $0.50/笔 |
| Cloudflare Worker | 验签 + 查 KV + 返回 JWT | $0（免费额度） |
| Cloudflare Workers KV | email → paid_at | $0（免费额度） |
| PayPal 中国 | LS 提现 → 国内银行卡 | 免费 |
| pro.js | 前端 JWT 检查 + UI 切换 | 本地 |
| thanks.html | 感谢卡片 | 本地 |

---

## 二、前置工作（2026-06-21 完成）

| # | 事项 | 步骤 | 状态 |
|---|------|------|------|
| 1 | 注册 Lemon Squeezy | lemonsqueezy.com → 个人账号 → Settings → Payout → 绑定 PayPal | ⬜ |
| 2 | PayPal 确认 | 确认已绑国内银行卡，能正常提现 | ⬜ |
| 3 | 创建 LS 产品 | $5 一次性，获取 Store ID + Product ID | ⬜ |
| 4 | 获取 webhook secret | LS → Settings → Webhooks → 生成 Signing Secret | ⬜ |
| 5 | CF KV namespace | CF Dashboard → Workers & Pages → KV → Create | ⬜ |

**完成后获得的 4 个值**：
- LS Store ID
- LS Product ID
- LS Webhook Signing Secret
- LS API Key（Settings → API，用于降级查询）
- CF KV Namespace ID

---

## 三、代码改动（13 个文件）

### 执行步骤

```
Step 1  → 重写 pricing.html（定价页）
Step 2  → 更新 i18n.json（增删改翻译键）
Step 3  → 更新 guide_template.html（nav + Pro Teaser）
Step 4  → 更新 home.html（nav + pricing teaser）
Step 5  → 更新 7 个静态页 nav 按钮
Step 6  → 新建 pro.js（JWT 检查 + UI 切换）
Step 7  → 新建 thanks.html（感谢卡片 + fetch Worker /lookup）
Step 8  → 新建 Cloudflare Worker（/webhook + /lookup + /verify + LS API 降级）
Step 9  → LS 后台：开启 Collect email + 设 redirect_url
Step 10 → 替换 LS checkout 占位符为真实链接（含 redirect_url）
Step 11 → Privacy 页面加邮箱存储说明
Step 12 → rebuild + acceptance 验证
```

### 3.1 `pr-site/pricing.html` — 整页重写

**删除**：
- 3 个 Scenario 区（valueEx 全系列）
- Annual Plan 横幅
- "Why monthly?" 文案
- 不存在的功能列表（DMG模拟/圣遗物优化/循环分析/配装对比）
- "MOST POPULAR" 徽章
- `alert(t('pricing.checkout_soon'))`
- ¥36/年 价格

**保留**：
- nav 结构（按钮文案改）
- footer 结构
- lang-switcher 引用

**新增**：
- 标题 → `☕ Support This Project`
- 副标题 → `26 guides, free forever. If they helped you, buy me a coffee.`
- 价格卡片 Free | ☕ Supporter
- 真实权益：
  - Free：✓ 26 篇攻略 · ✓ 基础计算器 · ✓ 强度榜 · ✓ 配队推荐
  - Supporter：✓ 所有 Free 权益 · 📧 新攻略邮件通知 · ❤️ 专属感谢卡 · 🙏 让项目持续更新
- LS checkout 按钮（先放占位符，Step 9 替换）
- 「已有支持记录？」邮箱输入框 + 恢复按钮
- 重写 FAQ（5 条）

**定价卡示例代码**：

```html
<a href="https://store.lemonsqueezy.com/checkout/buy/xxx" 
   class="btn btn-gold" data-i18n="support.cta">☕ Support $5</a>
<p data-i18n="support.pay_hint">🔒 Secure payment via Lemon Squeezy · One-time</p>
```

---

### 3.2 `pipeline/data/i18n.json` — 翻译键改动

**新增 `support.*` 键（15 个）**：

| 键 | EN | ZH |
|----|----|----|
| `support.title` | Support This Project | 支持这个项目 |
| `support.subtitle` | 26 guides, free forever... | 26篇攻略，永远免费... |
| `support.free_label` | Free | 免费 |
| `support.supporter_label` | ☕ Supporter | ☕ 支持者 |
| `support.supporter_price` | $5 | ¥35 |
| `support.supporter_sub` | One-time · No subscription | 一次性 · 无订阅 |
| `support.free_f1` | 26 character guides | 26篇角色攻略 |
| `support.free_f2` | Basic calculator | 基础计算器 |
| `support.free_f3` | Tier list | 强度榜 |
| `support.free_f4` | Team recommendations | 配队推荐 |
| `support.supporter_f1` | All Free features | 所有免费权益 |
| `support.supporter_f2` | 📧 New guide email alerts | 📧 新攻略邮件通知 |
| `support.supporter_f3` | ❤️ Personalized thank-you card | ❤️ 专属感谢卡片 |
| `support.cta` | ☕ Support $5 | ☕ 支持 ¥35 |
| `support.pay_hint` | Secure payment via Lemon Squeezy | Lemon Squeezy 安全支付 |
| `support.existing_title` | Already a supporter? | 已是支持者？ |
| `support.existing_desc` | Enter your email to restore access. | 输入邮箱恢复 Pro 权益。 |
| `support.email_placeholder` | your@email.com | 你的邮箱 |
| `support.verify_btn` | Restore | 恢复 |
| `support.faq1_q` | Where does the money go? | 钱用在哪？ |
| `support.faq1_a` | Domain renewal, coffee for late-night guide writing. | 域名续费 + 买咖啡熬夜更新攻略。 |
| `support.faq2_q` | How do guides stay updated? | 攻略怎么保持更新？ |
| `support.faq2_a` | Every version update within 48h. | 每次版本更新 48h 内更新受影响攻略。 |
| `support.faq3_q` | Why free? | 为什么不收费？ |
| `support.faq3_a` | Build guides should be free. Support if you find them useful. | 攻略应该免费。觉得有用就请杯咖啡。 |
| `support.faq4_q` | Payment issues? | 支付遇到问题？ |
| `support.faq4_a` | Contact xxx@gmail.com | 联系 xxx@gmail.com |

**修改已有键**：

| 键 | 旧值 | 新值 |
|----|------|------|
| `nav.pro` | `Pro $5/mo` / `会员 $5/月` | `☕ Support` / `☕ 支持` |
| `guide.pro_teaser_title` | `Pro DMG Simulator — Coming Soon` | `❤️ Support This Project` / `❤️ 支持这个项目` |
| `guide.pro_teaser_desc` | `Get exact damage numbers...` | `26 guides, free forever...` |
| `guide.pro_teaser_cta` | 长文案 | `If they helped you, consider supporting.` |
| `guide.pro_lock_btn` | `Learn More` | `☕ Support $5` / `☕ 支持 ¥35` |
| `home.btn_pro` | `⭐ Pro $5/mo` | `☕ Support` / `☕ 支持` |
| `home.pro_label` | `Pro` | `Supporter` / `支持者` |
| `home.pro_sub` | `Cancel anytime` | `One-time · No subscription` |
| `home.pro_btn` | `Go Pro — $5/month` | `☕ Support $5` / `☕ 支持 ¥35` |
| `home.pro_badge` | `MOST POPULAR` | (删除，保留空) |

**删除键**：
- `valueEx.*`（全部 12 个键）
- `pricing.annual_*`（约 5 个键）
- `pricing.checkout_soon`
- `pricing.why_monthly_desc`

---

### 3.3 `pipeline/templates/guide_template.html` — nav + Pro Teaser

**导航栏**：
```
之前：<li><a href="pricing.html" class="btn-pro" data-i18n="nav.pro">Pro $5/mo</a></li>
之后：<li><a href="pricing.html" class="btn-pro" data-i18n="nav.pro">☕ Support</a></li>
```

**Pro Teaser 区域**（26 篇攻略底部）：
```
之前：
  🔮 Pro DMG Simulator — Coming Soon
  Get exact damage numbers, compare artifact loadouts...
  [Learn More]

之后：
  ❤️ Support This Project
  26 guides, free forever. If they helped you, consider supporting.
  [☕ Support $5] → 定价页
```

按钮样式保留 `btn-gold`。

---

### 3.4 `pipeline/templates/home.html` — nav + pricing teaser

**导航栏**：同 3.3。

**Pricing teaser**（首页底部 pricing 预览区）：
```
之前：Pro $5/month → Pro unlocks advanced tools.
之后：☕ Support us → Help keep 26 guides updated and free.
```

---

### 3.5 7 个静态页 — nav 按钮

以下 7 个文件的导航栏 `Pro $5/mo` → `☕ Support`：

- `pr-site/calculator.html`
- `pr-site/guides.html`
- `pr-site/tier-list.html`
- `pr-site/about.html`
- `pr-site/privacy.html`
- `pr-site/pipeline.html`
- `pr-site/pricing.html`（自身）

**改动**：每页改一行 `<a>` 标签的 data-i18n 和内文。

---

### 3.6 `pr-site/js/pro.js` — 新建

**功能**：
1. 页面加载 → 检查 `localStorage.pro_jwt`
2. 有 JWT → 导航栏 `.btn-pro` 文本 → `❤️ Supporter`
3. 有 JWT → `.ad-native` → `display:none`
4. 定价页 → 邮箱输入 → `fetch(Worker)` → 查 KV → 返回 JWT → 刷新
5. 定价页 → 状态文本更新（验证中 / 成功 / 未找到 / 错误）

**加载方式**：所有页面在 `</body>` 前加 `<script src="../js/pro.js"></script>`。
- 通过 guide_template.html 和 home.html 覆盖 26 篇攻略 + 首页
- 7 个静态页手动添加

**pro.js 伪代码**：

```javascript
var WORKER_URL = 'https://pro.bricklayer.tech'; // 部署后替换
var JWT_KEY = 'pro_jwt';

// 页面加载 → 检查 Pro
if (localStorage.getItem(JWT_KEY)) applyProUI();

// 定价页 → 邮箱恢复
var emailInput = document.getElementById('pro-email-input');
var verifyBtn  = document.getElementById('pro-verify-btn');
if (verifyBtn && emailInput) {
  verifyBtn.onclick = function() {
    var email = emailInput.value.trim();
    if (!email.includes('@')) return showStatus('invalid');
    verifyBtn.disabled = true;
    fetch(WORKER_URL + '/verify?email=' + encodeURIComponent(email))
      .then(r => r.json())
      .then(function(d) {
        if (d.valid) {
          localStorage.setItem(JWT_KEY, d.token);
          location.reload();
        } else {
          verifyBtn.disabled = false;
          showStatus('not_found');
        }
      });
  };
}

function applyProUI() {
  // 导航栏
  document.querySelectorAll('.btn-pro').forEach(function(el) {
    el.textContent = '❤️ ' + t('pro.supporter');
    el.style.background = 'linear-gradient(135deg, #e84a7a, #c0392b)';
  });
  // 隐藏广告
  document.querySelectorAll('.ad-native').forEach(function(el) {
    el.style.display = 'none';
  });
}
```

---

### 3.7 `pr-site/support/thanks.html` — 新建

**功能**：
- 读取 URL 参数：`?order=ORDER_ID`
- 页面加载时 fetch Worker：`/lookup?order=ORDER_ID`
- Worker 返回 `{email, paid_at}` → 展示感谢卡
- Worker 返回错误 → 显示「订单查询失败，请联系 support@bricklayer.tech」
- 无参数时显示提示：「Support the project to get your personalized card.」
- 卡片含邮箱和日期
- 按钮：「📋 复制链接」「📸 截图分享」
- 展示完卡片后，存 JWT 到 localStorage → 后续访问自动显示 ❤️ Supporter
- 纯静态，不经 build.py，不索引
- 暗色背景（和主站一致）
- 居中卡片，渐变边框
- 大号 ❤️ + GenshinGuide logo
- 白色文字，适中留白

---

### 3.8 Cloudflare Worker — 新建（后端）

**文件名**：`worker.js`（部署到 CF Workers）

**功能**：
1. `POST /webhook` — 接收 LS webhook → 验签 → 提取 email → KV.put(email_hash, paid_at) → 返回 JWT
2. `GET /verify?email=xxx` — 查 KV → 找到 → 返回 JWT；未找到 → 返回错误

**JWT 结构**：
```json
{
  "email": "sha256_of_email",
  "paid_at": "2026-06-21",
  "iat": 1718928000
}
```

**Worker 端点**：

| 端点 | 触发方 | 功能 |
|------|--------|------|
| `POST /webhook` | LS | 验签 → 提取 order_id + email → KV.put(order_id, {email, paid_at}) |
| `GET /lookup?order=xxx` | thanks.html | 查 KV(order_id) → 返回 email + 日期 |
| `GET /verify?email=xxx` | pricing.html | 查 KV(遍历找 email) → 找到→返回 JWT；没找到→调 LS API 降级 |

**KV Schema**：
```
Key: order_id (LS 订单号)
Value: { "email": "player@gmail.com", "paid_at": "2026-06-21" }

额外索引（用于 /verify 快速查找）：
Key: "email:" + SHA256(email)
Value: order_id
```

**降级逻辑**（Worker `/verify`）：
```javascript
// 1. 查 KV
let orderId = await KV.get('email:' + sha256(email));
if (orderId) return generateJWT(email);

// 2. KV 没找到 → 调 LS API
let lsResponse = await fetch(
  `https://api.lemonsqueezy.com/v1/orders?filter[user_email]=${email}`,
  { headers: { 'Authorization': 'Bearer ' + LS_API_KEY } }
);
// 3. LS 有 → 补写 KV → 返回 JWT
// 4. LS 也无 → 返回 { valid: false }
```

---

## 四、不改的地方（保持现状）

| 位置 | 原因 |
|------|------|
| 首页统计栏 | `$0 Free Core Features` 保持，捐赠不影响免费定位 |
| 26 篇攻略内容 | 不变 |
| 计算器 | 不变 |
| `acceptance.js` | 静态页数没变（8 个） |
| `sitemap.xml` | 不加 support 页（个人页面，不索引） |
| `build.py STATIC_PAGES` | 不变 |
| 攻略 JSON 数据 | 不变 |

---

## 五、用户跨设备体验

| 场景 | 体验 |
|------|------|
| LS 付钱后同设备 | 付完 → LS 跳转 thanks.html?order=xxx → 调 Worker /lookup → 展示感谢卡 + 存 JWT → 自动生效 |
| 换设备/清缓存 | 定价页输入邮箱 → Worker /verify → 查 KV → 找到 → 返回 JWT → 恢复 |
| KV 丢失但 LS 有记录 | 同上 → KV 没找到 → 调 LS API 降级 → 找到 → 补写 KV → 返回 JWT → 恢复 |
| 两者都没找到 | 返回「无购买记录」 |
| 没恢复时 | 导航栏显示 `☕ Support`，点进去定价页可见邮箱输入 |
| Worker 挂了 | 页面正常浏览，恢复功能不可用，不影响其他功能 |

---

## 六、执行进度

| Step | 事项 | 状态 |
|------|------|------|
| 1 | 重写 pricing.html | ⬜ |
| 2 | 更新 i18n.json | ⬜ |
| 3 | 更新 guide_template.html | ⬜ |
| 4 | 更新 home.html | ⬜ |
| 5 | 更新 7 个静态页 nav | ⬜ |
| 6 | 新建 pro.js | ⬜ |
| 7 | 新建 thanks.html（含 Worker /lookup 调用） | ⬜ |
| 8 | 新建 Worker（/webhook + /lookup + /verify + LS API 降级） | ⬜ |
| 9 | LS 后台：开启 Collect email + 设 redirect_url | ⬜ |
| 10 | 替换 LS checkout 占位符为真实链接（含 redirect_url） | ⬜ |
| 11 | Privacy 页面加邮箱存储说明 | ⬜ |
| 12 | rebuild + acceptance 验证 | ⬜ |

---

*方案 v2 · PM 审查修订完毕 · 2026-06-21*
