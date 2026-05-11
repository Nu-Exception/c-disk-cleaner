import os
import re
import sys
import json
import time
import shutil
import ctypes
import socket
import getpass
import platform
import subprocess
import winreg
from pathlib import Path
from datetime import datetime

APP_TITLE = "Disk Cleaner v3"
APP_SUBTITLE = "Windows 安全磁盘清理工具"
APP_VERSION = "3.9"
AUTHOR = "CS"
USER_DIR = Path.home()
LOG_DIR = USER_DIR / "清理日志"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
REPORT_FILE = LOG_DIR / f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
CONFIG_FILE = USER_DIR / "disk_cleaner_config.json"
MIN_SCAN_SIZE = 100 * 1024 * 1024
LAST_RESULTS = []

COLORS = {
    "green": "0A", "white": "0F", "blue": "09", "red": "0C", "yellow": "0E", "purple": "0D"
}

SAFE_CACHE_KEYWORDS = ["cache", "caches", "code cache", "gpucache", "shadercache", "dxcache", "dxccache", "glcache", "nv_cache", "htmlcache", "browsercache", "webcache", "npm-cache", "pip cache", "temp", "tmp", "logs", "crashdumps", "thumbnail"]
HIGH_RISK_KEYWORDS = ["\\windows", "\\program files", "\\program files (x86)", "\\programdata", "\\system32", "\\syswow64", "\\drivers", "\\boot", "\\efi", "\\recovery", "\\system volume information"]
MEDIUM_RISK_KEYWORDS = ["\\users", "\\desktop", "\\documents", "\\downloads", "\\pictures", "\\videos", "\\music", "\\appdata\\roaming", "\\appdata\\locallow", "\\steamapps", "\\wechat files", "\\tencent files"]

SPECIAL_CLEAN_TARGETS = {
    "浏览器缓存": [r"AppData\\Local\\Google\\Chrome\\User Data\\.*\\Cache$", r"AppData\\Local\\Google\\Chrome\\User Data\\.*\\Code Cache$", r"AppData\\Local\\Google\\Chrome\\User Data\\.*\\GPUCache$", r"AppData\\Local\\Microsoft\\Edge\\User Data\\.*\\Cache$", r"AppData\\Local\\Microsoft\\Edge\\User Data\\.*\\Code Cache$", r"AppData\\Local\\Microsoft\\Edge\\User Data\\.*\\GPUCache$", r"AppData\\Local\\Mozilla\\Firefox\\Profiles\\.*\\cache2$"],
    "Steam 缓存": [r"Steam\\htmlcache$", r"Steam\\appcache$", r"Steam\\logs$", r"Steam\\config\\htmlcache$"],
    "显卡 Shader 缓存": [r"AMD\\DxCache$", r"AMD\\DxcCache$", r"AMD\\GLCache$", r"NVIDIA\\DXCache$", r"NVIDIA\\GLCache$", r"NVIDIA Corporation\\NV_Cache$", r"Intel\\.*Cache$"],
    "Windows 临时文件": [r"AppData\\Local\\Temp$", r"Windows\\Temp$"],
    "开发缓存 npm / pip": [r"npm-cache$", r"pip\\Cache$", r"\.cache\\pip$"],
    "游戏启动器缓存": [r"EA Desktop\\.*Cache$", r"EpicGamesLauncher\\Saved\\webcache.*$", r"Battle.net\\Cache$", r"Ubisoft Game Launcher\\cache$", r"Steam\\htmlcache$"],
    "缩略图和日志": [r"ThumbCache.*$", r"CrashDumps$", r"logs$", r"Logs$"]
}

def cls(): os.system("cls")
def line(n=90): return "=" * n
def center(s, n=90): return s.center(n)
def pause(): input("\n按回车返回...")

def write_log(msg):
    print(msg)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(msg + "\n")
    except Exception: pass

def format_size(size):
    size = float(size)
    for u in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024: return f"{size:.2f} {u}"
        size /= 1024
    return f"{size:.2f} PB"

def set_color(name="green"):
    os.system(f"color {COLORS.get(name, '0A')}")

def load_config():
    if CONFIG_FILE.exists():
        try: return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception: pass
    return {"color": "green"}

def save_config(cfg): CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception: return False

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True, encoding="gbk", errors="ignore")
    except Exception:
        return ""

def get_gpu_info():
    out = run_cmd("wmic path win32_VideoController get name")
    lines = [x.strip() for x in out.splitlines() if x.strip() and x.strip().lower() != "name"]
    return " / ".join(lines) if lines else "未知"

