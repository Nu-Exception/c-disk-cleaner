# -*- coding: utf-8 -*-
import os
import re
import json
import shutil
import socket
import getpass
import platform
import subprocess
import threading
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_NAME = "Disk Cleaner v4 GUI"
APP_VERSION = "4.1"
AUTHOR = "CS"

USER_DIR = Path.home()
LOG_DIR = USER_DIR / "清理日志"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"gui_cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

MIN_SCAN_SIZE = 100 * 1024 * 1024

SAFE_CACHE_KEYWORDS = [
    "cache", "caches", "code cache", "gpucache", "shadercache", "dxcache",
    "dxccache", "glcache", "nv_cache", "htmlcache", "browsercache", "webcache",
    "npm-cache", "pip cache", "temp", "tmp", "logs", "crashdumps", "thumbnail",
]

HIGH_RISK_KEYWORDS = [
    "\\windows", "\\program files", "\\program files (x86)", "\\programdata",
    "\\system32", "\\syswow64", "\\drivers", "\\boot", "\\efi", "\\recovery",
    "\\system volume information",
]

MEDIUM_RISK_KEYWORDS = [
    "\\users", "\\desktop", "\\documents", "\\downloads", "\\pictures",
    "\\videos", "\\music", "\\appdata\\roaming", "\\appdata\\locallow",
    "\\steamapps", "\\wechat files", "\\tencent files",
]

FILE_TYPE_MAP = {
    ".exe": "应用程序", ".msi": "安装包", ".zip": "压缩包", ".rar": "压缩包", ".7z": "压缩包",
    ".mp4": "视频", ".mkv": "视频", ".avi": "视频", ".mov": "视频",
    ".jpg": "图片", ".jpeg": "图片", ".png": "图片", ".gif": "图片", ".webp": "图片",
    ".doc": "Word", ".docx": "Word", ".xls": "Excel", ".xlsx": "Excel",
    ".ppt": "PPT", ".pptx": "PPT", ".pdf": "PDF", ".txt": "文本", ".log": "日志",
    ".py": "Python", ".js": "JavaScript", ".json": "JSON",
}

def write_log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(str(msg) + "\n")
    except Exception:
        pass

def format_size(size):
    try:
        size = float(size)
    except Exception:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def format_time(ts):
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "-"

def norm(path):
    return str(path).lower().replace("/", "\\")

def get_risk(path):
    text = norm(path)
    for k in HIGH_RISK_KEYWORDS:
        if k in text:
            return "高风险"
    for k in MEDIUM_RISK_KEYWORDS:
        if k in text:
            return "中风险"
    return "低风险"

def risk_raw(path):
    r = get_risk(path)
    if r.startswith("高"): return "high"
    if r.startswith("中"): return "medium"
    return "low"

def is_cache_like(path):
    text = norm(path)
    return any(k in text for k in SAFE_CACHE_KEYWORDS)

def get_size(path):
    p = Path(path)
    if not p.exists():
        return 0
    if p.is_file():
        try:
            return p.stat().st_size
        except Exception:
            return 0
    total = 0
    try:
        for root, dirs, files in os.walk(p):
            for name in files:
                try:
                    total += (Path(root) / name).stat().st_size
                except Exception:
                    pass
    except Exception:
        pass
    return total

def file_type(path):
    p = Path(path)
    if p.is_dir():
        return "文件夹"
    return FILE_TYPE_MAP.get(p.suffix.lower(), p.suffix.lower().replace(".", "").upper() or "文件")

def consequence(path):
    text = norm(path)
    if "\\windows" in text or "\\system32" in text:
        return "可能导致 Windows 系统损坏、更新失败、蓝屏或无法启动。"
    if "\\program files" in text:
        return "可能导致软件无法运行或卸载异常。"
    if "\\downloads" in text:
        return "可能删除下载内容，包括安装包、压缩包、视频等。"
    if "\\desktop" in text:
        return "可能删除桌面文件。"
    if "wechat files" in text:
        return "可能删除微信聊天文件、图片、视频和接收文件。"
    if "tencent files" in text:
        return "可能删除 QQ 文件、图片、视频和接收文件。"
    if "steamapps" in text:
        return "可能删除 Steam 游戏本体，需要重新下载。"
    if is_cache_like(path):
        return "通常是缓存，可重建；清理后软件首次启动可能变慢。"
    return "无法准确判断用途，建议打开目录确认后再处理。"

