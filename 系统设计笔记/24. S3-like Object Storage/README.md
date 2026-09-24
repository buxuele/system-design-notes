# 第24章：类S3对象存储

## 引言

在本章中，我们将设计一个类似于 **Amazon S3** 的**对象存储**服务。

存储系统大致可分为三类：
- **块存储**
- **文件存储**
- **对象存储**

**块存储**是起源于1960年代的设备。硬盘驱动器（HDD）和固态硬盘（SSD）就是这类设备的例子。
这些设备通常物理连接到服务器上，但也可以通过高速网络协议进行网络附加。
服务器可以格式化原始块并将其用作文件系统，也可以直接将控制权交给服务器。

**文件存储**建立在块存储之上。它提供了更高层次的抽象，使文件和文件夹的管理更加便捷。

**对象存储**以牺牲性能为代价，换取高耐久性、极大的规模和低成本。
它面向"冷"数据，主要用于归档和备份。
它没有层次化的目录结构，所有数据都以对象的形式存储在扁平结构中。
与其他存储类型相比，它的读写速度相对较慢。大多数云服务商都提供对象存储服务——Amazon S3、Google GCS等。

<div style="margin-left:3rem">
    <img src="./images/storage-comparison.png" alt="storage-comparison" width="500" />
</div>

|                 | 块存储                          | 文件存储                              | 对象存储                       |
|-----------------|--------------------------------|---------------------------------------|-------------------------------|
| 可变内容        | 是                              | 是                                    | 否（具有对象版本化）           |
| 成本            | 高                              | 中到高                                | 低                            |
| 性能            | 中到高，极高                   | 中到高                                | 低到中                        |
| 一致性          | 强一致性                        | 强一致性                              | 强一致性 [5]                  |
| 数据访问        | SAS/iSCSI/FC                   | 标准文件访问，CIFS/SMB，NFS          | RESTful API                   |
| 可扩展性        | 中等可扩展性                    | 高可扩展性                            | 极大可扩展性                  |
| 适用场景        | 虚拟机（VM）、数据库           | 通用文件系统访问                      | 二进制数据、非结构化数据      |

与对象存储相关的一些术语：
- **存储桶（Bucket）**——对象的逻辑容器。名称全局唯一。
- **对象（Object）**——存储在存储桶中的单个数据片段，包含对象数据和元数据。
- **版本化（Versioning）**——在同一存储桶中保留对象多个版本的功能。
- **统一资源标识符（URI）**——每个资源由唯一的URI标识。
- **服务等级协议（SLA）**——服务提供商与客户之间的合同。

Amazon S3 标准-不频繁访问存储类别的SLA：
- 跨多个可用区实现99.999999999%的耐久性
- 在整个可用区被破坏的情况下数据仍然具有韧性
- 设计可用性为99.9%

---

## 第1步：理解问题并确定设计范围

- C：应包含哪些功能？
- I：存储桶创建、对象上传/下载、版本化、列出存储桶中的对象
- C：典型数据规模是多少？
- I：我们需要高效地存储超大对象和小对象
- C：我们一年存储多少数据？
- I：100 PB
- C：能否假设数据耐久性为6个9（99.9999%），服务可用性为4个9（99.99%）？
- I：可以，听起来合理

### **非功能性需求**

- **100 PB的数据**
- **6个9的数据耐久性**
- **4个9的服务可用性**
- 存储效率。在保持高可靠性和性能的同时降低存储成本

### **粗略估算**

对象存储的瓶颈很可能出现在磁盘容量或每秒I/O次数（IOPS）上。

假设条件：
- 20%为小对象（小于1 MB），60%为中等对象（1–64 MB），20%为大对象（大于64 MB）
- 一块硬盘（SATA，7200转）每秒可执行100–150次随机寻道（100–150 IOPS）

