
# -*- coding: utf-8 -*-
import os, json, subprocess
from pathlib import Path
from disk_cleaner_core_v42 import *
LOG_FILE=log_file("cmd_cleanup"); LAST_RESULTS=[]
def w(m=""): print(m); write_text_log(LOG_FILE,m)
def line(n=100): return "="*n
def progress(c,t,prefix="扫描中"):
    t=max(t,1); r=min(c/t,1); width=35; done=int(width*r)
    print(f"\r{prefix}: [{'█'*done}{'-'*(width-done)}] {c}/{t}",end="",flush=True)
    if c>=t: print()
def pcb(c,t,text=""): progress(c,t)
def header():
    os.system("title 磁盘清理 v4.2 CMD"); os.system("color 0A")
    w("\n"+line()); w("磁盘清理 v4.2 CMD".center(100)); w(f"作者：{AUTHOR} | QQ：{QQ} | 微信：{WECHAT}".center(100)); w(line())
def sysinfo():
    i=system_info(); w("[电脑信息]"); w(f"用户：{i['username']} | 电脑：{i['computer']} | IP：{i['ip']} | WiFi：{i['wifi']}"); w(f"系统：{i['system']}"); w(f"显卡：{i['gpu']}"); w(f"日志：{LOG_FILE}")
    w("\n[磁盘信息]")
    for d in drives(): w(f"{d:<6} {disk_usage_text(d)}")
def choose():
    ds=drives(); w("\n请选择路径：")
    for i,d in enumerate(ds,1): w(f"[{i}] {d}  {disk_usage_text(d)}")
    w("[0] 手动输入路径"); s=input("请输入序号：").strip()
    if s=="0": p=Path(input("请输入路径：").strip().strip('"'))
    else:
        try:p=ds[int(s)-1]
        except Exception: w("输入无效"); return None
    if not p.exists() or not p.is_dir(): w("路径不存在或不是文件夹"); return None
    return p
def show(results):
    global LAST_RESULTS
    folders=[x for x in results if x["kind"]=="文件夹"]; files=[x for x in results if x["kind"]=="文件"]; LAST_RESULTS=folders+files
    w(line(140))
    if folders:
        w("[文件夹]"); w(f"{'序号':<6}{'大小':>12}  {'风险':<8}{'类型':<10}{'创建日期':<20}{'修改日期':<20} 路径")
        for i,it in enumerate(folders,1): w(f"[{i:<3}] {it['size_text']:>12}  {it['risk']:<8}{it['type']:<10}{it['created']:<20}{it['modified']:<20} {it['path']}")
    if files:
        off=len(folders); w("\n[文件]"); w(f"{'序号':<6}{'大小':>12}  {'风险':<8}{'类型':<10}{'创建日期':<20}{'修改日期':<20} 路径")
        for j,it in enumerate(files,1): w(f"[{off+j:<3}] {it['size_text']:>12}  {it['risk']:<8}{it['type']:<10}{it['created']:<20}{it['modified']:<20} {it['path']}")
    w(line(140)); w(f"合计：{format_size(sum(x['size'] for x in LAST_RESULTS))} | 数量：{len(LAST_RESULTS)}")
    w("操作：O序号 打开 | S序号 继续扫描 | D序号 删除 | C 清理模式 | E 导出CSV | B 返回"); w(line(140))
def parse_idx(text,n):
    text=text.strip().replace("，",",")
    if text.lower() in ["all","a","全部"]: return list(range(1,n+1))
    out=set()
    for part in text.split(","):
        part=part.strip()
        if "-" in part:
            try:
                a,b=map(int,part.split("-",1))
                for i in range(a,b+1):
                    if 1<=i<=n: out.add(i)
            except: pass
        else:
            try:
                i=int(part)
                if 1<=i<=n: out.add(i)
            except: pass
    return sorted(out)
def openp(p):
    p=Path(p)
    try:
        if p.is_dir(): os.startfile(p)
        else: subprocess.Popen(f'explorer /select,"{p}"')
    except Exception as e: w(f"打开失败：{e}")
