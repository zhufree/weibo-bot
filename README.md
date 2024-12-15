# 晋江小说微博机器人

一个自动从[晋江文学城](https://www.jjwxc.net/)抓取小说内容并发布到微博的 Python 机器人。机器人会自动选择小说，提取章节内容，并附带标题、作者、收藏数和标签等信息发布到微博。

## 功能特点

- 自动抓取小说内容并发布到微博
- 使用 APScheduler 支持定时发布
- 包含小说元数据（标题、作者、标签、收藏数）
- 自动处理微博字数限制
- 维护发布历史，避免重复发布

## 系统要求

- Python 3.10 或更高版本
- Poetry 包管理工具

## 依赖包

- playwright: 网页自动化
- pyquery: HTML 解析
- httpx: HTTP 客户端
- apscheduler: 任务调度

## 安装方法

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/weibo-bot.git
cd weibo-bot
```

2. 使用 Poetry 安装依赖：
```bash
poetry install
```

3. 配置设置：
创建 `config.py` 文件，设置微博账号凭据和其他必要配置。

## 使用方法

机器人支持以下运行模式：

1. 单次发布：
```python
python novel_bot.py
```

2. 定时发布：
可以在 `novel_bot.py` 中配置调度器实现定时发布。

## 项目结构

- `novel_bot.py`: 主程序脚本
- `data_cleaner.py`: 数据处理工具
- `pyproject.toml`: 项目依赖和配置
- `data/novel_data.json`: 小说数据和发布历史存储

## 开源协议

本项目遵循 LICENSE 文件中规定的协议条款。

## 作者

zhufree (zhufree2013@gmail.com)