def get_wifi_name():
    out = run_cmd("netsh wlan show interfaces")
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("SSID") and "BSSID" not in s:
            return s.split(":", 1)[1].strip()
    return "未连接或未检测到"

def get_ip_info():
    try:
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        return host, ip
    except Exception:
        return "未知", "未知"

def show_system_info():
    host, ip = get_ip_info()
    write_log("[电脑信息]")
    write_log(f"电脑用户名：{getpass.getuser()}")
    write_log(f"用户目录：{USER_DIR}")
    write_log(f"计算机名：{host}")
    write_log(f"本机 IP：{ip}")
    write_log(f"系统版本：{platform.platform()}")
    write_log(f"显卡信息：{get_gpu_info()}")
    write_log(f"当前 WiFi：{get_wifi_name()}")
    write_log("WiFi 密码：不显示。涉及网络凭据安全，建议在 Windows 设置或路由器后台自行查看。")
    write_log(f"管理员权限：{'是' if is_admin() else '否'}")
    write_log(f"日志文件：{LOG_FILE}")

def get_disk_info(path):
    try:
        u = shutil.disk_usage(path.anchor or path)
        return u.total, u.used, u.free
    except Exception: return 0,0,0

def list_drives():
    return [Path(f"{c}:\\") for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if Path(f"{c}:\\").exists()]

def show_drives():
    write_log("\n[磁盘信息]")
    for d in list_drives():
        total, used, free = get_disk_info(d)
        write_log(f"{str(d):<5} 总容量 {format_size(total):>10} | 已用 {format_size(used):>10} | 剩余 {format_size(free):>10}")

def norm(p): return str(p).lower().replace("/", "\\")
def risk(p):
    t = norm(p)
    if any(k in t for k in HIGH_RISK_KEYWORDS): return "high"
    if any(k in t for k in MEDIUM_RISK_KEYWORDS): return "medium"
    return "low"
def is_cache(p): return any(k in norm(p) for k in SAFE_CACHE_KEYWORDS)

def consequence(p):
    t = norm(p)
    if "\\windows" in t or "\\system32" in t: return "可能导致 Windows 损坏、更新失败、蓝屏或无法启动。"
    if "\\program files" in t: return "可能导致软件无法运行或卸载异常。"
    if "steamapps" in t: return "可能删除 Steam 游戏本体，需要重新下载。"
    if "wechat files" in t: return "可能删除微信文件、图片、视频和接收文件。"
    if is_cache(p): return "通常是缓存，可重建；清理后软件首次启动可能变慢。"
    return "无法准确判断用途，建议谨慎。"

def folder_size(path):
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            for f in files:
                try: total += (Path(root)/f).stat().st_size
                except Exception: pass
    except Exception: pass
    return total

def file_type(p):
    if p.is_dir(): return "文件夹"
    ext = p.suffix.lower()
    mapping = {".exe":"应用程序", ".msi":"安装包", ".zip":"压缩包", ".rar":"压缩包", ".7z":"压缩包", ".mp4":"视频", ".mkv":"视频", ".avi":"视频", ".jpg":"图片", ".png":"图片", ".webp":"图片", ".gif":"图片", ".txt":"文本", ".doc":"Word", ".docx":"Word", ".xls":"Excel", ".xlsx":"Excel", ".pdf":"PDF", ".py":"Python", ".js":"JavaScript", ".json":"JSON"}
    return mapping.get(ext, ext[1:].upper() if ext else "无扩展名文件")

def dates(p):
    try:
        st = p.stat()
        return datetime.fromtimestamp(st.st_ctime).strftime("%Y-%m-%d"), datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d")
    except Exception: return "未知", "未知"

def progress(text="处理中", steps=20, delay=0.02):
    print(text)
    for i in range(steps+1):
        bar = "█"*i + "░"*(steps-i)
        print(f"\r[{bar}] {int(i/steps*100)}%", end="")
        time.sleep(delay)
    print()

def choose_path():
    drives = list_drives()
    write_log("\n请选择位置：")
    for i,d in enumerate(drives,1):
        total, used, free = get_disk_info(d)
        write_log(f"[{i}] {d} 剩余 {format_size(free)} / 总容量 {format_size(total)}")
    write_log("[0] 手动输入路径")
    c = input("请输入序号：").strip()
    if c == "0": p = Path(input("路径：").strip().strip('"'))
    else:
        try: p = drives[int(c)-1]
        except Exception: write_log("输入无效。"); return None
    if not p.exists(): write_log("路径不存在。"); return None
    return p

