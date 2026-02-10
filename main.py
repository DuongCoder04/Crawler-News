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

from utils.db_client import DatabaseClient
from engine.static_crawler import StaticCrawler


def load_domain_configs():
    """Load tất cả domain configurations"""
    config_dir = Path('config/domains')
    configs = []
    
    if not config_dir.exists():
        logger.error(f"Config directory not found: {config_dir}")
        return configs
    
    for config_file in config_dir.glob('*.json'):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                configs.append(config)
                logger.info(f"Loaded config: {config['name']}")
        except Exception as e:
            logger.error(f"Error loading {config_file}: {e}")
    
    return configs


def run_once(domain_name: str = None):
    """
    Chạy crawler một lần (không dùng scheduler)
    
    Args:
        domain_name: Tên domain cần crawl, None = all domains
    """
    logger.info("Running crawler in one-time mode")
    
    # Load configs
    configs = load_domain_configs()
    
    if not configs:
        logger.error("No domain configs found!")
        return
    
    # Filter by domain name if specified
    if domain_name:
        configs = [c for c in configs if c['domain'] == domain_name or c['name'] == domain_name]
        if not configs:
            logger.error(f"Domain not found: {domain_name}")
            return
    
    # Initialize Database client
    try:
        db_client = DatabaseClient()
    except Exception as e:
        logger.error(f"Failed to initialize database client: {e}")
        logger.error("Please check database configuration in .env file")
        return
    
    # Run crawlers
    for config in configs:
        if not config.get('enabled', True):
            logger.info(f"Skipping disabled domain: {config['name']}")
            continue
        
        logger.info(f"Crawling {config['name']}...")
        
        try:
            crawler_type = config.get('crawler_type', 'static')
            
            if crawler_type == 'static':
                crawler = StaticCrawler(config, db_client)
                crawler.run()
            else:
                logger.warning(f"Unsupported crawler type: {crawler_type}")
                
        except Exception as e:
            logger.error(f"Error crawling {config['name']}: {e}")
    
    # Show summary
    try:
        total_news = db_client.get_news_count()
        logger.info(f"Total news in database: {total_news}")
    except Exception:
        pass


def run_scheduler():
    """Chạy crawler với scheduler"""
    import schedule
    import time
    from datetime import datetime
    
    logger.info("Running crawler in scheduler mode")
    logger.info("Crawler will run automatically based on schedule configuration")
    logger.info("Press Ctrl+C to stop")
    
    # Load configs
    configs = load_domain_configs()
    
    if not configs:
        logger.error("No domain configs found!")
        return
    
    # Initialize Database client
    try:
        db_client = DatabaseClient()
    except Exception as e:
        logger.error(f"Failed to initialize database client: {e}")
        return
    
    # Setup scheduled jobs for each domain
    for config in configs:
        if not config.get('enabled', True):
            logger.info(f"Skipping disabled domain: {config['name']}")
            continue
        
        # Get schedule config
        schedule_config = config.get('schedule', {})
        cron = schedule_config.get('cron', '0 */2 * * *')  # Default: every 2 hours
        description = schedule_config.get('description', 'No description')
        
        # Parse cron to schedule format
        # Format: minute hour day month weekday
        # Example: "0 */2 * * *" = every 2 hours
        parts = cron.split()
        
        if len(parts) >= 2:
            minute = parts[0]
            hour = parts[1]
            
            # Create job function for this domain
            def create_job(domain_config):
                def job():
                    logger.info(f"[Scheduled] Crawling {domain_config['name']}...")
                    try:
                        crawler = StaticCrawler(domain_config, db_client)
                        crawler.run()
                    except Exception as e:
                        logger.error(f"Error in scheduled crawl for {domain_config['name']}: {e}")
                return job
            
            # Schedule based on cron pattern
            if hour.startswith('*/'):
                # Every N hours
                hours = int(hour.replace('*/', ''))
                schedule.every(hours).hours.do(create_job(config))
                logger.info(f"Scheduled {config['name']}: Every {hours} hours - {description}")
            elif hour == '*':
                # Every hour
                schedule.every().hour.do(create_job(config))
                logger.info(f"Scheduled {config['name']}: Every hour - {description}")
            else:
                # Specific time
                time_str = f"{hour.zfill(2)}:{minute.zfill(2)}"
                schedule.every().day.at(time_str).do(create_job(config))
                logger.info(f"Scheduled {config['name']}: Daily at {time_str} - {description}")
    
    # Run initial crawl for all domains
    logger.info("=" * 60)
    logger.info("Running initial crawl for all domains...")
    logger.info("=" * 60)
    run_once()
    
    # Start scheduler loop
    logger.info("=" * 60)
    logger.info("Scheduler started. Waiting for next scheduled run...")
    logger.info("=" * 60)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
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
    
    logger.info("=" * 60)
    logger.info("X-Wise News Crawler System")
    logger.info("=" * 60)
    
    try:
        if args.mode == 'once':
            run_once(args.domain)
        else:
            run_scheduler()
            
    except KeyboardInterrupt:
        logger.info("Crawler stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
