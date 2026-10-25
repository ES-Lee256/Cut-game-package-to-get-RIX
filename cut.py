import sys
import os

def extract_blocks(input_file):
    """
    提取数据块：
    - 以 AA 55 开头
    - 以 80 结尾，且该 80 后面要么紧跟着 AA 55（下一个块头），
      要么是文件中的最后一个 80（对应最后一个块）。
    输出文件索引从 1 开始。
    """
    with open(input_file, 'rb') as f:
        data = f.read()

    head = b'\xAA\x55'
    tail = b'\x80'
    data_len = len(data)

    blocks = []
    pos = 0

    while pos < data_len:
        start = data.find(head, pos)
        if start == -1:
            break

        # 收集从头之后的所有 80 位置
        tail_positions = []
        search_pos = start + len(head)
        while True:
            t = data.find(tail, search_pos)
            if t == -1:
                break
            tail_positions.append(t)
            search_pos = t + 1

        if not tail_positions:
            # 没有找到任何 80，跳过这个头
            pos = start + 1
            continue

        # 判断哪些 80 后面紧跟 AA 55
        valid_tail = None
        for t in tail_positions:
            if t + 1 < data_len and data[t + 1:t + 3] == head:
                valid_tail = t
                break

        if valid_tail is None:
            # 没有符合条件的 80，取最后一个 80 作为尾（最后一个块）
            valid_tail = tail_positions[-1]

        # 提取块
        block = data[start:valid_tail + 1]
        blocks.append((start, valid_tail, block))

        # 继续从尾之后搜索下一个头
        pos = valid_tail + 1

    if not blocks:
        print("未找到任何符合条件的数据块。")
        print("No data blocks matching the criteria were found.")
        return

    base_name = os.path.splitext(os.path.basename(input_file))[0]

    for idx, (start, end, block) in enumerate(blocks, start=1):  # 索引从 1 开始
        output_name = f"{base_name}{idx}.rix"
        with open(output_name, 'wb') as out:
            out.write(block)

        print(f"块(block) {idx}: {output_name}")
        print(f"  偏移(offset): {start} -> {end}, 长度(length): {len(block)} 字节(byte)")
        preview = block[:16].hex().upper()
        print(f"  头部预览(head preview): {preview} ...")
        print()

    print(f"共提取 {len(blocks)} 个文件。")
    print(f"A total of {len(blocks)} files were extracted.")

def main():
    if len(sys.argv) != 2:
        print("用法: python cut.py <文件名>")
        print("Usage: python cut.py <filename>")
        sys.exit(1)

    input_file = sys.argv[1]
    try:
        extract_blocks(input_file)
    except FileNotFoundError:
        print(f"错误: 文件 '{input_file}' 不存在")
        print(f"Error: File '{input_file}' is not exist.")
        sys.exit(1)
    except Exception as e:
        print(f"处理时发生错误: {e}")
        print(f"An error occurred while processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
