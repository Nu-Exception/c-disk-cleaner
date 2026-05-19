
# -*- coding: utf-8 -*-
import os, re, csv, json, time, shutil, socket, getpass, hashlib, platform, subprocess
from pathlib import Path
from datetime import datetime

APP_NAME="磁盘清理"; APP_VERSION="4.2"; AUTHOR="CS"; QQ="476199719"; WECHAT="Entropy4761"
USER_DIR=Path.home(); LOG_DIR=USER_DIR/"清理日志"; LOG_DIR.mkdir(parents=True, exist_ok=True)
MIN_SCAN_SIZE=100*1024*1024; TOP_FILE_MIN_SIZE=100*1024*1024
SAFE_CACHE_KEYWORDS=["cache","caches","code cache","gpucache","shadercache","dxcache","dxccache","glcache","nv_cache","htmlcache","browsercache","webcache","npm-cache","pip cache","temp","tmp","logs","crashdumps","thumbnail"]
HIGH_RISK_KEYWORDS=["\\windows","\\program files","\\program files (x86)","\\programdata","\\system32","\\syswow64","\\drivers","\\boot","\\efi","\\recovery","\\system volume information","\\$recycle.bin"]
MEDIUM_RISK_KEYWORDS=["\\users","\\desktop","\\documents","\\downloads","\\pictures","\\videos","\\music","\\appdata\\roaming","\\appdata\\locallow","\\steamapps","\\wechat files","\\tencent files"]
FILE_TYPE_MAP={".exe":"应用程序",".msi":"安装包",".zip":"压缩包",".rar":"压缩包",".7z":"压缩包",".iso":"镜像文件",".mp4":"视频",".mkv":"视频",".avi":"视频",".mov":"视频",".jpg":"图片",".jpeg":"图片",".png":"图片",".gif":"图片",".webp":"图片",".doc":"Word",".docx":"Word",".xls":"Excel",".xlsx":"Excel",".ppt":"PPT",".pptx":"PPT",".pdf":"PDF",".txt":"文本",".log":"日志",".py":"Python",".js":"JavaScript",".json":"JSON",".md":"Markdown",".mp3":"音频",".wav":"音频",".flac":"音频"}
DOWNLOAD_CATEGORIES={"视频":[".mp4",".mkv",".avi",".mov",".flv",".wmv"],"图片":[".jpg",".jpeg",".png",".gif",".webp",".bmp"],"压缩包":[".zip",".rar",".7z",".tar",".gz"],"安装包":[".exe",".msi"],"文档":[".doc",".docx",".xls",".xlsx",".ppt",".pptx",".pdf",".txt",".md"],"音频":[".mp3",".wav",".flac"],"镜像":[".iso"],"代码":[".py",".js",".json",".html",".css",".java",".cpp",".c",".cs"]}
def timestamp(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def log_file(prefix="cleanup"): return LOG_DIR/f"{prefix}_{timestamp()}.txt"
def write_text_log(path,msg):
    try:
        with open(path,"a",encoding="utf-8") as f: f.write(str(msg)+"\n")
    except Exception: pass
def format_size(size):
    try: size=float(size)
    except Exception: return "0 B"
    for u in ["B","KB","MB","GB","TB"]:
        if size<1024: return f"{size:.2f} {u}"
        size/=1024
    return f"{size:.2f} PB"
def format_time(ts):
    try: return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception: return "-"
def norm(p): return str(p).lower().replace("/","\\")
def get_risk_raw(p):
    t=norm(p)
    if any(k in t for k in HIGH_RISK_KEYWORDS): return "high"
    if any(k in t for k in MEDIUM_RISK_KEYWORDS): return "medium"
    return "low"
def get_risk_cn(p): return {"low":"低风险","medium":"中风险","high":"高风险"}[get_risk_raw(p)]
def is_cache_like(p): return any(k in norm(p) for k in SAFE_CACHE_KEYWORDS)
def file_type(p):
    p=Path(p)
    if p.is_dir(): return "文件夹"
    return FILE_TYPE_MAP.get(p.suffix.lower(),p.suffix.lower().replace(".","").upper() or "文件")
def get_size(p):
    p=Path(p)
    if not p.exists(): return 0
    if p.is_file():
        try: return p.stat().st_size
        except Exception: return 0
    total=0
    for root,dirs,files in os.walk(p):
        for n in files:
            try: total+=(Path(root)/n).stat().st_size
            except Exception: pass
    return total
def item_info(p,size=None):
    p=Path(p)
    try: st=p.stat()
    except Exception: st=None
    if size is None: size=get_size(p)
    return {"path":str(p),"name":p.name,"size":size,"size_text":format_size(size),"kind":"文件夹" if p.is_dir() else "文件","type":file_type(p),"risk_raw":get_risk_raw(p),"risk":get_risk_cn(p),"cache":"是" if is_cache_like(p) else "否","created":format_time(st.st_ctime) if st else "-","modified":format_time(st.st_mtime) if st else "-"}
def consequence(p):
    t=norm(p)
    if "\\windows" in t or "\\system32" in t: return "可能导致 Windows 系统损坏、更新失败、蓝屏或无法启动。"
    if "\\program files" in t: return "可能导致软件无法运行或卸载异常。"
    if "\\downloads" in t: return "可能删除下载内容，包括安装包、压缩包、视频等。"
    if "\\desktop" in t: return "可能删除桌面文件。"
    if "wechat files" in t: return "可能删除微信聊天文件、图片、视频和接收文件。"
    if "tencent files" in t: return "可能删除 QQ 文件、图片、视频和接收文件。"
    if "steamapps" in t: return "可能删除 Steam 游戏本体，需要重新下载。"
    if is_cache_like(p): return "通常是缓存，可重建；清理后软件首次启动可能变慢。"
    return "无法准确判断用途，建议打开目录确认后再处理。"
def drives():
    return [Path(f"{c}:\\") for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if Path(f"{c}:\\").exists()]
def disk_usage(p):
    try:
        u=shutil.disk_usage(Path(p).anchor or p); return {"total":u.total,"used":u.used,"free":u.free}
    except Exception: return {"total":0,"used":0,"free":0}
def disk_usage_text(p):
    u=disk_usage(p); return f"总容量 {format_size(u['total'])} | 已用 {format_size(u['used'])} | 剩余 {format_size(u['free'])}"
def ip_info():
    try: return socket.gethostbyname(socket.gethostname())
    except Exception: return "-"
def wifi_name():
    try:
        out=subprocess.check_output("netsh wlan show interfaces",shell=True,text=True,encoding="gbk",errors="ignore")
        for l in out.splitlines():
            if "SSID" in l and "BSSID" not in l: return l.split(":",1)[1].strip()
    except Exception: pass
    return "-"
def gpu_info():
    try:
        out=subprocess.check_output("wmic path win32_VideoController get name",shell=True,text=True,encoding="gbk",errors="ignore")
        ns=[x.strip() for x in out.splitlines() if x.strip() and x.strip().lower()!="name"]
        return " / ".join(ns) if ns else "-"
    except Exception: return "-"
def system_info():
    return {"user_dir":str(USER_DIR),"username":getpass.getuser(),"computer":platform.node(),"system":platform.platform(),"ip":ip_info(),"wifi":wifi_name(),"gpu":gpu_info()}
def scan_large_items(target,min_size=MIN_SCAN_SIZE,recursive=False,progress_cb=None):
    target=Path(target); results=[]
    if recursive:
        items=[]
        for root,dirs,files in os.walk(target):
            items += [Path(root)/d for d in dirs] + [Path(root)/f for f in files]
    else:
        try: items=list(target.iterdir())
        except Exception: items=[]
    total=max(len(items),1)
    for i,p in enumerate(items,1):
        try:
            s=get_size(p)
            if s>=min_size: results.append(item_info(p,s))
        except Exception: pass
        if progress_cb: progress_cb(i,total,str(p))
    return sorted(results,key=lambda x:(x["kind"]!="文件夹",-x["size"]))
def scan_cache_dirs(target,min_size=MIN_SCAN_SIZE,progress_cb=None):
    target=Path(target); cands=[]
    for root,dirs,files in os.walk(target):
        p=Path(root)
        if get_risk_raw(p)=="high" and not is_cache_like(p): dirs[:]=[]; continue
        if is_cache_like(p): cands.append(p); dirs[:]=[]
    results=[]; total=max(len(cands),1)
    for i,p in enumerate(cands,1):
        s=get_size(p)
        if s>=min_size: results.append(item_info(p,s))
        if progress_cb: progress_cb(i,total,str(p))
    return sorted(results,key=lambda x:x["size"],reverse=True)
def scan_top_files(target,limit=100,min_size=TOP_FILE_MIN_SIZE,progress_cb=None):
    target=Path(target); files=[]; walked=0
    for root,dirs,names in os.walk(target):
        p=Path(root)
        if get_risk_raw(p)=="high" and p!=target: dirs[:]=[]; continue
        for n in names:
            fp=Path(root)/n
            try:
                s=fp.stat().st_size
                if s>=min_size: files.append(item_info(fp,s))
            except Exception: pass
        walked+=1
        if progress_cb and walked%20==0: progress_cb(walked,walked+1,str(p))
    return sorted(files,key=lambda x:x["size"],reverse=True)[:limit]
def analyze_downloads(download_path=None):
    if download_path is None:
        download_path=USER_DIR/"Downloads"
        if not download_path.exists(): download_path=USER_DIR/"下载"
    download_path=Path(download_path)
    summary={k:{"count":0,"size":0} for k in DOWNLOAD_CATEGORIES}; summary["其他"]={"count":0,"size":0}; details=[]
    if not download_path.exists(): return download_path,summary,details
    for root,dirs,files in os.walk(download_path):
        for n in files:
            fp=Path(root)/n
            try: s=fp.stat().st_size
            except Exception: continue
            ext=fp.suffix.lower(); cat="其他"
            for c,exts in DOWNLOAD_CATEGORIES.items():
                if ext in exts: cat=c; break
            summary[cat]["count"]+=1; summary[cat]["size"]+=s; details.append(item_info(fp,s))
    return download_path,summary,sorted(details,key=lambda x:x["size"],reverse=True)
def scan_empty_dirs(target,progress_cb=None):
    found=[]; walked=0; target=Path(target)
    for root,dirs,files in os.walk(target,topdown=False):
        p=Path(root)
        try:
            if p!=target and not any(p.iterdir()): found.append(str(p))
        except Exception: pass
        walked+=1
        if progress_cb and walked%30==0: progress_cb(walked,walked+1,str(p))
    return found
def try_send_to_trash(path):
    p=Path(path)
    try:
        from send2trash import send2trash
        send2trash(str(p)); return True,""
    except Exception: pass
    try:
        ps="$shell=New-Object -ComObject Shell.Application; $folder=$shell.Namespace(10); $folder.MoveHere('"+str(p).replace("'","''")+"')"
        subprocess.run(["powershell","-NoProfile","-Command",ps],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return True,""
    except Exception as e: return False,str(e)
def permanent_delete(path):
    p=Path(path)
    if not p.exists(): return 0,0,0
    if p.is_file() or p.is_symlink():
        try: s=p.stat().st_size; p.unlink(); return s,0,1
        except Exception: return 0,1,0
    deleted=failed=count=0
    try: items=list(p.iterdir())
    except Exception: return 0,1,0
    for it in items:
        try:
            if it.is_file() or it.is_symlink():
                s=it.stat().st_size; it.unlink(); deleted+=s; count+=1
            else:
                s=get_size(it); shutil.rmtree(it); deleted+=s; count+=1
        except Exception: failed+=1
    return deleted,failed,count
def delete_item(path,recycle=True,clear_contents=True):
    p=Path(path)
    if not p.exists(): return {"deleted":0,"failed":0,"count":0,"mode":"missing"}
    if get_risk_raw(p)=="high": return {"deleted":0,"failed":1,"count":0,"mode":"blocked_high_risk"}
    targets=[p] if (p.is_file() or not clear_contents) else list(p.iterdir())
    deleted=failed=count=0
    if recycle:
        for t in targets:
            s=get_size(t); ok,err=try_send_to_trash(t)
            if ok: deleted+=s; count+=1
            else: failed+=1
        return {"deleted":deleted,"failed":failed,"count":count,"mode":"recycle"}
    for t in targets:
        d,f,c=permanent_delete(t); deleted+=d; failed+=f; count+=c
    return {"deleted":deleted,"failed":failed,"count":count,"mode":"permanent"}
def delete_empty_dirs(empty_dirs,recycle=True):
    ok=fail=0
    for d in empty_dirs:
        try:
            if recycle:
                done,err=try_send_to_trash(d)
                ok += 1 if done else 0; fail += 0 if done else 1
            else:
                Path(d).rmdir(); ok+=1
        except Exception: fail+=1
    return ok,fail
def file_hash(path,chunk_size=1024*1024):
    h=hashlib.md5()
    try:
        with open(path,"rb") as f:
            while True:
                b=f.read(chunk_size)
                if not b: break
                h.update(b)
        return h.hexdigest()
    except Exception: return None
def find_duplicate_files(target,min_size=10*1024*1024,progress_cb=None):
    target=Path(target); by_size={}; walked=0
    for root,dirs,files in os.walk(target):
        p=Path(root)
        if get_risk_raw(p)=="high" and p!=target: dirs[:]=[]; continue
        for n in files:
            fp=Path(root)/n
            try:
                s=fp.stat().st_size
                if s>=min_size: by_size.setdefault(s,[]).append(fp)
            except Exception: pass
        walked+=1
        if progress_cb and walked%20==0: progress_cb(walked,walked+1,str(p))
    groups=[g for g in by_size.values() if len(g)>1]; dups=[]; total=max(len(groups),1)
    for i,g in enumerate(groups,1):
        hashes={}
        for fp in g:
            h=file_hash(fp)
            if h: hashes.setdefault(h,[]).append(fp)
        for h,fs in hashes.items():
            if len(fs)>1:
                for fp in fs:
                    it=item_info(fp); it["dup_hash"]=h; dups.append(it)
        if progress_cb: progress_cb(i,total,"重复文件检测")
    return sorted(dups,key=lambda x:(x.get("dup_hash",""),-x["size"]))
def export_csv(results,out):
    out=Path(out)
    with open(out,"w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f); w.writerow(["类别","类型","大小","字节","风险","缓存","创建日期","修改日期","路径"])
        for it in results: w.writerow([it.get("kind"),it.get("type"),it.get("size_text"),it.get("size"),it.get("risk"),it.get("cache"),it.get("created"),it.get("modified"),it.get("path")])
    return out
