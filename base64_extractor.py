#!/usr/bin/env python3
"""
Base64 Archive Extractor

A flexible tool for decoding base64-encoded data and extracting archives.
Supports ZIP, RAR, TAR, and other common archive formats.

Usage:
    python base64_extractor.py [options]
    python base64_extractor.py -i input.txt -o extracted_files
    python base64_extractor.py --input data.b64 --format zip
"""

import base64
import zipfile
import tarfile
import os
import sys
import argparse
import re
from pathlib import Path
import tempfile
import shutil

class Base64ArchiveExtractor:
    def __init__(self):
        self.supported_formats = {
            'zip': self.extract_zip,
            'tar': self.extract_tar,
            'tar.gz': self.extract_tar,
            'tar.bz2': self.extract_tar,
            'tar.xz': self.extract_tar,
        }
        
        # Archive signatures for auto-detection
        self.archive_signatures = {
            b'PK\x03\x04': 'zip',
            b'PK\x05\x06': 'zip',
            b'PK\x07\x08': 'zip',
            b'Rar!': 'rar',
            b'\x1f\x8b': 'tar.gz',
            b'BZh': 'tar.bz2',
            b'\xfd7zXZ': 'tar.xz',
            b'ustar\x00': 'tar',
            b'ustar  \x00': 'tar',
        }
    
    def clean_base64_data(self, data):
        """Clean and normalize base64 data"""
        # Remove whitespace, newlines, and common prefixes
        data = re.sub(r'\s+', '', data)
        
        # Remove common base64 prefixes
        prefixes = [
            'data:',
            'data:application/zip;base64,',
            'data:application/octet-stream;base64,',
            'base64:',
        ]
        
        for prefix in prefixes:
            if data.lower().startswith(prefix.lower()):
                data = data[len(prefix):]
                break
        
        return data
    
    def read_base64_input(self, input_source):
        """Read base64 data from file, stdin, or string"""
        if input_source == '-' or input_source is None:
            print("[*] Reading from stdin (paste base64 data, then Ctrl+D)...")
            data = sys.stdin.read()
        elif os.path.isfile(input_source):
            print(f"[*] Reading from file: {input_source}")
            with open(input_source, 'r', encoding='utf-8') as f:
                data = f.read()
        else:
            # Treat as direct base64 string
            print("[*] Using provided base64 string")
            data = input_source
        
        return self.clean_base64_data(data)
    
    def decode_base64(self, b64_data):
        """Decode base64 data with error handling"""
        try:
            # Add padding if necessary
            missing_padding = len(b64_data) % 4
            if missing_padding:
                b64_data += '=' * (4 - missing_padding)
            
            decoded_data = base64.b64decode(b64_data)
            print(f"[+] Successfully decoded {len(decoded_data)} bytes")
            return decoded_data
        
        except Exception as e:
            print(f"[-] Error decoding base64: {e}")
            return None
    
    def detect_archive_format(self, data):
        """Auto-detect archive format from binary signature"""
        for signature, format_type in self.archive_signatures.items():
            if data.startswith(signature):
                return format_type
        
        # Check for TAR at offset 257 (where "ustar" signature appears)
        if len(data) > 262:
            tar_sig = data[257:262]
            if tar_sig == b'ustar':
                return 'tar'
        
        return None
    
    def save_decoded_file(self, data, output_dir, filename=None, format_hint=None):
        """Save decoded data to file with appropriate extension"""
        if not filename:
            # Auto-detect format
            detected_format = self.detect_archive_format(data)
            
            if format_hint and format_hint in self.supported_formats:
                file_format = format_hint
            elif detected_format:
                file_format = detected_format
            else:
                file_format = 'bin'  # Unknown format
            
            # Generate filename
            if file_format == 'zip':
                filename = 'decoded_archive.zip'
            elif file_format.startswith('tar'):
                filename = f'decoded_archive.{file_format}'
            elif file_format == 'rar':
                filename = 'decoded_archive.rar'
            else:
                filename = 'decoded_data.bin'
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(data)
        
        print(f"[+] Saved decoded file: {filepath}")
        return filepath, self.detect_archive_format(data)
    
    def extract_zip(self, archive_path, extract_dir):
        """Extract ZIP archive"""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                # Check for password protection
                try:
                    zip_ref.testzip()
                except RuntimeError as e:
                    if "Bad password" in str(e):
                        print("[-] ZIP file is password protected")
                        password = input("Enter password (or press Enter to skip): ").strip()
                        if password:
                            zip_ref.setpassword(password.encode())
                        else:
                            return False
                
                # List contents
                file_list = zip_ref.namelist()
                print(f"[*] ZIP contains {len(file_list)} files:")
                for filename in file_list[:10]:  # Show first 10 files
                    print(f"    - {filename}")
                if len(file_list) > 10:
                    print(f"    ... and {len(file_list) - 10} more files")
                
                # Extract all files
                zip_ref.extractall(extract_dir)
                print(f"[+] Extracted ZIP to: {extract_dir}")
                return True
                
        except zipfile.BadZipFile:
            print("[-] Invalid ZIP file")
            return False
        except Exception as e:
            print(f"[-] Error extracting ZIP: {e}")
            return False
    
    def extract_tar(self, archive_path, extract_dir):
        """Extract TAR archive (including compressed variants)"""
        try:
            # Try different compression modes
            modes = ['r', 'r:gz', 'r:bz2', 'r:xz']
            
            for mode in modes:
                try:
                    with tarfile.open(archive_path, mode) as tar_ref:
                        # List contents
                        members = tar_ref.getmembers()
                        print(f"[*] TAR contains {len(members)} items:")
                        for member in members[:10]:  # Show first 10 files
                            print(f"    - {member.name} ({member.size} bytes)")
                        if len(members) > 10:
                            print(f"    ... and {len(members) - 10} more items")
                        
                        # Extract all files
                        tar_ref.extractall(extract_dir)
                        print(f"[+] Extracted TAR to: {extract_dir}")
                        return True
                        
                except tarfile.ReadError:
                    continue
            
            print("[-] Could not read TAR file with any compression mode")
            return False
            
        except Exception as e:
            print(f"[-] Error extracting TAR: {e}")
            return False
    
    def extract_archive(self, archive_path, extract_dir, format_type=None):
        """Extract archive based on format"""
        if not format_type:
            # Auto-detect from file
            with open(archive_path, 'rb') as f:
                data = f.read(1024)  # Read first 1KB for detection
            format_type = self.detect_archive_format(data)
        
        if not format_type:
            print("[-] Could not detect archive format")
            return False
        
        print(f"[*] Detected format: {format_type}")
        
        if format_type == 'rar':
            print("[-] RAR extraction requires 'rarfile' library (pip install rarfile)")
            print("[*] You can manually extract the RAR file")
            return False
        
        if format_type in self.supported_formats:
            return self.supported_formats[format_type](archive_path, extract_dir)
        else:
            print(f"[-] Unsupported format: {format_type}")
            return False
    
    def analyze_extracted_files(self, extract_dir):
        """Analyze extracted files and provide summary"""
        if not os.path.exists(extract_dir):
            return
        
        files = []
        total_size = 0
        
        for root, dirs, filenames in os.walk(extract_dir):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, extract_dir)
                size = os.path.getsize(filepath)
                files.append((rel_path, size))
                total_size += size
        
        print(f"\n[*] Extraction Summary:")
        print(f"    Total files: {len(files)}")
        print(f"    Total size: {total_size:,} bytes ({total_size/1024:.1f} KB)")
        
        if files:
            print(f"    Files extracted:")
            for filepath, size in sorted(files)[:20]:  # Show first 20 files
                print(f"      - {filepath} ({size:,} bytes)")
            if len(files) > 20:
                print(f"      ... and {len(files) - 20} more files")
        
        # Look for interesting files
        interesting_extensions = ['.pdf', '.doc', '.docx', '.txt', '.log', '.key', '.pem', '.crt']
        interesting_files = [f for f, s in files if any(f.lower().endswith(ext) for ext in interesting_extensions)]
        
        if interesting_files:
            print(f"\n[*] Potentially interesting files:")
            for filepath in interesting_files:
                print(f"      - {filepath}")
    
    def process(self, input_source, output_dir, archive_format=None, keep_archive=False):
        """Main processing function"""
        print("="*60)
        print("BASE64 ARCHIVE EXTRACTOR")
        print("="*60)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Read and decode base64 data
        b64_data = self.read_base64_input(input_source)
        if not b64_data:
            print("[-] No base64 data found")
            return False
        
        print(f"[*] Base64 data length: {len(b64_data)} characters")
        
        decoded_data = self.decode_base64(b64_data)
        if not decoded_data:
            return False
        
        # Save decoded file
        archive_path, detected_format = self.save_decoded_file(
            decoded_data, output_dir, format_hint=archive_format
        )
        
        # Create extraction subdirectory
        extract_dir = os.path.join(output_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        # Extract archive
        success = self.extract_archive(archive_path, extract_dir, detected_format or archive_format)
        
        if success:
            self.analyze_extracted_files(extract_dir)
            
            # Clean up archive file if requested
            if not keep_archive:
                os.remove(archive_path)
                print(f"[*] Removed temporary archive: {archive_path}")
        else:
            print(f"[-] Extraction failed, archive saved at: {archive_path}")
        
        print(f"\n[+] Process complete. Output directory: {output_dir}")
        return success

def main():
    parser = argparse.ArgumentParser(
        description="Extract files from base64-encoded archives",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python base64_extractor.py                           # Read from stdin
  python base64_extractor.py -i data.txt              # Read from file
  python base64_extractor.py -i - -o my_output        # Stdin to custom output dir
  python base64_extractor.py -i data.b64 --format zip # Force ZIP format
  python base64_extractor.py -i data.txt --keep       # Keep intermediate archive file
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        default='-',
        help='Input file containing base64 data (default: stdin)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='extracted_files',
        help='Output directory (default: extracted_files)'
    )
    
    parser.add_argument(
        '--format',
        choices=['zip', 'tar', 'tar.gz', 'tar.bz2', 'tar.xz', 'rar'],
        help='Force specific archive format (auto-detect if not specified)'
    )
    
    parser.add_argument(
        '--keep',
        action='store_true',
        help='Keep the intermediate decoded archive file'
    )
    
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Only decode and analyze the archive, do not extract'
    )
    
    args = parser.parse_args()
    
    # Create extractor and process
    extractor = Base64ArchiveExtractor()
    
    try:
        success = extractor.process(
            input_source=args.input,
            output_dir=args.output,
            archive_format=args.format,
            keep_archive=args.keep or args.analyze_only
        )
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n[-] Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
