# My Echo 安装指南

本指南将详细介绍如何在您的服务器上安装和配置 My Echo 高情感 AI 伴侣框架。无论您是技术新手还是有一定经验的开发者，按照本指南的步骤操作，都能够成功部署属于自己的 AI 伴侣。

## 1. 环境准备

### 1.1 操作系统要求

My Echo 可以在多种操作系统上运行，包括 Windows、Linux 和 macOS。不同的操作系统在安装过程中会有一些细微的差别，本指南将同时涵盖这三种主流操作系统的安装方法。

对于生产环境部署，我们强烈推荐使用 Linux 系统（推荐 Ubuntu 20.04 LTS 或更高版本），因为 Linux 系统在稳定性、资源占用和安全性方面都有明显优势。如果您使用的是 Windows Server 或 Windows 桌面系统，同样可以正常运行本项目，但建议在生产环境中使用 Linux。如果您是 macOS 用户，无论是 Intel 芯片还是 Apple Silicon 芯片的 Mac，都可以按照本指南进行安装部署，项目的代码和依赖在 macOS 上都能良好运行。

### 1.2 检查 Python 版本

在开始安装之前，您需要确保系统中已经安装了 Python 3.10 或更高版本。My Echo 的部分依赖库要求 Python 版本不低于 3.10，因此请务必检查您的 Python 版本是否符合要求。您可以通过在终端或命令提示符中执行以下命令来查看当前 Python 版本：

```bash
python --version
```

或者：

```bash
python3 --version
```

如果命令返回的版本号低于 3.10（例如显示 Python 3.8 或 Python 3.9），则需要升级 Python 版本。对于 Linux 系统，您可以通过包管理器安装最新版本的 Python；对于 Windows 系统，您可以前往 Python 官方网站下载并安装最新版本。macOS 用户可以使用 Homebrew 包管理器来安装或升级 Python。安装完成后，请再次执行上述命令确认版本号已更新到 3.10 或更高。

### 1.3 安装 Git

Git 是一个分布式版本控制系统，用于管理项目代码。如果您还没有安装 Git，需要先安装它。在 Linux 系统（以 Ubuntu 为例）上，您可以使用以下命令安装 Git：

```bash
sudo apt update
sudo apt install git
```

在 macOS 上，如果您已经安装了 Homebrew，可以使用以下命令安装 Git：

```bash
brew install git
```

在 Windows 上，您可以前往 Git 官方网站下载安装程序，或者使用 Chocolatey 包管理器安装（如果您已经安装了 Chocolatey 的话）。安装完成后，您可以通过以下命令验证 Git 是否安装成功：

```bash
git --version
```

如果命令返回类似 `git version 2.x.x` 的版本信息，说明 Git 已经成功安装。

### 1.4 安装 uv 包管理器（推荐）

uv 是一个用 Rust 编写的超快 Python 包管理器，相比传统的 pip 工具，uv 的安装速度可以快 10 到 100 倍。我们强烈推荐使用 uv 来安装和管理项目依赖，它可以大大缩短安装时间并提供更好的依赖解析体验。如果您选择使用 uv，请按照以下步骤安装：

在 Linux 和 macOS 上，您可以使用以下命令安装 uv：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

在 Windows 上，您可以使用 PowerShell 安装 uv：

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

安装完成后，您可以通过以下命令验证 uv 是否安装成功：

```bash
uv --version
```

如果您更习惯使用 pip，My Echo 也完全支持使用 pip 进行依赖安装，这一点您无需担心。无论您选择 uv 还是 pip，都能顺利完成项目的安装部署工作。

## 2. 获取项目代码

### 2.1 克隆仓库

首先，您需要将 My Echo 项目的代码下载到您的服务器上。如果您已经在 GitHub 上创建了该项目的仓库，可以使用 git clone 命令克隆代码。如果您还没有创建仓库，可以先在本地初始化一个新的 Git 仓库，然后将现有代码添加进去。

使用 git clone 命令克隆项目的命令如下：

```bash
git clone https://github.com/您的用户名/my-echo.git
cd my-echo
```

执行上述命令后，Git 会将项目代码下载到当前目录下的 `my-echo` 文件夹中。如果您使用的是 SSH 协议连接到 GitHub（这种方式更安全，推荐已配置 SSH 密钥的用户使用），则命令如下：

```bash
git clone git@github.com:您的用户名/my-echo.git
cd my-echo
```

### 2.2 创建项目目录结构

