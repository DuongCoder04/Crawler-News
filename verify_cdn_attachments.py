"""
Verify CDN Attachments in Database
Check if attachments are properly saved with CDN URLs
"""

from utils.db_client import DatabaseClient
from utils.logger import setup_logger

setup_logger()

def verify_attachments():
    """Verify attachments in database"""
    
    db = DatabaseClient()
    conn = db._get_connection()
    cursor = conn.cursor()
    
    print("=" * 70)
    print("Verifying CDN Attachments in Database")
    print("=" * 70)
    
    # Check recent attachments
    cursor.execute("""
        SELECT id, url, object_type, object_id, file_name, extension, created_at
        FROM attachment
        WHERE object_type = 'news'
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    attachments = cursor.fetchall()
    
    if attachments:
        print(f"\n✅ Found {len(attachments)} recent attachments:\n")
        for att in attachments:
            print(f"ID: {att[0]}")
            print(f"URL: {att[1]}")
            print(f"Type: {att[2]}")
            print(f"News ID: {att[3]}")
            print(f"File: {att[4]}")
            print(f"Extension: {att[5]}")
            print(f"Created: {att[6]}")
            print("-" * 70)
    else:
        print("\n❌ No attachments found!")
    
    # Check news with attachments
    cursor.execute("""
        SELECT n.id, n.title, a.url
        FROM news n
        LEFT JOIN attachment a ON a.object_id::uuid = n.id AND a.object_type = 'news'
        WHERE a.url IS NOT NULL
        ORDER BY n.created_at DESC
        LIMIT 5
    """)
    
    news_with_attachments = cursor.fetchall()
    
    if news_with_attachments:
        print(f"\n✅ Found {len(news_with_attachments)} news with attachments:\n")
        for news in news_with_attachments:
            print(f"News ID: {news[0]}")
            print(f"Title: {news[1][:60]}...")
            print(f"CDN URL: {news[2]}")
            print("-" * 70)
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    verify_attachments()
