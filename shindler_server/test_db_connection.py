#!/usr/bin/env python3
"""
Database Connection Test Script
Tests connectivity to PostgreSQL database and provides diagnostic information
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2 import OperationalError
import socket

# Load environment variables
load_dotenv()

def test_dns_resolution(hostname):
    """Test DNS resolution for the hostname"""
    try:
        ip_address = socket.gethostbyname(hostname)
        print(f"✅ DNS Resolution: {hostname} -> {ip_address}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS Resolution Failed: {hostname} - {e}")
        return False

def test_port_connectivity(hostname, port):
    """Test if the port is reachable"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port Connectivity: {hostname}:{port} is reachable")
            return True
        else:
            print(f"❌ Port Connectivity: {hostname}:{port} is not reachable")
            return False
    except Exception as e:
        print(f"❌ Port Connectivity Test Failed: {e}")
        return False

def test_database_connection():
    """Test database connection with current environment variables"""
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    database = os.getenv("POSTGRES_DB", "defaultdb")
    username = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    
    print("🔍 Database Configuration:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Database: {database}")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password) if password else 'Not set'}")
    print()
    
    # Test DNS resolution
    if not test_dns_resolution(host):
        print("\n💡 Suggestions:")
        print("   1. Check if the hostname is correct")
        print("   2. Check your internet connection")
        print("   3. Try using IP address instead of hostname")
        return False
    
    # Test port connectivity
    if not test_port_connectivity(host, port):
        print("\n💡 Suggestions:")
        print("   1. Check if the database server is running")
        print("   2. Check if the port is correct")
        print("   3. Check firewall settings")
        print("   4. Check if the database is accessible from your network")
        return False
    
    # Test database connection
    try:
        print("🔗 Testing database connection...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
            connect_timeout=10
        )
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ Database Connection Successful!")
        print(f"   PostgreSQL Version: {version[0]}")
        
        # Test if our table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%unsafe_events%'
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ Found {len(tables)} unsafe_events tables:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("⚠️  No unsafe_events tables found")
        
        cursor.close()
        conn.close()
        return True
        
    except OperationalError as e:
        print(f"❌ Database Connection Failed: {e}")
        print("\n💡 Suggestions:")
        print("   1. Check database credentials")
        print("   2. Check if the database exists")
        print("   3. Check if the user has proper permissions")
        print("   4. Check SSL settings if required")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def suggest_local_setup():
    """Suggest local database setup"""
    print("\n🔧 Local Database Setup Suggestions:")
    print("1. Install PostgreSQL locally:")
    print("   - Windows: Download from https://www.postgresql.org/download/windows/")
    print("   - Or use Docker: docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres")
    print()
    print("2. Create a .env file in shindler_server/ with:")
    print("   POSTGRES_HOST=localhost")
    print("   POSTGRES_PORT=5432")
    print("   POSTGRES_DB=shindler_safety")
    print("   POSTGRES_USER=postgres")
    print("   POSTGRES_PASSWORD=your_password")
    print()
    print("3. Create the database:")
    print("   createdb shindler_safety")
    print()
    print("4. Run the table creation script:")
    print("   python create_srs_agumented_table.py")

if __name__ == "__main__":
    print("🚀 Database Connection Test")
    print("=" * 50)
    
    success = test_database_connection()
    
    if not success:
        suggest_local_setup()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! Database is ready.")
    else:
        print("❌ Database connection failed. Please check the suggestions above.")