基于上述假设，我们可以估算系统能持久化存储的对象总数：
- 为简化计算，取每种对象类型的中位大小——小对象0.5 MB，中等对象32 MB，大对象200 MB
- 给定100 PB（10^11 MB）的存储空间，40%的存储使用量对应约6.8亿个对象
- 假设每个对象的元数据为1 KB，则需要0.68 TB的空间来存储元数据信息

---

## 第2步：提出高层设计并获得认可

在深入设计之前，我们先探讨对象存储的一些有趣特性：
- **对象不可变性**——对象存储中的对象是不可变的（其他存储系统则不是）。我们可以删除或替换它们，但不能更新。
- **键值存储**——对象的URI就是其键，我们可以通过HTTP请求获取其内容。
- **一次写入，多次读取**——数据访问模式是一次写入、多次读取。根据LinkedIn的一些研究，95%的操作是读操作。
- 同时支持小对象和大对象

对象存储的设计哲学与 UNIX 类似——当我们保存一个文件时，会在一个称为 inode 的数据结构中创建文件名，而文件数据则存储在不同的磁盘位置。

inode 包含一个文件块指针列表，这些指针指向磁盘上的不同位置。

在访问文件时，我们首先从 inode 中获取其元数据，然后再获取文件内容。

对象存储的工作原理类似——使用元数据存储文件信息，而内容则存储在磁盘上：

<div style="margin-left:3rem">
    <img src="./images/object-store-vs-unix.png" alt="object-store-vs-unix" width="500" />
</div>

通过将元数据与文件内容分离，我们可以独立地扩展不同的存储：

<div style="margin-left:3rem">
    <img src="./images/bucket-and-object.png" alt="bucket-and-object" width="500" />
</div>

### **高层设计**

<div style="margin-left:3rem">
    <img src="./images/high-level-design.png" alt="high-level-design" width="500" />
</div>

- **负载均衡器** - 将 API 请求分发到服务副本
- **API 服务** - 无状态服务器，负责编排对元数据存储和对象存储的调用，以及 IAM 服务
- **身份与访问管理（IAM）** - 认证、授权和访问控制的中心位置
- **数据存储** - 存储和检索实际数据，操作基于对象 ID（UUID）
- **元数据存储** - 存储对象元数据

### **上传对象**

<div style="margin-left:3rem">
    <img src="./images/uploading-object.png" alt="uploading-object" width="500" />
</div>

- 通过 HTTP PUT 请求创建一个名为 "bucket-to-share" 的存储桶
- API 服务调用 IAM 确保用户已授权并具有写入权限
- API 服务调用元数据存储创建存储桶条目，创建成功后返回成功响应
- 存储桶创建后，发送 HTTP PUT 请求创建一个名为 "script.txt" 的对象
- API 服务验证用户身份并确保用户具有写入权限
- 验证通过后，对象负载通过 HTTP PUT 发送到数据存储，数据存储持久化并返回一个 UUID
- API 服务调用元数据存储创建一个新条目，包含 object_id、bucket_id 和 bucket_name 等元数据

示例对象上传请求：

```
PUT /bucket-to-share/script.txt HTTP/1.1
Host: foo.s3example.org
Date: Sun, 12 Sept 2021 17:51:00 GMT
Authorization: authorization string
Content-Type: text/plain
Content-Length: 4567
x-amz-meta-author: Alex

[4567 bytes of object data]
```

### **下载对象**

存储桶没有目录层级，但我们可以通过将存储桶名和对象名拼接来创建逻辑层级，以模拟文件夹结构。

获取对象的示例 GET 请求：

```
GET /bucket-to-share/script.txt HTTP/1.1
Host: foo.s3example.org
Date: Sun, 12 Sept 2021 18:30:01 GMT
Authorization: authorization string
```

<div style="margin-left:3rem">
    <img src="./images/download-object.png" alt="download-object" width="500" />
</div>

- 客户端向负载均衡器发送 HTTP GET 请求，即 `GET /bucket-to-share/script.txt`
- API 服务查询 IAM 以验证用户是否具有读取存储桶的正确权限
- 验证通过后，从元数据存储中检索对象的 UUID
- 根据 UUID 从数据存储中检索对象负载并返回给客户端

