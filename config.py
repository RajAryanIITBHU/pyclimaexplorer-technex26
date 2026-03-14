"""Configuration settings for PyClimaExplorer."""

from pathlib import Path

# App settings
APP_TITLE = "PyClimaExplorer"
APP_SUBTITLE = "3D Climate Data Visualization with PyDeck"
PAGE_ICON = "🌍"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# Data settings
SAMPLE_DATA_SHAPE = (180, 360)  # lat, lon resolution
SAMPLE_DATA_TIME_RANGE = ("2020-01-01", "2023-12-31")
SAMPLE_DATA_FREQ = "M"  # Monthly

# Visualization settings
DEFAULT_CMAP = "viridis"
CMAP_OPTIONS = {
    'Viridis': 'viridis',
    'Plasma': 'plasma',
    'Inferno': 'inferno',
    'Magma': 'magma',
    'Turbo': 'turbo',
    'Cool to Warm': 'RdBu',
    'Spectral': 'Spectral',
    'Thermal': 'thermal'
}

# PyDeck settings
PYDECK_INITIAL_VIEW_STATE = {
    "latitude": 20,
    "longitude": 0,
    "zoom": 1.5,
    "pitch": 15,
    "bearing": 0
}

# Map projections for 2D views
MAP_PROJECTIONS = ["PlateCarree", "Mollweide", "Robinson", "Orthographic"]

# Cache settings
CACHE_TTL = 3600  # 1 hour
MAX_CACHE_SIZE = 10  # Maximum number of cached datasets

# File paths
SAMPLE_DATA_DIR = Path("./sample_data")
SAMPLE_DATA_DIR.mkdir(exist_ok=True)