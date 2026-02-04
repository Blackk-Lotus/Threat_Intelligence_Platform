#!/usr/bin/env python3
"""
Threat Intelligence Platform Dashboard
By Aakash Gujja

A simple web interface to visualize collected IOCs and threat intelligence.
"""

from flask import Flask, render_template, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Database configuration
DB_PATH = 'threat_intel.db'

def init_db():
    """Initialize SQLite database if it doesn't exist"""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS iocs
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      type TEXT,
                      value TEXT,
                      source TEXT,
                      timestamp TEXT,
                      confidence INTEGER)''')

        # Add sample data for demonstration
        sample_data = [
            ('IP', '192.168.1.100', 'Sample Feed', datetime.now().isoformat(), 80),
            ('Domain', 'malicious-domain.com', 'RSS Feed', datetime.now().isoformat(), 90),
            ('Hash', 'a' * 64, 'Twitter', datetime.now().isoformat(), 75),
            ('URL', 'http://evil-site.com/malware', 'Web Scraper', datetime.now().isoformat(), 85),
        ]
        c.executemany('INSERT INTO iocs (type, value, source, timestamp, confidence) VALUES (?,?,?,?,?)',
                     sample_data)
        conn.commit()
        conn.close()

def get_ioc_stats():
    """Get statistics about collected IOCs"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    stats = {}
    c.execute('SELECT COUNT(*) FROM iocs')
    stats['total'] = c.fetchone()[0]

    c.execute('SELECT type, COUNT(*) FROM iocs GROUP BY type')
    stats['by_type'] = dict(c.fetchall())

    c.execute('SELECT source, COUNT(*) FROM iocs GROUP BY source')
    stats['by_source'] = dict(c.fetchall())

    conn.close()
    return stats

def get_recent_iocs(limit=50):
    """Get recent IOCs from database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM iocs ORDER BY id DESC LIMIT ?', (limit,))
    iocs = c.fetchall()
    conn.close()
    return iocs

@app.route('/')
def index():
    """Main dashboard page"""
    stats = get_ioc_stats()
    recent_iocs = get_recent_iocs(limit=10)
    return render_template('dashboard.html', stats=stats, iocs=recent_iocs)

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    return jsonify(get_ioc_stats())

@app.route('/api/iocs')
def api_iocs():
    """API endpoint for IOCs"""
    limit = int(request.args.get('limit', 50))
    iocs = get_recent_iocs(limit)
    return jsonify([{
        'id': ioc[0],
        'type': ioc[1],
        'value': ioc[2],
        'source': ioc[3],
        'timestamp': ioc[4],
        'confidence': ioc[5]
    } for ioc in iocs])

if __name__ == '__main__':
    init_db()
    print("=" * 60)
    print("Threat Intelligence Platform Dashboard")
    print("By Aakash Gujja")
    print("=" * 60)
    print("\nStarting dashboard on http://localhost:5000")
    print("Press CTRL+C to stop\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
