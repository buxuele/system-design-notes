# 部署到 Vercel 操作指南

仓库地址：https://github.com/buxuele/system-design-notes

## 导入步骤

1. 打开 https://vercel.com/new 并登录你的 Vercel 账号。
2. 在导入列表中选择 buxuele/system-design-notes，若未出现则点击 Adjust 仓库权限并授权该仓库。
3. 框架预设选择 VitePress，若自动识别为 Other 则手动填写下面三项。
4. 构建命令填写 npm run build。
5. 输出目录填写 .vitepress/dist。
6. 安装命令保持默认的 npm install。
7. 点击 Deploy，等待构建完成。
8. 仓库根目录的 vercel.json 已固化构建命令与输出目录，项目设置页里的同名项会被仓库配置覆盖，显示为默认的 dist 也不影响。

## 构建参数速查

1. Framework Preset: VitePress
2. Build Command: npm run build
3. Output Directory: .vitepress/dist
4. Install Command: npm install
5. Node.js 版本: 18 及以上，使用 Vercel 默认即可
6. 仓库内 vercel.json 等价固化了 Build Command 与 Output Directory，调整参数只需改仓库文件再推送

## 部署后验证

1. 打开分配的域名，首页应显示 28 章中文目录。
2. 点击任意章节，确认正文与配图正常显示。
3. 访问 /04-rate-limiter/ 这类规范路径，确认返回 200。
4. Vercel 控制台的 Git 选项保持开启，之后 git push 会自动触发部署。

## 本地等价验证

1. 安装依赖：npm install
2. 构建站点：npm run build
3. 本地预览：npm run preview
4. HTML 标签平衡校验：python3 tests/test_html_balance.py
5. Vue 模板解析校验：node tests/test_vue_template_parse.mjs
6. 产物死链校验：python3 tests/test_dist_links.py
7. 翻译脚本单测：python3 -m pytest tests/ -q

## 翻译脚本密钥

1. OpenRouter 密钥已从 translate_notes.py 移除，改为读取环境变量 OPENROUTER_API_KEY。
2. 本地密钥保存在根目录 .env 文件中，该文件已被 gitignore，不会上传。
3. 重新翻译前执行 source .env 导入密钥，再运行 python3 translate_notes.py。

## 本次修复记录

1. Chat System 与英文原版同样存在 div 未闭合，已闭合。
2. 五处 div 与正文同行导致被包进段落，已按英文原版结构拆行。
3. 目录页 28 条章节链接原先指向目录而非 README，已改写为规范路径。
4. Stock Exchange 中指向数字钱包章节的错误链接，已改为 /27-digital-wallet/。
5. translate_notes.py 中硬编码的 OpenRouter 密钥已被 GitHub 推送保护拦截并移除。
6. 翻译单测中源目录层级写错导致的失败已修正，仓库内无英文原版时自动跳过。