def clean(items,mode="manual"):
    if not items: w("没有可清理项目"); return
    if mode=="low": selected=[x for x in items if x["risk_raw"]=="low"]
    elif mode=="medium": selected=[x for x in items if x["risk_raw"] in ("low","medium")]
    else:
        idx=parse_idx(input("请输入序号，如 1,3,5 或 all："),len(items)); selected=[items[i-1] for i in idx]
    if not selected: w("没有选中项目"); return
    w(f"预计清理：{len(selected)} 项，{format_size(sum(x['size'] for x in selected))}")
    if input("输入 CLEAN 确认：").strip()!="CLEAN": w("已取消"); return
    recycle=input("删除方式：[1] 放入回收站（推荐） [2] 永久删除：").strip()!="2"
    before=disk_usage(selected[0]["path"])["free"]; deleted=failed=0
    for it in selected:
        if it["risk_raw"]=="high": w(f"跳过高风险：{it['path']}"); continue
        if mode=="manual": w(f"路径：{it['path']}\n风险：{it['risk']}\n后果：{consequence(it['path'])}")
        res=delete_item(it["path"],recycle=recycle,clear_contents=True); deleted+=res["deleted"]; failed+=res["failed"]; w(f"完成：{format_size(res['deleted'])} | {it['path']}")
    after=disk_usage(selected[0]["path"])["free"]; w(line()); w(f"本次释放：{format_size(deleted)}"); w(f"清理前剩余：{format_size(before)}"); w(f"清理后剩余：{format_size(after)}"); w(f"失败：{failed}"); w(line())
def loop():
    while True:
        cmd=input("请输入操作：").strip()
        if not cmd: continue
        if cmd.lower()=="b": return
        if cmd.lower()=="e":
            out=LOG_DIR/f"cmd_results_{timestamp()}.csv"; export_csv(LAST_RESULTS,out); w(f"已导出：{out}"); continue
        if cmd.lower()=="c":
            w("[1] 手动序号清理\n[2] 批量清理低风险\n[3] 激进清理低/中风险\n[0] 返回"); m=input("请选择：").strip()
            if m=="1": clean(LAST_RESULTS,"manual")
            elif m=="2": clean(LAST_RESULTS,"low")
            elif m=="3": clean(LAST_RESULTS,"medium")
            return
        try: prefix=cmd[0].lower(); it=LAST_RESULTS[int(cmd[1:])-1]
        except Exception: w("输入无效"); continue
        if prefix=="o": openp(it["path"])
        elif prefix=="s":
            p=Path(it["path"])
            if p.is_dir(): show(scan_large_items(p,progress_cb=pcb))
            else: w("文件不能继续扫描")
        elif prefix=="d": clean([it],"manual")
def downloads():
    p,summary,details=analyze_downloads(); w(f"\n下载目录：{p}"); w(line())
    for c,d in summary.items(): w(f"{c:<8} 数量：{d['count']:<6} 体积：{format_size(d['size'])}")
    w(line()); show(details[:100]); loop()
def duplicates():
    p=choose()
    if p: show(find_duplicate_files(p,progress_cb=pcb)); loop()
def emptydirs():
    p=choose()
    if not p: return
    found=scan_empty_dirs(p,progress_cb=pcb)
    if not found: w("没有发现空文件夹"); return
    for i,d in enumerate(found,1): w(f"[{i}] {d}")
    if input(f"共 {len(found)} 个，是否删除？(y/n): ").lower()=="y":
        ok,fail=delete_empty_dirs(found,recycle=True); w(f"成功：{ok} 失败：{fail}")
def main():
    while True:
        header(); sysinfo(); w(line()); w("[1] 扫描大文件/文件夹\n[2] 扫描缓存\n[3] Top 100 大文件\n[4] 下载目录分析\n[5] 重复文件检测\n[6] 删除空文件夹\n[7] 打开日志目录\n[0] 退出"); w(line())
        c=input("请输入选项：").strip()
        if c=="1":
            p=choose(); 
            if p: show(scan_large_items(p,progress_cb=pcb)); loop()
        elif c=="2":
            p=choose()
            if p: show(scan_cache_dirs(p,progress_cb=pcb)); loop()
        elif c=="3":
            p=choose()
            if p: show(scan_top_files(p,progress_cb=pcb)); loop()
        elif c=="4": downloads()
        elif c=="5": duplicates()
        elif c=="6": emptydirs()
        elif c=="7": os.startfile(LOG_DIR)
        elif c=="0": break
        else: w("输入无效")
        input("按回车继续...")
if __name__=="__main__": main()
