
# -*- coding: utf-8 -*-
import os, subprocess, threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from disk_cleaner_core_v42 import *

class App:
    def __init__(self,root):
        self.root=root; self.root.title("磁盘清理 v4.2"); self.root.geometry("1280x780"); self.root.minsize(1100,680)
        self.results=[]; self.sort_reverse=True; self.path_var=tk.StringVar(value=str(drives()[0]) if drives() else str(USER_DIR)); self.status_var=tk.StringVar(value="就绪"); self.progress_var=tk.DoubleVar(value=0); self.recycle_var=tk.BooleanVar(value=True)
        self.style(); self.ui(); self.home()
    def style(self):
        s=ttk.Style()
        try:s.theme_use("clam")
        except: pass
        s.configure("TFrame",background="#101820"); s.configure("Side.TFrame",background="#0B1117"); s.configure("TLabel",background="#101820",foreground="#EAEAEA",font=("Microsoft YaHei",10)); s.configure("Title.TLabel",background="#101820",foreground="#FFF",font=("Microsoft YaHei",18,"bold")); s.configure("Sub.TLabel",background="#101820",foreground="#B8C7D9",font=("Microsoft YaHei",10)); s.configure("TButton",font=("Microsoft YaHei",10),padding=6); s.configure("Treeview",font=("Microsoft YaHei",9),rowheight=26); s.configure("Treeview.Heading",font=("Microsoft YaHei",10,"bold"))
    def ui(self):
        self.root.configure(bg="#101820"); side=ttk.Frame(self.root,style="Side.TFrame",width=190); side.pack(side="left",fill="y"); side.pack_propagate(False)
        tk.Label(side,text="磁盘清理\nv4.2",bg="#0B1117",fg="white",font=("Microsoft YaHei",18,"bold")).pack(pady=(25,20))
        for t,cmd in [("首页",self.home),("磁盘扫描",self.scan_large),("缓存清理",self.scan_cache),("Top大文件",self.top_files),("下载分析",self.download),("重复文件",self.duplicates),("空文件夹",self.emptydirs),("设置/日志",self.settings)]:
            tk.Button(side,text=t,command=cmd,bg="#14202B",fg="#EAEAEA",relief="flat",activebackground="#1D8CF8",activeforeground="white",font=("Microsoft YaHei",11),pady=8).pack(fill="x",padx=12,pady=4)
        main=ttk.Frame(self.root,padding=16); main.pack(side="left",fill="both",expand=True)
        top=ttk.Frame(main); top.pack(fill="x"); ttk.Label(top,text="磁盘清理 v4.2",style="Title.TLabel").pack(side="left"); ttk.Label(top,text=f"作者：{AUTHOR} | QQ：{QQ} | 微信：{WECHAT}",style="Sub.TLabel").pack(side="right")
        pf=ttk.Frame(main); pf.pack(fill="x",pady=(14,8)); ttk.Entry(pf,textvariable=self.path_var).pack(side="left",fill="x",expand=True,padx=(0,8)); ttk.Button(pf,text="选择路径",command=self.choose).pack(side="left",padx=3); ttk.Button(pf,text="打开路径",command=self.open_current).pack(side="left",padx=3); ttk.Checkbutton(pf,text="默认放入回收站",variable=self.recycle_var).pack(side="left",padx=10)
        af=ttk.Frame(main); af.pack(fill="x",pady=6)
        for t,cmd in [("清理选中",self.clean_selected),("批量清理低风险",self.clean_low),("激进清理低/中风险",self.clean_med),("打开选中",self.open_selected),("导出CSV",self.export),("刷新结果",self.refresh_results)]:
            ttk.Button(af,text=t,command=cmd).pack(side="left",padx=3)
        self.info=tk.Text(main,height=5,bg="#162230",fg="#EAEAEA",relief="flat",font=("Microsoft YaHei",10)); self.info.pack(fill="x",pady=8); self.info.config(state="disabled")
        tf=ttk.Frame(main); tf.pack(fill="both",expand=True,pady=8)
        cols=("kind","type","size","risk","cache","created","modified","path"); self.tree=ttk.Treeview(tf,columns=cols,show="headings",selectmode="extended")
        names={"kind":"类别","type":"类型","size":"大小","risk":"风险","cache":"缓存","created":"创建日期","modified":"修改日期","path":"路径"}; widths={"kind":70,"type":90,"size":100,"risk":80,"cache":60,"created":150,"modified":150,"path":560}
        for c in cols: self.tree.heading(c,text=names[c],command=lambda x=c:self.sort(x)); self.tree.column(c,width=widths[c],anchor="w")
        self.tree.tag_configure("low",background="#E9F9EE"); self.tree.tag_configure("medium",background="#FFF6D6"); self.tree.tag_configure("high",background="#FFE2E2"); self.tree.tag_configure("folder",foreground="#0B5CAD")
        y=ttk.Scrollbar(tf,orient="vertical",command=self.tree.yview); x=ttk.Scrollbar(tf,orient="horizontal",command=self.tree.xview); self.tree.configure(yscrollcommand=y.set,xscrollcommand=x.set); self.tree.grid(row=0,column=0,sticky="nsew"); y.grid(row=0,column=1,sticky="ns"); x.grid(row=1,column=0,sticky="ew"); tf.rowconfigure(0,weight=1); tf.columnconfigure(0,weight=1)
        bf=ttk.Frame(main); bf.pack(fill="x",pady=(8,0)); ttk.Progressbar(bf,variable=self.progress_var,maximum=100).pack(side="left",fill="x",expand=True,padx=(0,10)); ttk.Label(bf,textvariable=self.status_var,style="Sub.TLabel").pack(side="left")
    def set_info(self,t): self.info.config(state="normal"); self.info.delete("1.0","end"); self.info.insert("1.0",t); self.info.config(state="disabled")
    def summary(self):
        i=system_info(); disks=" | ".join([f"{d} {disk_usage_text(d)}" for d in drives()[:4]])
        return f"电脑用户：{i['username']}    计算机名：{i['computer']}    IP：{i['ip']}    WiFi：{i['wifi']}\n系统：{i['system']}\n显卡：{i['gpu']}\n{disks}"
    def home(self): self.clear(); self.set_info(self.summary()+"\n\n建议：优先使用“缓存清理”和“Top大文件”。默认删除方式为放入回收站。"); self.status_var.set("首页"); self.progress_var.set(0)
    def settings(self): self.clear(); self.set_info(f"作者：{AUTHOR}\nQQ：{QQ}\n微信：{WECHAT}\n日志目录：{LOG_DIR}\n\n默认建议使用回收站删除，降低误删风险。"); os.startfile(LOG_DIR)
    def choose(self):
        f=filedialog.askdirectory(initialdir=self.path_var.get() or str(USER_DIR))
        if f: self.path_var.set(f); self.set_info(self.summary())
    def open_current(self):
        p=Path(self.path_var.get())
        if p.exists(): os.startfile(p)
    def run(self,fn): threading.Thread(target=fn,daemon=True).start()
    def pcb(self,c,t,text=""): self.progress_var.set(min(c/max(t,1)*100,100)); self.status_var.set(f"处理中：{c}/{t}"); self.root.update_idletasks()
    def clear(self):
        for i in self.tree.get_children(): self.tree.delete(i)
    def insert(self):
        self.clear(); ordered=[x for x in self.results if x["kind"]=="文件夹"]+[x for x in self.results if x["kind"]=="文件"]; self.results=ordered
        for idx,it in enumerate(ordered):
            tags=[it["risk_raw"]]; 
            if it["kind"]=="文件夹": tags.append("folder")
            self.tree.insert("", "end", iid=str(idx), tags=tuple(tags), values=(it["kind"],it["type"],it["size_text"],it["risk"],it["cache"],it["created"],it["modified"],it["path"]))
        self.status_var.set(f"完成：{len(ordered)} 项 | 合计 {format_size(sum(x['size'] for x in ordered))}"); self.progress_var.set(100)
    def target(self):
        p=Path(self.path_var.get())
        if not p.exists() or not p.is_dir(): messagebox.showerror("错误","路径不存在或不是文件夹"); return None
        return p
    def scan_large(self):
        p=self.target()
        if p: self.run(lambda: self._scan(lambda: scan_large_items(p,progress_cb=self.pcb), f"扫描路径：{p}\n{disk_usage_text(p)}"))
    def scan_cache(self):
        p=self.target()
        if p: self.run(lambda: self._scan(lambda: scan_cache_dirs(p,progress_cb=self.pcb), f"缓存扫描完成。\n扫描路径：{p}\n建议优先清理低风险缓存。"))
    def top_files(self):
        p=self.target()
        if p: self.run(lambda: self._scan(lambda: scan_top_files(p,limit=100,progress_cb=self.pcb), f"Top 100 大文件扫描完成。\n扫描路径：{p}"))
    def _scan(self,func,info):
        self.progress_var.set(0); self.results=func(); self.insert(); self.set_info(info)
    def download(self):
        def task():
            p,s,d=analyze_downloads(); lines=[f"下载目录：{p}",""]
            for c,v in s.items(): lines.append(f"{c:<8} 数量：{v['count']:<6} 体积：{format_size(v['size'])}")
            self.results=d[:200]; self.insert(); self.set_info("\n".join(lines))
        self.run(task)
    def duplicates(self):
        p=self.target()
        if not p: return
        if not messagebox.askyesno("重复文件检测","重复文件检测会计算哈希，大目录可能耗时较久，是否继续？"): return
        self.run(lambda: self._scan(lambda: find_duplicate_files(p,progress_cb=self.pcb), f"重复文件检测完成。\n扫描路径：{p}\n请谨慎删除，建议每组至少保留一个文件。"))
    def emptydirs(self):
        p=self.target()
        if not p: return
        def task():
            found=scan_empty_dirs(p,progress_cb=self.pcb)
            if not found: messagebox.showinfo("结果","没有发现空文件夹"); return
            if messagebox.askyesno("确认",f"发现 {len(found)} 个空文件夹，是否删除？"):
                ok,fail=delete_empty_dirs(found,recycle=self.recycle_var.get()); messagebox.showinfo("完成",f"成功：{ok}\n失败：{fail}")
        self.run(task)
    def selected(self):
        out=[]
        for iid in self.tree.selection():
            try: out.append(self.results[int(iid)])
            except: pass
        return out
    def clean_items(self,items,title):
        if not items: messagebox.showinfo("提示","没有可清理项目"); return
        high=[x for x in items if x["risk_raw"]=="high"]; items=[x for x in items if x["risk_raw"]!="high"]
        if high: messagebox.showwarning("提示",f"已跳过 {len(high)} 个高风险项目")
        if not items: return
        total=sum(x["size"] for x in items); mode="放入回收站" if self.recycle_var.get() else "永久删除"
        if not messagebox.askyesno("确认清理",f"{title}\n数量：{len(items)}\n预计释放：{format_size(total)}\n方式：{mode}\n是否继续？"): return
        def task():
            before=disk_usage(items[0]["path"])["free"]; deleted=failed=0
            for i,it in enumerate(items,1):
                r=delete_item(it["path"],recycle=self.recycle_var.get(),clear_contents=True); deleted+=r["deleted"]; failed+=r["failed"]; self.pcb(i,len(items),it["path"])
            after=disk_usage(items[0]["path"])["free"]; messagebox.showinfo("清理完成",f"本次释放：{format_size(deleted)}\n清理前剩余：{format_size(before)}\n清理后剩余：{format_size(after)}\n失败数量：{failed}")
        self.run(task)
    def clean_selected(self):
        items=self.selected()
        if any(x["risk_raw"]=="medium" for x in items):
            if not messagebox.askyesno("中风险提示","选中项包含中风险项目，可能包含用户资料或配置。是否继续？"): return
        self.clean_items(items,"清理选中项")
    def clean_low(self): self.clean_items([x for x in self.results if x["risk_raw"]=="low"],"批量清理低风险")
    def clean_med(self):
        if messagebox.askyesno("激进模式","激进模式会清理低风险和中风险项目。是否继续？"): self.clean_items([x for x in self.results if x["risk_raw"] in ("low","medium")],"激进清理低/中风险")
    def open_selected(self):
        items=self.selected()
        if not items: messagebox.showinfo("提示","请先选择一项"); return
        p=Path(items[0]["path"])
        if p.is_dir(): os.startfile(p)
        else: subprocess.Popen(f'explorer /select,"{p}"')
    def export(self):
        if not self.results: messagebox.showinfo("提示","没有可导出的结果"); return
        out=LOG_DIR/f"gui_results_{timestamp()}.csv"; export_csv(self.results,out); messagebox.showinfo("完成",f"已导出：{out}")

    def refresh_results(self):
        """刷新当前表格结果：重新检查路径是否存在、重新计算大小，并移除已删除或已清空的项目。"""
        if not self.results:
            messagebox.showinfo("提示", "当前没有可刷新的结果")
            return

        def task():
            refreshed = []
            total = len(self.results)
            for i, it in enumerate(list(self.results), 1):
                p = Path(it.get("path", ""))
                if not p.exists():
                    self.pcb(i, total, str(p))
                    continue

                size = get_size(p)
                # 已清理为空的缓存/文件夹不再显示；普通文件大小为 0 也不显示
                if size <= 0:
                    self.pcb(i, total, str(p))
                    continue

                new_item = item_info(p, size)
                # 对于缓存列表，低于 100MB 的项目刷新后移除，避免清理后仍显示
                if it.get("cache") == "是" and size < MIN_SCAN_SIZE:
                    self.pcb(i, total, str(p))
                    continue

                refreshed.append(new_item)
                self.pcb(i, total, str(p))

            self.results = refreshed
            self.insert()
            self.set_info(
                f"刷新完成。\n"
                f"当前显示项目：{len(refreshed)} 项\n"
                f"合计体积：{format_size(sum(x['size'] for x in refreshed))}\n"
                f"说明：已删除、已清空、或缓存体积低于 100MB 的项目已从列表移除。"
            )

        self.run(task)

    def sort(self,col):
        key={"kind":"kind","type":"type","size":"size","risk":"risk","cache":"cache","created":"created","modified":"modified","path":"path"}[col]
        self.results.sort(key=lambda x:x[key],reverse=self.sort_reverse); self.sort_reverse=not self.sort_reverse; self.insert()
def main():
    root=tk.Tk(); App(root); root.mainloop()
if __name__=="__main__": main()
