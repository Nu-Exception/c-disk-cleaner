# 🧹 磁盘清理 v4

> Windows 安全磁盘清理工具

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

# 📌 作者信息

* 作者：CS
* QQ：476199719
* 微信：Entropy4761

---

# 📖 项目介绍

磁盘清理 v4 是一个基于 Python 开发的 Windows 磁盘清理工具。

主要用于：

* 清理缓存
* 分析大文件
* 扫描磁盘空间
* 删除临时文件
* 软件卸载管理
* 空文件夹清理

---

# ✨ 功能特性

## ✅ 已实现功能

* GUI 图形界面
* 磁盘扫描
* 缓存清理
* 风险等级系统
* 批量清理
* 激进模式
* 文件类型识别
* 文件日期识别
* 空文件夹清理
* 软件卸载管理
* 注册表保守清理
* 打开目录
* EXE 打包
* 自定义 LOGO

---

# 🖥 项目截图

（这里以后可以放软件截图）

---

# 🚀 使用方法

## Python 运行

```bash
python disk_cleaner_v4_gui.py
```

---

## EXE 打包

```bash
pyinstaller --onefile --clean --noconsole --icon=cs_logo.ico --name="磁盘清理_v4" disk_cleaner_v4_gui.py
```

---

# 📂 项目结构

```text
disk_cleaner_v4_gui_package_fix/
│
├── disk_cleaner_v4_gui.py
├── Disk_Cleaner_v4_GUI.bat
├── Build_GUI_EXE_With_Logo_FIXED.bat
├── cs_logo.ico
├── README.md
└── LICENSE
```

---

# ⚠ 注意事项

* 高风险目录不要随意删除
* 微信/QQ 文件夹请谨慎处理
* 建议清理前确认重要文件
* 建议保留日志文件

---

# 📜 License

MIT License
