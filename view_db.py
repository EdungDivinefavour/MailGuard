#!/usr/bin/env python3
"""Simple script to view MailGuard database contents."""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / 'mailguard-server' / 'instance' / 'mailguard.db'

def view_database():
    """Display database contents in a readable format."""
    if not DB_PATH.exists():
        print(f"❌ Database not found at: {DB_PATH}")
        print("The database will be created when the first email is processed.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("📊 MailGuard Database Viewer")
    print("=" * 60)
    print(f"📁 Database: {DB_PATH}")
    print(f"📋 Tables: {', '.join(tables)}\n")
    
    # View email_log table
    if 'email_log' in tables:
        cursor.execute("SELECT COUNT(*) FROM email_log")
        count = cursor.fetchone()[0]
        print(f"📧 Email Log: {count} emails")
        print("-" * 60)
        
        cursor.execute("""
            SELECT id, timestamp, sender, subject, status, 
                   flagged, policy_applied, processing_time_ms 
            FROM email_log 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        
        emails = cursor.fetchall()
        print(emails)
        if emails:
            for email in emails:
                print(f"\nID: {email['id']}")
                print(f"  Time: {email['timestamp']}")
                print(f"  From: {email['sender']}")
                print(f"  Subject: {email['subject']}")
                print(f"  Status: {email['status']} | Policy: {email['policy_applied']}")
                print(f"  Flagged: {'Yes' if email['flagged'] else 'No'}")
                print(f"  Processing: {email['processing_time_ms']}ms")
        else:
            print("  No emails found.")
    
    # View detections
    if 'detection' in tables:
        cursor.execute("SELECT COUNT(*) FROM detection")
        count = cursor.fetchone()[0]
        print(f"\n\n🔍 Detections: {count} total")
        print("-" * 60)
        
        cursor.execute("""
            SELECT d.*, e.subject 
            FROM detection d
            LEFT JOIN email_log e ON d.email_id = e.id
            ORDER BY d.id DESC
            LIMIT 10
        """)
        
        detections = cursor.fetchall()
        if detections:
            for det in detections:
                print(f"\nDetection ID: {det['id']}")
                print(f"  Email: {det['subject']}")
                print(f"  Type: {det['pattern_type']}")
                print(f"  Confidence: {det['confidence']}")
                print(f"  Action: {det['action']}")
        else:
            print("  No detections found.")
    
    conn.close()

if __name__ == '__main__':
    view_database()
