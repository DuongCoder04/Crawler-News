"""
Main Entry Point - Enhanced Version
Khởi động crawler system với beautiful console output
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
                logger.info(f"Loaded config: {config['name']}")
        except Exception as e:
            Console.error(f"Error loading {config_file}: {e}")
    
    return configs


def run_once(domain_name: str = None):
    """
    Chạy crawler một lần (không dùng scheduler)
    
    Args:
        domain_name: Tên domain cần crawl, None = all domains
    """
    Console.subheader("One-Time Crawl Mode")
    
    # Load configs
    configs = load_domain_configs()
    
    if not configs:
        Console.error("No domain configs found!")
        return
    
    Console.info(f"Loaded {len(configs)} domain configurations")
    
    # Filter by domain name if specified
    if domain_name:
        configs = [c for c in configs 
                  if c['domain'].lower() == domain_name.lower() 
                  or c['name'].lower() == domain_name.lower()]
        if not configs:
            Console.error(f"Domain not found: {domain_name}")
            return
        Console.info(f"Filtering for domain: {domain_name}")
    
    # Initialize Database client
    try:
        db_client = DatabaseClient()
        Console.success(f"Connected to database: {db_client.connection_params['database']}@{db_client.connection_params['host']}")
    except Exception as e:
        Console.error(f"Failed to connect to database: {e}")
        Console.warning("Please check database configuration in .env file")
        return
    
    # Run crawlers
    total_new = 0
    total_duplicate = 0
    
    for config in configs:
        if not config.get('enabled', True):
            Console.warning(f"Skipping disabled domain: {config['name']}")
            continue
        
        Console.crawling(config['name'])
        
        try:
            crawler_type = config.get('crawler_type', 'static')
            
            if crawler_type == 'static':
                crawler = StaticCrawler(config, db_client)
                result = crawler.run()
                
                # Show stats if available
                if hasattr(crawler, 'stats'):
                    stats = crawler.stats
                    Console.stats(
                        config['name'],
                        stats.get('new', 0),
                        stats.get('duplicate', 0),
                        stats.get('total', 0)
                    )
                    total_new += stats.get('new', 0)
                    total_duplicate += stats.get('duplicate', 0)
            else:
                Console.warning(f"Unsupported crawler type: {crawler_type}")
                
        except Exception as e:
            Console.error(f"Error crawling {config['name']}: {e}")
            logger.exception(e)
    
    # Show summary
    Console.separator()
    Console.subheader("Crawl Summary")
    Console.success(f"New articles: {total_new}")
    Console.info(f"Duplicates skipped: {total_duplicate}")
    
    try:
        total_news = db_client.get_news_count()
        Console.database_info(total_news)
    except Exception:
        pass


def run_scheduler():
    """Chạy crawler với scheduler"""
    import schedule
    import time
    from datetime import datetime
    
    Console.subheader("Scheduler Mode")
    Console.info("Crawler will run automatically based on schedule configuration")
    Console.warning("Press Ctrl+C to stop")
    
    # Load configs
    configs = load_domain_configs()
    
    if not configs:
        Console.error("No domain configs found!")
        return
    
    # Initialize Database client
    try:
        db_client = DatabaseClient()
        Console.success(f"Connected to database: {db_client.connection_params['database']}@{db_client.connection_params['host']}")
    except Exception as e:
        Console.error(f"Failed to connect to database: {e}")
        return
    
    # Setup scheduled jobs for each domain
    Console.subheader("Scheduling Jobs")
    
    scheduled_count = 0
    for config in configs:
        if not config.get('enabled', True):
            Console.warning(f"Skipping disabled domain: {config['name']}")
            continue
        
        # Get schedule config
        schedule_config = config.get('schedule', {})
        cron = schedule_config.get('cron', '0 */2 * * *')  # Default: every 2 hours
        description = schedule_config.get('description', 'No description')
        
        # Parse cron to schedule format
        parts = cron.split()
        
        if len(parts) >= 2:
            minute = parts[0]
            hour = parts[1]
            
            # Create job function for this domain
            def create_job(domain_config):
                def job():
                    Console.timestamp()
                    Console.crawling(f"{domain_config['name']} (Scheduled)")
                    try:
                        crawler = StaticCrawler(domain_config, db_client)
                        crawler.run()
                        Console.success(f"Completed: {domain_config['name']}")
                    except Exception as e:
                        Console.error(f"Error in scheduled crawl for {domain_config['name']}: {e}")
                        logger.exception(e)
                return job
            
            # Schedule based on cron pattern
            if hour.startswith('*/'):
                # Every N hours
                hours = int(hour.replace('*/', ''))
                schedule.every(hours).hours.do(create_job(config))
                Console.schedule_info(config['name'], f"Every {hours} hours - {description}")
                scheduled_count += 1
            elif hour == '*':
                # Every hour
                schedule.every().hour.do(create_job(config))
                Console.schedule_info(config['name'], f"Every hour - {description}")
                scheduled_count += 1
            else:
                # Specific time
                time_str = f"{hour.zfill(2)}:{minute.zfill(2)}"
                schedule.every().day.at(time_str).do(create_job(config))
                Console.schedule_info(config['name'], f"Daily at {time_str} - {description}")
                scheduled_count += 1
    
    if scheduled_count == 0:
        Console.error("No domains scheduled! Please enable at least one domain.")
        return
    
    Console.success(f"Scheduled {scheduled_count} crawler(s)")
    
    # Run initial crawl for all domains
    Console.separator()
    Console.subheader("Initial Crawl")
    Console.info("Running initial crawl for all enabled domains...")
    run_once()
    
    # Start scheduler loop
    Console.separator()
    Console.waiting()
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            Console.separator()
            Console.warning("Scheduler stopped by user")
            Console.info("Goodbye! 👋")
            break
        except Exception as e:
            Console.error(f"Scheduler error: {e}")
            logger.exception(e)
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
        Console.separator()
        Console.warning("Crawler stopped by user")
        Console.info("Goodbye! 👋")
    except Exception as e:
        Console.error(f"Fatal error: {e}")
        logger.exception(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
