#!/usr/bin/env python3
"""
Health check script for Docker containers.
Verifies that the API and database are properly connected.
"""
import sys
import requests
import time
from urllib.parse import urlparse
import psycopg2
import os


def check_api(url="http://localhost:8000/health", retries=5, delay=2):
    """Check if the API is healthy."""
    for i in range(retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ API is healthy: {response.json()}")
                return True
        except Exception as e:
            print(f"⏳ API check attempt {i+1}/{retries} failed: {e}")
            if i < retries - 1:
                time.sleep(delay)
    return False


def check_database(database_url=None, retries=5, delay=2):
    """Check if the database is accessible."""
    if not database_url:
        database_url = os.getenv("DATABASE_URL", "postgresql://chipengine:chipengine@localhost:5432/chipengine")
    
    # Parse the database URL
    parsed = urlparse(database_url)
    
    if parsed.scheme == "sqlite":
        print("✅ SQLite database configured")
        return True
    
    # For PostgreSQL
    for i in range(retries):
        try:
            conn = psycopg2.connect(
                host=parsed.hostname or "localhost",
                port=parsed.port or 5432,
                user=parsed.username or "chipengine",
                password=parsed.password or "chipengine",
                database=parsed.path.lstrip("/") or "chipengine"
            )
            conn.close()
            print("✅ PostgreSQL database is accessible")
            return True
        except Exception as e:
            print(f"⏳ Database check attempt {i+1}/{retries} failed: {e}")
            if i < retries - 1:
                time.sleep(delay)
    return False


def main():
    """Run health checks."""
    print("🏥 Running ChipEngine health checks...")
    
    api_healthy = check_api()
    db_healthy = check_database()
    
    if api_healthy and db_healthy:
        print("\n✅ All systems operational!")
        return 0
    else:
        print("\n❌ Health check failed!")
        if not api_healthy:
            print("  - API is not responding")
        if not db_healthy:
            print("  - Database is not accessible")
        return 1


if __name__ == "__main__":
    sys.exit(main())