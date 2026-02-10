"""
Main Entry Point
Khởi động crawler system
"""

import sys
import json
import argparse
from pathlib import Path
from loguru import logger

# Setup logger first
from utils.logger import setup_logger
from utils.console import Console

from utils.db_client import DatabaseClient
from engine.static_crawler import StaticCrawler


def load_domain_configs():
    """Load tất cả domain configurations"""
    config_dir = Path('config/domains')
    configs = []
    
    if not config_dir.exists():
        Console.error(f"Config directory not found: {config_dir}")
        return configs
    
    for config_file in config_dir.glob('*.json'):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                configs.append(config)
                Console.info(f"Loaded config: {config['name']}", icon=False)
        except Exception as e:
            Console.error(f"Error loading {config_file}: {e}")
    
    return configs


def run_once(domain_name: str = None):
    """
    Chạy crawler một lần (không dùng scheduler)
    
    Args:
        domain_name: Tên domain cần crawl, None = all domains
    """
    Console.subheader("🔄 ONE-TIME CRAWL MODE")
    
    # Load configs
    configs = load_domain_configs()
    
    if not configs:
        Console.error("No domain configs found!")
        return
    
    # Filter by domain name if specified
    if domain_name:
        configs = [c for c in configs if c['domain'] == domain_name or c['name'] == domain_name]
        if not configs:
            Console.error(f"Domain not found: {domain_name}")
            return
    
    # Initialize Database client
    try:
        Console.info(f"{Console.ICON_DATABASE} Connecting to database...", icon=False)
        db_client = DatabaseClient()
        Console.success(f"{Console.ICON_CHECK} Database connected", icon=False)
    except Exception as e:
        Console.error(f"Failed to initialize database client: {e}")
        Console.error("Please check database configuration in .env file")
        return
    
    # Run crawlers
    for config in configs:
        if not config.get('enabled', True):
            Console.warning(f"Skipping disabled domain: {config['name']}")
            continue
        
        Console.crawl_start(config['name'])
        
        try:
            crawler_type = config.get('crawler_type', 'static')
            
            if crawler_type == 'static':
                crawler = StaticCrawler(config, db_client)
                crawler.run()
            else:
                Console.warning(f"Unsupported crawler type: {crawler_type}")
                
        except Exception as e:
            Console.error(f"Error crawling {config['name']}: {e}")
    
    # Show summary
    try:
        total_news = db_client.get_news_count()
        Console.summary_box("📊 CRAWL SUMMARY", {
            "Total news in database": total_news,
            "Status": "✅ Complete"
        })
    except Exception:
        pass


def run_scheduler():
    """Chạy crawler với scheduler"""
    import schedule
    import time
    from datetime import datetime
    
    Console.subheader("🕐 SCHEDULER MODE")
    Console.info("Crawler will run automatically based on schedule", icon=False)
    Console.warning("Press Ctrl+C to stop", icon=False)
    print()
    
    # Load configs
    configs = load_domain_configs()
    
    if not configs:
        Console.error("No domain configs found!")
        return
    
    # Initialize Database client
    try:
        Console.info(f"{Console.ICON_DATABASE} Connecting to database...", icon=False)
        db_client = DatabaseClient()
        Console.success(f"{Console.ICON_CHECK} Database connected", icon=False)
        print()
    except Exception as e:
        Console.error(f"Failed to initialize database client: {e}")
        return
    
    # Setup scheduled jobs for each domain
    Console.subheader("📅 SCHEDULED JOBS")
    scheduled_count = 0
    
    for config in configs:
        if not config.get('enabled', True):
            Console.warning(f"⊘ Disabled: {config['name']}")
            continue
        
        # Get schedule config
        schedule_config = config.get('schedule', {})
        cron = schedule_config.get('cron', '0 */2 * * *')
        description = schedule_config.get('description', 'No description')
        
        # Parse cron to schedule format
        parts = cron.split()
        
        if len(parts) >= 2:
            minute = parts[0]
            hour = parts[1]
            
            # Create job function for this domain
            def create_job(domain_config):
                def job():
                    Console.crawl_start(f"[Scheduled] {domain_config['name']}")
                    try:
                        crawler = StaticCrawler(domain_config, db_client)
                        crawler.run()
                    except Exception as e:
                        Console.error(f"Error in scheduled crawl for {domain_config['name']}: {e}")
                return job
            
            # Schedule based on cron pattern
            if hour.startswith('*/'):
                hours = int(hour.replace('*/', ''))
                schedule.every(hours).hours.do(create_job(config))
                Console.success(f"{Console.ICON_CLOCK} {config['name']}: Every {hours} hours", icon=False)
                scheduled_count += 1
            elif hour == '*':
                schedule.every().hour.do(create_job(config))
                Console.success(f"{Console.ICON_CLOCK} {config['name']}: Every hour", icon=False)
                scheduled_count += 1
            else:
                time_str = f"{hour.zfill(2)}:{minute.zfill(2)}"
                schedule.every().day.at(time_str).do(create_job(config))
                Console.success(f"{Console.ICON_CLOCK} {config['name']}: Daily at {time_str}", icon=False)
                scheduled_count += 1
    
    if scheduled_count == 0:
        Console.error("No domains scheduled!")
        return
    
    # Run initial crawl
    Console.header("🚀 INITIAL CRAWL")
    run_once()
    
    # Start scheduler loop
    Console.header("⏳ SCHEDULER RUNNING")
    Console.info("Waiting for next scheduled run...", icon=False)
    Console.info(f"Active jobs: {scheduled_count}", icon=False)
    print()
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            print()
            Console.warning("Scheduler stopped by user")
            break
        except Exception as e:
            Console.error(f"Scheduler error: {e}")
            time.sleep(60)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='X-Wise News Crawler')
    parser.add_argument(
        '--mode',
        choices=['once', 'scheduler'],
        default='once',
        help='Run mode: once (one-time) or scheduler (continuous)'
    )
    parser.add_argument(
        '--domain',
        type=str,
        help='Domain to crawl (only for once mode)'
    )
    
    args = parser.parse_args()
    
    # Print banner
    Console.banner()
    
    try:
        if args.mode == 'once':
            run_once(args.domain)
        else:
            run_scheduler()
            
    except KeyboardInterrupt:
        print()
        Console.warning("Crawler stopped by user")
    except Exception as e:
        Console.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
