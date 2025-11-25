# 📱 RENDER API DEPLOYMENT GUIDE

## 1️⃣ RESTORE API INTEGRATION

**File Created**: `build_dashboard_pro_api.py`

This new dashboard fetches data from your Render API instead of embedding it statically.

**To Use**:
```bash
# Replace the old dashboard builder in orchestrator
# Edit master_orchestrator.py line 132 to use:
python3 build_dashboard_pro_api.py
```

---

## 2️⃣ ADD ENDPOINTS TO RENDER BACKEND

**File Created**: `backend_api.py`

**Instructions**:

### Step 1: Locate Your Render Backend Code
```bash
cd /path/to/your/render-backend
```

### Step 2: Copy These 3 Endpoints

Open your main Flask/FastAPI file (e.g., `app.py` or `main.py`) and add:

```python
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json

# ADD THESE 3 ENDPOINTS:

@app.route('/api/get_jobs', methods=['GET'])
def get_jobs():
    # ... (copy from backend_api.py)

@app.route('/api/get_strategy/<int:job_id>', methods=['GET'])
def get_strategy(job_id):
    # ... (copy from backend_api.py)

@app.route('/api/update_status', methods=['POST'])
def update_status():
    # ... (copy from backend_api.py)
```

### Step 3: Install Dependencies (if needed)
```bash
pip install flask flask-cors
pip freeze > requirements.txt
```

### Step 4: Ensure `jobs.db` is Uploaded to Render

**Option A**: Git (if DB is small)
```bash
git add jobs.db
git commit -m "Add jobs database"
git push
```

**Option B**: Persistent Disk (recommended)
- In Render Dashboard → Your Service → Settings
- Add a Persistent Disk at `/var/data`
- Update `DB_PATH = '/var/data/jobs.db'`
- Upload `jobs.db` manually or sync it via a script

### Step 5: Deploy
```bash
git push  # Render auto-deploys
```

---

## 3️⃣ UPDATE DASHBOARD TO USE YOUR RENDER URL

**Edit**: `build_dashboard_pro_api.py` (Line 9)

```python
API_BASE = "https://YOUR-ACTUAL-RENDER-URL.onrender.com"
```

Replace `YOUR-ACTUAL-RENDER-URL` with your actual Render service URL.

---

## ✅ VERIFICATION

### Test Locally:
```bash
# Run backend locally
python backend_api.py

# In another terminal
curl http://localhost:5000/api/get_jobs
```

### Test on Render:
```bash
curl https://your-app.onrender.com/api/get_jobs
```

You should see JSON with your jobs!

---

## 📱 MOBILE ACCESS

Once deployed:
1. Run: `python3 build_dashboard_pro_api.py`
2. Push `index.html` to GitHub
3. Open on mobile: `https://yourusername.github.io/job-search-automation/index.html`

**It will now pull live data from Render!** 🎉

---

## 🔧 TROUBLESHOOTING

**CORS Error on Mobile?**
Add to backend:
```python
from flask_cors import CORS
CORS(app, origins=["https://yourusername.github.io"])
```

**Database Not Found?**
Check `DB_PATH` in backend matches where `jobs.db` is stored on Render.

**Strategy Kits Not Showing?**
Verify the `strategy_kits` table exists:
```bash
sqlite3 jobs.db "SELECT COUNT(*) FROM strategy_kits;"
```
