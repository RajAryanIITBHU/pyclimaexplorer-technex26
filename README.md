# PyClimaExplorer

**Interactive 3D Climate Data Visualization Platform**

PyClimaExplorer is a powerful, interactive web application for visualizing and analyzing climate data in 3D. Built with **Streamlit** and **Three.js**, it provides an immersive experience for exploring NetCDF climate datasets through multiple visualization modes including 3D globes, 2D maps, time series analysis, and statistical tools.

![PyClimaExplorer 3D Globe Visualization](https://via.placeholder.com/800x400?text=PyClimaExplorer+3D+Globe+Visualization)

---

## Table of Contents

- [Features](#-features)
- [Technology Stack](#️-technology-stack)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Data Format Requirements](#-data-format-requirements)
- [Usage Guide](#-usage-guide)
- [Visualization Modes](#visualization-modes)
- [Configuration](#️-configuration)
- [Performance Optimization](#-performance-optimization)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## Features

### Core Features

| Feature | Description |
|---|---|
|  **True 3D Globe Visualization** | Interactive Earth globe with climate data overlays |
|  **Multiple Map Projections** | PlateCarree, Mollweide, Robinson, and Orthographic views |
|  **Time Series Analysis** | Analyze temporal patterns at any location |
|  **Statistical Analysis** | Comprehensive statistical tools with distribution plots |
|  **Variable Comparison** | Compare different time periods or variables |
|  **PyDesk 3D Terrain Maps** | Advanced 3D topographic visualization |

### Technical Features

-  **30fps Optimized Performance** — Smooth globe rotation and interaction
-  **Real-time Data Processing** — Instant updates when changing parameters
-  **Multiple File Format Support** — NetCDF files (`.nc`, `.netcdf`)
-  **Sample Data Generator** — Built-in synthetic climate data for testing
-  **Responsive Design** — Works across different screen sizes
-  **Skeleton Loading** — Smooth loading states with animated skeletons

---

##  Technology Stack

### Frontend

- **Streamlit** — Web application framework
- **Three.js / Globe.gl** — 3D globe rendering
- **Plotly** — Interactive charts and graphs
- **Matplotlib** — Static visualizations and colorbars
- **Custom CSS** — Styling and animations

### Backend

- **Python 3.10+** — Core programming language
- **XArray** — NetCDF data handling
- **Pandas** — Data manipulation
- **NumPy** — Numerical computations
- **Cartopy** — Map projections and geospatial analysis
- **SciPy** — Scientific computing utilities

### Data Processing

- **NetCDF4** — Climate data format support
- **Base64** — Image encoding for textures
- **Hashlib** — File integrity checking
- **Tempfile** — Temporary file management

---

##  Installation

### Prerequisites

- Python **3.10** or higher
- `pip` package manager
- Git *(optional, for cloning)*

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/pyclimaexplorer.git
cd pyclimaexplorer
```

### Step 2: Create Virtual Environment *(Recommended)*

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python -c "import streamlit; import xarray; import plotly; print('All dependencies installed successfully!')"
```

### `requirements.txt`

```txt

streamlit==1.28.0
click==8.3.1
blinker==1.9.0
packaging==23.2
toml==0.10.2
typing_extensions==4.15.0
xarray==2023.12.0
pandas==2.1.3
numpy==1.24.3
netCDF4==1.6.5
cftime==1.6.5
scipy==1.15.3
plotly==5.18.0
matplotlib==3.8.0
Cartopy==0.25.0
pyproj==3.7.1
shapely==2.1.2
pyshp==3.0.3
pillow==10.4.0
pydeck==0.8.0
tenacity==8.5.0
requests==2.32.5
python-dateutil==2.9.0.post0
pytz==2026.1.post1
tzdata==2025.3
pyyaml==6.0.2
cachetools==5.5.2
watchdog==6.0.0
psutil==6.1.1
urllib3==2.6.3
certifi==2026.2.25
idna==3.11
charset-normalizer==3.4.5
```

---

##  Quick Start

### Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at **http://localhost:8501**

### First Steps

1. **Load Data** — Use the sidebar to either:
   - Check *"Use sample climate data"* for demo purposes
   - Upload your own NetCDF file
2. **Select Variable** — Choose a climate variable to visualize
3. **Explore Tabs** — Navigate through different visualization modes

---

##  Data Format Requirements

### Supported File Formats

- NetCDF (`.nc`, `.netcdf`)
- Compatible with CF-compliant climate datasets

### Required Dimensions

| Dimension | Description |
|---|---|
| `lat` | Latitude coordinates (degrees, -90 to 90) |
| `lon` | Longitude coordinates (degrees, -180 to 180 or 0 to 360) |
| `time` | *(optional)* Time dimension for temporal data |

### Required Variables

At least one data variable with dimensions `(time, lat, lon)` or `(lat, lon)`.

### Example Structure

```python
Dimensions:    (time: 48, lat: 180, lon: 360)
Coordinates:
  * time       (time) datetime64[ns] 2020-01-01 ... 2023-12-01
  * lat        (lat) float64 -89.5 -88.5 ... 88.5 89.5
  * lon        (lon) float64 0.5 1.5 ... 358.5 359.5
Data variables:
    temperature    (time, lat, lon) float32 ...
    precipitation  (time, lat, lon) float32 ...
    wind_speed     (time, lat, lon) float32 ...
```

---

##  Usage Guide

### 1. Sidebar Controls

#### Data Source Section
- **Use sample data** — Generate synthetic climate data for testing
- **Upload NetCDF** — Upload your own climate dataset
- Status badge shows current data state

#### Variable Selection
- Choose from available climate variables
- View variable metadata and quick statistics
- Min/Max values displayed for reference

#### Globe Settings

| Setting | Description |
|---|---|
| Rotation Speed | Adjust auto-rotation (0–2) |
| Show Atmosphere | Toggle atmospheric glow |
| Show Grid Lines | Display lat/lon grid |
| Show Borders | Display country borders |
| Color Scheme | Select from multiple colormaps |

### 2. Main Tabs

####  3D Globe Tab
- Interactive 3D Earth with data overlay
- Drag to rotate, scroll to zoom
- Auto-rotation option
- Real-time FPS counter
- Colorbar for value reference

####  2D Spatial View Tab
- Multiple map projections
- Point analysis at specific coordinates
- Interactive zoom and pan
- Value display at cursor position

####  Time Series Tab
- Select time range for analysis
- Choose location by lat/lon
- View trends with statistical overlay
- Download time series data

####  Statistics Tab
- Global statistical summary
- Distribution histogram
- Zonal mean analysis
- Regional comparisons (equatorial vs polar)

####  Comparison Tab
- Compare two time periods
- Compare different variables
- Scatter plots with correlation
- Difference statistics

####  PyDesk 3D Map Tab
- 3D terrain visualization
- Adjustable viewing angle
- Contour overlay option
- Lighting and shading effects

---

##  Configuration

### Customizing Colormaps

Available color schemes in `colormap_options`:

```python
colormap_options = {
    'Turbo (Rainbow)': 'turbo',
    'Viridis':         'viridis',
    'Plasma':          'plasma',
    'Inferno':         'inferno',
    'Magma':           'magma',
    'Cool to Warm':    'RdBu',
    'Spectral':        'Spectral',
    'Hot':             'hot',
    'Thermal':         'thermal'
}
```

### Performance Settings

| Setting | Location | Default |
|---|---|---|
| Globe resolution | `load_sample_data()` | 180×360 |
| FPS target | Globe HTML | 30 |
| Texture quality | Figure creation DPI | 150 |

### Cache Configuration

```python
@st.cache_resource(ttl=3600)  # Cache expires after 1 hour
```

---

##  Performance Optimization

### For Large Datasets

Downsample data before loading:

```python
# Select every 2nd point
ds_downsampled = ds.isel(
    lat=slice(None, None, 2),
    lon=slice(None, None, 2)
)
```

- Increase cache TTL for frequently accessed data
- Use sample data for testing and development

### Memory Management

- Automatic cleanup of temporary files
- Data loading with proper file handling
- NaN value handling throughout
- Efficient array operations with NumPy

---

##  Troubleshooting

### Common Issues and Solutions

#### App fails to start

```bash
# Check Python version
python --version  # Must be 3.10+

# Verify Streamlit installation
streamlit --version

# Clear Streamlit cache
streamlit cache clear
```

#### File upload errors

- Ensure file is CF-compliant NetCDF
- Check file size (<200MB recommended)
- Verify dimensions are named `lat`, `lon`, `time`

#### 3D globe not displaying

- Check internet connection (CDN access)
- Enable WebGL in browser
- Update graphics drivers

#### Memory errors

- Reduce dataset resolution
- Close other applications
- Increase system swap space

### Debug Mode

Add to `app.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

##  Contributing

### Guidelines

1. Fork the repository
2. Create a feature branch
3. Follow [PEP 8](https://pep8.org/) style guide
4. Add tests for new features
5. Update documentation
6. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black app.py
```

---

##  License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **TECHNEX'26 Hackathon** — Inspiration and platform
- **Streamlit Team** — Amazing framework
- **Three.js / Globe.gl** — 3D visualization libraries
- **Climate Data Community** — Data standards and formats
- **Open Source Contributors** — Various libraries used



---

<p align="center">Made with ❤️ for the climate science community</p>
