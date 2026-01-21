# Deploy to PythonAnywhere

## Step 1: Create Account
1. Go to https://www.pythonanywhere.com
2. Sign up for a free account (e.g., username: `vaishnavrak`)

## Step 2: Upload Code
1. Go to **Files** tab
2. Click **Upload a file** or use **Bash console**:
```bash
git clone https://github.com/vaishnav-rak/claude-expense-tracker.git
```

## Step 3: Create MySQL Database
1. Go to **Databases** tab
2. Set a MySQL password and click **Initialize MySQL**
3. Create a database named `expenses`:
   - Under "Create a database", type `expenses` and click **Create**
4. Note your database info:
   - Host: `YOUR_USERNAME.mysql.pythonanywhere-services.com`
   - Database: `YOUR_USERNAME$expenses`

## Step 4: Set Up Virtual Environment
1. Go to **Consoles** tab → **Bash**
2. Run these commands:
```bash
cd claude-expense-tracker
mkvirtualenv --python=/usr/bin/python3.10 expense-env
pip install -r requirements.txt
```

## Step 5: Configure WSGI
1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration** → **Python 3.10**
4. Set these paths:
   - **Source code**: `/home/YOUR_USERNAME/claude-expense-tracker`
   - **Working directory**: `/home/YOUR_USERNAME/claude-expense-tracker`
   - **Virtualenv**: `/home/YOUR_USERNAME/.virtualenvs/expense-env`

5. Click on **WSGI configuration file** link and replace contents with:
```python
import sys
import os

project_home = '/home/YOUR_USERNAME/claude-expense-tracker'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['DATABASE_URL'] = 'mysql+pymysql://YOUR_USERNAME:YOUR_DB_PASSWORD@YOUR_USERNAME.mysql.pythonanywhere-services.com/YOUR_USERNAME$expenses'
os.environ['SECRET_KEY'] = 'generate-a-random-secret-key-here'

from app import app as application
```

## Step 6: Create Database Tables
1. Go to **Consoles** → **Bash**
2. Run:
```bash
cd claude-expense-tracker
workon expense-env
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Step 7: Reload and Test
1. Go to **Web** tab
2. Click **Reload** button
3. Visit: `https://YOUR_USERNAME.pythonanywhere.com`

## Troubleshooting
- Check **Error log** in Web tab for issues
- Ensure all paths use your actual PythonAnywhere username
- Make sure MySQL password is correct in WSGI file

## Your Live URL
```
https://YOUR_USERNAME.pythonanywhere.com
```

Replace `YOUR_USERNAME` with your actual PythonAnywhere username throughout.
