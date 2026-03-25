# AI Coach 项目初始化指南

本指南将帮助你在本地环境中设置并运行 AI Coach 项目。 啦啦啦。

## 前置要求

- Python 3.9 或更高版本
- Git

## 初始化步骤

### 1. 检查并安装 Git

首先检查是否已安装 Git：

```bash
git --version
```

如果没有安装，请先下载并安装 Git：
- Windows: https://git-scm.com/download/win
- macOS: `brew install git`（需要 Homebrew）
- Linux: `sudo apt install git` 或 `sudo yum install git`

### 2. 克隆项目

```bash
git clone git@github.com:mghys/lol-ai-coach.git
cd lol-ai-coach
```

### 3. 检查 Python 环境

确保已安装 Python 3.9+：

```bash
python --version
```

### 4. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 5. 安装依赖

```bash
pip install -r requirements.txt
```

### 6. 配置环境变量

根据需要创建 `.env` 文件，配置数据库连接等环境变量。

## 启动项目

```bash
python main.py
```

## 常见问题

- **依赖安装失败**：确保 Python 版本符合要求，并尝试升级 pip
- **PaddlePaddle 安装问题**：某些系统可能需要额外的系统依赖，参考 [PaddlePaddle 官方文档](https://www.paddlepaddle.org.cn/)
