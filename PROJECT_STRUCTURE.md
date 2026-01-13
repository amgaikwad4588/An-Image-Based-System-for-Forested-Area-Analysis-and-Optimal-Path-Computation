# 📁 EcoView Imaging - Project Structure

## 🎯 One-Click Files (Start Here)
```
📄 README.md                 # Complete documentation
📄 QUICKSTART.md            # Quick start guide
🚀 start_ecoview.bat        # Windows one-click startup (If you are running it first time wait for 4-5 mins)
🚀 start_ecoview.sh         # Mac/Linux one-click startup
🔧 setup_check.py           # Setup validation script
  Manual Control:
  # Validate setup
python setup_check.py

# Start everything
python PythonScripts/unified_api.py

# (In new terminal)
cd treesense && python -m http.server 3000
```

## 🐍 Backend (Python API)
```
PythonScripts/
└── unified_api.py          # Main API server (all endpoints)
```

## 🌐 Frontend (Web Interface)
```
treesense/
├── index.html              # Home page
├── predict.html            # Dashboard
├── tree_species.html       # Species identification
├── optimal_path.html       # Path planning
├── historical_data.html    # Analytics & history
├── settings.html           # Settings & preferences
└── src/assets/css/
    └── theme.css           # Main stylesheet
```

## 📊 Data & Resources
```
Dataset/                    # Training data (optional)
├── data.yaml
├── train/
├── valid/
└── test/
```

## 📋 Configuration
```
📄 requirements.txt         # Python dependencies
📄 LICENSE.md              # License information
```

## 🗑️ Cleaned Up (Removed)
- ❌ `PythonScripts/tree_species_api.py` (consolidated into unified_api.py)
- ❌ `PythonScripts/optimal_path_api.py` (consolidated into unified_api.py)

## 🚀 How to Run

### Option 1: One-Click (Recommended)
- **Windows**: Double-click `start_ecoview.bat`
- **Mac/Linux**: Run `./start_ecoview.sh`

### Option 2: Manual
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start API server
python PythonScripts/unified_api.py

# 3. Start web server (new terminal)
cd treesense
python -m http.server 3000
```

### Option 3: Validation First
```bash
# Check setup
python setup_check.py

# Then follow manual steps above
```

## 🌐 Access Points
- **Web Interface**: http://localhost:3000
- **API Server**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## 📱 Features Available
1. **Species Identification** - AI-powered tree species recognition
2. **Optimal Path Planning** - Intelligent routing through vegetation
3. **Historical Analytics** - Data visualization and export
4. **Settings Management** - Customize your experience
5. **Unified Dashboard** - Central control center

---
**Ready to start? Use the one-click setup files above! 🌳**
