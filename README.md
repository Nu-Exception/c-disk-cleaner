# 磁盘清理 v4

Windows 安全磁盘清理工具  
作者：CS

---

# 项目介绍

磁盘清理 v4 是一个基于 Python 开发的 Windows 磁盘清理工具。

目标：

- 快速扫描磁盘空间占用
- 清理缓存与垃圾文件
- 辅助用户分析大文件
- 提供安全的风险提示
- 避免误删系统关键文件
- 提供图形界面与命令行双版本

适用于：

- C盘爆满
- AppData 体积过大
- 游戏缓存占用空间
- 浏览器缓存清理
- npm / Python 缓存清理
- 临时文件清理
- 大文件分析

---

# 当前版本

Version: v4.1

---

# 功能列表

## 1. 磁盘扫描

支持扫描：

- 文件夹
- 文件
- 所有盘符
- 指定目录

支持显示：

- 文件大小
- 文件类型
- 创建日期
- 修改日期
- 风险等级
- 是否缓存目录

---

## 2. 缓存扫描

自动识别：

- 浏览器缓存
- GPU Shader 缓存
- Steam 缓存
- Edge 缓存
- Chrome 缓存
- npm-cache
- pip Cache
- Temp
- Logs
- WebCache
- Code Cache

---

## 3. 批量清理

支持：

### 安全模式

逐项确认。

### 批量模式

自动清理低风险缓存。

### 激进模式

自动清理低风险 + 中风险，并提供最终确认。

---

## 4. 风险等级系统

### low（低风险）

通常为：

- Cache
- Temp
- Logs
- Shader Cache

一般可安全删除。

### medium（中风险）

可能包含：

- 用户配置
- 聊天缓存
- 游戏配置
- 下载文件

清理前会提示。

### high（高风险）

例如：

- Windows
- System32
- Program Files

默认禁止危险清理。

---

## 5. 打开目录功能

支持打开扫描结果所在目录。

---

## 6. 继续扫描功能

支持继续扫描某个文件夹。

---

## 7. 文件类型识别

自动识别：

- 视频
- 图片
- 压缩包
- EXE
- PDF
- Word
- Excel
- PPT
- 日志文件
- Python 文件
- JSON 文件

等常见文件类型。

---

## 8. 空文件夹清理

支持一键删除空文件夹。

---

## 9. 软件卸载管理

支持：

- 读取已安装软件
- 搜索软件
- 调用卸载程序
- 保守模式注册表清理

---

## 10. 系统信息显示

显示：

- 当前用户
- 计算机名
- IP 地址
- 当前 WiFi 名称
- 显卡信息
- 磁盘剩余空间

---

## 11. 日志系统

自动生成：

- 清理日志
- 扫描报告

默认目录：

C:\Users\用户名\清理日志

---

## 12. GUI 图形界面

支持：

- 图形化扫描
- 表格显示
- 进度条
- 多选
- 批量操作
- 导出 CSV

---

## 13. 自定义 LOGO

支持：

- EXE 图标
- 自定义头像
- 品牌化打包

---

# 项目结构

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

# 使用方法

## 方法1：直接运行 Python 版

电脑需要安装 Python。

双击：

Disk_Cleaner_v4_GUI.bat

即可运行。

---

## 方法2：打包 EXE

双击：

Build_GUI_EXE_With_Logo_FIXED.bat

生成：

dist\磁盘清理_v4.exe

---

# GitHub 上传建议

建议上传：

- disk_cleaner_v4_gui.py
- Disk_Cleaner_v4_GUI.bat
- Build_GUI_EXE_With_Logo_FIXED.bat
- cs_logo.ico
- README.md
- LICENSE

---

# 不建议上传

- dist/
- build/
- __pycache__/
- *.spec

---

# 推荐 .gitignore

```gitignore
dist/
build/
__pycache__/
*.spec
*.pyc
```

---

# 依赖环境

Python 3.10+

推荐安装：

pip install pyinstaller

---

# 后续开发计划

计划增加：

- 回收站删除模式
- 重复文件检测
- Top100 大文件排行
- 磁盘树状图
- 空间可视化
- 自动更新
- 多线程扫描
- 多语言支持
- 深色主题
- Windows 开机监控

---

# 注意事项

清理工具存在误删风险。

请注意：

- 高风险目录不要随意删除
- 中风险目录建议先打开确认
- 游戏目录请谨慎处理
- 微信/QQ 文件目录请谨慎处理

---

# License

MIT License

---

# 作者信息

Author: CS
