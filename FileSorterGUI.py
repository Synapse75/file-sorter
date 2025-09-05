import tkinter as tk
from tkinter import filedialog, messagebox
import os
from FileSorter import sort_files_by_extension

def choose_folder():
    p = filedialog.askdirectory(initialdir=os.path.dirname(__file__))
    if p:
        folder_var.set(p)

def run_sort():
    folder = folder_var.get()
    if not folder or not os.path.isdir(folder):
        messagebox.showerror("错误", "请选择有效的文件夹")
        return
    # 收集用户为每个后缀填写的目标文件夹名（仅收集被勾选的）
    name_map = {}
    for ext, var in mapping_entries.items():
        enabled = mapping_enabled.get(ext)
        if enabled and not enabled.get():
            continue  # 未勾选 → 不生成该后缀的文件夹，保留文件原位
        v = var.get().strip()
        if v:
            # GUI 中显示的无后缀标签是 "(无后缀)"，FileSorter 使用 "(noext)"
            key = "(noext)" if ext == "(无后缀)" else ext
            name_map[key] = v
    try:
        sort_files_by_extension(folder, name_map=name_map)
        messagebox.showinfo("完成", "排序完成")
    except Exception as e:
        messagebox.showerror("错误", f"排序失败:\n{e}")

# 新增：扫描并返回后缀列表（递归）
def get_extensions(folder):
    exts = set()
    no_ext = False
    for root_dir, dirs, files in os.walk(folder):
        for fname in files:
            _, ext = os.path.splitext(fname)
            if ext:
                exts.add(ext.lower())  # 保留点，如 ".txt"
            else:
                no_ext = True
    sorted_exts = sorted(exts)
    if no_ext:
        sorted_exts.append("(无后缀)")
    return sorted_exts

root = tk.Tk()
root.title("File Sorter")

folder_var = tk.StringVar(value=os.path.dirname(__file__))

# 防抖等待时间（毫秒）和计划任务句柄
DEBOUNCE_MS = 400
_update_job = None

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill="both", expand=True)

entry = tk.Entry(frame, textvariable=folder_var, width=50)
entry.pack(side="left", padx=(0,5))
tk.Button(frame, text="浏览...", command=choose_folder).pack(side="left")

# 操作按钮区：开始排序 / 显示后缀（保留） / 退出
btn_frame = tk.Frame(root, pady=5)
btn_frame.pack()
tk.Button(btn_frame, text="开始归类", command=run_sort).pack(side="left", padx=5)
tk.Button(btn_frame, text="退出", command=root.destroy).pack(side="left", padx=5)

# mapping_entries: ext -> tk.StringVar
mapping_entries = {}
# mapping_enabled: ext -> tk.BooleanVar (表示是否勾选，默认 True)
mapping_enabled = {}

def build_mapping_rows(exts):
    # 清空旧行
    for child in mapping_inner_frame.winfo_children():
        child.destroy()
    mapping_entries.clear()
    mapping_enabled.clear()

    if not exts:
        lbl = tk.Label(mapping_inner_frame, text="未找到文件后缀")
        lbl.pack(anchor="w", padx=5, pady=2)
        return

    for e in exts:
        row = tk.Frame(mapping_inner_frame)
        row.pack(fill="x", padx=5, pady=2)

        lbl = tk.Label(row, text=e, width=12, anchor="w")
        lbl.pack(side="left")

        # 默认文件夹名：去掉点，如 ".txt" -> "txt"，无后缀 -> "others"
        if e.startswith("."):
            default = e[1:]
        else:
            default = "others"

        var = tk.StringVar(value=default)
        ent = tk.Entry(row, textvariable=var, width=28)
        ent.pack(side="left", padx=(6,0))

        # 勾选框（默认勾选，勾上表示会创建对应文件夹并移动该后缀文件）
        enabled_var = tk.BooleanVar(value=True)
        chk = tk.Checkbutton(row, variable=enabled_var)
        chk.pack(side="left", padx=(6,0))

        mapping_entries[e] = var
        mapping_enabled[e] = enabled_var

# 用滚动区域替代原来的 Listbox（保留可滚动）
list_frame = tk.Frame(root, padx=10, pady=5)
list_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(list_frame)
vscroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
canvas.configure(yscrollcommand=vscroll.set)

vscroll.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

mapping_inner_frame = tk.Frame(canvas)
# 创建一个窗口把 inner frame 放到 canvas 里
canvas.create_window((0,0), window=mapping_inner_frame, anchor="nw")

def _on_mapping_config(event):
    # 更新滚动区域大小
    canvas.configure(scrollregion=canvas.bbox("all"))

mapping_inner_frame.bind("<Configure>", _on_mapping_config)

# 新增：在 List 区 创建后绑定 folder_var 的变动，使用防抖避免频繁扫描
def _schedule_update_extensions(*args):
    global _update_job
    if _update_job is not None:
        try:
            root.after_cancel(_update_job)
        except Exception:
            pass
        _update_job = None
    _update_job = root.after(DEBOUNCE_MS, _update_extensions)

def _update_extensions():
    global _update_job
    _update_job = None
    folder = folder_var.get()
    if not folder or not os.path.isdir(folder):
        # 清空并显示提示（不弹窗，自动响应）
        for child in mapping_inner_frame.winfo_children():
            child.destroy()
        lbl = tk.Label(mapping_inner_frame, text="请输入或选择有效文件夹")
        lbl.pack(anchor="w", padx=5, pady=2)
        return
    try:
        exts = get_extensions(folder)
    except Exception as e:
        for child in mapping_inner_frame.winfo_children():
            child.destroy()
        lbl = tk.Label(mapping_inner_frame, text=f"扫描失败: {e}")
        lbl.pack(anchor="w", padx=5, pady=2)
        return

    # 以行的方式显示后缀与右侧输入框+勾选框
    build_mapping_rows(exts)

# 绑定 StringVar 改变（包括 choose_folder 设置）以自动更新
folder_var.trace_add("write", _schedule_update_extensions)

# 启动时立即触发一次更新（显示默认文件夹的后缀）
_schedule_update_extensions()

root.mainloop()