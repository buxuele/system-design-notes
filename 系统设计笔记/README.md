
# [系统设计面试：内部指南（第一卷和第二卷）](https://bytebytego.com/courses/system-design-interview)
这些笔记基于《系统设计面试》书籍——[第一卷和第二卷 第二版](https://www.goodreads.com/book/show/54109255-system-design-interview-an-insider-s-guide)

查看笔记：https://pagefy.io/system-design/system-design-interview-by-alex-xu

**注意：** 这些笔记仍在编写中。

 * [第1章 - 从零扩展到数百万用户](/01-scaling/)
 * [第2章 - 估算分析](/02-back-of-the-envelope-estimation/)
 * [第3章 - 系统设计面试框架](/03-system-design-framework/)
 * [第4章 - 设计限流器](/04-rate-limiter/)
 * [第5章 - 设计一致性哈希](/05-consistent-hashing/)
 * [第6章 - 设计键值存储](/06-key-value-store/)
 * [第7章 - 设计分布式系统中的唯一ID生成器](/07-unique-id-generator/)
 * [第8章 - 设计URL缩短器](/08-url-shortener/)
 * [第9章 - 设计网络爬虫](/09-web-crawler/)
 * [第10章 - 设计通知系统](/10-notification-system/)
 * [第11章 - 设计新闻流系统](/11-news-feed-system/)
 * [第12章 - 设计聊天系统](/12-chat-system/)
 * [第13章 - 设计搜索自动补全系统](/13-search-autocomplete/)
 * [第14章 - 设计YouTube](/14-youtube/)
 * [第15章 - 设计Google Drive](/15-google-drive/)
 * [第16章 - 邻近服务](/16-proximity-service/)
 * [第17章 - 附近好友](/17-nearby-friends/)
 * [第18章 - 设计Google地图](/18-google-maps/)
 * [第19章 - 分布式消息队列](/19-distributed-message-queue/)
 * [第20章 - 指标监控和告警系统](/20-metrics-monitoring-and-alerting-system/)
 * [第21章 - 广告点击事件聚合](/21-ad-click-event-aggregation/)
 * [第22章 - 酒店预订系统](/22-hotel-reservation-system/)
 * [第23章 - 分布式邮件服务](/23-distributed-email-service/)
 * [第24章 - 类S3对象存储](/24-s3-like-object-storage/)
 * [第25章 - 实时游戏排行榜](/25-real-time-gaming-leaderboard/)
 * [第26章 - 支付系统](/26-payment-system/)
 * [第27章 - 数字钱包](/27-digital-wallet/)
 * [第28章 - 股票交易所](/28-stock-exchange/)


## 附加资源

### 限流
- [断路器算法](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Uber限流器](https://github.com/uber-go/ratelimit/blob/master/ratelimit.go)


### 一致性哈希
- [一致性哈希](https://tom-e-white.com/2007/11/consistent-hashing.html)
- [CS168：一致性哈希导论]( http://theory.stanford.edu/~tim/s16/l/l1.pdf)
- [Apache Cassandra](http://www.cs.cornell.edu/Projects/ladis2009/papers/Lakshman-ladis2009.PDF)
- [Discord扩展](https://blog.discord.com/scaling-elixir-f9b8e1e7c29b)
- [Google Maglev](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/44824.pdf)


### 键值存储
- [Amazon Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
- [Cassandra架构](https://docs.datastax.com/en/archived/cassandra/3.0/cassandra/architecture/archIntro.html)
- [Google BigTable架构](https://static.googleusercontent.com/media/research.google.com/en//archive/bigtable-osdi06.pdf)
- [Amazon Dynamo DB内部原理](https://www.allthingsdistributed.com/2007/10/amazons_dynamo.html)
- [Amazon Dynamo DB设计模式](https://www.youtube.com/watch?v=HaEPXoXVf2k)
- [Amazon Dynamo DB内部](https://www.youtube.com/watch?v=yvBR71D0nAQ)


### 唯一ID生成器
- [票据服务器：廉价的分布式唯一主键](https://code.flickr.net/2010/02/08/ticket-servers-distributed-unique-primary-keys-on-the-cheap)
- [Snowflake](https://blog.twitter.com/engineering/en_us/a/2010/announcing-snowflake.html)


### 网络爬虫
- [网络爬取](http://infolab.stanford.edu/~olston/publications/crawling_survey.pdf)
- [Google动态渲染](https://developers.google.com/search/docs/guides/dynamic-rendering)


### 聊天系统
- [Discord如何存储数十亿条消息](https://discord.com/blog/how-discord-stores-billions-of-messages)
- [Flannel：应用层边缘缓存，让Slack扩展](https://slack.engineering/flannel-an-application-level-edge-cache-to-make-slack-scale/)


### 搜索自动补全
- [我们如何构建Prefixy](https://medium.com/@prefixyteam/how-we-built-prefixy-a-scalable-prefix-search-service-for-powering-autocomplete-c20f98e2eff1)
- [前缀哈希树](https://people.eecs.berkeley.edu/~sylvia/papers/pht.pdf)


### YouTube
- [YouTube架构](http://highscalability.com/youtube-architecture)
- [YouTube可扩展性2012](https://www.youtube.com/watch?v=w5WVu624fY8)
- [大规模视频转码](https://www.egnyte.com/blog/2018/12/transcoding-how-we-serve-videos-at-scale/)
- [Facebook视频广播](https://engineering.fb.com/ios/under-the-hood-broadcasting-live-video-to-millions/)
- [Netflix大规模视频编码](https://netflixtechblog.com/high-quality-video-encoding-at-scale-d159db052746)
- [Netflix基于镜头的编码](https://netflixtechblog.com/optimized-shot-based-encodes-now-streaming-4b9464204830)


### Google Drive
- [差分同步](https://neil.fraser.name/writing/sync/)
- [差分同步视频](https://www.youtube.com/watch?v=S2Hp_1jqpY8)
- [Dropbox 的扩展之道](https://www.youtube.com/watch?v=PE4gwstWhmc&feature=youtu.be)