---

// sprint 1

## 第3步：设计深入解析

### **数据存储**

以下是 API 服务与数据存储的交互方式：

<div style="margin-left:3rem">
    <img src="./images/data-store-interactions.png" alt="data-store-interactions" width="500" />
</div>

数据存储的主要组件：

<div style="margin-left:3rem">
    <img src="./images/data-store-main-components.png" alt="data-store-main-components" width="500" />
</div>

数据路由服务提供 RESTful 或 gRPC API 来访问数据节点集群。
它是一个无状态服务，可以通过增加更多服务器来扩展。

其主要职责包括：
- 查询放置服务以获取最佳数据节点来存储数据
- 从数据节点读取数据并返回给 API 服务
- 向数据节点写入数据

放置服务决定哪些数据节点应存储对象。
它维护一个虚拟集群映射，用于确定集群的物理拓扑。

<div style="margin-left:3rem">
    <img src="./images/virtual-cluster-map.png" alt="virtual-cluster-map" width="500" />
</div>

该服务还会向所有数据节点发送心跳，以确定是否应将其从虚拟集群中移除。

由于这是一个关键服务，建议维护一个由 5 个或 7 个副本组成的集群，通过 Paxos 或 Raft 共识算法同步。
例如，一个 7 节点集群可以容忍 3 个节点故障。

数据节点存储实际的对象数据。
通过将数据复制到多个数据节点来确保可靠性和持久性。

每个数据节点运行一个守护进程，向放置服务发送心跳。

心跳包含：
- 数据节点管理多少个磁盘驱动器（HDD 或 SSD）？
- 每个驱动器上存储了多少数据？

#### 数据持久化流程

<div style="margin-left:3rem">
    <img src="./images/data-persistence-flow.png" alt="data-persistence-flow" width="500" />
</div>

- API 服务将对象数据转发给数据存储
- 数据路由服务将数据发送到主数据节点
- 主数据节点将数据本地保存，并复制到两个从数据节点。复制成功后返回响应。
- 对象的 UUID 被返回给 API 服务。

注意事项：
- 给定一个对象 UUID，其复制组通过一致性哈希算法确定性地选择
- 在第 4 步中，主数据节点在返回响应之前先复制对象数据。这倾向于强一致性，而非更低延迟。

<div style="margin-left:3rem">
    <img src="./images/consistency-vs-latency.png" alt="consistency-vs-latency" width="500" />
</div>

#### 数据组织方式

管理数据的一种简单方法是将每个对象存储在单独的文件中。

这种方式可行，但在文件系统中处理大量小文件时性能不佳：
- 硬盘上的数据块会被浪费，因为每个文件都占用整个块大小。典型块大小为 4KB。
- 文件数量多意味着索引节点（inode）数量多。操作系统无法很好地处理过多 inode，而且还有最大 inode 限制。

这些问题可以通过预写日志（WAL）将许多小文件合并为更大的文件来解决。当文件达到其容量上限（通常为几个 GB）时，会创建一个新文件：

<div style="margin-left:3rem">
    <img src="./images/wal-optimization.png" alt="wal-optimization" width="500" />
</div>

这种方法的缺点是需要对文件的写入访问进行串行化。多个核心访问同一文件时必须互相等待。
为了解决这个问题，我们可以将文件限定在特定的核心上，以避免锁竞争。

#### 对象查找

为了支持在同一文件中存储多个对象，我们需要维护一张表，告诉数据节点：
- `object_id`
- 对象存储的 `filename`
- 对象起始位置的 `file_offset`
- `object_size`

我们可以将这张表部署在基于文件的数据库（如 RocksDB）或传统关系型数据库中。
由于访问模式是低写入、高读取，关系型数据库效果更好。

我们应该如何部署它？
我们可以将数据库部署在集群中独立扩展，被所有数据节点访问。