def scan_items(target, recursive=False, top_n=80):
    progress("正在扫描，请稍等...", 25, 0.01)
    folders, files = [], []
    iterator = target.rglob("*") if recursive else target.iterdir()
    for item in iterator:
        try:
            if item.is_dir():
                size = folder_size(item)
                created, modified = dates(item)
                folders.append({"path":item,"size":size,"risk":risk(item),"type":"文件夹","created":created,"modified":modified,"cache":is_cache(item)})
            elif item.is_file():
                size = item.stat().st_size
                created, modified = dates(item)
                files.append({"path":item,"size":size,"risk":risk(item),"type":file_type(item),"created":created,"modified":modified,"cache":is_cache(item)})
        except Exception: pass
    folders.sort(key=lambda x:x["size"], reverse=True); files.sort(key=lambda x:x["size"], reverse=True)
    return folders[:top_n], files[:top_n]

def display_scan(folders, files):
    results = []
    write_log(line(120)); write_log("[文件夹列表]"); write_log(line(120))
    write_log(f"{'序号':<6}{'大小':>12}  {'风险':<8}{'类型':<10}{'创建日期':<12}{'修改日期':<12} 路径")
    for it in folders:
        results.append(it); write_log(f"[{len(results):<3}] {format_size(it['size']):>12}  {it['risk']:<8}{it['type']:<10}{it['created']:<12}{it['modified']:<12} {it['path']}")
    write_log(line(120)); write_log("[文件列表]"); write_log(line(120))
    for it in files:
        results.append(it); write_log(f"[{len(results):<3}] {format_size(it['size']):>12}  {it['risk']:<8}{it['type']:<10}{it['created']:<12}{it['modified']:<12} {it['path']}")
    write_log(line(120))
    return results

def parse_indexes(s, maxn):
    s = s.strip().replace("，", ",")
    if s.lower() in ("all","a","全部"): return list(range(1,maxn+1))
    out=set()
    for part in s.split(','):
        part=part.strip()
        if '-' in part:
            try:
                a,b=map(int,part.split('-',1)); out.update(i for i in range(a,b+1) if 1<=i<=maxn)
            except Exception: pass
        else:
            try:
                i=int(part); 
                if 1<=i<=maxn: out.add(i)
            except Exception: pass
    return sorted(out)

def delete_contents(p):
    deleted=failed=count=0
    if p.is_file():
        try: deleted=p.stat().st_size; p.unlink(); return deleted,0,1
        except Exception as e: write_log(f"删除失败：{p} -> {e}"); return 0,1,0
    for item in list(p.iterdir()):
        try:
            if item.is_dir(): s=folder_size(item); shutil.rmtree(item); deleted+=s; count+=1
            else: s=item.stat().st_size; item.unlink(); deleted+=s; count+=1
        except Exception as e: failed+=1; write_log(f"删除失败：{item} -> {e}")
    return deleted,failed,count



def open_item_location(item):
    """打开扫描结果对应的位置。文件夹直接打开，文件则打开所在目录并尝试选中文件。"""
    try:
        p = Path(item["path"])
        if p.is_dir():
            os.startfile(p)
            write_log(f"已打开目录：{p}")
        elif p.is_file():
            # Windows Explorer 支持 /select, 选中文件
            subprocess.Popen(f'explorer /select,"{p}"', shell=True)
            write_log(f"已打开文件所在目录：{p.parent}")
        else:
            parent = p.parent if p.parent.exists() else USER_DIR
            os.startfile(parent)
            write_log(f"目标不存在，已打开上级目录：{parent}")
    except Exception as e:
        write_log(f"打开失败：{e}")