如果您还没有将代码上传到 GitHub，也可以直接在服务器上创建项目目录。创建项目目录的步骤如下：

首先，创建项目主目录并进入该目录：

```bash
mkdir my-echo
cd my-echo
```

然后，创建项目所需的数据目录结构：

```bash
mkdir -p 音频数据/CunCun_Opus_Library
mkdir -p logs
mkdir -p backups
```

上述命令会创建音频数据目录（用于存放语音文件）、日志目录（用于存放运行日志）和备份目录（用于存放数据库备份）。这些目录是项目正常运行所必需的，请确保它们都已被成功创建。您可以通过 `ls -la` 命令查看当前目录结构是否正确。

### 2.3 获取项目文件

在这一步中，您需要将项目的所有源代码文件复制到刚才创建的目录中。这些文件包括 `config.py`、`cuncun_utils.py`、`database_manager.py`、`feishu_cuncun_pro.py` 等核心文件，以及 `requirements.txt` 和 `prompt_template.txt` 等配置文件。

如果您已经在本地完成了开发工作，可以将这些文件复制到服务器上。您可以使用 SCP 命令（在 Linux 和 macOS 上）或 FTP 工具（在 Windows 上）来传输文件。复制完成后，请确保所有文件都已正确放置在项目目录中，并且文件名和目录结构与项目要求一致。

## 3. 安装依赖

### 3.1 创建虚拟环境

在安装项目依赖之前，我们强烈建议您创建一个 Python 虚拟环境。虚拟环境可以隔离项目的依赖关系，避免不同项目之间的依赖冲突，这是 Python 项目管理的最佳实践之一。

如果您选择使用 uv 包管理器，创建虚拟环境的命令如下：

```bash
uv venv
```

创建完成后，需要激活虚拟环境。在 Linux 和 macOS 上，激活虚拟环境的命令如下：

```bash
source .venv/bin/activate
```

在 Windows 上，激活虚拟环境的命令如下：

```powershell
.venv\Scripts\activate
```

激活虚拟环境后，您会看到命令行提示符前面多了一个 `(.venv)` 的标识，这表示您当前处于虚拟环境中。如果您选择使用 pip 管理依赖，创建虚拟环境的命令如下：

```bash
python -m venv venv
```

激活虚拟环境的方法与上述 uv 创建的虚拟环境相同。

### 3.2 安装 Python 依赖包

激活虚拟环境后，就可以开始安装项目的 Python 依赖包了。这些依赖包都在 `requirements.txt` 文件中列出，包括 Flask、OpenAI SDK、ChromaDB 等核心库。

如果您使用 uv 安装依赖，命令如下：

```bash
uv pip install -r requirements.txt
```

如果您使用 pip 安装依赖，命令如下：

```bash
pip install -r requirements.txt
```

安装过程可能需要几分钟时间，取决于您的网络速度和服务器性能。在安装过程中，您会看到一系列的下载和安装日志，请耐心等待直到安装完成。如果安装过程中出现错误，请仔细阅读错误信息，通常是因为网络问题或依赖冲突导致的。您可以尝试更换 pip 源（例如使用清华源或阿里源）来解决网络问题，或者删除虚拟环境后重新创建来解决依赖冲突。

安装完成后，您可以通过以下命令验证重要的依赖包是否已正确安装：

```bash
python -c "import flask; import chromadb; import openai; print('依赖安装成功')"
```

如果命令返回「依赖安装成功」，说明所有核心依赖都已正确安装。

## 4. 配置环境变量

### 4.1 创建环境配置文件

My Echo 使用环境变量来管理敏感配置信息，如 API 密钥、密码等。这种方式可以保护您的敏感信息不被泄露到代码仓库中。项目提供了一个 `.env.example` 文件作为配置模板，您需要基于该模板创建实际的 `.env` 配置文件。

首先，复制配置模板文件：

```bash
cp .env.example .env
```

或者在 Windows 上：

```powershell
copy .env.example .env
```

然后，使用文本编辑器打开 `.env` 文件进行编辑。在 Linux 和 macOS 上，您可以使用 nano 或 vim 编辑器：

```bash
nano .env
```

在 Windows 上，您可以直接使用记事本或任何代码编辑器打开文件。

### 4.2 配置飞书平台信息

飞书平台配置是项目运行所必需的，这些配置用于让您的 AI 伴侣能够接收和发送飞书消息。您需要在飞书开放平台上创建一个应用，并获取相应的凭证信息。

配置飞书应用 ID 和密钥的步骤如下：