def item_info(path, size=None):
    p = Path(path)
    try:
        st = p.stat()
    except Exception:
        st = None
    if size is None:
        size = get_size(p)
    return {
        "path": str(p),
        "name": p.name,
        "size": size,
        "size_text": format_size(size),
        "kind": "文件夹" if p.is_dir() else "文件",
        "type": file_type(p),
        "risk": get_risk(p),
        "cache": "是" if is_cache_like(p) else "否",
        "created": format_time(st.st_ctime) if st else "-",
        "modified": format_time(st.st_mtime) if st else "-",
    }

def drives():
    out = []
    for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        p = Path(f"{c}:\\")
        if p.exists():
            out.append(str(p))
    return out

def disk_usage_text(path):
    try:
        u = shutil.disk_usage(Path(path).anchor or path)
        return f"总容量 {format_size(u.total)} | 已用 {format_size(u.used)} | 剩余 {format_size(u.free)}"
    except Exception:
        return "-"

def ip_info():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "-"

def wifi_name():
    try:
        out = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True, encoding="gbk", errors="ignore")
        for line in out.splitlines():
            if "SSID" in line and "BSSID" not in line:
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "-"

def gpu_info():
    try:
        out = subprocess.check_output("wmic path win32_VideoController get name", shell=True, text=True, encoding="gbk", errors="ignore")
        names = [x.strip() for x in out.splitlines() if x.strip() and x.strip().lower() != "name"]
        return " / ".join(names) if names else "-"
    except Exception:
        return "-"

def delete_contents(path):
    p = Path(path)
    deleted = 0
    failed = 0
    count = 0
    if p.is_file():
        try:
            size = p.stat().st_size
            p.unlink()
            return size, 0, 1
        except Exception as e:
            write_log(f"删除失败：{p} -> {e}")
            return 0, 1, 0
    try:
        items = list(p.iterdir())
    except Exception:
        return 0, 1, 0
    for item in items:
        try:
            if item.is_file() or item.is_symlink():
                s = item.stat().st_size
                item.unlink()
                deleted += s
                count += 1
            elif item.is_dir():
                s = get_size(item)
                shutil.rmtree(item)
                deleted += s
                count += 1
        except Exception as e:
            failed += 1
            write_log(f"删除失败：{item} -> {e}")
    return deleted, failed, count

class DiskCleanerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} - Version {APP_VERSION}")
        self.root.geometry("1180x720")
        self.results = []
        self.sort_reverse = True

        self.path_var = tk.StringVar(value=drives()[0] if drives() else str(USER_DIR))
        self.status_var = tk.StringVar(value="就绪")
        self.progress_var = tk.DoubleVar(value=0)

        self.build_ui()
        self.refresh_system_info()

    def build_ui(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        title = ttk.Label(top, text=f"{APP_NAME}  Version {APP_VERSION}    作者：{AUTHOR}", font=("Microsoft YaHei", 14, "bold"))
        title.pack(anchor="w")

        info_frame = ttk.LabelFrame(self.root, text="电脑信息", padding=8)
        info_frame.pack(fill="x", padx=10, pady=5)
        self.info_label = ttk.Label(info_frame, text="", justify="left")
        self.info_label.pack(anchor="w")

        path_frame = ttk.LabelFrame(self.root, text="扫描位置", padding=8)
        path_frame.pack(fill="x", padx=10, pady=5)

        ttk.Entry(path_frame, textvariable=self.path_var).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(path_frame, text="选择文件夹", command=self.choose_folder).pack(side="left", padx=3)
        ttk.Button(path_frame, text="打开路径", command=self.open_current_path).pack(side="left", padx=3)

        button_frame = ttk.Frame(self.root, padding=(10, 5))
        button_frame.pack(fill="x")

        buttons = [
            ("扫描大文件/文件夹", self.scan_large),
            ("扫描缓存", self.scan_cache),
            ("扫描明细", self.scan_detail),
            ("删除空文件夹", self.delete_empty_dirs),
            ("批量清理低风险", self.batch_clean_low),
            ("激进清理低/中风险", self.batch_clean_medium),
            ("手动清理选中项", self.clean_selected),
            ("打开选中目录", self.open_selected),
            ("导出结果", self.export_results),
            ("打开日志", self.open_logs),
        ]
        for text, cmd in buttons:
            ttk.Button(button_frame, text=text, command=cmd).pack(side="left", padx=3, pady=2)

        table_frame = ttk.Frame(self.root, padding=10)
        table_frame.pack(fill="both", expand=True)

        columns = ("kind", "type", "size", "risk", "cache", "created", "modified", "path")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="extended")
        headers = {
            "kind": "类别", "type": "类型", "size": "大小", "risk": "风险",
            "cache": "缓存", "created": "创建日期", "modified": "修改日期", "path": "路径"
        }
        widths = {
            "kind": 70, "type": 90, "size": 100, "risk": 80,
            "cache": 60, "created": 150, "modified": 150, "path": 500
        }
        for col in columns:
            self.tree.heading(col, text=headers[col], command=lambda c=col: self.sort_by(c))
            self.tree.column(col, width=widths[col], anchor="w")

        ybar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        xbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        bottom = ttk.Frame(self.root, padding=10)
        bottom.pack(fill="x")
        self.progress = ttk.Progressbar(bottom, variable=self.progress_var, maximum=100)
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Label(bottom, textvariable=self.status_var).pack(side="left")

    def refresh_system_info(self):
        path = self.path_var.get()
        text = (
            f"电脑用户名：{getpass.getuser()}    计算机名：{platform.node()}    系统：{platform.platform()}\n"
            f"IP：{ip_info()}    当前 WiFi：{wifi_name()}    显卡：{gpu_info()}\n"
            f"当前路径磁盘信息：{disk_usage_text(path)}"
        )
        self.info_label.config(text=text)

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.path_var.get() or str(USER_DIR))
        if folder:
            self.path_var.set(folder)
            self.refresh_system_info()

    def open_current_path(self):
        p = Path(self.path_var.get())
        if p.exists():
            os.startfile(p)

    def set_status(self, text):
        self.status_var.set(text)
        self.root.update_idletasks()

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insert_results(self):
        self.clear_table()
        folders = [x for x in self.results if x["kind"] == "文件夹"]
        files = [x for x in self.results if x["kind"] == "文件"]
        ordered = folders + files
        for idx, it in enumerate(ordered):
            self.tree.insert("", "end", iid=str(idx), values=(
                it["kind"], it["type"], it["size_text"], it["risk"], it["cache"],
                it["created"], it["modified"], it["path"]
            ))
        self.results = ordered
        total = sum(x["size"] for x in self.results)
        self.set_status(f"完成：共 {len(self.results)} 项，合计 {format_size(total)}")

    def run_thread(self, func):
        t = threading.Thread(target=func, daemon=True)
        t.start()

    def scan_large(self):
        def task():
            self.progress_var.set(0)
            self.set_status("正在扫描大文件/文件夹...")
            target = Path(self.path_var.get())
            results = []
            try:
                items = list(target.iterdir())
            except Exception as e:
                messagebox.showerror("错误", str(e))
                return
            total = max(len(items), 1)
            for i, p in enumerate(items, 1):
                size = get_size(p)
                if size >= MIN_SCAN_SIZE:
                    results.append(item_info(p, size))
                self.progress_var.set(i / total * 100)
            results.sort(key=lambda x: x["size"], reverse=True)
            self.results = results
            self.insert_results()
            self.refresh_system_info()
        self.run_thread(task)

    def scan_detail(self):
        def task():
            self.progress_var.set(0)
            self.set_status("正在扫描文件夹和文件明细...")
            target = Path(self.path_var.get())
            results = []
            try:
                items = list(target.iterdir())
            except Exception as e:
                messagebox.showerror("错误", str(e))
                return
            total = max(len(items), 1)
            for i, p in enumerate(items, 1):
                results.append(item_info(p))
                self.progress_var.set(i / total * 100)
            results.sort(key=lambda x: (x["kind"] != "文件夹", -x["size"]))
            self.results = results
            self.insert_results()
            self.refresh_system_info()
        self.run_thread(task)

    def scan_cache(self):
        def task():
            self.progress_var.set(0)
            self.set_status("正在扫描缓存目录...")
            target = Path(self.path_var.get())
            candidates = []
            for root, dirs, files in os.walk(target):
                p = Path(root)
                if risk_raw(p) == "high" and not is_cache_like(p):
                    dirs[:] = []
                    continue
                if is_cache_like(p):
                    candidates.append(p)
                    dirs[:] = []
            results = []
            total = max(len(candidates), 1)
            for i, p in enumerate(candidates, 1):
                size = get_size(p)
                if size >= MIN_SCAN_SIZE:
                    results.append(item_info(p, size))
                self.progress_var.set(i / total * 100)
            results.sort(key=lambda x: x["size"], reverse=True)
            self.results = results
            self.insert_results()
            self.refresh_system_info()
        self.run_thread(task)

    def get_selected_items(self):
        selected = []
        for iid in self.tree.selection():
            try:
                selected.append(self.results[int(iid)])
            except Exception:
                pass
        return selected

    def clean_items(self, items, mode_name="清理"):
        if not items:
            messagebox.showinfo("提示", "没有可清理项目。")
            return

        total = sum(x["size"] for x in items)
        if not messagebox.askyesno("确认", f"{mode_name} {len(items)} 项，预计释放 {format_size(total)}。\n是否继续？"):
            return

        def task():
            deleted_total = 0
            failed_total = 0
            total_count = max(len(items), 1)
            for i, it in enumerate(items, 1):
                p = Path(it["path"])
                if risk_raw(p) == "high":
                    write_log(f"跳过高风险：{p}")
                    continue
                deleted, failed, count = delete_contents(p)
                deleted_total += deleted
                failed_total += failed
                self.progress_var.set(i / total_count * 100)
            messagebox.showinfo("完成", f"清理完成。\n释放：{format_size(deleted_total)}\n失败：{failed_total}")
            self.refresh_system_info()
            self.scan_cache()
        self.run_thread(task)

    def clean_selected(self):
        items = self.get_selected_items()
        risky = [x for x in items if risk_raw(x["path"]) == "medium"]
        if risky:
            msg = "选中项包含中风险目录，可能包含用户资料、软件配置或聊天文件。\n是否继续？"
            if not messagebox.askyesno("中风险提示", msg):
                return
        self.clean_items(items, "手动清理")

    def batch_clean_low(self):
        items = [x for x in self.results if risk_raw(x["path"]) == "low"]
        self.clean_items(items, "批量清理低风险")

    def batch_clean_medium(self):
        items = [x for x in self.results if risk_raw(x["path"]) in ("low", "medium")]
        msg = "激进模式将清理低风险和中风险项目。\n中风险可能包含用户资料或软件配置。\n是否继续？"
        if messagebox.askyesno("激进模式确认", msg):
            self.clean_items(items, "激进清理")

    def open_selected(self):
        items = self.get_selected_items()
        if not items:
            messagebox.showinfo("提示", "请先选择一项。")
            return
        p = Path(items[0]["path"])
        try:
            if p.is_dir():
                os.startfile(p)
            else:
                subprocess.Popen(f'explorer /select,"{p}"')
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def delete_empty_dirs(self):
        target = Path(self.path_var.get())
        found = []
        self.set_status("正在扫描空文件夹...")
        for root, dirs, files in os.walk(target, topdown=False):
            p = Path(root)
            try:
                if p != target and not any(p.iterdir()):
                    found.append(p)
            except Exception:
                pass
        if not found:
            messagebox.showinfo("结果", "没有发现空文件夹。")
            return
        if not messagebox.askyesno("确认", f"发现 {len(found)} 个空文件夹，是否一键删除？"):
            return
        ok = fail = 0
        for p in found:
            try:
                p.rmdir()
                ok += 1
            except Exception:
                fail += 1
        messagebox.showinfo("完成", f"删除完成：成功 {ok}，失败 {fail}")
        self.set_status(f"空文件夹删除完成：成功 {ok}，失败 {fail}")

    def export_results(self):
        if not self.results:
            messagebox.showinfo("提示", "没有可导出的结果。")
            return
        out = LOG_DIR / f"gui_scan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(out, "w", encoding="utf-8-sig") as f:
            f.write("类别,类型,大小,风险,缓存,创建日期,修改日期,路径\n")
            for it in self.results:
                f.write(f"{it['kind']},{it['type']},{it['size_text']},{it['risk']},{it['cache']},{it['created']},{it['modified']},{it['path']}\n")
        messagebox.showinfo("完成", f"已导出：{out}")

    def open_logs(self):
        os.startfile(LOG_DIR)

    def sort_by(self, col):
        key_map = {
            "kind": "kind", "type": "type", "size": "size", "risk": "risk", "cache": "cache",
            "created": "created", "modified": "modified", "path": "path"
        }
        key = key_map[col]
        self.results.sort(key=lambda x: x[key], reverse=self.sort_reverse)
        self.sort_reverse = not self.sort_reverse
        self.insert_results()

def main():
    root = tk.Tk()
    app = DiskCleanerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