def operate_results(results):
    while True:
        write_log("\n操作：")
        write_log("  输入序号      清理项目，例如：1 或 1,3,5 或 1-5")
        write_log("  S序号         进入并扫描该文件夹，例如：S1")
        write_log("  O序号         打开该项目所在目录，例如：O1")
        write_log("  B             返回主菜单")
        write_log("  N             不删除，返回")
        raw=input("请输入：").strip()
        if raw.lower() in ("b","n",""): return
        if raw.lower().startswith("o"):
            try:
                idx=int(raw[1:]); item=results[idx-1]
                open_item_location(item)
            except Exception:
                write_log("输入无效。示例：O1")
            continue
        if raw.lower().startswith("s"):
            try:
                idx=int(raw[1:]); item=results[idx-1]
                if Path(item["path"]).is_dir():
                    f1,f2=scan_items(Path(item["path"]), recursive=False); new=display_scan(f1,f2); operate_results(new)
                else: write_log("该项目不是文件夹，不能进入扫描。你可以使用 O序号 打开所在目录。")
            except Exception: write_log("输入无效。示例：S1")
            continue
        idxs=parse_indexes(raw,len(results))
        if not idxs: write_log("没有有效序号。继续。 "); continue
        selected=[results[i-1] for i in idxs]
        write_log(f"已选择 {len(selected)} 项，预计体积：{format_size(sum(x['size'] for x in selected))}")
        for it in selected:
            p=Path(it["path"]); r=it["risk"]
            write_log(f"\n路径：{p}\n风险：{r}\n后果：{consequence(p)}")
            if r=="high": write_log("高风险项目禁止直接清理。已跳过。 "); continue
            if r=="medium":
                if input("中风险项目，确认请输入 YES：").strip()!="YES": write_log("已跳过。 "); continue
            elif input("确认清理？(y/n): ").strip().lower()!="y": write_log("已跳过。 "); continue
            d,fail,c=delete_contents(p)
            write_log(f"完成：释放 {format_size(d)}，删除条目 {c}，失败 {fail}")

def scan_big():
    p=choose_path();
    if not p: return
    f1,f2=scan_items(p, recursive=False); results=display_scan(f1,f2); operate_results(results); pause()

def scan_detail():
    p=choose_path();
    if not p: return
    rec=input("是否递归扫描所有子目录？较慢 (y/n): ").strip().lower()=="y"
    f1,f2=scan_items(p, recursive=rec); results=display_scan(f1,f2); operate_results(results); pause()

def find_cache(p):
    res=[]; progress("正在扫描缓存目录...",25,0.01)
    for root, dirs, files in os.walk(p):
        path=Path(root); r=risk(path)
        if r=="high" and not is_cache(path): dirs[:]=[]; continue
        if is_cache(path):
            s=folder_size(path)
            if s>=10*1024*1024: res.append({"path":path,"size":s,"risk":r,"type":"缓存目录","created":dates(path)[0],"modified":dates(path)[1],"cache":True})
            dirs[:]=[]
    res.sort(key=lambda x:x["size"], reverse=True)
    return res

def cache_scan(clean=False):
    p=choose_path();
    if not p: return
    res=find_cache(p); display_scan(res, [])
    if clean: operate_results(res)
    pause()

def pattern_matches(p, patterns):
    t=str(p).replace('/','\\')
    return any(re.search(x,t,re.I) for x in patterns)

def special_clean():
    names=list(SPECIAL_CLEAN_TARGETS.keys())
    while True:
        cls(); write_log(line()); write_log(center("常用缓存专项清理")); write_log(line())
        for i,n in enumerate(names,1): write_log(f"[{i}] {n}")
        write_log("[0] 返回")
        c=input("请选择：").strip()
        if c=="0": return
        try: name=names[int(c)-1]
        except Exception: continue
        roots=[USER_DIR] if input("扫描范围：[1] 当前用户目录 [2] 所有盘符：").strip()!="2" else list_drives()
        res=[]
        for root in roots:
            for cur,dirs,files in os.walk(root):
                p=Path(cur)
                if pattern_matches(p,SPECIAL_CLEAN_TARGETS[name]):
                    s=folder_size(p)
                    if s>10*1024*1024: res.append({"path":p,"size":s,"risk":risk(p),"type":name,"created":dates(p)[0],"modified":dates(p)[1],"cache":True})
                    dirs[:]=[]
        res.sort(key=lambda x:x["size"], reverse=True)
        display_scan(res,[]); operate_results(res); pause()

def find_empty_dirs(target):
    empties=[]; progress("正在查找空文件夹...",20,0.01)
    for root, dirs, files in os.walk(target, topdown=False):
        p=Path(root)
        try:
            if not any(p.iterdir()): empties.append({"path":p,"size":0,"risk":risk(p),"type":"空文件夹","created":dates(p)[0],"modified":dates(p)[1],"cache":False})
        except Exception: pass
    return empties

def delete_empty_dirs():
    p=choose_path();
    if not p: return
    res=find_empty_dirs(p); display_scan(res,[])
    if not res: pause(); return
    if input("是否一键删除所有低/中风险空文件夹？(y/n): ").strip().lower()=="y":
        cnt=fail=0
        for it in res:
            if it["risk"]=="high": continue
            try: Path(it["path"]).rmdir(); cnt+=1
            except Exception as e: fail+=1; write_log(f"删除失败：{it['path']} -> {e}")
        write_log(f"完成：删除空文件夹 {cnt} 个，失败 {fail} 个")
    pause()

