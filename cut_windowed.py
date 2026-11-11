import os
import sys
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
from contextlib import redirect_stderr, redirect_stdout


GUI_TEXT = {
    "zh-CN": {
        "title": "RIX 资源块提取工具",
        "input": "输入文件",
        "import": "导入文件",
        "output": "导出目录",
        "browse": "选择目录",
        "start": "开始提取",
        "choose_file": "选择输入文件",
        "choose_directory": "选择导出目录",
        "missing_file": "请选择输入文件。\n",
        "invalid_file": "错误：输入文件不存在。\n",
        "missing_directory": "错误：请填写导出目录。\n",
        "starting": "开始提取...\n",
        "complete": "处理完成。\n",
        "error": "处理时发生错误: {}\n",
    },
    "zh-TW": {
        "title": "RIX 資源區塊擷取工具",
        "input": "輸入檔案",
        "import": "匯入檔案",
        "output": "匯出目錄",
        "browse": "選擇目錄",
        "start": "開始擷取",
        "choose_file": "選擇輸入檔案",
        "choose_directory": "選擇匯出目錄",
        "missing_file": "請選擇輸入檔案。\n",
        "invalid_file": "錯誤：輸入檔案不存在。\n",
        "missing_directory": "錯誤：請填寫匯出目錄。\n",
        "starting": "開始擷取...\n",
        "complete": "處理完成。\n",
        "error": "處理時發生錯誤: {}\n",
    },
    "en": {
        "title": "RIX Resource Block Extractor",
        "input": "Input file",
        "import": "Import file",
        "output": "Export folder",
        "browse": "Browse",
        "start": "Start extraction",
        "choose_file": "Select input file",
        "choose_directory": "Select export folder",
        "missing_file": "Please select an input file.\n",
        "invalid_file": "Error: The input file does not exist.\n",
        "missing_directory": "Error: Please enter an export folder.\n",
        "starting": "Starting extraction...\n",
        "complete": "Processing complete.\n",
        "error": "An error occurred while processing: {}\n",
    },
}

EXTRACTION_TEXT = {
    "zh-CN": {
        "not_found": "未找到任何符合条件的数据块。",
        "block": "块",
        "offset": "偏移",
        "length": "长度",
        "bytes": "字节",
        "preview": "头部预览",
        "total": "共提取 {} 个文件。",
    },
    "zh-TW": {
        "not_found": "未找到任何符合條件的資料區塊。",
        "block": "區塊",
        "offset": "位移",
        "length": "長度",
        "bytes": "位元組",
        "preview": "檔頭預覽",
        "total": "共擷取 {} 個檔案。",
    },
    "en": {
        "not_found": "No data blocks matching the criteria were found.",
        "block": "Block",
        "offset": "Offset",
        "length": "Length",
        "bytes": "bytes",
        "preview": "Header preview",
        "total": "A total of {} files were extracted.",
    },
}


def extract_blocks(input_file, output_dir=None, language=None):
    """
    提取数据块：
    - 以 AA 55 开头
    - 以 80 结尾，且该 80 后面要么紧跟着 AA 55（下一个块头），
      要么是文件中的最后一个 80（对应最后一个块）。
    输出文件索引从 1 开始。
    """
    with open(input_file, 'rb') as f:
        data = f.read()

    output_dir = output_dir or os.getcwd()
    os.makedirs(output_dir, exist_ok=True)

    head = b'\xAA\x55'
    tail = b'\x80'
    data_len = len(data)

    blocks = []
    pos = 0

    while pos < data_len:
        start = data.find(head, pos)
        if start == -1:
            break

        tail_positions = []
        search_pos = start + len(head)
        while True:
            t = data.find(tail, search_pos)
            if t == -1:
                break
            tail_positions.append(t)
            search_pos = t + 1

        if not tail_positions:
            pos = start + 1
            continue

        valid_tail = None
        for t in tail_positions:
            if t + 1 < data_len and data[t + 1:t + 3] == head:
                valid_tail = t
                break

        if valid_tail is None:
            valid_tail = tail_positions[-1]

        block = data[start:valid_tail + 1]
        blocks.append((start, valid_tail, block))
        pos = valid_tail + 1

    if not blocks:
        if language in EXTRACTION_TEXT:
            print(EXTRACTION_TEXT[language]["not_found"])
        else:
            print("未找到任何符合条件的数据块。")
            print("No data blocks matching the criteria were found.")
        return

    base_name = os.path.splitext(os.path.basename(input_file))[0]
    messages = EXTRACTION_TEXT.get(language)
    for idx, (start, end, block) in enumerate(blocks, start=1):
        output_name = f"{base_name}{idx}.rix"
        output_path = os.path.join(output_dir, output_name)
        with open(output_path, 'wb') as out:
            out.write(block)

        preview = block[:16].hex().upper()
        if messages:
            print(f"{messages['block']} {idx}: {output_path}")
            print(
                f"  {messages['offset']}: {start} -> {end}, "
                f"{messages['length']}: {len(block)} {messages['bytes']}"
            )
            print(f"  {messages['preview']}: {preview} ...")
        else:
            print(f"块(block) {idx}: {output_path}")
            print(f"  偏移(offset): {start} -> {end}, 长度(length): {len(block)} 字节(byte)")
            print(f"  头部预览(head preview): {preview} ...")
        print()

    if messages:
        print(messages["total"].format(len(blocks)))
    else:
        print(f"共提取 {len(blocks)} 个文件。")
        print("A total of {} files were extracted.".format(len(blocks)))


