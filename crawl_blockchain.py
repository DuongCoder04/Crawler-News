#!/usr/bin/env python3
"""
Crawl Blockchain News
Script chuyên dụng để crawl tin tức blockchain/crypto
"""

import json
from engine.static_crawler import StaticCrawler
from utils.db_client import DatabaseClient
from utils.logger import setup_logger
from loguru import logger

def main():
    """Crawl blockchain/tech news from VnExpress"""
    
    logger.info("=" * 60)
    logger.info("Blockchain News Crawler")
    logger.info("=" * 60)
    
    # Load VnExpress config
    logger.info("Loading VnExpress configuration...")
    with open('config/domains/vnexpress.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Initialize database client
    logger.info("Connecting to database...")
    try:
        db_client = DatabaseClient()
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return
    
    # Only crawl 'so-hoa' category (tech/blockchain/crypto)
    logger.info("Configuring for blockchain/tech news only...")
    config['category_mapping'] = {
        'so-hoa': 'TECH'  # Số hóa = Digital/Tech (includes blockchain, crypto, fintech)
    }
    
    # Create and run crawler
    logger.info("Starting crawler...")
    try:
        crawler = StaticCrawler(config, db_client)
        crawler.run()
    except Exception as e:
        logger.error(f"Crawler error: {e}")
        return
    
    # Show summary
    logger.info("=" * 60)
    logger.info("Crawl Summary")
    logger.info("=" * 60)
    
    try:
        total_news = db_client.get_news_count()
        logger.info(f"Total news in database: {total_news}")
    except Exception as e:
        logger.error(f"Failed to get news count: {e}")
    
    logger.success("Blockchain news crawl completed!")

if __name__ == '__main__':
    main()