def reg_clean():
    write_log("注册表清理为保守模式：仅检测无效卸载项。清理前建议创建系统还原点。")
    if input("是否继续？(y/n): ").strip().lower()!='y': return
    backup=LOG_DIR / f"registry_backup_hint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    backup.write_text("注册表清理前建议手动创建系统还原点。本工具只做保守清理。", encoding="utf-8")
    write_log(f"已生成提示文件：{backup}")
    pause()

def uninstall_manager():
    roots=[(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),(winreg.HKEY_CURRENT_USER,r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")]
    apps=[]
    for hive,keypath in roots:
        try:
            key=winreg.OpenKey(hive,keypath)
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    sub=winreg.EnumKey(key,i); sk=winreg.OpenKey(key,sub)
                    name=winreg.QueryValueEx(sk,"DisplayName")[0]
                    try: pub=winreg.QueryValueEx(sk,"Publisher")[0]
                    except Exception: pub=""
                    try: un=winreg.QueryValueEx(sk,"UninstallString")[0]
                    except Exception: un=""
                    if name and un: apps.append({"name":name,"publisher":pub,"uninstall":un})
                except Exception: pass
        except Exception: pass
    apps.sort(key=lambda x:x['name'].lower())
    kw=input("搜索软件名/厂商，直接回车显示前80个：").strip().lower()
    shown=[a for a in apps if kw in (a['name']+' '+a['publisher']).lower()][:80]
    for i,a in enumerate(shown,1): write_log(f"[{i}] {a['name']} | {a['publisher']}")
    c=input("输入序号卸载，B返回：").strip()
    if c.lower()=='b': return
    try: a=shown[int(c)-1]
    except Exception: return
    write_log(f"即将卸载：{a['name']}\n命令：{a['uninstall']}")
    if input("确认卸载？(y/n): ").strip().lower()=='y': subprocess.Popen(a['uninstall'], shell=True)
    pause()

def settings():
    cfg=load_config();
    write_log("颜色：[1] green [2] white [3] blue [4] red [5] yellow [6] purple")
    c=input("选择：").strip(); names=list(COLORS.keys())
    try: cfg['color']=names[int(c)-1]; save_config(cfg); set_color(cfg['color'])
    except Exception: write_log("无效选择。")
    pause()

def export_summary():
    out=LOG_DIR/f"disk_cleaner_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps({"app":APP_TITLE,"version":APP_VERSION,"author":AUTHOR,"user":getpass.getuser(),"log":str(LOG_FILE)}, ensure_ascii=False, indent=2), encoding="utf-8")
    write_log(f"已导出：{out}"); pause()

def header():
    cls(); print(line()); print(center(APP_TITLE)); print(center(APP_SUBTITLE)); print(center(f"Version {APP_VERSION}")); print(center(f"作者：{AUTHOR}")); print(line())

def menu():
    header(); show_system_info(); show_drives(); print(line())
    print("[1] 扫描磁盘大文件夹 / 大文件")
    print("[2] 扫描缓存文件")
    print("[3] 清理缓存文件（序号选择）")
    print("[4] 常用缓存专项清理")
    print("[5] 手动精准清理（扫描后输入序号）")
    print("[6] 扫描文件夹和文件明细（含类型/日期）")
    print("[7] 删除空文件夹")
    print("[8] 注册表清理（保守模式）")
    print("[9] 软件卸载管理")
    print("[10] 设置")
    print("[11] 导出工具摘要")
    print("[12] 打开日志文件夹")
    print("[0] 退出")
    print(line())

def main():
    cfg=load_config(); set_color(cfg.get('color','green'))
    while True:
        menu(); c=input("请输入选项：").strip()
        if c=='1': scan_big()
        elif c=='2': cache_scan(False)
        elif c=='3': cache_scan(True)
        elif c=='4': special_clean()
        elif c=='5': scan_big()
        elif c=='6': scan_detail()
        elif c=='7': delete_empty_dirs()
        elif c=='8': reg_clean()
        elif c=='9': uninstall_manager()
        elif c=='10': settings()
        elif c=='11': export_summary()
        elif c=='12': os.startfile(LOG_DIR)
        elif c=='0': break
        else: write_log("输入无效。")

if __name__ == "__main__": main()
