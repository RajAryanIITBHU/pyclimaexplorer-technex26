import streamlit as st
import xarray as xr
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import io
import base64
from datetime import datetime, timedelta
import tempfile
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from PIL import Image
import requests
from scipy.interpolate import griddata
import warnings
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any
import hashlib

warnings.filterwarnings('ignore')

# Page configuration - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="PyClimaExplorer | 3D Climate Globe",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS WITH SKELETON LOADING ANIMATIONS
# ============================================================================
st.markdown("""
<style>
    /* Block container padding */
    .block-container {
            
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Main title styling */
    .main-title {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(45deg, #3498db, #2ecc71, #f1c40f, #e74c3c);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: left;
        margin-bottom: 0rem;
        padding-bottom: 0rem;
    }
    
    .subtitle {
        text-align: left;
        color: #888;
        font-size: 1rem;
        margin-top: 0rem;
        margin-bottom: 0rem !important;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e1e2f, #2d2d44);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3498db;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(52, 152, 219, 0.1);
        border: 1px solid #3498db;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #0a0a0f;
    }
    
    .st-emotion-cache-16txtl3 {
        padding: 0rem;
    }
    
    .st-emotion-cache-ch5dnh {
        margin: 1rem 0.5rem;
    }
    
    hr {
        margin: 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: #0a0a0f;
        padding: 0.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(52, 152, 219, 0.1);
    }
    
    /* Skeleton loading animation */
    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    .skeleton {
        background: linear-gradient(90deg, #2a2a2a 25%, #3a3a3a 50%, #2a2a2a 75%);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
        border-radius: 8px;
        height: 20px;
        margin: 10px 0;
    }
    
    .skeleton-card {
        background: linear-gradient(90deg, #1e1e2f 25%, #2d2d44 50%, #1e1e2f 75%);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
        border-radius: 10px;
        padding: 1rem;
        height: 100px;
    }
    
    .skeleton-globe {
        background: linear-gradient(90deg, #1a1a2a 25%, #2a2a3a 50%, #1a1a2a 75%);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
        border-radius: 10px;
        height: 600px;
        width: 100%;
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(45deg, #3498db, #2980b9);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.2s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .badge-success {
        background: rgba(46, 204, 113, 0.2);
        color: #2ecc71;
        border: 1px solid #2ecc71;
    }
    
    .badge-warning {
        background: rgba(241, 196, 15, 0.2);
        color: #f1c40f;
        border: 1px solid #f1c40f;
    }
    
    .badge-error {
        background: rgba(231, 76, 60, 0.2);
        color: #e74c3c;
        border: 1px solid #e74c3c;
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #1e1e2f;
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        border: 1px solid #3498db;
        font-size: 0.8rem;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'data_loaded': False,
        'current_var': None,
        'globe_rotation_speed': 0.0,
        'globe_atmosphere': True,
        'globe_gridlines': True,
        'globe_borders': True,
        'ds': None,
        'loading_state': False,
        'error_message': None,
        'last_upload_hash': None,
        'pydesk_data': None,
        'use_sample': False,
        'uploaded_file': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
@contextmanager
def loading_spinner(text="Loading..."):
    """Context manager for loading states"""
    st.session_state.loading_state = True
    with st.spinner(text):
        try:
            yield
        finally:
            st.session_state.loading_state = False

def show_skeleton(count=3, type="line"):
    """Show skeleton loading placeholders"""
    if type == "line":
        for _ in range(count):
            st.markdown('<div class="skeleton"></div>', unsafe_allow_html=True)
    elif type == "card":
        cols = st.columns(count)
        for col in cols:
            with col:
                st.markdown('<div class="skeleton-card"></div>', unsafe_allow_html=True)
    elif type == "globe":
        st.markdown('<div class="skeleton-globe"></div>', unsafe_allow_html=True)

def safe_nan_operation(func, default=None):
    """Safely handle NaN operations"""
    try:
        result = func()
        return result if not np.isnan(result) else default
    except:
        return default

def format_lat_lon(lat, lon):
    """Format latitude and longitude with direction"""
    lat_dir = "N" if lat >= 0 else "S"
    lon_dir = "E" if lon >= 0 else "W"
    return f"{abs(lat):.2f}°{lat_dir}, {abs(lon):.2f}°{lon_dir}"

def get_file_hash(file) -> str:
    """Generate hash for uploaded file"""
    if file is None:
        return None
    file.seek(0)
    file_hash = hashlib.md5(file.getvalue()).hexdigest()
    file.seek(0)
    return file_hash

# ============================================================================
# DATA LOADING FUNCTIONS (CACHED)
# ============================================================================
@st.cache_resource(ttl=3600, show_spinner="Generating sample climate data...")
def load_sample_data():
    """Create a realistic sample dataset with seasonal patterns"""
    # Create high-resolution grid
    lats = np.linspace(-90, 90, 180)
    lons = np.linspace(-180, 180, 360)
    times = pd.date_range('2020-01-01', '2023-12-31', freq='M')
    
    # Create meshgrid for lat/lon
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    
    # Initialize data array
    data = np.zeros((len(times), len(lats), len(lons)))
    
    # Create realistic temperature patterns
    for t, time in enumerate(times):
        month = time.month
        seasonal_factor = np.sin(2 * np.pi * (month - 1) / 12)
        
        for i, lat in enumerate(lats):
            base_temp = 25 * np.cos(np.radians(lat)) + 5
            seasonal_amp = 15 * (1 - np.abs(lat) / 90)
            seasonal = seasonal_amp * seasonal_factor
            
            for j, lon in enumerate(lons):
                land_factor = 1 + 0.1 * np.sin(3 * np.radians(lon)) * np.cos(2 * np.radians(lat))
                noise = np.random.normal(0, 0.5)
                data[t, i, j] = base_temp + seasonal + noise * land_factor
    
    # Create dataset
    ds = xr.Dataset(
        {
            'temperature': (['time', 'lat', 'lon'], data),
            'precipitation': (['time', 'lat', 'lon'], np.random.gamma(2, 2, data.shape)),
            'wind_speed': (['time', 'lat', 'lon'], np.abs(np.random.normal(5, 3, data.shape))),
        },
        coords={
            'time': times,
            'lat': lats,
            'lon': lons,
        }
    )
    
    # Add attributes
    ds.temperature.attrs.update({'units': '°C', 'long_name': 'Surface Temperature'})
    ds.precipitation.attrs.update({'units': 'mm/day', 'long_name': 'Precipitation'})
    ds.wind_speed.attrs.update({'units': 'm/s', 'long_name': 'Wind Speed'})
    
    return ds

@st.cache_resource(ttl=3600, show_spinner="Loading NetCDF file...")
def load_netcdf(file):
    """Load NetCDF file with error handling"""
    try:
        file_bytes = file.getvalue()
        with io.BytesIO(file_bytes) as bytes_io:
            ds = xr.open_dataset(bytes_io)
            ds.load()
            return ds
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

# ============================================================================
# PYDESK 3D MAP GENERATOR
# ============================================================================
def generate_pydesk_3d_map(ds, selected_var, time_idx, cmap_name):
    """Generate PyDesk-style 3D terrain map"""
    if ds is None:
        return None
    
    try:
        # Get data slice
        if 'time' in ds.dims:
            data = ds[selected_var].isel(time=time_idx)
        else:
            data = ds[selected_var]
        
        # Create meshgrid
        lon, lat = np.meshgrid(ds.lon.values, ds.lat.values)
        values = data.values
        
        # Handle NaN values
        values = np.nan_to_num(values, nan=np.nanmin(values))
        
        # Create 3D surface plot
        fig = go.Figure()
        
        # Add surface with lighting for 3D effect
        fig.add_trace(go.Surface(
            x=lon,
            y=lat,
            z=values,
            colorscale=cmap_name,
            lighting=dict(
                ambient=0.8,
                diffuse=0.8,
                fresnel=0.1,
                specular=0.1,
                roughness=0.5
            ),
            lightposition=dict(
                x=100,
                y=100,
                z=1000
            ),
            colorbar=dict(
                title=f"{selected_var}<br>{ds[selected_var].attrs.get('units', '')}",
                titleside="right"
            ),
            contours=dict(
                z=dict(
                    show=True,
                    usecolormap=True,
                    highlightcolor="limegreen",
                    project=dict(z=True)
                )
            )
        ))
        
        # Update layout for 3D view
        fig.update_layout(
            title=dict(
                text=f"PyDesk 3D Terrain Map - {selected_var}",
                x=0.5,
                font=dict(size=20)
            ),
            scene=dict(
                xaxis=dict(
                    title="Longitude",
                    gridcolor='#444',
                    gridwidth=2
                ),
                yaxis=dict(
                    title="Latitude",
                    gridcolor='#444',
                    gridwidth=2
                ),
                zaxis=dict(
                    title=f"{selected_var} {ds[selected_var].attrs.get('units', '')}",
                    gridcolor='#444',
                    gridwidth=2
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
                bgcolor='#0a0a0f'
            ),
            paper_bgcolor='#0a0a0f',
            font=dict(color='white'),
            height=700,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        return fig
    except Exception as e:
        st.error(f"Error generating PyDesk map: {str(e)}")
        return None

# ============================================================================
# SIDEBAR LAYOUT (REORGANIZED)
# ============================================================================
with st.sidebar:
    # Title at top
    st.markdown('<p class="main-title">PyClimaExplorer</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">3D Climate Data Visualization</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ========================================================================
    # DATA SOURCE SECTION (MOVED TO TOP)
    # ========================================================================
    with st.expander("Data Source", expanded=True):
        use_sample = st.checkbox(
            "Use sample climate data",
            value=st.session_state.use_sample,
            help="Generate synthetic climate data for demonstration",
            key="use_sample_checkbox"
        )
        st.session_state.use_sample = use_sample
        
        uploaded_file = None
        if not use_sample:
            uploaded_file = st.file_uploader(
                "Upload NetCDF file",
                type=['nc', 'netcdf'],
                help="Upload a NetCDF file containing climate variables",
                key="file_uploader"
            )
            st.session_state.uploaded_file = uploaded_file
        
        # Show data status badge
        if st.session_state.ds is not None:
            st.markdown(
                '<span class="badge badge-success">✓ Data Loaded</span>',
                unsafe_allow_html=True
            )
        elif use_sample:
            st.markdown(
                '<span class="badge badge-warning">⟳ Sample Data Ready</span>',
                unsafe_allow_html=True
            )
    
    # ========================================================================
    # DATA LOADING LOGIC (MOVED INSIDE SIDEBAR)
    # ========================================================================
    # Check if we need to load new data
    current_hash = get_file_hash(st.session_state.uploaded_file)

    if st.session_state.use_sample and st.session_state.ds is None:
        # Load sample data
        with loading_spinner("Generating sample climate data..."):
            st.session_state.ds = load_sample_data()
            st.session_state.data_loaded = True
            st.rerun()

    elif st.session_state.uploaded_file is not None and current_hash != st.session_state.last_upload_hash:
        # Load new uploaded file
        st.session_state.ds = load_netcdf(st.session_state.uploaded_file)
        if st.session_state.ds is not None:
            st.session_state.data_loaded = True
            st.session_state.last_upload_hash = current_hash
            st.success(f"Successfully loaded: {st.session_state.uploaded_file.name}")
            st.rerun()
    
    # ========================================================================
    # VARIABLE SELECTION SECTION (MOVED BELOW DATA SOURCE)
    # ========================================================================
    if st.session_state.ds is not None:
        with st.expander("Variable Selection", expanded=True):
            ds = st.session_state.ds
            variables = list(ds.data_vars.keys())
            variable_labels = [f"{v} ({ds[v].attrs.get('units', 'N/A')})" for v in variables]
            
            selected_var_idx = st.selectbox(
                "Select variable to visualize",
                options=range(len(variables)),
                format_func=lambda x: variable_labels[x],
                key="var_selector"
            )
            selected_var = variables[selected_var_idx]
            st.session_state.current_var = selected_var
            
            # Show variable info
            if selected_var:
                var_info = ds[selected_var].attrs.get('long_name', selected_var)
                st.caption(f"**{var_info}**")
                
                # Quick stats
                data_flat = ds[selected_var].values.flatten()
                data_flat = data_flat[~np.isnan(data_flat)]
                if len(data_flat) > 0:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Min", f"{np.min(data_flat):.2f}")
                    with col2:
                        st.metric("Max", f"{np.max(data_flat):.2f}")
    
    # ========================================================================
    # GLOBE SETTINGS (STAY IN MIDDLE)
    # ========================================================================
    if st.session_state.ds is not None:
        with st.expander("Globe Settings", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.globe_rotation_speed = st.slider(
                    "Rotation Speed",
                    min_value=0.0,
                    max_value=2.0,
                    value=st.session_state.globe_rotation_speed,
                    step=0.1,
                    help="Adjust rotation speed (0 to disable)"
                )
            with col2:
                st.session_state.globe_atmosphere = st.checkbox(
                    "Show Atmosphere",
                    value=st.session_state.globe_atmosphere,
                    help="Add atmospheric glow effect"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.globe_gridlines = st.checkbox(
                    "Show Grid Lines",
                    value=st.session_state.globe_gridlines,
                    help="Display latitude/longitude grid"
                )
            with col2:
                st.session_state.globe_borders = st.checkbox(
                    "Show Borders",
                    value=st.session_state.globe_borders,
                    help="Display country borders"
                )
            
            # Color scheme
            colormap_options = {
                'Turbo (Rainbow)': 'turbo',
                'Viridis': 'viridis',
                'Plasma': 'plasma',
                'Inferno': 'inferno',
                'Magma': 'magma',
                'Cool to Warm': 'RdBu',
                'Spectral': 'Spectral',
                'Hot': 'hot',
                'Thermal': 'thermal'
            }
            
            selected_cmap_display = st.selectbox(
                "Color Scheme",
                options=list(colormap_options.keys()),
                index=0
            )
            cmap_name = colormap_options[selected_cmap_display]
    
    # ========================================================================
    # ABOUT SECTION (AT VERY BOTTOM)
    # ========================================================================
    with st.expander("About", expanded=False):
        st.markdown("""
        **PyClimaExplorer**  
        Version 2.0 | TECHNEX'26
        
        Features:
        - 3D Globe Visualization
        - PyDesk 3D Terrain Maps
        - Time Series Analysis
        - Statistical Tools
        - Multi-variable Comparison
        
        Built with:
        - Streamlit
        - Three.js
        - Plotly
        - XArray
        """)

# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

if st.session_state.ds is None:
    # No data selected - show skeleton and instructions
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("Please upload a NetCDF file or enable sample data in the sidebar")
    

# ============================================================================
# MAIN TABS (ONLY SHOW IF DATA IS LOADED)
# ============================================================================
if st.session_state.ds is not None:
    ds = st.session_state.ds
    selected_var = st.session_state.current_var or list(ds.data_vars.keys())[0]
    
    # Get cmap_name from session state or use default
    if 'cmap_name' not in locals():
        cmap_name = 'turbo'
    
    # Time selection (if applicable)
    has_time = 'time' in ds.dims
    selected_time_idx = 0
    
    if has_time:
        time_values = ds.time.values
        time_labels = [pd.Timestamp(t).strftime('%Y-%m-%d') for t in time_values]
        
        selected_time_idx = st.select_slider(
            "Select time step",
            options=range(len(time_values)),
            value=len(time_values) // 2,
            format_func=lambda x: time_labels[x],
            key="time_selector"
        )
    
    # Create tabs (ADDED PYDESK TAB)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "3D Globe",
        "2D Spatial View",
        "Time Series",
        "Statistics",
        "Comparison",
        "PyDesk 3D Map"
    ])
    
    # ========================================================================
    # TAB 1: 3D GLOBE
    # ========================================================================
    # ========================================================================
# TAB 1: 3D GLOBE - FIXED TEXTURE ALIGNMENT
# ========================================================================
    with tab1:
        st.header("3D Globe Visualization")
        st.markdown(
            '<div class="info-box">🎮 30fps optimized WebGL sphere. Click and drag to rotate, scroll to zoom.</div>',
            unsafe_allow_html=True
        )

        try:
            # Get data for selected time
            if has_time:
                data_3d = ds[selected_var].isel(time=selected_time_idx)
                current_time = time_labels[selected_time_idx]
            else:
                data_3d = ds[selected_var]
                current_time = "Static"

            # FIXED: Proper texture orientation for globe.gl
            # Globe.gl expects latitude from -90 to 90 (bottom to top in image)
            # and longitude from -180 to 180 (left to right in image)

            # Sort data correctly
            data_3d = data_3d.sortby('lat', ascending=True)  # Important: ascending=True puts -90 first (bottom)
            data_3d = data_3d.sortby('lon', ascending=True)  # -180 first (left)

            # Create colormap
            vmin, vmax = float(data_3d.min()), float(data_3d.max())

            if np.isnan(vmin) or np.isnan(vmax) or vmin == vmax:
                vmin, vmax = 0, 100

            norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
            cmap = plt.get_cmap(cmap_name)

            # Convert data to RGBA
            rgba_pixels = cmap(norm(data_3d.values))
            mask = np.isnan(data_3d.values)
            rgba_pixels[mask] = [0, 0, 0, 0]

            # FIXED: Create texture image with correct orientation
            buf = io.BytesIO()
            fig, ax = plt.subplots(figsize=(20, 10), dpi=150)

            # Use origin='lower' to put -90 at bottom, +90 at top
            ax.imshow(rgba_pixels, 
                     extent=[-180, 180, -90, 90], 
                     aspect='auto', 
                     origin='lower')  # Changed from 'upper' to 'lower'

            ax.axis('off')
            plt.tight_layout(pad=0)
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', pad_inches=0, facecolor='black')
            plt.close()

            b64_img = base64.b64encode(buf.getvalue()).decode('utf-8')
            texture_data_uri = f"data:image/png;base64,{b64_img}"

            # Create colorbar
            fig_cbar, ax_cbar = plt.subplots(figsize=(8, 1), dpi=100)
            cb = plt.colorbar(
                plt.cm.ScalarMappable(norm=norm, cmap=cmap),
                cax=ax_cbar,
                orientation='horizontal',
                label=f'{selected_var} [{ds[selected_var].attrs.get("units", "")}]'
            )
            cb.ax.tick_params(colors='white')
            cb.set_label(label=f'{selected_var} [{ds[selected_var].attrs.get("units", "")}]', color='white')
            fig_cbar.patch.set_facecolor('#0a0a0f')
            ax_cbar.set_facecolor('#0a0a0f')

            buf_cbar = io.BytesIO()
            plt.savefig(buf_cbar, format='png', dpi=100, bbox_inches='tight', facecolor='#0a0a0f')
            plt.close()
            b64_cbar = base64.b64encode(buf_cbar.getvalue()).decode('utf-8')

            # Create Three.js globe HTML
            auto_rotate = "true" if st.session_state.globe_rotation_speed > 0 else "false"

            globe_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        background-color: #0a0a0f;
                        overflow: hidden;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    }}
                    #globe-container {{
                        width: 100%;
                        height: 100vh;
                        position: relative;
                    }}
                    .info-panel {{
                        position: absolute;
                        bottom: 30px;
                        left: 30px;
                        background: rgba(10, 10, 15, 0.85);
                        color: white;
                        padding: 15px 25px;
                        border-radius: 10px;
                        border: 1px solid #333;
                        backdrop-filter: blur(10px);
                        z-index: 100;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
                    }}
                    .info-panel h3 {{
                        margin: 0 0 5px 0;
                        color: #3498db;
                        font-weight: 400;
                    }}
                    .info-panel .value {{
                        font-size: 24px;
                        font-weight: 600;
                        margin: 5px 0;
                    }}
                    .info-panel .unit {{
                        color: #888;
                        font-size: 14px;
                    }}
                    .colorbar-container {{
                        position: absolute;
                        bottom: 30px;
                        right: 30px;
                        width: 300px;
                        height: 50px;
                        background: rgba(10, 10, 15, 0.85);
                        border-radius: 8px;
                        padding: 10px;
                        border: 1px solid #333;
                        backdrop-filter: blur(10px);
                        z-index: 100;
                    }}
                    .controls-hint {{
                        position: absolute;
                        top: 30px;
                        right: 30px;
                        color: #888;
                        background: rgba(0,0,0,0.7);
                        padding: 8px 15px;
                        border-radius: 20px;
                        font-size: 12px;
                        border: 1px solid #333;
                        z-index: 100;
                    }}
                    .fps-counter {{
                        position: absolute;
                        bottom: 30px;
                        right: 350px;
                        color: #888;
                        background: rgba(0,0,0,0.5);
                        padding: 4px 8px;
                        border-radius: 4px;
                        font-size: 11px;
                        border: 1px solid #333;
                        z-index: 100;
                    }}
                </style>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
                <script src="https://unpkg.com/globe.gl"></script>
            </head>
            <body>
                <div id="globe-container"></div>

                <div class="info-panel">
                    <h3>{selected_var}</h3>
                    <div class="value">{current_time}</div>
                    <div class="unit">Range: {vmin:.1f} - {vmax:.1f} {ds[selected_var].attrs.get('units', '')}</div>
                </div>

                <div class="colorbar-container">
                    <img src="data:image/png;base64,{b64_cbar}" style="width: 100%; height: 100%; object-fit: contain;">
                </div>

                <div class="fps-counter">
                    <span id="fps">30</span> FPS
                </div>

                <div class="controls-hint">
                    🖱️ Drag to rotate | Scroll to zoom | Auto-rotation: {"ON" if st.session_state.globe_rotation_speed > 0 else "OFF"}
                </div>

                <script>
                    // FPS counter
                    let frameCount = 0;
                    let lastTime = performance.now();
                    const fpsElement = document.getElementById('fps');

                    // Initialize globe
                    const globe = Globe()
                        (document.getElementById('globe-container'))
                        .globeImageUrl('{texture_data_uri}')
                        .backgroundImageUrl('')
                        .showGraticules({str(st.session_state.globe_gridlines).lower()})
                        .showAtmosphere({str(st.session_state.globe_atmosphere).lower()})
                        .atmosphereColor('#88ccff')
                        .atmosphereAltitude(0.25);

                    // Configure controls
                    const controls = globe.controls();
                    controls.autoRotate = {auto_rotate};
                    controls.autoRotateSpeed = {st.session_state.globe_rotation_speed};
                    controls.enableZoom = true;
                    controls.enablePan = false;
                    controls.maxDistance = 400;
                    controls.minDistance = 150;

                    // Add country borders if enabled
                    if ({str(st.session_state.globe_borders).lower()}) {{
                        // FIXED: Use Natural Earth data with correct projection
                        fetch('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries. geojson')
                            .then(res => res.json())
                            .then(countries => {{
                                globe.polygonsData(countries.features)
                                    .polygonCapColor(() => 'rgba(0,0,0,0)')
                                    .polygonSideColor(() => 'rgba(0,0,0,0)')
                                    .polygonStrokeColor(() => 'rgba(255,255,255,0.8)') // Increased opacity
                                    .polygonAltitude(0.01)
                                    .polygonLabel((d) => d.properties.NAME);
                            }})
                            .catch(error => console.error('Error loading borders:', error));
                    }}

                    // Add a simple outline of continents as fallback if borders fail
                    setTimeout(() => {{
                        if ({str(st.session_state.globe_borders).lower()} && globe.polygonsData().length === 0) {{
                            console.log('Using fallback borders');
                            // Simple graticules are already shown if enabled
                        }}
                    }}, 3000);

                    // FPS counter and throttling
                    function animate(time) {{
                        requestAnimationFrame(animate);

                        // Update controls
                        controls.update();

                        // Update FPS counter every second
                        frameCount++;
                        if (time - lastTime >= 1000) {{
                            fpsElement.textContent = frameCount;
                            frameCount = 0;
                            lastTime = time;
                        }}
                    }}

                    // Start animation
                    animate();

                    // Handle resize
                    window.addEventListener('resize', () => {{
                        globe.width(window.innerWidth);
                        globe.height(window.innerHeight);
                    }});
                </script>
            </body>
            </html>
            """

            # Display the globe
            components.html(globe_html, height=700)

        except Exception as e:
            st.error(f"Error rendering 3D globe: {str(e)}")
            show_skeleton(type="globe")

    # ========================================================================
    # TAB 2: 2D SPATIAL VIEW - FIXED FLIPPED ISSUE
    # ========================================================================
    with tab2:
        st.header("2D Spatial Distribution")
        
        try:
            if has_time:
                data_slice = ds[selected_var].isel(time=selected_time_idx)
                title_time = time_labels[selected_time_idx]
            else:
                data_slice = ds[selected_var]
                title_time = ""
            
            projection = st.radio(
                "Map Projection",
                ["PlateCarree", "Mollweide", "Robinson", "Orthographic"],
                horizontal=True,
                key="projection_radio"
            )
            
            if projection == "Orthographic":
                fig = plt.figure(figsize=(15, 8))
                ax = fig.add_subplot(1, 1, 1, projection=ccrs.Orthographic(central_longitude=0, central_latitude=30))
                ax.set_global()
                ax.coastlines()
                ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.5)
                ax.add_feature(cfeature.OCEAN, facecolor='black')
                ax.add_feature(cfeature.LAND, facecolor='black')
                ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
                
                # FIXED: Use correct orientation for pcolormesh
                im = ax.pcolormesh(
                    ds.lon, 
                    ds.lat, 
                    data_slice.values,
                    transform=ccrs.PlateCarree(),
                    cmap=cmap_name,
                    shading='auto'
                )
                plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.05,
                            label=f'{selected_var} [{ds[selected_var].attrs.get("units", "")}]')
                plt.title(f"{selected_var} - {title_time}")
                
                st.pyplot(fig)
                plt.close()
            else:
                # FIXED: For Plotly, we need to flip the data vertically since images are stored top-to-bottom
                # while our data is stored bottom-to-top (latitude from -90 to 90)
                data_values = data_slice.values
                
                # Flip the data vertically to correct orientation
                data_values_flipped = np.flipud(data_values)
                
                fig = px.imshow(
                    data_values_flipped,
                    x=ds.lon.values,
                    y=ds.lat.values[::-1],  # Reverse latitude for correct labeling
                    labels=dict(x="Longitude", y="Latitude", color=selected_var),
                    title=f"{selected_var} - {title_time}",
                    aspect="auto",
                    color_continuous_scale=cmap_name,
                    origin='upper'  # This ensures the image is displayed correctly
                )
                
                fig.update_layout(
                    height=600,
                    xaxis_title="Longitude",
                    yaxis_title="Latitude",
                    template='plotly_dark'
                )
                
                # Update y-axis to show correct labels
                fig.update_yaxes(
                    tickvals=np.linspace(0, len(ds.lat)-1, 9),
                    ticktext=[f"{lat:.0f}°" for lat in np.linspace(ds.lat.max(), ds.lat.min(), 9)]
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Point analysis
            st.subheader("Point Analysis")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_lat = st.slider(
                    "Latitude",
                    float(ds.lat.min()),
                    float(ds.lat.max()),
                    float(ds.lat.mean()),
                    format="%.2f°"
                )
            with col2:
                selected_lon = st.slider(
                    "Longitude",
                    float(ds.lon.min()),
                    float(ds.lon.max()),
                    float(ds.lon.mean()),
                    format="%.2f°"
                )
            
            # Find nearest grid point
            lat_idx = np.abs(ds.lat.values - selected_lat).argmin()
            lon_idx = np.abs(ds.lon.values - selected_lon).argmin()
            
            actual_lat = ds.lat.values[lat_idx]
            actual_lon = ds.lon.values[lon_idx]
            
            # Get value with error handling
            try:
                if has_time:
                    point_value = ds[selected_var].isel(
                        time=selected_time_idx,
                        lat=lat_idx,
                        lon=lon_idx
                    ).values
                else:
                    point_value = ds[selected_var].isel(
                        lat=lat_idx,
                        lon=lon_idx
                    ).values
                
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    if np.isnan(point_value):
                        st.metric(
                            "Value at location",
                            "No Data",
                            delta=format_lat_lon(actual_lat, actual_lon)
                        )
                        st.caption("No valid data at this location")
                    else:
                        st.metric(
                            "Value at location",
                            f"{point_value:.2f} {ds[selected_var].attrs.get('units', '')}",
                            delta=format_lat_lon(actual_lat, actual_lon)
                        )
                    st.markdown('</div>', unsafe_allow_html=True)
                    
            except Exception as e:
                with col3:
                    st.error(f"Error reading data: {str(e)}")
                    
        except Exception as e:
            st.error(f"Error in 2D view: {str(e)}")
            show_skeleton(type="globe")
    
    # ========================================================================
    # TAB 3: TIME SERIES
    # ========================================================================
    with tab3:
        st.header("Time Series Analysis")
        
        if has_time and len(time_values) > 1:
            try:
                # Time range selection
                time_range = st.select_slider(
                    "Select time range",
                    options=range(len(time_values)),
                    value=(0, len(time_values)-1),
                    format_func=lambda x: time_labels[x],
                    key="time_range"
                )
                
                t_start, t_end = time_range
                
                # Location selection
                st.subheader("Select Location")
                col1, col2 = st.columns(2)
                
                with col1:
                    lat_ts = st.select_slider(
                        "Latitude",
                        options=ds.lat.values[::5],
                        value=float(ds.lat.values[len(ds.lat)//2])
                    )
                with col2:
                    lon_ts = st.select_slider(
                        "Longitude",
                        options=ds.lon.values[::5],
                        value=float(ds.lon.values[len(ds.lon)//2])
                    )
                
                # Get nearest indices
                lat_idx_ts = np.abs(ds.lat.values - lat_ts).argmin()
                lon_idx_ts = np.abs(ds.lon.values - lon_ts).argmin()
                
                # Extract time series
                time_series_data = ds[selected_var].isel(
                    time=slice(t_start, t_end+1),
                    lat=lat_idx_ts,
                    lon=lon_idx_ts
                )
                
                time_series_values = time_series_data.values
                time_subset = ds.time.values[t_start:t_end+1]
                
                # Remove NaN values
                mask = ~np.isnan(time_series_values)
                if not np.all(mask):
                    time_series_values = time_series_values[mask]
                    time_subset = time_subset[mask]
                
                if len(time_series_values) > 0:
                    # Create time series plot
                    fig_ts = go.Figure()
                    
                    fig_ts.add_trace(go.Scatter(
                        x=time_subset,
                        y=time_series_values,
                        mode='lines+markers',
                        name=selected_var,
                        line=dict(color='#3498db', width=3),
                        marker=dict(size=6, color='#e74c3c'),
                        fill='tozeroy',
                        fillcolor='rgba(52, 152, 219, 0.1)'
                    ))
                    
                    # Add trend line
                    if len(time_series_values) > 1:
                        z = np.polyfit(range(len(time_series_values)), time_series_values, 1)
                        p = np.poly1d(z)
                        fig_ts.add_trace(go.Scatter(
                            x=time_subset,
                            y=p(range(len(time_series_values))),
                            mode='lines',
                            name='Trend',
                            line=dict(color='#2ecc71', width=2, dash='dash')
                        ))
                    
                    fig_ts.update_layout(
                        title=f"{selected_var} at {format_lat_lon(ds.lat.values[lat_idx_ts], ds.lon.values[lon_idx_ts])}",
                        xaxis_title="Time",
                        yaxis_title=f"{selected_var} [{ds[selected_var].attrs.get('units', '')}]",
                        height=500,
                        hovermode='x unified',
                        showlegend=True,
                        template='plotly_dark'
                    )
                    
                    st.plotly_chart(fig_ts, use_container_width=True)
                    
                    # Statistics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    stats = {
                        "Mean": np.nanmean(time_series_data.values),
                        "Std Dev": np.nanstd(time_series_data.values),
                        "Min": np.nanmin(time_series_data.values),
                        "Max": np.nanmax(time_series_data.values)
                    }
                    
                    for col, (label, value) in zip([col1, col2, col3, col4], stats.items()):
                        with col:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric(label, f"{value:.2f}" if not np.isnan(value) else "N/A")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                else:
                    st.warning("No valid data points at selected location")
                    
            except Exception as e:
                st.error(f"Error in time series analysis: {str(e)}")
                show_skeleton(type="line", count=5)
        else:
            st.info("Time dimension not available or insufficient time points")
    
    # ========================================================================
    # TAB 4: STATISTICS
    # ========================================================================
    with tab4:
        st.header("Statistical Analysis")
        
        try:
            # Flatten data
            data_flat = ds[selected_var].values.flatten()
            data_flat = data_flat[~np.isnan(data_flat)]
            
            if len(data_flat) > 0:
                # Summary statistics
                col1, col2, col3, col4 = st.columns(4)
                
                stats = {
                    "Mean": np.mean(data_flat),
                    "Median": np.median(data_flat),
                    "Std Dev": np.std(data_flat),
                    "Range": np.ptp(data_flat)
                }
                
                for col, (label, value) in zip([col1, col2, col3, col4], stats.items()):
                    with col:
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric(label, f"{value:.2f}")
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Distribution plot
                fig_hist = go.Figure()
                
                fig_hist.add_trace(go.Histogram(
                    x=data_flat,
                    nbinsx=50,
                    name=selected_var,
                    marker_color='#3498db',
                    opacity=0.75
                ))
                
                fig_hist.update_layout(
                    title=f"Distribution of {selected_var}",
                    xaxis_title=f"{selected_var} [{ds[selected_var].attrs.get('units', '')}]",
                    yaxis_title="Frequency",
                    height=400,
                    showlegend=False,
                    template='plotly_dark',
                    bargap=0.05
                )
                
                st.plotly_chart(fig_hist, use_container_width=True)
                
                # Zonal mean
                if 'lat' in ds.dims:
                    st.subheader("Zonal Mean (Average by Latitude)")
                    
                    if has_time:
                        zonal_mean = ds[selected_var].mean(dim=['lon', 'time'], skipna=True)
                    else:
                        zonal_mean = ds[selected_var].mean(dim=['lon'], skipna=True)
                    
                    fig_zonal = go.Figure()
                    
                    fig_zonal.add_trace(go.Scatter(
                        x=ds.lat.values,
                        y=zonal_mean.values,
                        mode='lines',
                        name='Zonal Mean',
                        line=dict(color='#e74c3c', width=3),
                        fill='tozeroy',
                        fillcolor='rgba(231, 76, 60, 0.1)'
                    ))
                    
                    fig_zonal.update_layout(
                        title=f"Zonal Mean of {selected_var}",
                        xaxis_title="Latitude",
                        yaxis_title=f"{selected_var} [{ds[selected_var].attrs.get('units', '')}]",
                        height=400,
                        template='plotly_dark'
                    )
                    
                    st.plotly_chart(fig_zonal, use_container_width=True)
                    
                    # Regional analysis
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        equatorial_mask = np.abs(ds.lat.values) <= 15
                        equatorial_mean = np.nanmean(zonal_mean.values[equatorial_mask])
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("Equatorial Mean (±15°)", f"{equatorial_mean:.2f}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        north_polar_mask = ds.lat.values >= 60
                        south_polar_mask = ds.lat.values <= -60
                        
                        north_mean = np.nanmean(zonal_mean.values[north_polar_mask])
                        south_mean = np.nanmean(zonal_mean.values[south_polar_mask])
                        
                        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                        st.metric("North Polar (>60°)", f"{north_mean:.2f}")
                        st.metric("South Polar (<-60°)", f"{south_mean:.2f}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
        except Exception as e:
            st.error(f"Error in statistical analysis: {str(e)}")
            show_skeleton(type="card", count=4)
    
    # ========================================================================
    # TAB 5: COMPARISON
    # ========================================================================
    with tab5:
        st.header("Comparison Mode")
        st.markdown(
            '<div class="info-box">Compare two different time periods or variables</div>',
            unsafe_allow_html=True
        )
        
        comparison_type = st.radio(
            "Compare by:",
            ["Time Periods", "Variables"],
            horizontal=True,
            key="comparison_type"
        )
        
        try:
            if comparison_type == "Time Periods" and has_time and len(time_values) > 1:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Period 1")
                    t1_idx = st.selectbox(
                        "Select first time",
                        options=range(len(time_values)),
                        index=0,
                        format_func=lambda x: time_labels[x],
                        key="t1"
                    )
                
                with col2:
                    st.subheader("Period 2")
                    t2_idx = st.selectbox(
                        "Select second time",
                        options=range(len(time_values)),
                        index=len(time_values)-1,
                        format_func=lambda x: time_labels[x],
                        key="t2"
                    )
                
                # Get data
                data1 = ds[selected_var].isel(time=t1_idx)
                data2 = ds[selected_var].isel(time=t2_idx)
                diff = data2 - data1
                
                # Create comparison plot
                fig_comp = go.Figure()
                
                d1_flat = data1.values.flatten()
                d2_flat = data2.values.flatten()
                diff_flat = diff.values.flatten()
                mask = ~(np.isnan(d1_flat) | np.isnan(d2_flat))
                
                fig_comp.add_trace(go.Scatter(
                    x=d1_flat[mask],
                    y=d2_flat[mask],
                    mode='markers',
                    name='Data Points',
                    marker=dict(
                        color=diff_flat[mask],
                        colorscale='RdBu_r',
                        showscale=True,
                        colorbar=dict(title="Difference"),
                        size=3,
                        opacity=0.6
                    )
                ))
                
                # Add 1:1 line
                if len(d1_flat[mask]) > 0:
                    min_val = min(np.nanmin(data1), np.nanmin(data2))
                    max_val = max(np.nanmax(data1), np.nanmax(data2))
                    fig_comp.add_trace(go.Scatter(
                        x=[min_val, max_val],
                        y=[min_val, max_val],
                        mode='lines',
                        name='1:1 Line',
                        line=dict(color='white', dash='dash')
                    ))
                
                fig_comp.update_layout(
                    title=f"{selected_var}: {time_labels[t1_idx]} vs {time_labels[t2_idx]}",
                    xaxis_title=time_labels[t1_idx],
                    yaxis_title=time_labels[t2_idx],
                    height=500,
                    template='plotly_dark'
                )
                
                st.plotly_chart(fig_comp, use_container_width=True)
                
                # Difference statistics
                diff_values = diff.values.flatten()
                diff_values = diff_values[~np.isnan(diff_values)]
                
                if len(diff_values) > 0:
                    col1, col2, col3 = st.columns(3)
                    
                    diff_stats = {
                        "Mean Difference": np.mean(diff_values),
                        "Max Difference": np.max(diff_values),
                        "Min Difference": np.min(diff_values)
                    }
                    
                    for col, (label, value) in zip([col1, col2, col3], diff_stats.items()):
                        with col:
                            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                            st.metric(label, f"{value:.2f}")
                            st.markdown('</div>', unsafe_allow_html=True)
            
            elif comparison_type == "Variables" and len(variables) > 1:
                col1, col2 = st.columns(2)
                
                with col1:
                    var1 = st.selectbox(
                        "Select first variable",
                        options=variables,
                        index=0,
                        key="var1"
                    )
                
                with col2:
                    var2 = st.selectbox(
                        "Select second variable",
                        options=variables,
                        index=min(1, len(variables)-1),
                        key="var2"
                    )
                
                if has_time:
                    time_idx = st.select_slider(
                        "Select time",
                        options=range(len(time_values)),
                        value=len(time_values)//2,
                        format_func=lambda x: time_labels[x]
                    )
                    
                    data1 = ds[var1].isel(time=time_idx)
                    data2 = ds[var2].isel(time=time_idx)
                else:
                    data1 = ds[var1]
                    data2 = ds[var2]
                
                # Flatten data
                d1_flat = data1.values.flatten()
                d2_flat = data2.values.flatten()
                mask = ~(np.isnan(d1_flat) | np.isnan(d2_flat))
                
                if len(d1_flat[mask]) > 0:
                    correlation = np.corrcoef(d1_flat[mask], d2_flat[mask])[0, 1]
                    
                    fig_scatter = go.Figure()
                    
                    fig_scatter.add_trace(go.Scatter(
                        x=d1_flat[mask],
                        y=d2_flat[mask],
                        mode='markers',
                        name='Data Points',
                        marker=dict(
                            color='#3498db',
                            size=3,
                            opacity=0.6
                        )
                    ))
                    
                    # Add trend line
                    if len(d1_flat[mask]) > 1:
                        z = np.polyfit(d1_flat[mask], d2_flat[mask], 1)
                        p = np.poly1d(z)
                        x_line = np.linspace(np.nanmin(d1_flat), np.nanmax(d1_flat), 100)
                        fig_scatter.add_trace(go.Scatter(
                            x=x_line,
                            y=p(x_line),
                            mode='lines',
                            name=f'Trend (r={correlation:.2f})',
                            line=dict(color='#e74c3c', width=2)
                        ))
                    
                    fig_scatter.update_layout(
                        title=f"{var1} vs {var2} (Correlation: {correlation:.3f})",
                        xaxis_title=f"{var1} [{ds[var1].attrs.get('units', '')}]",
                        yaxis_title=f"{var2} [{ds[var2].attrs.get('units', '')}]",
                        height=500,
                        template='plotly_dark'
                    )
                    
                    st.plotly_chart(fig_scatter, use_container_width=True)
                    
        except Exception as e:
            st.error(f"Error in comparison: {str(e)}")
            show_skeleton(type="globe")
    
    # ========================================================================
    # TAB 6: PYDESK 3D MAP
    # ========================================================================
    with tab6:
        st.header("PyDesk 3D Terrain Map")
        st.markdown(
            '<div class="info-box"> 3D topographic visualization with elevation-based coloring</div>',
            unsafe_allow_html=True
        )
        
        try:
            # Generate PyDesk 3D map
            with st.spinner("Generating 3D terrain map..."):
                pydesk_fig = generate_pydesk_3d_map(
                    ds, 
                    selected_var, 
                    selected_time_idx if has_time else 0,
                    cmap_name
                )
                
                if pydesk_fig:
                    st.plotly_chart(pydesk_fig, use_container_width=True)
                    
                    # Add some controls
                    st.subheader("View Controls")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("🔄 Reset View"):
                            st.rerun()
                    
                    with col2:
                        if st.button("📸 Screenshot", help="Download current view"):
                            st.info("Screenshot feature coming soon!")
                    
                    with col3:
                        show_contours = st.checkbox("Show Contours", value=True)
                        
                        if show_contours and pydesk_fig:
                            # Update figure to show contours
                            pydesk_fig.update_traces(
                                contours=dict(
                                    z=dict(
                                        show=True,
                                        usecolormap=True,
                                        highlightcolor="limegreen",
                                        project=dict(z=True)
                                    )
                                )
                            )
                            
                else:
                    st.error("Could not generate 3D map")
                    show_skeleton(type="globe")
                    
        except Exception as e:
            st.error(f"Error in PyDesk visualization: {str(e)}")
            show_skeleton(type="globe")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col2:
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p style='font-size: 0.9rem;'>
            PyClimaExplorer · Built for TECHNEX'26 Hackathon · v2.0
        </p>
        <p style='font-size: 0.8rem; color: #444;'>
             Optimized for 30fps performance |  Real-time climate data analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# ERROR HANDLING
# ============================================================================
if st.session_state.error_message:
    st.error(st.session_state.error_message)
    if st.button("Clear Error"):
        st.session_state.error_message = None
        st.rerun()