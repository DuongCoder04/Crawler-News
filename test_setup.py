"""
Test Setup Script
Kiểm tra xem crawler đã setup đúng chưa
"""

import sys
from pathlib import Path

def test_imports():
    """Test import các modules"""
    print("🔍 Testing imports...")
    
    try:
        from config import settings
        print("✅ config.settings")
        
        from utils.logger import logger
        print("✅ utils.logger")
        
        from utils.db_client import DatabaseClient
        print("✅ utils.db_client")
        
        from storage.cache import RedisCache
        print("✅ storage.cache")
        
        from engine.static_crawler import StaticCrawler
        print("✅ engine.static_crawler")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration"""
    print("\n🔍 Testing configuration...")
    
    try:
        from config import settings
        
        print(f"Database: {settings.DB_WISE_NAME}@{settings.DB_WISE_HOST}:{settings.DB_WISE_PORT}")
        print(f"User: {settings.DB_WISE_USER}")
        print(f"Redis: {'✅ Enabled' if settings.REDIS_ENABLED else '⚠️  Disabled'}")
        
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from utils.db_client import DatabaseClient
        
        db_client = DatabaseClient()
        
        # Test get categories
        categories = db_client.get_categories()
        print(f"✅ Database connected")
        print(f"   Found {len(categories)} NEWS categories")
        
        # Test get news count
        news_count = db_client.get_news_count()
        print(f"   Current news count: {news_count}")
        
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("🧪 X-Wise News Crawler - Setup Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test failed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ Setup complete! Ready to crawl.")
        print("\nNext: python main.py --mode once --domain vnexpress.net")
        return 0
    else:
        print("\n⚠️  Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
