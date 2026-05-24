import psycopg2
from datetime import datetime

conn = psycopg2.connect('postgresql://bugbounty_user:changeme123@localhost:5432/bug_bounty_production')
cur = conn.cursor()

# Check report distribution by month
cur.execute('''
    SELECT 
        EXTRACT(YEAR FROM submitted_at) as year,
        EXTRACT(MONTH FROM submitted_at) as month,
        COUNT(*) as count,
        MIN(submitted_at) as first_report,
        MAX(submitted_at) as last_report
    FROM vulnerability_reports 
    GROUP BY year, month 
    ORDER BY year, month
''')

print('Report distribution by month:')
print('=' * 80)
for row in cur.fetchall():
    year = int(row[0]) if row[0] else 0
    month = int(row[1]) if row[1] else 0
    count = row[2]
    first = row[3]
    last = row[4]
    month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_name = month_names[month] if month < len(month_names) else str(month)
    print(f'{month_name} {year}: {count} reports (from {first} to {last})')

# Check total
cur.execute('SELECT COUNT(*) FROM vulnerability_reports')
total = cur.fetchone()[0]
print('=' * 80)
print(f'Total reports: {total}')

cur.close()
conn.close()