首先，登录[飞书开放平台](https://open.feishu.cn/)，在应用管理页面创建或选择一个已有的应用。创建应用后，您可以在应用的基本信息页面找到 App ID 和 App Secret。将这两个值分别填入配置文件中：

```
FEISHU_APP_ID=您的飞书应用ID
FEISHU_APP_SECRET=您的飞书应用密钥
```

接下来，需要配置验证令牌（Verify Token）。在飞书开放平台的事件订阅页面，您可以设置验证令牌。这个令牌用于验证飞书服务器的回调请求是否合法。请设置一个足够复杂的令牌，并将其填入配置：

```
FEISHU_VERIFY_TOKEN=您的验证令牌
```

最后，建议启用消息加密功能以增强安全性。在飞书开放平台的事件订阅页面，启用加密选项后会生成一个 Encrypt Key。将这个密钥填入配置：

```
FEISHU_ENCRYPT_KEY=您的加密密钥
```

### 4.3 配置 AI 模型服务

My Echo 使用 DeepSeek 作为主要的对话模型，并使用硅基流动服务进行向量化和 Embedding 计算。这些服务的配置同样需要在 `.env` 文件中完成。

获取 DeepSeek API Key 的步骤如下：

访问 [DeepSeek 开放平台](https://platform.deepseek.com/)，注册账号并登录。在用户中心或 API 管理页面，您可以创建并获取 API Key。将获取到的 Key 填入配置：

```
DEEPSEEK_API_KEY=您的DeepSeek API Key
```

硅基流动 API Key 是可选的，如果您需要使用向量化和语义搜索功能，则需要配置此项。访问[硅基流动官网](https://www.siliconflow.cn/)，注册账号并获取 API Key：

```
SILICONFLOW_API_KEY=您的硅基流动API Key
```

### 4.4 配置运维选项

除了上述必需的配置外，项目还提供了一些可选的运维配置，用于定制日志、备份和行为参数。这些配置如果您不设置，项目会使用默认值。

日志文件路径配置决定了日志的存储位置，默认值为 `./logs/feishu-cuncun.log`。如果您需要修改日志路径，可以配置：

```
LOG_FILE=./logs/feishu-cuncun.log
```

数据库备份目录配置决定了自动备份文件存储的位置，默认值为 `./backups`：

```
BACKUP_DIR=./backups
```

管理员 Open ID 配置用于接收系统告警通知。当系统发生错误或异常时，会向该 Open ID 发送告警消息。您可以在日志中找到自己的 Open ID：

```
ADMIN_OPEN_ID=您的Open ID
```

服务端口配置决定了 Flask 应用监听的端口号，默认为 8081：

```
PORT=8081
```

## 5. 飞书应用配置详解

### 5.1 创建飞书企业自建应用

飞书企业自建应用是 My Echo 与飞书平台交互的桥梁。创建应用的流程相对简单，但需要注意一些关键设置，否则可能导致机器人无法正常工作。

首先，使用您的企业账号登录[飞书开放平台](https://open.feishu.cn/)。如果您还没有企业账号，需要先注册一个飞书企业。登录后，在控制台页面点击「创建企业自建应用」按钮，开始创建流程。

在创建应用页面，您需要填写以下信息：

应用名称是用户看到机器人时显示的名称，建议使用有意义的名称，例如「我的 AI 伴侣」或「小存存」。应用描述用于说明应用的功能和用途，这部分信息会展示给企业管理员审核。应用图标建议上传一个清晰美观的图片，这会显示在机器人的头像位置。

创建完成后，您会进入应用的管理页面。在这里，您可以进一步配置应用的权限、事件回调等高级功能。

### 5.2 配置应用权限

应用权限决定了机器人能够执行的操作范围。为了让 AI 伴侣能够正常工作，需要开通以下权限：

在应用的「权限管理」页面，搜索并开通以下权限：

`im:message` 权限允许机器人发送和接收消息，这是实现对话功能所必需的基础权限。`im:message:send_as_bot` 权限允许机器人以机器人身份发送消息，确保消息发送方显示为机器人而非应用。`im:resource` 权限允许机器人上传和下载文件，这对于发送语音消息至关重要。

完成权限配置后，您需要提交应用版本审核。在应用的「版本管理与发布」页面，创建新版本并填写版本说明，然后提交审核。审核通常会在几分钟内完成，之后您就可以在飞书客户端中搜索并添加机器人了。

### 5.3 配置事件订阅

事件订阅是让飞书服务器将消息推送到您的服务器的关键配置。在应用的「事件订阅」页面，您可以配置机器人接收消息的回调地址。

首先，在「回调 URL配置」部分，输入您的服务器地址。地址格式应为 `https://您的域名/`（注意最后的斜杠不能省略）。如果您的服务器还没有域名，可以使用公网 IP 地址，但需要注意某些情况下飞书可能不支持纯 IP 地址的回调。

接下来，填写「验证令牌」（Verify Token）。这个令牌需要与您在 `.env` 文件中配置的 `FEISHU_VERIFY_TOKEN` 完全一致。飞书服务器会向您的回调地址发送验证请求，只有令牌匹配验证才会通过。

建议启用「加密」选项以增强安全性。启用后，飞书会使用您配置的 Encrypt Key 对消息内容进行加密传输，您的服务器再进行解密处理。这一层加密可以防止消息在传输过程中被截获。

最后，在「事件订阅」部分，订阅「接收消息」事件。这样当用户在飞书客户端向机器人发送消息时，飞书服务器就会将消息推送到您的服务器。

### 5.4 测试飞书连接

完成上述配置后，您可以通过以下步骤测试飞书连接是否正常：

首先，在服务器上启动项目：

```bash
python feishu_cuncun_pro.py
```

如果一切正常，您应该会看到类似「存存 V2.2 启动成功: 8081」的日志输出。

然后，在飞书客户端中搜索并添加您的机器人。添加成功后，向机器人发送一条消息，例如「你好」。

如果连接正常，您应该能在服务器日志中看到收到消息的记录，机器人也会在几秒钟内回复您的消息。如果机器人没有响应，请检查以下几点：服务器是否可以从公网访问、端口是否已开放、回调 URL 是否正确配置、验证令牌是否匹配等。

## 6. 启动和验证

### 6.1 开发模式启动

在开发环境中，您可以直接使用 Python 命令启动项目，这种方式便于调试和查看日志。启动命令如下：

```bash
python feishu_cuncun_pro.py
```

启动成功后，您会看到类似以下的输出：

```
🚀 存存 V2.2 启动成功: 8081 (带告警与定时运维)
```

此时项目已经正常运行在 8081 端口上。您可以打开浏览器访问 `http://localhost:8081/health` 来检查服务状态。如果返回类似以下 JSON 内容，说明服务运行正常：

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

在开发模式下，所有日志都会直接打印到控制台，这对于排查问题很有帮助。当收到飞书消息时，您会看到详细的处理日志，包括消息内容、匹配结果、AI 回复等信息。

### 6.2 生产模式启动

对于生产环境，我们推荐使用 Gunicorn 或类似的生产级 WSGI 服务器来运行项目，这样可以提供更好的性能和稳定性。

使用 Gunicorn 启动的推荐命令如下：

```bash
gunicorn -w 4 -b 0.0.0.0:8081 feishu_cuncun_pro:app
```

上述命令的参数说明如下：`-w 4` 表示启动 4 个工作进程，这可以充分利用服务器的多核 CPU；`-b 0.0.0.0:8081` 表示监听所有网卡的 8081 端口，使服务可以从公网访问；`feishu_cuncun_pro:app` 指定了 Flask 应用的位置。

如果您想使用 systemd 来管理服务（Linux 系统），可以创建一个服务单元文件 `/etc/systemd/system/my-echo.service`，内容如下：

```ini
[Unit]
Description=My Echo AI Companion
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/my-echo
Environment="PATH=/path/to/my-echo/.venv/bin"
ExecStart=/path/to/my-echo/.venv/bin/gunicorn -w 4 -b 0.0.0.0:8081 feishu_cuncun_pro:app
Restart=always

[Install]
WantedBy=multi-user.target
```

创建服务文件后，执行以下命令启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable my-echo
sudo systemctl start my-echo
```

### 6.3 验证完整功能

完成启动后，您应该进行完整的功能测试以确保所有组件都正常工作。以下是推荐的测试步骤：

第一项测试是健康检查。通过浏览器或 curl 命令访问 `http://您的服务器地址:8081/health`，确认所有组件状态都为 `true`。

第二项测试是消息对话。在飞书客户端中向机器人发送消息，观察机器人是否能够正常回复。建议测试多种类型的消息，包括简短问候、长文本消息、包含特殊字符的消息等。

第三项测试是历史记忆。向机器人发送一条包含个人信息的消息，然后过一段时间再次提及该信息，观察机器人是否能够记住并正确引用之前的内容。

第四项测试是语音功能（如果已配置语音库）。发送一条会触发语音回复的消息，观察机器人是否能够正确匹配语音并发送音频消息。

第五项测试是日志记录。查看 `logs` 目录下的日志文件，确认消息处理过程已被正确记录。

## 7. Docker 部署（可选）

### 7.1 准备工作

如果您更习惯使用 Docker 容器化方式部署项目，My Echo 也提供了相应的支持。Docker 部署具有环境隔离、部署便捷、易于迁移等优点。

首先，确保您的服务器上已经安装了 Docker 和 Docker Compose。您可以通过以下命令验证安装：

```bash
docker --version
docker-compose --version
```

如果命令返回版本信息，说明 Docker 环境已就绪。如果尚未安装，请参考 [Docker 官方文档](https://docs.docker.com/get-docker/)进行安装。

### 7.2 创建 Dockerfile

在项目根目录创建 `Dockerfile` 文件，内容如下：

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建必要目录
RUN mkdir -p logs backups 音频数据/CunCun_Opus_Library

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8081

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8081", "feishu_cuncun_pro:app"]
```

### 7.3 创建 Docker Compose 配置

在项目根目录创建 `docker-compose.yml` 文件，内容如下：

```yaml
version: '3.8'

services:
  my-echo:
    build: .
    container_name: my-echo
    ports:
      - "8081:8081"
    environment:
      - FEISHU_APP_ID=${FEISHU_APP_ID}
      - FEISHU_APP_SECRET=${FEISHU_APP_SECRET}
      - FEISHU_VERIFY_TOKEN=${FEISHU_VERIFY_TOKEN}
      - FEISHU_ENCRYPT_KEY=${FEISHU_ENCRYPT_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - SILICONFLOW_API_KEY=${SILICONFLOW_API_KEY}
      - ADMIN_OPEN_ID=${ADMIN_OPEN_ID}
      - LOG_FILE=/app/logs/feishu-cuncun.log
      - BACKUP_DIR=/app/backups
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./backups:/app/backups
      - ./音频数据:/app/音频数据
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

注意，在使用 Docker Compose 部署之前，您需要确保 `.env` 文件中的敏感配置已正确设置，因为 Docker Compose 会从 `.env` 文件中读取这些环境变量。

### 7.4 启动 Docker 容器

完成上述配置后，执行以下命令构建并启动容器：

```bash
docker-compose up -d --build
```

首次运行会执行构建过程，可能需要几分钟时间。构建完成后，容器会在后台运行。您可以通过以下命令查看容器状态和日志：

```bash
# 查看容器状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f my-echo
```

如果需要停止服务，执行：

```bash
docker-compose down
```

如果需要更新代码并重新部署，执行：

```bash
docker-compose down
docker-compose up -d --build
```

## 8. 后续配置

### 8.1 配置开机自启

对于 Linux 服务器，您可以通过 systemd 服务来实现开机自启。创建服务文件 `/etc/systemd/system/my-echo.service`，内容参考前面「生产模式启动」部分的内容。创建完成后，执行以下命令启用开机自启：

```bash
sudo systemctl enable my-echo
```

对于 Windows 服务器，您可以通过「任务计划程序」来实现开机自启。打开任务计划程序，创建基本任务，设置触发条件为「计算机启动时」，操作为「启动程序」并选择您的启动脚本。

### 8.2 配置域名和 SSL（推荐）

为了让飞书服务器能够访问您的回调地址，建议配置一个域名并启用 HTTPS。飞书要求回调 URL 必须是 HTTPS 协议（除非是 IP 地址）。

购买域名后，您可以配置 DNS 解析将域名指向您的服务器 IP。然后使用 Let's Encrypt 免费获取 SSL 证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot nginx -d 您的域名
```

获得 SSL 证书后，更新飞书开放平台中的回调 URL 为 `https://您的域名/`。

### 8.3 配置防火墙

确保服务器防火墙已开放 8081 端口（或您配置的其他端口）。对于 Ubuntu 系统，可以使用 UFW 防火墙：

```bash
sudo ufw allow 8081/tcp
sudo ufw enable
```

如果使用云服务器（如阿里云、腾讯云、AWS 等），还需要在云平台的安全组中开放相应端口。

恭喜您完成了 My Echo 的安装和配置！现在您可以开始与您的 AI 伴侣进行对话了。如果在使用过程中遇到任何问题，请参考本指南的常见问题章节或提交 Issue 寻求帮助。
