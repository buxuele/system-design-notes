# 第8章：设计一个 URL 缩短服务

## 引言
本章讨论如何设计一个类似 TinyURL 的 URL 缩短服务。系统的主要目标包括**URL 缩短**、**重定向**以及**高可扩展性**，以应对大规模的流量。

### 需求
- 缩短后的 URL 必须**唯一**，并且**尽可能短**。
- 每天支持**1 亿次 URL 生成**，并具备 10 年的支持能力。
- 支持**高效的读操作**，读写比例为 10:1。
- 存储 3650 亿条记录，10 年内大约需要 **365 TB** 的存储空间。

---

## 第一步：高层设计

### API 接口
1. **URL 缩短：**
   - 接口：`POST api/v1/data/shorten`
   - 参数：`{longUrl: longURLString}`
   - 返回：`shortURL`

2. **URL 重定向：**
   - 接口：`GET api/v1/shortUrl`
   - 返回：用于重定向的 `longURL`。

    <p align="center">
    <img src="./images/url-redirection.png" alt="URL Redirection" width="600">
    </p>

### URL 重定向
- **301 重定向：** 表示请求的 URL 已“永久”移动到新的长 URL。浏览器会缓存该响应，后续对同一 URL 的请求将不再发送到 URL 缩短服务。
- **302 重定向：** 临时性重定向，适用于点击跟踪等分析场景。

### URL 缩短
<p align="center">
    <img src="./images/url-shortening.png" alt="URL Shortening" width="400">
</p>

- 使用**哈希函数**生成短 URL，将长 URL 映射为唯一的缩短版本。
- 哈希函数必须满足以下要求：
    - 每个长 URL 必须映射为一个哈希值。
    - 每个哈希值必须能反向映射回原始的长 URL。

---

## 第二步：深入设计

### 数据模型
将 `<shortURL, longURL>` 的映射存储在关系型数据库中，以优化内存使用。表结构包括：
- `id`（主键），
- `shortURL`，
- `longURL`。

    <img src="./images/table-schema.png" alt="Table Schema" width="300">

### 哈希函数
#### 1. 基 62 编码：
- 使用字符集 `[0-9, a-z, A-Z]` 进行数字编码，共提供 **62 个可能字符**。
- 进制转换是 URL 缩短服务中另一种常用方法。
- 可以为短 URL 分配一个唯一 ID，然后将 ID 进行基 62 转换得到短 URL。
- 7 位哈希值最多可支持 **3.5 万亿个唯一 URL**，足以容纳 3650 亿个 URL。

**示例：**  
将 ID `2009215674938` 转换为基 62：
- `2009215674938` → `zn9edcu`。

#### 2. 哈希 + 冲突解决：
- 使用 CRC32、MD5 或 SHA-1 等哈希函数。

    <img src="./images/hash-function.png" alt="Hash Function" width="500">

- 一种方法是截取哈希值的前 7 个字符，但这种方法可能会导致哈希冲突。
- 为解决冲突，可以递归地追加一个预定义字符串，直到不再发生冲突，但这种方式可能开销较大。
- 使用**布隆过滤器（Bloom Filters）**来高效地检测和解决冲突。

    <p align="center">
    <img src="./images/url-lookup.png" alt="URL Lookup" width="500">
    </p>

### 对比

- **哈希 + 冲突解决：**
    - 短 URL 长度固定
    - 不需要唯一 ID 生成器
    - 可能发生冲突，需要解决
    - 无法直接找到下一个可用的短 URL，因为它不依赖于 ID

- **基 62 编码：**
    - 长度不固定，随 ID 增长
    - 需要唯一 ID 生成器
    - 不会发生冲突
    - 如果 ID 递增，查找下一个短 URL 很方便（但可能存在安全隐患）

---

### URL 缩短流程

<p align="center">
    <img src="./images/url-shortening-flow.png" alt="URL Shortening" width="500">
</p>

1. 检查 `longURL` 是否存在于数据库中。
2. 如果存在，返回已有的 `shortURL`。
3. 否则：
   - 使用**分布式 ID 生成器**生成一个唯一 ID。
   - 将 ID 通过基 62 转换为 `shortURL`。
   - 将 `<id, shortURL, longURL>` 的映射存入数据库。

---

### URL 重定向流程
<p align="center">
    <img src="./images/url-redirecting-flow.png" alt="URL Shortening" width="600">
</p>

1. 用户点击一个 `shortURL`。
2. 查询 `<shortURL, longURL>` 映射：
   - 首先检查**缓存**，以加快访问速度。
   - 如果缓存中没有，则查询数据库。
3. 将用户重定向到 `longURL`。

---

## 其他考虑事项
### 限流器
- 通过限制每个 IP 的请求次数来防止滥用。

### 可扩展性
1. **Web 层：** 无状态，可通过增减 Web 服务器进行扩展。
2. **数据库层：** 使用复制和分片技术。

### 数据分析
- 收集点击率、来源和时间戳等数据，用于业务洞察。

### 高可用性与可靠性
- 通过数据库复制和容错设计，确保服务的一致性和可靠性。