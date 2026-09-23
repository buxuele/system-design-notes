# 系统设计笔记中文站

《系统设计面试：内部指南》第一卷与第二卷的完整中文翻译，共 28 章，使用 VitePress 构建为静态站点。

原仓库：https://github.com/liquidslr/system-design-notes

# 章节目录

1. 第1章 - 从零扩展到数百万用户：[笔记](./系统设计笔记/01. Scaling/README.md)
2. 第2章 - 估算分析：[笔记](./系统设计笔记/02. Back Of the Envelope Estimation/README.md)
3. 第3章 - 系统设计面试框架：[笔记](./系统设计笔记/03. System Design Framework/README.md)
4. 第4章 - 设计限流器：[笔记](./系统设计笔记/04. Rate Limiter/README.md)
5. 第5章 - 设计一致性哈希：[笔记](./系统设计笔记/05. Consistent Hashing/README.md)
6. 第6章 - 设计键值存储：[笔记](./系统设计笔记/06. Key-Value Store/README.md)
7. 第7章 - 设计分布式系统中的唯一ID生成器：[笔记](./系统设计笔记/07. Unique-Id Generator/README.md)
8. 第8章 - 设计URL缩短器：[笔记](./系统设计笔记/08. URL Shortener/README.md)
9. 第9章 - 设计网络爬虫：[笔记](./系统设计笔记/09. Web Crawler/README.md)
10. 第10章 - 设计通知系统：[笔记](./系统设计笔记/10. Notification System/README.md)
11. 第11章 - 设计新闻流系统：[笔记](./系统设计笔记/11. News Feed System/README.md)
12. 第12章 - 设计聊天系统：[笔记](./系统设计笔记/12. Chat System/README.md)
13. 第13章 - 设计搜索自动补全系统：[笔记](./系统设计笔记/13. Search Autocomplete/README.md)
14. 第14章 - 设计YouTube：[笔记](./系统设计笔记/14. Youtube/README.md)
15. 第15章 - 设计Google Drive：[笔记](./系统设计笔记/15. Google Drive/README.md)
16. 第16章 - 邻近服务：[笔记](./系统设计笔记/16. Proximity Service/README.md)
17. 第17章 - 附近好友：[笔记](./系统设计笔记/17. Nearby Friends/README.md)
18. 第18章 - 设计Google地图：[笔记](./系统设计笔记/18. Google Maps/README.md)
19. 第19章 - 分布式消息队列：[笔记](./系统设计笔记/19. Distributed Message Queue/README.md)
20. 第20章 - 指标监控和告警系统：[笔记](./系统设计笔记/20. Metrics Monitoring and Alerting System/README.md)
21. 第21章 - 广告点击事件聚合：[笔记](./系统设计笔记/21. Ad Click Event Aggregation/README.md)
22. 第22章 - 酒店预订系统：[笔记](./系统设计笔记/22. Hotel Reservation System/README.md)
23. 第23章 - 分布式邮件服务：[笔记](./系统设计笔记/23. Distributed Email Service/README.md)
24. 第24章 - 类S3对象存储：[笔记](./系统设计笔记/24. S3-like Object Storage/README.md)
25. 第25章 - 实时游戏排行榜：[笔记](./系统设计笔记/25. Real-time Gaming Leaderboard/README.md)
26. 第26章 - 支付系统：[笔记](./系统设计笔记/26. Payment System/README.md)
27. 第27章 - 数字钱包：[笔记](./系统设计笔记/27.  Digital Wallet/README.md)
28. 第28章 - 股票交易所：[笔记](./系统设计笔记/28. Stock Exchange/README.md)

# 本地运行

1. 安装依赖：npm install
2. 启动开发服务：npm run dev
3. 构建静态站点：npm run build
4. 本地预览构建产物：npm run preview

# 测试

1. HTML 标签平衡校验：python3 tests/test_html_balance.py
2. Vue 模板解析校验：node tests/test_vue_template_parse.mjs
3. 构建产物死链校验：python3 tests/test_dist_links.py
4. 翻译脚本单测：python3 -m pytest tests/ -q

# 翻译工具

1. 翻译脚本为 translate_notes.py，参数说明见 中文翻译说明.md。
2. 执行 python3 translate_notes.py 可增量重译指定章节。

# 部署

1. GitHub 仓库：https://github.com/buxuele/system-design-notes
2. Vercel 构建命令：npm run build
3. Vercel 输出目录：.vitepress/dist
