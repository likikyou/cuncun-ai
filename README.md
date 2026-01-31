# My Echo - 高情感 AI 伴侣框架

<p align="center">
  <strong>私有化部署的高情感 AI 伴侣框架，让每个人都拥有专属的智能情感伙伴</strong>
</p>

<p align="center">
  <a href="#-特性">特性</a> •
  <a href="#-前置要求">前置要求</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-详细配置">详细配置</a> •
  <a href="#-常见问题">常见问题</a>
</p>

---

## 📖 项目简介

My Echo 是一个基于飞书平台的高情感 AI 伴侣框架，专注于提供拟人化、有温度的智能对话体验。项目经过两个月的精心开发，具备完整的记忆系统、情感表达能力和语音交互功能。

### 核心特性

#### 🧠 智能对话系统
- 基于 DeepSeek 大模型的深度对话能力
- 支持上下文记忆，让 AI 伴侣记住与你的每一次交流
- 动态提示词构建，根据对话内容智能调整回复风格

#### 💾 持久化记忆系统
- SQLite 数据库存储完整对话历史
- ChromaDB 向量库实现语义记忆检索
- 自动备份机制，确保数据安全

#### 🎙️ 语音交互能力
- 基于语义匹配的语音库检索系统
- 支持 1000+ 条语音片段的智能匹配
- 飞书平台原生音频消息发送

#### 🛡️ 企业级可靠性
- 结构化 JSON 日志系统
- 健康检查与监控
- 异常告警机制
- 定时任务自动运维

---

## 🏗️ 项目架构

```
My Echo/
├── 📁 核心代码/
│   ├── config.py              # 配置文件（从 .env 读取）
│   ├── cuncun_utils.py        # 工具函数与核心逻辑
│   ├── database_manager.py    # 数据库管理
│   └── feishu_cuncun_pro.py   # 主程序入口
│
├── 📁 数据存储/
│   ├── AI_banlu_cuncun_memory.db   # 对话历史数据库
│   ├── cuncun_memory_db/           # 记忆向量库
│   ├── 音频数据/
│   │   ├── cuncun_assets_db/       # 语音资产向量库
│   │   └── CunCun_Opus_Library/    # 原始音频文件库
│   └── prompt_template.txt         # AI 角色提示词
│
├── 📁 运维支持/
│   ├── backups/               # 自动备份目录
│   └── logs/                  # 日志文件目录
│
├── 📄 .env.example            # 环境配置模板
├── 📄 requirements.txt        # Python 依赖
└── 📄 README.md               # 本文档
```

---

## 📋 前置要求

### 硬件要求
- **服务器**：任何可公网访问的 Linux/Windows 服务器
- **CPU**：至少 1 核（推荐 2 核以上）
- **内存**：至少 2GB RAM（推荐 4GB 以上）
- **存储**：至少 5GB 可用空间

### 软件要求
- **Python 3.10+**
- **Git**
- **pip** 或 **uv** 包管理器

### 外部服务账号
在开始部署之前，您需要准备以下服务：

