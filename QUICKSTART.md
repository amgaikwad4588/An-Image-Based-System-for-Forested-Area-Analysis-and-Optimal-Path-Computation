# 🚀 EcoView Imaging - Quick Start Guide

## One-Click Setup (Recommended)

### Windows Users
1. **Download** the project folder
2. **Double-click** `start_ecoview.bat`
3. **Wait** for setup to complete (2-3 minutes first time)
4. **Open** browser to `http://localhost:3000`

### Mac/Linux Users
1. **Download** the project folder
2. **Open Terminal** in project folder
3. **Run**: `chmod +x start_ecoview.sh && ./start_ecoview.sh`
4. **Open** browser to `http://localhost:3000`

## Manual Setup (If needed)

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Validate setup
python setup_check.py

# 3. Start API server
python PythonScripts/unified_api.py

# 4. Start web server (new terminal)
cd treesense
python -m http.server 3000
```

## What You'll See

1. **Home Page** - Project overview and navigation
2. **Dashboard** - Unified control center
3. **Species** - Upload tree images for AI identification
4. **Optimal Path** - Calculate routes through vegetation
5. **History** - View analytics and export data
6. **Settings** - Customize your experience

## First Steps

1. **Try Species Identification**:
   - Go to Species tab
   - Upload any tree image
   - See AI-powered species analysis

2. **Test Optimal Path**:
   - Go to Optimal Path tab
   - Upload a terrain image
   - Get intelligent routing

3. **Explore Analytics**:
   - Go to History tab
   - View your analysis data
   - Export reports

## Troubleshooting

**"Python not found"**:
- Install Python 3.8+ from python.org
- Make sure to check "Add to PATH" during installation

**"Port in use"**:
- Close other applications using ports 8000/3000
- Or restart your computer

**"Dependencies failed"**:
- Check internet connection
- Try: `pip install --upgrade pip`
- Then: `pip install -r requirements.txt`

## Need Help?

- Check `README.md` for detailed documentation
- Run `python setup_check.py` to validate setup
- Ensure all files are in the correct folder structure

---
**Ready to explore environmental AI? Start with the one-click setup above! 🌳**
