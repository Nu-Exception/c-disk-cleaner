# 🧹 Disk Cleaner v3

Windows 安全磁盘清理工具

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Windows](https://img.shields.io/badge/Platform-Windows-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

Disk Cleaner v3 是一个基于 Python 的 Windows 磁盘清理工具。

主要用于扫描磁盘中的：

- 临时文件
- 缓存文件
- 大文件
- 空目录
- 软件残留

并提供风险等级提示，避免误删重要数据。

---

# ✨ 主要功能

| 功能 | 说明 |
|---|---|
| 🔍 大文件扫描 | 快速定位占用空间较大的文件 |
| 📁 空目录扫描 | 查找无用空文件夹 |
| 🗑 批量删除 | 支持批量清理文件 |
| ⚠ 风险等级提示 | 避免误删系统文件 |
| 📊 文件信息显示 | 显示大小、类型、时间 |
| 🚀 启动项查看 | 查看部分系统启动项 |
| 💾 注册表提示 | 提示可能存在的缓存项 |
| 🖥 系统信息显示 | 显示磁盘与系统信息 |

---

# 🚀 使用方法

## 方式 1：Python 运行

需要安装 Python 3

```bash
python disk_cleaner_v3.py
```

---

## 方式 2：BAT 启动

双击：

```text
Disk_Cleaner_v3.bat
```

---

## 方式 3：打包 EXE

双击：

```text
build_exe.bat
```

生成：

```text
dist/DiskCleaner_v3.exe
```

---

# 📦 项目结构

```text
Disk-Cleaner-v3/
├── disk_cleaner_v3.py
├── Disk_Cleaner_v3.bat
├── build_exe.bat
├── README.md
└── LICENSE
```

---

# 📋 扫描结果说明

| 标识 | 含义 |
|---|---|
| low | 临时文件 / 缓存 |
| medium | 软件缓存 / 用户文件 |
| high | 可能涉及系统关键文件 |

高风险项目默认不会自动删除。

---

# ⚠ 注意事项

- 请勿删除系统目录文件
- 删除前请确认文件用途
- 建议使用管理员权限运行
- 建议先进行小范围测试

---

# 🛡 安全说明

程序默认会跳过部分常见系统目录，例如：

- Windows
- Program Files
- ProgramData

本工具仅提供清理建议。

---

# 📄 License

MIT License

---

# 👤 作者

CS

QQ：476199719
微信：Entropy4761
