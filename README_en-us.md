[简体中文](README.md)|[繁體中文](README_zh-tw.md)|English
# RIX Resource Block Extraction Tool

This project provides a small utility for extracting `.rix` files from game package binaries by identifying specific data blocks embedded in the package.

It is designed for highly targeted extraction of music-related resources, especially where `.rix` chunks appear inside larger game archives.

## 1. .rix File Signature

The tool recognizes `.rix` data blocks with the following structure:

- File header: `AA 55`
  - Hex: `0xAA 0x55`
- File footer: `80`
  - Hex: `0x80`

The extraction logic searches for binary blocks that:

- begin with `AA 55`
- end with `80`
- and where that `80` is followed either by the next block header `AA 55` or by the end of the file

This makes it possible to isolate valid resource blocks from larger binary files.

---

## 2. How the Tool Works

The script reads the entire input file as binary data and scans it for valid block starts.

The extraction process is as follows:

1. Open the input file in binary mode
2. Search for `AA 55` headers
3. From each header, search forward for all `80` bytes
4. Determine which `80` byte is the valid end of the block:
   - If the `80` is immediately followed by another `AA 55`, it is treated as the end of the current block
   - Otherwise, if no valid next header is found, the last `80` in the scanning range is used as the block terminator
5. Extract the entire block from start to end
6. Save each extracted block as a new `.rix` file
7. Number the output files starting from `1`

Example output naming:

```bash
game.bin
game1.rix
game2.rix
game3.rix
```
---

## 3. Usage

Run the tool from the command line as follows:

```bash
python cut.py <filename>
```

Example:

```bash
python cut.py package.dat
```

When executed, the tool scans the file, extracts matching data blocks, and writes them into the current directory.

If the file does not exist, the script exits with an error message. If no valid blocks are found, it prints a notice indicating that no matching `.rix` data blocks were found.

---

## 4. Script Behavior

The main logic is handled by:

```python
extract_blocks(input_file)
```

This function:

- reads the binary content
- finds valid block boundaries
- extracts each block
- writes it to disk
- prints offset and length information for each block

The script prints debug information such as:

- block number
- output file name
- start/end offsets
- block length
- first 16 bytes in hex

This helps verify that the extracted data is structurally valid and corresponds to the expected resource format.

---

## 5. Supported Games

This tool is intended for extracting music-related `.rix` resources from the following games and packages:

- ~~Xuan-Yuan Sword 2~~

  (Strikethrough here means the statement is invalid: This game does not have a matching package; the RIX files are placed loose externally, same for the rest.)
- ~~XuanYuan Sword: The Dance of the Maple~~
- Sword and Fairy (DOS)
- Magic Sword: Heroic Fantasy 2
- Yao Mo Dao
- Magic Century 2
- Angel Empire 2
- Star Volunteer
- Zhengzong Taiwan 16 Mahjong
- Zhengzong Taiwan 16 Mahjong 2
- Monopoly 2
- Monopoly 3
- Fighting King
- L-MAN
- Spring and Autumn Warring States 2

These titles are the main target set for this extraction workflow because their resource packages frequently contain structured `.rix` data blocks.

---

## 6. Package File Notes

This tool is intentionally limited to:

- searching only `music`-related resource packages
- performing highly specific extraction of `.rix` files
- avoiding broad, indiscriminate full-package unpacking

In other words, it does not attempt to extract every possible file type from the archive. Instead, it focuses on identifying only the blocks that match the known `.rix` signature pattern.

This makes the tool especially useful when:

- the package contains many unrelated data types
- you need to isolate only music resources
- you want high-specificity extraction instead of full binary dumping

---

## 7. Example Output

A typical runtime output looks like this:

```text
块(block) 1: game1.rix
  偏移(offset): 128 -> 2048, 长度(length): 1921 字节(byte)
  头部预览(head preview): AA5501...

块(block) 2: game2.rix
  偏移(offset): 4096 -> 8192, 长度(length): 4097 字节(byte)
  头部预览(head preview): AA5502...

共提取 2 个文件。
A total of 2 files were extracted.
```

This output confirms the extracted block count and provides offset/size information for each resource chunk.

---

## 8. Notes

- This tool relies on known binary structure patterns and is intended for specific game archives
- It is best suited to resource packages that contain `.rix` blocks with the `AA 55` header and `80` terminator
- If a package does not contain matching signatures, no valid files will be extracted

---

## 9. Summary

This utility is a binary block extraction script designed to isolate `.rix` music resources from game package files. It identifies resource blocks by their distinctive signature:

- Header: `AA 55`
- Footer: `80`

It is intended as a focused extraction tool for older game packages, especially those containing music-related resources.

---

## 10. License

This project is intended for personal, research, and archival use in the context of reverse engineering and file recovery from game package data. Please ensure compliance with applicable copyright and distribution laws for the games and media involved.
