import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/claude-expense-tracker'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['DATABASE_URL'] = 'mysql+pymysql://YOUR_USERNAME:YOUR_DB_PASSWORD@YOUR_USERNAME.mysql.pythonanywhere-services.com/YOUR_USERNAME$expenses'
os.environ['SECRET_KEY'] = 'your-secret-key-here'

from app import app as application
