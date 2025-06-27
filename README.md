# Base64 Archive Extractor

A powerful and flexible Python tool for decoding base64-encoded data and extracting various archive formats. Perfect for CTF challenges, digital forensics, data recovery, and general archive processing tasks.

## 🚀 Features

- **Multi-Format Support**: ZIP, TAR (all variants), RAR detection
- **Flexible Input**: Files, stdin, direct strings, with auto-cleaning
- **Smart Detection**: Automatic archive format recognition via magic numbers
- **Password Support**: Handles password-protected ZIP files
- **Comprehensive Analysis**: File inventory, size reporting, interesting file detection
- **Robust Error Handling**: Graceful handling of corrupted or invalid data
- **Security Focused**: Safe extraction with path validation

## 📦 Supported Formats

| Format | Extension | Extraction | Notes |
|--------|-----------|------------|-------|
| ZIP | `.zip` | ✅ Full support | Includes password protection |
| TAR | `.tar` | ✅ Full support | Uncompressed archives |
| GZIP | `.tar.gz`, `.tgz` | ✅ Full support | GZip compressed TAR |
| BZIP2 | `.tar.bz2`, `.tbz2` | ✅ Full support | BZip2 compressed TAR |
| XZ | `.tar.xz`, `.txz` | ✅ Full support | XZ compressed TAR |
| RAR | `.rar` | 🔍 Detection only | Requires `rarfile` library |

## 🛠️ Installation

### Requirements
- Python 3.6+
- No external dependencies for basic functionality

### Optional Dependencies
```bash
# For RAR extraction support
pip install rarfile

# For enhanced compression support
pip install lzma backports.lzma
```

### Quick Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/base64-archive-extractor.git
cd base64-archive-extractor

# Make executable (optional)
chmod +x base64_extractor.py

# Test with help
python base64_extractor.py --help
```

## 💻 Usage

### Basic Examples

#### Extract from stdin
```bash
# Paste base64 data directly
python base64_extractor.py
# Paste your base64 data, then Ctrl+D (Linux/Mac) or Ctrl+Z (Windows)
```

#### Extract from file
```bash
# Read base64 from file
python base64_extractor.py -i encoded_data.txt

# Specify custom output directory
python base64_extractor.py -i data.b64 -o my_extraction_folder
```

#### Pipeline usage
```bash
# From clipboard (Linux)
xclip -o | python base64_extractor.py

# From web download
curl -s https://example.com/data.b64 | python base64_extractor.py

# From another command
echo "UEsDBBQAAAAI..." | python base64_extractor.py
```

### Advanced Options

#### Force specific format
```bash
# Force ZIP extraction even if detection fails
python base64_extractor.py -i data.txt --format zip

# Force TAR.GZ extraction
python base64_extractor.py -i data.b64 --format tar.gz
```

#### Keep intermediate files
```bash
# Keep the decoded archive file for manual inspection
python base64_extractor.py -i data.txt --keep
```

#### Analysis only
```bash
# Decode and analyze without extracting
python base64_extractor.py -i data.b64 --analyze-only
```

### Command-Line Options

```
usage: base64_extractor.py [-h] [-i INPUT] [-o OUTPUT] 
                          [--format {zip,tar,tar.gz,tar.bz2,tar.xz,rar}]
                          [--keep] [--analyze-only]

Extract files from base64-encoded archives

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file containing base64 data (default: stdin)
  -o OUTPUT, --output OUTPUT
                        Output directory (default: extracted_files)
  --format {zip,tar,tar.gz,tar.bz2,tar.xz,rar}
                        Force specific archive format (auto-detect if not specified)
  --keep                Keep the intermediate decoded archive file
  --analyze-only        Only decode and analyze the archive, do not extract
```

## 📋 Example Output

```
============================================================
BASE64 ARCHIVE EXTRACTOR
============================================================
[*] Reading from file: encoded_data.txt
[*] Base64 data length: 45234 characters
[+] Successfully decoded 33891 bytes
[+] Saved decoded file: extracted_files/decoded_archive.zip
[*] Detected format: zip
[*] ZIP contains 15 files:
    - document.pdf
    - images/photo1.jpg
    - data/config.json
    ... and 12 more files
[+] Extracted ZIP to: extracted_files/extracted

[*] Extraction Summary:
    Total files: 15
    Total size: 2,845,692 bytes (2779.0 KB)
    Files extracted:
      - document.pdf (1,245,760 bytes)
      - images/photo1.jpg (892,445 bytes)
      - data/config.json (1,234 bytes)

[*] Potentially interesting files:
      - document.pdf
      - data/config.json
      - certificates/private.key