class CutApp:
    def __init__(self, root):
        self.root = root
        self.language = "zh-CN"
        self.root.geometry("540x370")
        self.root.minsize(460, 320)

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

        self.input_label = ttk.Label(frame)
        self.input_label.grid(
            row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 8)
        )
        self.input_path = tk.StringVar()
        ttk.Entry(frame, textvariable=self.input_path).grid(
            row=0, column=1, sticky="ew", pady=(0, 8)
        )
        self.import_button = ttk.Button(frame, command=self.select_file)
        self.import_button.grid(
            row=0, column=2, padx=(8, 0), pady=(0, 8)
        )

        self.output_label = ttk.Label(frame)
        self.output_label.grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=(0, 8)
        )
        self.output_path = tk.StringVar(value=os.getcwd())
        ttk.Entry(frame, textvariable=self.output_path).grid(
            row=1, column=1, sticky="ew", pady=(0, 8)
        )
        self.directory_button = ttk.Button(frame, command=self.select_directory)
        self.directory_button.grid(
            row=1, column=2, padx=(8, 0), pady=(0, 8)
        )

        self.console = scrolledtext.ScrolledText(
            frame, height=10, state=tk.DISABLED, wrap=tk.WORD
        )
        self.console.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(2, 8))

        language_frame = ttk.Frame(frame)
        language_frame.grid(row=3, column=0, columnspan=2, sticky="w")
        self.language_buttons = {}
        for code, label in (
            ("zh-CN", "简体中文"),
            ("zh-TW", "繁體中文"),
            ("en", "English"),
        ):
            button = ttk.Button(
                language_frame,
                text=label,
                command=lambda selected=code: self.set_language(selected),
            )
            button.pack(side=tk.LEFT, padx=(0, 4))
            self.language_buttons[code] = button

        self.run_button = ttk.Button(frame, command=self.run_extraction)
        self.run_button.grid(row=3, column=2, sticky="e")
        self.apply_language()

    def set_language(self, language):
        self.language = language
        self.apply_language()

    def apply_language(self):
        text = GUI_TEXT[self.language]
        self.root.title(text["title"])
        self.input_label.configure(text=text["input"])
        self.import_button.configure(text=text["import"])
        self.output_label.configure(text=text["output"])
        self.directory_button.configure(text=text["browse"])
        self.run_button.configure(text=text["start"])
        for code, button in self.language_buttons.items():
            button.configure(state=tk.DISABLED if code == self.language else tk.NORMAL)

    def write_console(self, text):
        self.console.configure(state=tk.NORMAL)
        self.console.insert(tk.END, text)
        self.console.see(tk.END)
        self.console.configure(state=tk.DISABLED)

    def select_file(self):
        path = filedialog.askopenfilename(title=GUI_TEXT[self.language]["choose_file"])
        if path:
            self.input_path.set(path)

    def select_directory(self):
        initial_dir = self.output_path.get()
        if not os.path.isdir(initial_dir):
            initial_dir = os.getcwd()
        path = filedialog.askdirectory(
            title=GUI_TEXT[self.language]["choose_directory"],
            initialdir=initial_dir
        )
        if path:
            self.output_path.set(path)

    def run_extraction(self):
        input_file = self.input_path.get().strip()
        output_dir = self.output_path.get().strip()
        self.console.configure(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.configure(state=tk.DISABLED)

        text = GUI_TEXT[self.language]
        if not input_file:
            self.write_console(text["missing_file"])
            return
        if not os.path.isfile(input_file):
            self.write_console(text["invalid_file"])
            return
        if not output_dir:
            self.write_console(text["missing_directory"])
            return

        self.run_button.configure(state=tk.DISABLED)
        try:
            self.write_console(text["starting"])
            with redirect_stdout(self), redirect_stderr(self):
                extract_blocks(input_file, output_dir, self.language)
            self.write_console(text["complete"])
        except Exception as error:
            self.write_console(text["error"].format(error))
        finally:
            self.run_button.configure(state=tk.NORMAL)

    def write(self, text):
        self.write_console(text)
        return len(text)

    def flush(self):
        pass


def main():
    if len(sys.argv) == 2:
        input_file = sys.argv[1]
        try:
            extract_blocks(input_file)
        except FileNotFoundError:
            print(f"错误: 文件 '{input_file}' 不存在")
            print(f"Error: File '{input_file}' is not exist.")
            sys.exit(1)
        except Exception as error:
            print(f"处理时发生错误: {error}")
            print(f"An error occurred while processing: {error}")
            sys.exit(1)
        return

    if len(sys.argv) > 1:
        print("用法: python cut.py [文件名]")
        print("Usage: python cut.py [filename]")
        sys.exit(1)

    root = tk.Tk()
    CutApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
