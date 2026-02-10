"""
Console Utilities
Format đẹp cho terminal output
"""

from colorama import Fore, Back, Style, init
from datetime import datetime

# Initialize colorama
init(autoreset=True)


class Console:
    """Console formatter với colors và styles"""
    
    @staticmethod
    def header(text: str):
        """Print header với border"""
        width = 70
        print(f"\n{Fore.CYAN}{'=' * width}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{text.center(width)}")
        print(f"{Fore.CYAN}{'=' * width}{Style.RESET_ALL}\n")
    
    @staticmethod
    def subheader(text: str):
        """Print subheader"""
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}▶ {text}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'-' * 60}{Style.RESET_ALL}")
    
    @staticmethod
    def success(text: str):
        """Print success message"""
        print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")
    
    @staticmethod
    def error(text: str):
        """Print error message"""
        print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")
    
    @staticmethod
    def warning(text: str):
        """Print warning message"""
        print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")
    
    @staticmethod
    def info(text: str):
        """Print info message"""
        print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")
    
    @staticmethod
    def crawling(domain: str):
        """Print crawling message"""
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}🕷️  Crawling: {domain}{Style.RESET_ALL}")
    
    @staticmethod
    def article(title: str, status: str = "new"):
        """Print article info"""
        if status == "new":
            icon = f"{Fore.GREEN}📰"
            status_text = f"{Fore.GREEN}NEW"
        else:
            icon = f"{Fore.YELLOW}📄"
            status_text = f"{Fore.YELLOW}SKIP"
        
        # Truncate title if too long
        max_len = 50
        if len(title) > max_len:
            title = title[:max_len] + "..."
        
        print(f"  {icon} [{status_text}{Style.RESET_ALL}] {title}")
    
    @staticmethod
    def stats(domain: str, new: int, duplicate: int, total: int):
        """Print crawl statistics"""
        print(f"\n{Fore.CYAN}📊 Statistics for {domain}:{Style.RESET_ALL}")
        print(f"  {Fore.GREEN}✓ New articles:      {new}{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}⊘ Duplicates:        {duplicate}{Style.RESET_ALL}")
        print(f"  {Fore.BLUE}Σ Total processed:   {total}{Style.RESET_ALL}")
    
    @staticmethod
    def schedule_info(domain: str, schedule: str):
        """Print schedule information"""
        print(f"{Fore.CYAN}⏰ {domain}: {Fore.WHITE}{schedule}{Style.RESET_ALL}")
    
    @staticmethod
    def separator():
        """Print separator line"""
        print(f"{Fore.WHITE}{Style.DIM}{'─' * 70}{Style.RESET_ALL}")
    
    @staticmethod
    def database_info(count: int):
        """Print database info"""
        print(f"\n{Fore.CYAN}💾 Database: {Fore.WHITE}{count} total articles{Style.RESET_ALL}")
    
    @staticmethod
    def waiting():
        """Print waiting message"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}⏳ Scheduler running... Press Ctrl+C to stop{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{Style.DIM}Checking for scheduled jobs every minute...{Style.RESET_ALL}\n")
    
    @staticmethod
    def timestamp():
        """Print current timestamp"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Fore.WHITE}{Style.DIM}[{now}]{Style.RESET_ALL}")
    
    @staticmethod
    def banner():
        """Print application banner"""
        banner = f"""
{Fore.CYAN}{Style.BRIGHT}
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              🗞️  X-WISE NEWS CRAWLER SYSTEM  🗞️                     ║
║                                                                   ║
║                    Automated News Collection                      ║
║                         Version 1.0.0                             ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
        print(banner)