[+] Process complete. Output directory: extracted_files
```

## 🎯 Use Cases

### CTF Challenges
- **Hidden Archives**: Extract files from base64-encoded ZIP/TAR data
- **Multi-Stage Challenges**: Decode nested archives and data
- **Steganography**: Recover hidden archive data from various sources
- **Forensics**: Analyze extracted files for flags and clues

### Digital Forensics
- **Evidence Recovery**: Extract archived evidence from base64 data
- **Data Carving**: Recover archives from network captures or memory dumps
- **Incident Response**: Analyze suspicious archive files
- **Malware Analysis**: Extract payload archives from encoded samples

### Data Recovery
- **Backup Restoration**: Recover files from base64-encoded backups
- **Email Attachments**: Extract archives from email-encoded attachments
- **Database Recovery**: Decode archived data stored in databases
- **Cloud Storage**: Process base64-encoded archive data from APIs

### General Use
- **API Responses**: Handle base64-encoded file downloads
- **Configuration Management**: Extract configuration archives
- **Automation**: Integrate into data processing pipelines
- **File Conversion**: Convert between base64 and archive formats

## 🔧 Technical Details

### Base64 Cleaning
The tool automatically handles various base64 formats:
- Removes whitespace and newlines
- Strips common prefixes (`data:`, `base64:`, etc.)
- Corrects missing padding
- Validates encoding before processing

### Archive Detection
Uses binary signatures (magic numbers) for format detection:
- **ZIP**: `PK\x03\x04`, `PK\x05\x06`, `PK\x07\x08`
- **RAR**: `Rar!`
- **GZIP**: `\x1f\x8b`
- **BZIP2**: `BZh`
- **XZ**: `\xfd7zXZ`
- **TAR**: `ustar` at offset 257

### Security Features
- **Path Validation**: Prevents directory traversal attacks
- **Safe Extraction**: Validates extraction paths
- **Size Limits**: Monitors extraction sizes
- **Error Isolation**: Handles corrupted archives safely

## 🚨 Troubleshooting

### Common Issues

**"Invalid base64 encoding" error**
- Check for missing characters or corruption
- Verify the data is actually base64-encoded
- Try cleaning the data manually (remove extra characters)

**"Could not detect archive format" warning**
- Use `--format` to force a specific format
- Check if the decoded data is actually an archive
- Use `--analyze-only` to inspect the raw decoded data

**"Password protected" ZIP files**
- The tool will prompt for passwords automatically
- Common passwords: `password`, `123456`, `infected`
- For automated processing, consider using ZIP cracking tools

**Memory issues with large files**
- Large archives may require significant RAM
- Consider using `--analyze-only` for inspection first
- Split large base64 data into smaller chunks if needed

### Debug Steps

1. **Verify Input**: Ensure base64 data is valid
   ```bash
   echo "your_base64_data" | base64 -d > test.bin
   file test.bin
   ```

2. **Check Format**: Use analysis mode
   ```bash
   python base64_extractor.py -i data.txt --analyze-only
   ```

3. **Force Format**: Try specific formats
   ```bash
   python base64_extractor.py -i data.txt --format zip
   ```

4. **Manual Inspection**: Keep intermediate files
   ```bash
   python base64_extractor.py -i data.txt --keep
   ```

## 🤝 Contributing

Contributions are welcome! Here are ways you can help:

### Adding Format Support
- Implement new archive format extractors
- Add magic number signatures for detection
- Enhance compression algorithm support

### Improving Functionality
- Add GUI interface
- Implement recursive archive extraction
- Add file content analysis
- Enhance password cracking capabilities

### Bug Fixes & Enhancements
- Improve error handling
- Optimize memory usage for large files
- Add progress bars for long operations
- Enhance cross-platform compatibility

### Development Setup
```bash
git clone https://github.com/yourusername/base64-archive-extractor.git
cd base64-archive-extractor

# Install development dependencies
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black base64_extractor.py

# Lint code
flake8 base64_extractor.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Related Tools

- **[file](https://linux.die.net/man/1/file)**: File type identification
- **[binwalk](https://github.com/ReFirmLabs/binwalk)**: Firmware analysis and extraction
- **[foremost](http://foremost.sourceforge.net/)**: File carving tool
- **[7zip](https://www.7-zip.org/)**: Universal archive tool
- **[rarfile](https://pypi.org/project/rarfile/)**: Python RAR support

## 📞 Support

If you encounter issues or have questions:

1. **Check the troubleshooting section** above
2. **Search existing issues** on GitHub
3. **Create a new issue** with:
   - Sample base64 data (if not sensitive)
   - Error messages and output
   - Operating system and Python version
   - Steps to reproduce the problem

## 🏆 Acknowledgments

- **Archive format specifications** from various RFC documents
- **Magic number databases** from file type identification projects
- **CTF community** for testing and feedback
- **Digital forensics community** for use case insights
- **Python community** for excellent libraries and documentation

---

**Happy extracting!** 🗃️✨
