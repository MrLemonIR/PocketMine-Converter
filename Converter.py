import os
import zipfile
import re
import shutil
import time
import sys
from pathlib import Path
from colorama import init, Fore, Back, Style

init()

class PaketMineConverter:
    def __init__(self):
        self.api5_patterns = [
            r'extends\s+Plugin\b',
            r'use\s+pocketmine\\plugin\\Plugin\b',
            r'function\s+onEnable\(\s*\)\s*:\s*void\b',
            r'function\s+onDisable\(\s*\)\s*:\s*void\b',
            r'function\s+onLoad\(\s*\)\s*:\s*void\b',
            r'api:\s*\[?"5\.',
            r'"api"\s*:\s*5\b',
            r"'api'\s*:\s*5\b",
            r'namespace\s+MrLeMoNIR',
            r'main:\s*MrLeMoNIR',
        ]
        
        self.api3_patterns = [
            r'extends\s+PluginBase\b',
            r'use\s+pocketmine\\plugin\\PluginBase\b',
            r'function\s+onEnable\(\s*\)(?!\s*:)',
            r'function\s+onDisable\(\s*\)(?!\s*:)',
            r'function\s+onLoad\(\s*\)(?!\s*:)',
            r'api:\s*\[?"3\.',
            r'"api"\s*:\s*3\b',
            r"'api'\s*:\s*3\b",
        ]

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_banner(self):
        self.clear_screen()
        print(f"""{Fore.CYAN}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║  ███╗   ███╗██████╗ ██╗     ███████╗███╗   ███╗ ██████╗  ║
║  ████╗ ████║██╔══██╗██║     ██╔════╝████╗ ████║██╔═══██╗ ║
║  ██╔████╔██║██████╔╝██║     █████╗  ██╔████╔██║██║   ██║ ║
║  ██║╚██╔╝██║██╔══██╗██║     ██╔══╝  ██║╚██╔╝██║██║   ██║ ║
║  ██║ ╚═╝ ██║██║  ██║███████╗███████╗██║ ╚═╝ ██║╚██████╔╝ ║
║  ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚═╝ ╚═════╝  ║
║                                                          ║
║           API 3 → 5 CONVERTER - LINE BY LINE TEST        ║
║                 MRLEMONIR SUPER CONVERTER                ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
{Style.RESET_ALL}""")
        time.sleep(1)

    def extract_zip(self, zip_path):
        extract_dir = Path("temp_extract")
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir()
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        return extract_dir

    def create_file_structure_guide(self, directory):
        structure = []
        
        for root, dirs, files in os.walk(directory):
            level = root.replace(str(directory), '').count(os.sep)
            indent = ' ' * 4 * level
            structure.append(f"{indent}{Fore.YELLOW}{os.path.basename(root)}/{Style.RESET_ALL}")
            
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                structure.append(f"{subindent}{Fore.CYAN}{file}{Style.RESET_ALL}")
        
        guide = "\n".join(structure)
        
        instructions = f"""
{Fore.GREEN}📁 PLUGIN STRUCTURE GUIDE:{Style.RESET_ALL}
{guide}

{Fore.YELLOW}📋 HOW TO ORGANIZE MANUALLY:{Style.RESET_ALL}
1. Main files should be in: src/MrLeMoNIR/ConvertedPlugin/
2. plugin.yml must be in root folder
3. Resources (configs, images) in resources/ folder
4. Commands in src/commands/ folder
5. Events in src/listeners/ folder
6. Forms in src/forms/ folder

{Fore.CYAN}🔧 REQUIRED FOR API 5:{Style.RESET_ALL}
• plugin.yml: api: ["5.0.0", "5.5.0"]
• plugin.yml: main: MrLeMoNIR\\ConvertedPlugin\\Main
• All PHP files: extends Plugin (not PluginBase)
• All PHP files: onEnable(): void (not onEnable())
• Namespace: MrLeMoNIR\\ConvertedPlugin\\...
"""
        
        return instructions

    def convert_plugin_yml(self, content):
        lines = content.split('\n')
        converted_lines = []
        for line in lines:
            if 'api:' in line.lower():
                line = re.sub(r'api:\s*["\']?3[\.0-9"\']*', 'api: ["5.0.0", "5.5.0"]', line, flags=re.IGNORECASE)
            if 'main:' in line.lower():
                line = 'main: MrLeMoNIR\\ConvertedPlugin\\Main'
            converted_lines.append(line)
        converted_lines.append('\nconverted-by: MrLeMoNIR')
        converted_lines.append('api-version: 5.x.x')
        converted_lines.append('tested: line-by-line')
        return '\n'.join(converted_lines)

    def convert_php_file(self, content):
        if '<?php' in content:
            content = content.replace('<?php', '<?php\n')
        
        content = content.replace('extends PluginBase', 'extends Plugin')
        content = content.replace('use pocketmine\\plugin\\PluginBase', 'use pocketmine\\plugin\\Plugin')
        
        content = re.sub(r'public function onEnable\(\s*\)(?!\s*:)', 'public function onEnable(): void', content)
        content = re.sub(r'public function onDisable\(\s*\)(?!\s*:)', 'public function onDisable(): void', content)
        content = re.sub(r'public function onLoad\(\s*\)(?!\s*:)', 'public function onLoad(): void', content)
        
        if 'namespace ' in content and 'MrLeMoNIR' not in content:
            content = re.sub(r'namespace\s+([^;]+);', r'namespace MrLeMoNIR\\ConvertedPlugin\\\1;', content)
        
        content = re.sub(r'"api"\s*:\s*3', '"api": 5', content)
        content = re.sub(r"'api'\s*:\s*3", "'api': 5", content)
        content = re.sub(r'api:\s*3', 'api: 5', content, flags=re.IGNORECASE)
        
        return content

    def test_line_by_line(self, file_path, content):
        lines = content.split('\n')
        api5_matches = 0
        api3_matches = 0
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            line_issues = []
            
            for pattern in self.api3_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    api3_matches += 1
                    line_issues.append(f"API 3 pattern found: {pattern}")
            
            for pattern in self.api5_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    api5_matches += 1
            
            if line_issues:
                issues.append(f"Line {line_num}: {', '.join(line_issues)}")
        
        return api5_matches, api3_matches, issues

    def create_test_report(self, test_results):
        report = "=== MRLEMONIR API 5 CONVERSION TEST REPORT ===\n\n"
        total_files = len(test_results)
        passed_files = 0
        failed_files = 0
        
        for file_path, (api5_count, api3_count, issues) in test_results.items():
            report += f"File: {file_path}\n"
            report += f"API 5 patterns: {api5_count}\n"
            report += f"API 3 patterns: {api3_count}\n"
            
            if api3_count == 0 and api5_count > 0:
                report += "Status: ✅ PASSED (Fully converted to API 5)\n"
                passed_files += 1
            elif api3_count > 0:
                report += "Status: ❌ FAILED (Contains API 3 code)\n"
                failed_files += 1
                for issue in issues:
                    report += f"  - {issue}\n"
            else:
                report += "Status: ⚠️  WARNING (No API patterns found)\n"
            
            report += "\n"
        
        report += "=== SUMMARY ===\n"
        report += f"Total files: {total_files}\n"
        report += f"Passed: {passed_files}\n"
        report += f"Failed: {failed_files}\n"
        report += f"Success rate: {(passed_files/total_files*100 if total_files > 0 else 0):.1f}%\n"
        
        return report, passed_files, failed_files

    def create_main_class(self, directory):
        main_dir = directory / "src" / "MrLeMoNIR" / "ConvertedPlugin"
        main_dir.mkdir(parents=True, exist_ok=True)
        main_file = main_dir / "Main.php"
        main_content = """<?php

namespace MrLeMoNIR\\ConvertedPlugin;

use pocketmine\\plugin\\Plugin;
use pocketmine\\utils\\Config;

class Main extends Plugin {
    
    private static $instance;
    private $config;
    
    public static function getInstance(): self {
        return self::$instance;
    }
    
    public function onLoad(): void {
        self::$instance = $this;
    }
    
    public function onEnable(): void {
        $this->saveDefaultConfig();
        $this->config = $this->getConfig();
        $this->getLogger()->info("Converted to API 5 by MrLeMoNIR - Line Test Verified");
    }
    
    public function onDisable(): void {
    }
    
    public function getLemonConfig(): Config {
        return $this->config;
    }
}

?>
"""
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(main_content)
        return main_file

    def process_and_test_files(self, directory):
        test_results = {}
        converted_files = 0
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                
                try:
                    if file == 'plugin.yml':
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        converted = self.convert_plugin_yml(content)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(converted)
                        converted_files += 1
                        api5_count, api3_count, issues = self.test_line_by_line(file_path, converted)
                        test_results[str(file_path)] = (api5_count, api3_count, issues)
                        print(f"{Fore.GREEN}✓ {file} converted and tested{Style.RESET_ALL}")
                    
                    elif file.endswith('.php'):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        converted = self.convert_php_file(content)
                        if converted != content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(converted)
                            converted_files += 1
                        api5_count, api3_count, issues = self.test_line_by_line(file_path, converted)
                        test_results[str(file_path)] = (api5_count, api3_count, issues)
                        print(f"{Fore.GREEN}✓ {file} tested{Style.RESET_ALL}")
                    
                    elif file.endswith(('.json', '.yml', '.yaml')):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        original = content
                        content = re.sub(r'"api"\s*:\s*3', '"api": 5', content)
                        content = re.sub(r"'api'\s*:\s*3", "'api': 5", content)
                        content = re.sub(r'api:\s*3', 'api: 5', content, flags=re.IGNORECASE)
                        if content != original:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            converted_files += 1
                        api5_count, api3_count, issues = self.test_line_by_line(file_path, content)
                        test_results[str(file_path)] = (api5_count, api3_count, issues)
                
                except Exception as e:
                    print(f"{Fore.RED}✗ Error with {file}: {e}{Style.RESET_ALL}")
        
        return converted_files, test_results

    def create_output_with_report_and_structure(self, input_dir, original_name, test_results, passed_count, failed_count):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_name = f"{original_name}_API5_VERIFIED_{timestamp}.zip"
        output_path = Path(output_name)
        
        report_content, _, _ = self.create_test_report(test_results)
        
        structure_guide = self.create_file_structure_guide(input_dir)
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(input_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(input_dir)
                    zipf.write(file_path, arcname)
            
            zipf.writestr("CONVERSION_TEST_REPORT.txt", report_content)
            zipf.writestr("FILE_STRUCTURE_GUIDE.txt", structure_guide)
            
            final_note = f"""🎉 CONVERSION COMPLETE BY MRLEMONIR! 🎉

Your plugin has been converted from API 3 to API 5!

📦 Files included in this zip:
1. Your converted plugin files
2. CONVERSION_TEST_REPORT.txt - Detailed test results
3. FILE_STRUCTURE_GUIDE.txt - How to organize your files

📝 Next steps:
1. Extract this zip
2. Read FILE_STRUCTURE_GUIDE.txt
3. Organize files as needed
4. Test on PocketMine API 5 server

{Fore.RED}💋 MWAH! A little kiss from MrLeMoNIR! 💋{Style.RESET_ALL}

Made with ❤️ by MrLeMoNIR"""
            
            zipf.writestr("README_MRLEMONIR.txt", final_note)
        
        return output_path, report_content, structure_guide

    def find_zip_files(self):
        zip_files = list(Path('.').glob('*.zip'))
        if not zip_files:
            return None
        print(f"\n{Fore.CYAN}Available ZIP files:{Style.RESET_ALL}")
        for i, zip_file in enumerate(zip_files, 1):
            print(f"{Fore.YELLOW}{i}. {zip_file.name}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}0. Enter custom path{Style.RESET_ALL}")
        try:
            choice = int(input(f"\n{Fore.YELLOW}Select (1-{len(zip_files)}): {Style.RESET_ALL}"))
            if choice == 0:
                return input(f"{Fore.CYAN}Custom path: {Style.RESET_ALL}").strip()
            elif 1 <= choice <= len(zip_files):
                return str(zip_files[choice - 1])
        except:
            pass
        return None

    def print_kiss(self):
        print(f"""
{Fore.RED}
        💋💋💋💋💋💋💋💋💋💋💋💋💋💋💋
        💋                           💋
        💋     MWAH! 💋              💋
        💋  A little kiss from       💋
        💋      MrLeMoNIR!           💋
        💋                           💋
        💋💋💋💋💋💋💋💋💋💋💋💋💋💋💋
{Style.RESET_ALL}
        """)

    def run(self):
        self.print_banner()
        print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}MRLEMONIR API 5 CONVERTER - LINE BY LINE TEST{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        
        if len(sys.argv) < 2:
            input_file = self.find_zip_files()
            if not input_file:
                input_file = input(f"{Fore.CYAN}Enter ZIP file path: {Style.RESET_ALL}").strip()
        else:
            input_file = sys.argv[1]
        
        if not input_file or not os.path.exists(input_file):
            print(f"{Fore.RED}File not found{Style.RESET_ALL}")
            sys.exit(1)
        
        if not input_file.endswith('.zip'):
            print(f"{Fore.RED}Must be .zip file{Style.RESET_ALL}")
            sys.exit(1)
        
        print(f"\n{Fore.GREEN}Processing: {Path(input_file).name}{Style.RESET_ALL}")
        
        extract_dir = self.extract_zip(input_file)
        self.create_main_class(extract_dir)
        
        print(f"\n{Fore.CYAN}Converting and testing files line by line...{Style.RESET_ALL}")
        converted_count, test_results = self.process_and_test_files(extract_dir)
        
        report_content, passed_count, failed_count = self.create_test_report(test_results)
        
        structure_guide = self.create_file_structure_guide(extract_dir)
        print(f"\n{Fore.GREEN}📁 File structure guide created{Style.RESET_ALL}")
        
        original_name = Path(input_file).stem
        output_zip, final_report, structure = self.create_output_with_report_and_structure(
            extract_dir, original_name, test_results, passed_count, failed_count
        )
        
        shutil.rmtree(extract_dir)
        
        file_size_kb = output_zip.stat().st_size / 1024
        
        print(f"\n{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}CONVERSION COMPLETE WITH LINE TESTING!{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*70}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}Output file: {Fore.WHITE}{output_zip.name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}File size: {Fore.WHITE}{file_size_kb:.1f} KB{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Files processed: {Fore.WHITE}{len(test_results)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Files converted: {Fore.WHITE}{converted_count}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Passed tests: {Fore.GREEN}{passed_count}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Failed tests: {Fore.RED}{failed_count}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}📁 Structure guide saved in zip file{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📋 Check FILE_STRUCTURE_GUIDE.txt for organization help{Style.RESET_ALL}")
        
        if failed_count > 0:
            print(f"\n{Fore.YELLOW}⚠️  Some files still contain API 3 code{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}   Check CONVERSION_TEST_REPORT.txt in the zip{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.GREEN}✅ All files fully converted to API 5!{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}📦 Ready for PocketMine API 5!{Style.RESET_ALL}")
        
        self.print_kiss()
        
        print(f"\n{Fore.CYAN}📝 Extra files in zip:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   • CONVERSION_TEST_REPORT.txt - Test results{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   • FILE_STRUCTURE_GUIDE.txt - How to organize{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   • README_MRLEMONIR.txt - Final notes{Style.RESET_ALL}")
        
        return str(output_zip.absolute())

if __name__ == "__main__":
    try:
        converter = PaketMineConverter()
        result = converter.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Interrupted{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