缺点：
- 需要激进地扩展集群以服务所有请求
- 数据节点与数据库集群之间存在额外的网络延迟

另一种方案是利用数据节点只关心与自身相关的数据这一事实，
因此我们可以将关系型数据库部署在数据节点内部。

SQLite 是一个不错的选择，因为它是一个轻量级的基于文件的关系型数据库。

#### 更新后的数据持久化流程

<div style="margin-left:3rem">
    <img src="./images/updated-data-persistence-flow.png" alt="updated-data-persistence-flow" width="500" />
</div>

- API 服务发送请求以保存新对象
- 数据节点服务将新对象追加到名为 "/data/c" 的文件末尾
- 在对象映射表中插入该对象的新记录

#### 持久性

数据持久性是我们设计中的重要要求。为了实现 9 个 9（6 nines）的持久性，需要仔细检查每一个故障场景。

首先要解决的问题是硬件故障。我们可以通过复制数据节点来降低故障概率。
除此之外，我们还应该跨不同的故障域进行复制（跨机架、跨数据中心、独立网络等）。
一个关键事件可能导致同一域内发生多个硬件故障：

<div style="margin-left:3rem">
    <img src="./images/failure-domain-isolation.png" alt="failure-domain-isolation" width="500" />
</div>

假设典型硬盘的年故障率为 0.81%，制作三份副本可以给我们带来 6 个 9 的持久性。

以这种方式复制数据节点可以赋予我们所需的持久性，但我们也可以利用纠删码来降低存储成本。

纠删码使我们能够使用校验位，从而在发生故障时重建丢失的位：

<div style="margin-left:3rem">
    <img src="./images/erasure-coding.png" alt="erasure-coding" width="500" />
</div>

想象这些位就是数据节点。如果其中两个宕机，可以利用剩余的四个进行恢复。

存在不同的纠删码方案。在我们的场景中，可以使用 8+4 纠删码，跨不同故障域进行分割以最大化可靠性：

<div style="margin-left:3rem">
    <img src="./images/erasure-coding-across-failure-domains.png" alt="erasure-coding-across-failure-domains" width="500" />
</div>

纠删码使我们能够以更低的存储成本（改善 50%）为代价来实现持久性，但由于数据路由服务需要从多个位置收集数据，访问速度会有所下降：

<div style="margin-left:3rem">
    <img src="./images/erasure-coding-vs-replication.png" alt="erasure-coding-vs-replication" width="500" />
</div>