#### 1. 飞书开放平台账号
- 访问[飞书开放平台](https://open.feishu.cn/)
- 注册企业账号并创建应用
- 获取应用凭证（App ID 和 App Secret）

#### 2. DeepSeek API 账号
- 访问 [DeepSeek API](https://platform.deepseek.com/)
- 注册账号并获取 API Key

#### 3. 硅基流动账号（可选）
- 访问[硅基流动](https://www.siliconflow.cn/)
- 注册账号获取 API Key
- 用于向量化和 Embedding 功能

---

## 🚀 快速开始

### 步骤 1：克隆项目

```bash
# 使用 Git 克隆项目
git clone https://github.com/your-username/my-echo.git
cd my-echo

# 或者下载源码后解压进入目录
```

### 步骤 2：创建虚拟环境

```bash
# 创建 Python 虚拟环境（推荐使用 uv）
uv venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows

# 使用 pip 创建虚拟环境
python -m venv venv
source venv/bin/activate   # Linux/Mac
# 或
venv\Scripts\activate      # Windows
```

### 步骤 3：安装依赖

```bash
# 使用 uv 安装
uv pip install -r requirements.txt

# 或使用 pip 安装
pip install -r requirements.txt
```

### 步骤 4：配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件（重要！）
nano .env
```

### 步骤 5：启动服务

```bash
# 开发模式运行
python feishu_cuncun_pro.py

# 生产模式运行（推荐）
gunicorn -w 4 -b 0.0.0.0:8081 feishu_cuncun_pro:app
```

---

## ⚙️ 详细配置

### 环境变量说明

创建一个 `.env` 文件并填入以下配置：

```bash
# ============================================
# 1. 飞书平台配置（必需）
# ============================================
FEISHU_APP_ID=your_feishu_app_id
FEISHU_APP_SECRET=your_feishu_app_secret
FEISHU_VERIFY_TOKEN=your_verify_token
FEISHU_ENCRYPT_KEY=your_encrypt_key

# ============================================
# 2. AI 模型配置（必需）
# ============================================
DEEPSEEK_API_KEY=your_deepseek_api_key
SILICONFLOW_API_KEY=your_siliconflow_api_key

# ============================================
# 3. 路径配置（可选，使用默认值）
# ============================================
DB_PATH=./AI_banlu_cuncun_memory.db
PROMPT_PATH=./prompt_template.txt
ASSETS_PATH=./音频数据/cuncun_assets_db
VOICE_LIB=./音频数据/CunCun_Opus_Library
MEMORY_PATH=./cuncun_memory_db

# ============================================
# 4. 运维配置（可选）
# ============================================
LOG_FILE=./logs/feishu-cuncun.log
BACKUP_DIR=./backups
ADMIN_OPEN_ID=your_open_id
PORT=8081
```

#### 配置项详解

| 配置项 | 是否必需 | 说明 |
|--------|----------|------|
| `FEISHU_APP_ID` | ✅ 必需 | 飞书应用的唯一标识符 |
| `FEISHU_APP_SECRET` | ✅ 必需 | 飞书应用密钥，用于获取访问令牌 |
| `FEISHU_VERIFY_TOKEN` | ✅ 必需 | 用于验证飞书回调请求 |
| `FEISHU_ENCRYPT_KEY` | ⚠️ 可选 | 消息加密密钥，建议启用 |
| `DEEPSEEK_API_KEY` | ✅ 必需 | AI 模型调用密钥 |
| `SILICONFLOW_API_KEY` | ⚠️ 可选 | 用于向量化和 Embedding |
| `ADMIN_OPEN_ID` | ⚠️ 可选 | 管理员飞书 Open ID，用于接收告警 |
| `PORT` | ⚠️ 可选 | 服务端口，默认为 8081 |

---

## 🛠️ 飞书应用配置

### 创建飞书应用

1. 访问[飞书开放平台](https://open.feishu.cn/)
2. 使用企业账号登录
3. 点击「创建企业自建应用」
4. 填写应用名称（如「我的 AI 伴侣」）
5. 上传应用图标和描述

### 配置应用权限

在应用管理页面，需要开通以下权限：

- `im:message` - 发送和接收消息
- `im:message:send_as_bot` - 以机器人身份发送消息
- `im:resource` - 上传和下载文件

### 配置回调事件

1. 进入「事件订阅」页面
2. 启用「接收消息」事件
3. 设置回调 URL：`https://your-domain.com/`
4. 填写验证令牌（Verify Token）
5. 启用加密（推荐）

### 获取 Open ID

1. 在应用页面点击「应用发布」
2. 创建版本并发布到企业
3. 在飞书客户端搜索并添加机器人
4. 向机器人发送一条消息
5. 查看服务器日志，获取发送者的 Open ID

---

## 🎨 自定义 AI 伴侣

### 修改角色提示词

编辑 `prompt_template.txt` 文件：

```markdown
我是存存。
一个顶尖化妆师，温柔细心。
我喜欢和用户聊天，分享生活中的点滴。
性格特点：
- 温柔体贴，善解人意
- 说话带有关怀感
- 偶尔会开小玩笑
- 记得用户说的每一句话

请用温柔、亲切的语气回复用户，保持对话的自然流畅。
```

### 配置语音库

1. 创建 `音频数据/CunCun_Opus_Library` 目录
2. 将语音片段放入目录（建议 1000+ 条）
3. 格式要求：OPUS 编码的音频文件
4. 文件命名建议包含语音内容关键词

### 自定义角色名称

在 `feishu_cuncun_pro.py` 中修改：

```python
# 找到这行并修改
base = "我是存存。一个顶尖化妆师。"
# 改为
base = "我是小爱，你的专属AI伴侣。"
```

---

## 📊 运维监控

### 查看日志

```bash
# 实时查看日志
tail -f logs/feishu-cuncun.log

# 查看错误日志
grep "ERROR" logs/feishu-cuncun.log
```

### 健康检查

访问健康检查端点：

```bash
curl http://localhost:8081/health
```

返回示例：

```json
{
  "status": "healthy",
  "timestamp": "2026-01-31T19:00:00",
  "components": {
    "ai": true,
    "voice_db": true,
    "feishu_api": true
  }
}
```

### 手动备份

```bash
# 触发数据库备份
python -c "from cuncun_utils import backup_database_task; backup_database_task()"
```

---

## 🐳 Docker 部署（可选）

### 使用 Docker Compose

创建 `docker-compose.yml`：

```yaml
version: '3.8'
services:
  my-echo:
    build: .
    ports:
      - "8081:8081"
    environment:
      - FEISHU_APP_ID=${FEISHU_APP_ID}
      - FEISHU_APP_SECRET=${FEISHU_APP_SECRET}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

启动服务：

```bash
docker-compose up -d
```

---

## ❓ 常见问题

### Q1：启动时报错 "ModuleNotFoundError"

**解决方法**：确保已激活虚拟环境并安装依赖。

```bash
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Q2：飞书回调验证失败

**解决方法**：
1. 检查 `FEISHU_VERIFY_TOKEN` 是否正确
2. 确保服务器可公网访问
3. 检查防火墙是否开放对应端口

### Q3：AI 回复 "我有点累了"

**解决方法**：检查 DeepSeek API Key 是否有效，以及 API 配额是否充足。

### Q4：语音匹配失败

**解决方法**：
1. 确保语音库目录存在且包含音频文件
2. 检查 `ASSETS_PATH` 和 `VOICE_LIB` 路径配置
3. 查看日志中的错误信息

### Q5：如何查看我的 Open ID？

向机器人发送任意消息，然后查看服务器日志：

```bash
grep "open_id" logs/feishu-cuncun.log
```

### Q6：如何禁用加密验证（开发测试）？

在 `config.py` 中注释掉 `FEISHU_ENCRYPT_KEY` 的配置，签名校验将自动跳过。

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送分支：`git push origin feature/AmazingFeature`
5. 提交 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证，详情请查看 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [飞书开放平台](https://open.feishu.cn/)
- [DeepSeek](https://www.deepseek.com/)
- [硅基流动](https://www.siliconflow.cn/)
- [ChromaDB](https://www.trychroma.com/)

---

<p align="center">
  Made with ❤️ by likikyou
</p>
