# 🌳 EcoView Imaging - AI-Powered Environmental Monitoring

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**EcoView Imaging** is an advanced AI-powered environmental monitoring platform that transforms aerial and satellite imagery into actionable insights for forestry management, biodiversity assessment, and ecological conservation.

##  Features

-  **Smart Tree Detection** - Advanced AI algorithms for precise tree counting and canopy analysis
-  **Species Identification** - Machine learning-powered recognition of 25+ tree species
-  **Optimal Path Planning** - Intelligent routing algorithms for forest navigation
-  **Analytics Dashboard** - Comprehensive data visualization and historical trends
-  **Green Cover Analysis** - Detailed vegetation density mapping
-  **Historical Data** - Export, analyze, and track environmental changes over time

##  Quick Start (One-Click Setup)

### Prerequisites
- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Windows Users
1. **Download the project** and extract to your desired folder
2. **Double-click** `start_ecoview.bat` 
3. **Wait** for the setup to complete (first time may take 2-3 minutes)
4. **Open** your browser and go to `http://localhost:3000`

### Mac/Linux Users
1. **Download the project** and extract to your desired folder
2. **Open Terminal** and navigate to the project folder
3. **Run**: `chmod +x start_ecoview.sh && ./start_ecoview.sh`
4. **Open** your browser and go to `http://localhost:3000`

### Manual Setup (Alternative)
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the API server
python PythonScripts/unified_api.py

# 3. In a new terminal, start the web server
cd treesense
python -m http.server 3000

# 4. Open browser to http://localhost:3000
```

## 📁 Project Structure

```
EcoView-Imaging/
├── 📄 README.md                 # This file
├── 🚀 start_ecoview.bat        # Windows startup script
├── 🚀 start_ecoview.sh         # Mac/Linux startup script
├── 📋 requirements.txt         # Python dependencies
├── 🐍 PythonScripts/
│   └── unified_api.py          # Main API server
├── 🌐 treesense/
│   ├── index.html              # Home page
│   ├── predict.html            # Dashboard
│   ├── tree_species.html       # Species identification
│   ├── optimal_path.html       # Path planning
│   ├── historical_data.html    # Analytics
│   ├── settings.html           # Settings
│   └── src/assets/css/
│       └── theme.css           # Main stylesheet
└── 📊 Dataset/                 # Training data
```

##  How to Use

### 1. **Species Identification**
- Go to **Species** tab
- Upload an image of a tree
- Get AI-powered species identification with confidence scores
- View detailed characteristics and analysis

### 2. **Optimal Path Planning**
- Go to **Optimal Path** tab
- Upload a terrain image
- Get intelligent routing through vegetation
- View path overlay on original image

### 3. **Historical Analytics**
- Go to **History** tab
- View analysis trends and species distribution
- Export data in CSV/JSON formats
- Generate comprehensive reports

### 4. **Settings & Customization**
- Go to **Settings** tab
- Configure analysis parameters
- Customize display preferences
- Manage data and backups

##  API Endpoints

The unified API server provides these endpoints:

- `POST /process` - Optimal path calculation
- `POST /identify_species` - Tree species identification
- `GET /species_info` - Available species list
- `GET /health` - Server health check

##  Supported Tree Species

### Deciduous Trees
Oak, Maple, Birch, Willow, Elm, Ash, Beech, Cherry, Apple, Poplar

### Coniferous Trees
Pine, Cedar, Spruce, Fir, Hemlock, Juniper, Larch

### Tropical Trees
Palm, Eucalyptus, Bamboo, Mango, Banyan

### Flowering Trees
Magnolia, Dogwood, Redbud, Crabapple

##  Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**"Port already in use" error:**
- Close other applications using port 8000 or 3000
- Or change ports in the startup scripts

**"API connection failed":**
- Ensure the API server is running (`unified_api.py`)
- Check that port 8000 is not blocked by firewall

**Browser compatibility:**
- Use Chrome, Firefox, Safari, or Edge (latest versions)
- Enable JavaScript in your browser

### Getting Help

1. **Check the console** for error messages
2. **Verify Python version**: `python --version` (should be 3.8+)
3. **Check dependencies**: `pip list` to see installed packages
4. **Restart the servers** if issues persist

##  Performance Tips

- **High Accuracy Mode**: Enable in Settings for better results (slower processing)
- **Image Size**: Recommended 1000x1000 pixels for optimal performance
- **File Formats**: JPG, PNG, WEBP supported
- **Batch Processing**: Process multiple images sequentially for best results

##  Data Privacy

- All processing happens locally on your machine
- No data is sent to external servers
- Images are stored locally in browser storage
- You can clear all data anytime in Settings

##  Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request


##  Acknowledgments

- Built with Flask, OpenCV, and modern web technologies
- Inspired by environmental conservation efforts
- Designed for forestry professionals and researchers

---

**Made with 🌍 for the planet** - EcoView Imaging Team

*For support or questions, please open an issue on GitHub.*# Ecoview-IMAGING
# Eco_View
# An-Image-Based-System-for-Forested-Area-Analysis-and-Optimal-Path-Computation
