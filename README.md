# 🧹 磁盘清理 v4.2

> Windows 安全磁盘清理工具  
> GUI 图形界面 + CMD 命令行双版本

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Version](https://img.shields.io/badge/Version-v4.2-orange)

---

## 📌 作者信息

- 作者：CS
- QQ：476199719
- 微信：Entropy4761

---

## 📖 项目介绍

磁盘清理 v4.2 是一个基于 Python 开发的 Windows 磁盘清理工具，支持图形界面和命令行两种使用方式。

项目目标：

- 快速分析磁盘空间占用
- 清理缓存、临时文件和无用目录
- 降低误删风险
- 提供风险等级、回收站删除和清理前后空间对比
- 为普通用户提供更直观的清理体验

---

## ✨ v4.2 新增功能

### ✅ 回收站删除模式

默认将清理项目放入回收站，避免误删后无法恢复。

### ✅ Top 100 大文件扫描

快速找出占用空间最大的文件，适合定位视频、压缩包、镜像、安装包等大文件。

### ✅ 下载目录分析

自动统计下载目录中不同类型文件的占用空间：

- 视频
- 图片
- 压缩包
- 安装包
- 文档
- 音频
- 镜像
- 代码
- 其他

### ✅ 重复文件检测

通过“文件大小 + MD5 哈希”检测重复文件，适合查找重复视频、图片、压缩包。

### ✅ 清理前后空间对比

清理完成后显示：

- 本次释放空间
- 清理前剩余空间
- 清理后剩余空间
- 失败数量

### ✅ GUI 界面优化

- 新增左侧导航栏
- 新增首页信息展示
- 风险等级颜色区分
- 表格显示优化
- 支持多选清理
- 支持导出 CSV
- 支持打开选中目录
- 新增刷新结果按钮：清理后可刷新列表，自动移除已删除、已清空或低于显示阈值的项目

---

## 🧩 已实现功能

- GUI 图形界面
- CMD 命令行界面
- 磁盘大文件扫描
- 缓存扫描
- Top 100 大文件扫描
- 下载目录分析
- 重复文件检测
- 空文件夹删除
- 文件类型识别
- 文件创建日期识别
- 文件修改日期识别
- 风险等级系统
- 批量清理低风险
- 激进清理低/中风险
- 默认回收站删除
- 打开扫描结果目录
- 导出 CSV
- 日志系统
- 自定义 LOGO
- EXE 打包脚本

---

## 🛡 风险等级说明

### 低风险

通常为缓存、临时文件、日志、Shader Cache 等，一般可以清理。

### 中风险

可能包含用户资料、软件配置、下载文件、聊天文件或游戏数据。清理前建议确认。

### 高风险

通常是系统目录、驱动目录或程序主体目录。工具会默认跳过，不建议清理。

---

## 📂 项目结构

```text
disk_cleaner_v42_package/
│
├── disk_cleaner_core_v42.py
├── disk_cleaner_v4_gui.py
├── disk_cleaner_v4_cmd.py
├── Disk_Cleaner_v4.2_GUI.bat
├── Disk_Cleaner_v4.2_CMD.bat
├── Build_GUI_EXE.bat
├── Build_CMD_EXE.bat
├── Build_All_EXE.bat
├── cs_logo.ico
├── README.md
├── LICENSE
└── .gitignore
```

---

## 🚀 使用方法

### 运行 GUI 图形界面

```text
双击 Disk_Cleaner_v4.2_GUI.bat
```

### 运行 CMD 命令行版

```text
双击 Disk_Cleaner_v4.2_CMD.bat
```

---

## 📦 打包 EXE

### 打包 GUI 版

```text
双击 Build_GUI_EXE.bat
```

生成：

```text
dist\磁盘清理_v4.2_GUI.exe
```

### 打包 CMD 版

```text
双击 Build_CMD_EXE.bat
```

生成：

```text
dist\磁盘清理_v4.2_CMD.exe
```

### 一键打包全部版本

```text
双击 Build_All_EXE.bat
```

---

## ⚠ 注意事项

- 清理工具存在误删风险，请谨慎操作。
- 默认建议使用“回收站删除模式”。
- 高风险目录不建议清理。
- 中风险目录请先打开目录确认。
- 微信、QQ、Steam、下载目录等位置请谨慎处理。
- 重复文件删除前请确认至少保留一份。

---

## 🔧 依赖环境

- Python 3.10+
- Windows 10 / Windows 11

打包需要：

```bash
pip install pyinstaller
```

---

## 📌 GitHub 上传建议

建议上传：

```text
disk_cleaner_core_v42.py
disk_cleaner_v4_gui.py
disk_cleaner_v4_cmd.py
*.bat
cs_logo.ico
README.md
LICENSE
.gitignore
```

不建议上传：

```text
dist/
build/
__pycache__/
*.spec
*.pyc
```

---

## 📜 License

MIT License


---

## v4.2 修复说明

- 修复 CMD 版启动时 `WindowsPath.__format__` 报错问题。
