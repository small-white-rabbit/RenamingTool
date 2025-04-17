import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
from uuid import uuid4

class BatchRenameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量文件重命名工具-YH.2025-04-17")
        self.root.geometry("600x550")  # 增加高度以适应新输入框
        self.files = []
        self.directory = ""

        # 界面布局
        self.create_widgets()

    def create_widgets(self):
        # 文件夹选择
        tk.Label(self.root, text="文件夹路径:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.path_entry = tk.Entry(self.root, width=50)
        self.path_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="浏览", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)

        # 重命名规则
        tk.Label(self.root, text="重命名规则:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.rule_var = tk.StringVar(value="prefix_number")
        tk.Radiobutton(self.root, text="前缀+序号 (如: file_001)", variable=self.rule_var, value="prefix_number").grid(row=1, column=1, sticky="w")
        tk.Radiobutton(self.root, text="自定义规则", variable=self.rule_var, value="custom").grid(row=2, column=1, sticky="w")

        # 前缀输入
        tk.Label(self.root, text="前缀:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.prefix_entry = tk.Entry(self.root, width=30)
        self.prefix_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.prefix_entry.insert(0, "file_")

        # 起始序号
        tk.Label(self.root, text="起始序号:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.start_num_entry = tk.Entry(self.root, width=10)
        self.start_num_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.start_num_entry.insert(0, "1")

        # 添加词条
        tk.Label(self.root, text="添加词条:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.add_text_entry = tk.Entry(self.root, width=30)
        self.add_text_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.position_var = tk.StringVar(value="end")
        tk.OptionMenu(self.root, self.position_var, "开头", "结尾", "指定位置").grid(row=5, column=2, padx=5, pady=5)

        # 指定位置
        tk.Label(self.root, text="插入位置:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.position_entry = tk.Entry(self.root, width=10)
        self.position_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        self.position_entry.insert(0, "0")
        self.position_entry.config(state="disabled")

        # 删除词组
        tk.Label(self.root, text="删除词组:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        self.remove_text_entry = tk.Entry(self.root, width=30)
        self.remove_text_entry.grid(row=7, column=1, padx=5, pady=5, sticky="w")

        # 词条类型
        tk.Label(self.root, text="词条类型:").grid(row=8, column=0, padx=5, pady=5, sticky="w")
        self.text_type_var = tk.StringVar(value="fixed")
        tk.Radiobutton(self.root, text="固定词条", variable=self.text_type_var, value="fixed").grid(row=8, column=1, sticky="w")
        tk.Radiobutton(self.root, text="序号词条", variable=self.text_type_var, value="sequential").grid(row=9, column=1, sticky="w")

        # 预览和执行
        tk.Button(self.root, text="预览", command=self.preview).grid(row=10, column=1, pady=10)
        tk.Button(self.root, text="执行重命名", command=self.rename_files).grid(row=10, column=2, pady=10)

        # 预览区域
        tk.Label(self.root, text="预览:").grid(row=11, column=0, padx=5, pady=5, sticky="w")
        self.preview_text = tk.Text(self.root, height=10, width=60)
        self.preview_text.grid(row=12, column=0, columnspan=3, padx=5, pady=5)

        # 绑定位置选择事件
        self.position_var.trace("w", self.toggle_position_entry)

    def browse_folder(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory = directory
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)
            self.load_files()

    def load_files(self):
        self.files = [f for f in os.listdir(self.directory) if os.path.isfile(os.path.join(self.directory, f))]
        self.files.sort()

    def toggle_position_entry(self, *args):
        if self.position_var.get() == "指定位置":
            self.position_entry.config(state="normal")
        else:
            self.position_entry.config(state="disabled")

    def preview(self):
        if not self.directory or not self.files:
            messagebox.showerror("错误", "请先选择文件夹！")
            return

        self.preview_text.delete(1.0, tk.END)
        new_names = self.generate_new_names()

        for old_name, new_name in new_names:
            self.preview_text.insert(tk.END, f"{old_name} -> {new_name}\n")

    def generate_new_names(self):
        new_names = []
        prefix = self.prefix_entry.get()
        try:
            start_num = int(self.start_num_entry.get())
        except ValueError:
            start_num = 1

        add_text = self.add_text_entry.get()
        remove_text = self.remove_text_entry.get()
        position = self.position_var.get()
        text_type = self.text_type_var.get()

        try:
            insert_pos = int(self.position_entry.get()) if position == "指定位置" else 0
        except ValueError:
            insert_pos = 0

        rule = self.rule_var.get()

        for index, old_name in enumerate(self.files, start=start_num):
            name, ext = os.path.splitext(old_name)
            # 删除指定词组
            if remove_text:
                name = name.replace(remove_text, "")

            # 应用重命名规则
            if rule == "prefix_number":
                new_name = f"{prefix}{index:03d}{ext}"
            else:
                new_name = f"{name}{ext}"

            # 添加词条
            if add_text:
                text_to_add = add_text if text_type == "fixed" else f"{add_text}{index:03d}"
                if position == "开头":
                    new_name = f"{text_to_add}{new_name}"
                elif position == "结尾":
                    new_name = f"{name}{text_to_add}{ext}"
                else:  # 指定位置
                    new_name = f"{name[:insert_pos]}{text_to_add}{name[insert_pos:]}{ext}"

            new_names.append((old_name, new_name))

        return new_names

    def rename_files(self):
        if not self.directory or not self.files:
            messagebox.showerror("错误", "请先选择文件夹！")
            return

        new_names = self.generate_new_names()
        errors = []

        for old_name, new_name in new_names:
            old_path = os.path.join(self.directory, old_name)
            new_path = os.path.join(self.directory, new_name)
            try:
                os.rename(old_path, new_path)
            except Exception as e:
                errors.append(f"重命名 {old_name} 失败：{e}")

        self.load_files()  # 刷新文件列表
        self.preview()  # 更新预览

        if errors:
            messagebox.showwarning("警告", "\n".join(errors))
        else:
            messagebox.showinfo("成功", "文件重命名完成！")

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchRenameApp(root)
    root.mainloop()