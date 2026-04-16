# AI 提示词管理器

<div align="center">

![Logo](https://github.com/kungful/ai_prompt_manage/blob/b567880fb0cd0997ce09f462547dd96f61ead5a5/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202026-04-16%20223756.png)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)

</div>

一个简洁高效的 AI 提示词管理工具，帮助你整理、收藏和快速复制 AI 图片生成的提示词。

## 功能特点

- 📁 **图片管理** - 拖拽上传图片，轻松管理你的作品
- ⭐ **收藏夹** - 一键收藏喜欢的提示词
- 🏷️ **标签分类** - 通过标签快速筛选和查找
- 🔍 **全文搜索** - 支持提示词、标题、标签的快速搜索
- 🌙 **深色/浅色主题** - 舒适的视觉体验
- 📦 **数据导入导出** - 方便备份和迁移
- 🖼️ **多选批量操作** - 支持批量删除和导出

## 界面预览

![界面预览](https://github.com/kungful/ai_prompt_manage/blob/b567880fb0cd0997ce09f462547dd96f61ead5a5/%E5%B1%8F%E5%B9%95%E6%88%AA%E5%9B%BE%202026-04-16%20223756.png)

## 安装使用

### 方法一：直接运行

1. 下载最新版本的 `PromptManager.exe`
2. 双击运行即可

### 方法二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/kungful/ai_prompt_manage.git
cd ai_prompt_manage

# 安装依赖
pip install PySide6

# 运行
python main.py
```

## 使用说明

### 首页
- 查看所有已保存的图片和提示词
- 支持搜索和标签筛选
- 点击图片查看详情或复制提示词

### 收藏夹
- 点击图片下方的 ⭐ 图标收藏
- 在顶部导航栏点击 ⭐ 查看收藏列表

### 载入
- 拖拽图片到上传区域
- 填写标题、标签和提示词
- 点击保存

### 设置
- 切换深色/浅色主题
- 导出数据为 ZIP 备份
- 从 ZIP 导入数据

## 项目结构

```
GUI_Cover/
├── main.py          # 主程序
├── load_page.py     # 载入页面
├── ui_main.py      # UI 定义
├── prompts_data.json # 数据存储
├── images/          # 图片存储
└── 赞赏码.jpg       # 赞助码
```

## 技术栈

- **GUI 框架**: PySide6
- **编程语言**: Python 3.8+

## 反馈与贡献

如果你在使用过程中遇到问题或有好的建议，欢迎：

- 🐛 [提交 Issue](https://github.com/kungful/ai_prompt_manage/issues)
- ⭐ [提交 PR](https://github.com/kungful/ai_prompt_manage/pulls)
- 📧 联系邮箱: kungful@email.com

## 支持项目

如果你觉得这个项目对你有帮助，可以考虑以下方式支持：

- ⭐ 给项目点个 Star
- 🍴 Fork 并完善它
- 💝 [扫码赞助](https://github.com/kungful/ai_prompt_manage)

## 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">

Made with ❤️ by [kungful](https://github.com/kungful)

</div>