其他注意事项：
- 复制需要 200% 的存储开销（例如 3 副本），而纠删码仅为 50%
- 纠删码 [可提供 11 个 9 的持久性](https://github.com/Backblaze/erasure-coding-durability)，而复制仅为 6 个 9
- 纠删码需要更多的计算来生成和存储校验位

总之，复制更适合对延迟敏感的应用，而纠删码在存储成本效率和持久性方面更具吸引力。
纠删码的实现难度也要高得多。

#### 正确性验证

如果磁盘完全失效，故障很容易检测。但在磁盘部分内存损坏的情况下，情况就不那么直观了。

为了检测这种情况，我们可以使用校验和——文件内容的哈希值，用于验证文件的完整性。

在我们的场景中，我们将为每个文件和每个对象存储校验和：

<div style="margin-left:3rem">
    <img src="./images/checksums-for-correctness.png" alt="checksums-for-correctness" width="500" />
</div>

在纠删码（8+4）的情况下，我们需要分别获取 8 个数据块，并逐一验证它们的校验和。

// sprint 2

### **元数据数据模型**

表结构：

<div style="margin-left:3rem">
    <img src="./images/metadata-data-model.png" alt="metadata-data-model" width="500" />
</div>

需要支持的查询：
- 按名称查找对象 ID
- 根据名称插入/删除对象
- 列出共享同一前缀的桶中的对象

用户可创建的桶数量通常有限，因此桶表的大小较小，可以放入单个数据库服务器中。
但我们仍需要扩展服务器的读吞吐量。

对象表可能无法放入单个数据库服务器中。因此，我们可以通过分片来扩展该表：
- 按 `bucket_id` 分片会导致热点问题，因为一个桶可能包含数十亿个对象
- 按 `bucket_id` 分片使负载分布更均匀，但查询速度会变慢
- 我们选择按 `hash(bucket_name, object_name)` 分片，因为大多数查询都基于对象/桶名称。

即使采用这种分片方案，在桶中列出对象仍然会很慢。

### **列出桶中的对象**

在单个数据库中，基于前缀（类似目录）列出对象的工作方式如下：

```
SELECT * FROM object WHERE bucket_id = "123" AND object_name LIKE `abc/%`
```

当数据库分片后，这很难实现。为此，我们可以在每个分片上运行查询，并在内存中聚合结果。
但这使得分页变得困难，因为不同分片包含的结果数量不同，我们需要为每个分片维护独立的 limit/offset。

我们可以利用对象存储通常不优化对象列出这一事实，因此可以牺牲列出性能。
我们还可以创建一个针对桶 ID 分片的非规范化表来列出对象。
这样，我们的列出查询将足够快，因为它被隔离到单个数据库实例中。

### **对象版本控制**

版本控制通过引入一个 `object_version` 列（类型为 TIMEUUID）来实现，使我们能够基于它对记录进行排序。

每个新版本都会生成一个新的 `object_id`：

<div style="margin-left:3rem">
    <img src="./images/object-versioning.png" alt="object-versioning" width="500" />
</div>

删除对象会创建一个带有特殊 `object_id` 的新版本，表示该对象已被删除。对其查询将返回 404：

<div style="margin-left:3rem">
    <img src="./images/deleting-versioned-object.png" alt="deleting-versioned-object" width="500" />
</div>

### **优化大文件上传**

可以通过使用多部分上传来优化大文件上传——将大文件拆分为多个块，独立上传：

<div style="margin-left:3rem">
    <img src="./images/multipart-upload.png" alt="multipart-upload" width="500" />
</div>

- 客户端调用服务以启动多部分上传
- 数据存储返回一个唯一标识该上传的上传 ID
- 客户端将大文件拆分为多个块，使用上传 ID 独立上传
- 当一个块上传完成后，数据存储返回一个 etag（md5 校验和），用于标识该上传块
- 所有部分上传完成后，客户端发送完成多部分上传请求，其中包含 upload_id、部分编号和所有 etag
- 数据存储从各个部分重新组装对象。该过程可能需要几分钟。之后，向客户端返回成功响应。

此时，不再有用的旧部分可以被移除。我们可以引入垃圾回收器来处理这个问题。

### **垃圾回收**

垃圾回收是回收不再使用的存储空间的过程。数据变成垃圾的方式有以下几种：
- **惰性对象删除** —— 对象被标记为删除但并未实际删除
- **孤立数据** —— 例如上传中途失败，旧的部分需要被删除
- **损坏的数据** —— 校验和验证失败的数据

垃圾回收器还负责回收副本中未使用的空间。  
在复制模式下，数据会从主节点和副本节点同时删除。在纠删码（8+4）模式下，数据会从全部 12 个节点删除。

为了实现删除操作，我们将使用一种称为**压缩（compaction）**的过程：
- 垃圾回收器将未被删除的对象从 `data/b` 复制到 `data/d`
- 复制完成后，使用数据库事务更新 `object_mapping` 表
- 为了避免生成过多小文件，只有当文件大小超过一定阈值时才会执行压缩

<div style="margin-left:3rem">
    <img src="./images/compaction.png" alt="compaction" width="500" />
</div>

---

## 第4步：总结

我们涵盖的内容：
- 设计类似 S3 的对象存储系统
- 比较对象存储、块存储与文件存储的区别
- 介绍了桶中对象的上传、下载、列举与版本控制
- 深入探讨了设计细节——数据存储与元数据存储、复制与纠删码、多部分上传、分片机制
