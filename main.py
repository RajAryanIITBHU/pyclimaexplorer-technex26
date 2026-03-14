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
warnings.filterwarnings('ignore')

# Page configuration - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="PyClimaExplorer | 3D Climate Globe",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 3rem !important;
        font-weight: 700 !important;
        background: linear-gradient(45deg, #3498db, #2ecc71, #f1c40f, #e74c3c);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-align: center;
        margin-bottom: 0rem;
        padding-bottom: 0rem;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.2rem;
        margin-top: -1rem;
        margin-bottom: 2rem;
    }
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1e1e2f, #2d2d44);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3498db;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
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
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: #0a0a0f;
        padding: 0.5rem;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Title with custom styling
st.markdown('<p class="main-title">🌍 PyClimaExplorer</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">3D Climate Data Visualization</p>', unsafe_allow_html=True)

# Initialize session state for storing data and settings
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'current_var' not in st.session_state:
    st.session_state.current_var = None
if 'globe_rotation_speed' not in st.session_state:
    st.session_state.globe_rotation_speed = 0.0
if 'globe_atmosphere' not in st.session_state:
    st.session_state.globe_atmosphere = True
if 'globe_gridlines' not in st.session_state:
    st.session_state.globe_gridlines = True
if 'globe_borders' not in st.session_state:
    st.session_state.globe_borders = True

# Sidebar
with st.sidebar:
    st.markdown("## 🎮 Controls")
    st.markdown("---")
    
    # File upload section with nice styling
    st.markdown("### 📁 Data Source")
    
    # Option to use sample data
    use_sample = st.checkbox("Use sample climate data", value=True, 
                            help="Generate synthetic climate data for demonstration")
    
    uploaded_file = None
    if not use_sample:
        uploaded_file = st.file_uploader(
            "Upload NetCDF file", 
            type=['nc', 'netcdf'],
            help="Upload a NetCDF file containing climate variables (temperature, precipitation, etc.)"
        )
    
    st.markdown("---")
    
    # Globe customization section
    st.markdown("### 🌐 Globe Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.globe_rotation_speed = st.slider(
            "Rotation Speed", 
            min_value=0.0, 
            max_value=2.0, 
            value=0.0, 
            step=0.1,
            help="Adjust rotation speed (0 to disable auto-rotation)"
        )
    with col2:
        st.session_state.globe_atmosphere = st.checkbox(
            "Show Atmosphere", 
            value=True,
            help="Add atmospheric glow effect"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.globe_gridlines = st.checkbox(
            "Show Grid Lines", 
            value=True,
            help="Display latitude/longitude grid"
        )
    with col2:
        st.session_state.globe_borders = st.checkbox(
            "Show Borders", 
            value=True,
            help="Display country borders"
        )
    
    st.markdown("---")
    
    # Color map selection - Using proper plotly colorscale names
    st.markdown("### 🎨 Color Settings")
    
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
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("### ℹ️ About")
    st.info(
        "This tool visualizes climate data on a true 3D rotating globe. "
        "Built with Streamlit + Three.js for smooth 30fps optimized performance."
    )

# Data loading function with caching
@st.cache_resource(ttl=3600, show_spinner="Loading climate data...")
def load_sample_data():
    """Create a realistic sample dataset with seasonal patterns"""
    # Create high-resolution grid
    lats = np.linspace(-90, 90, 180)  # 1 degree resolution
    lons = np.linspace(-180, 180, 360)  # 1 degree resolution
    times = pd.date_range('2020-01-01', '2023-12-31', freq='M')
    
    # Create meshgrid for lat/lon
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    
    # Initialize data array
    data = np.zeros((len(times), len(lats), len(lons)))
    
    # Create realistic temperature patterns
    for t, time in enumerate(times):
        month = time.month
        # Seasonal cycle
        seasonal_factor = np.sin(2 * np.pi * (month - 1) / 12)
        
        for i, lat in enumerate(lats):
            # Base temperature: warm at equator, cold at poles
            base_temp = 25 * np.cos(np.radians(lat)) + 5
            
            # Seasonal variation (stronger at poles)
            seasonal_amp = 15 * (1 - np.abs(lat) / 90)
            seasonal = seasonal_amp * seasonal_factor
            
            # Zonal variations (land-ocean contrast)
            for j, lon in enumerate(lons):
                # Add some continent-like patterns
                land_factor = 1 + 0.1 * np.sin(3 * np.radians(lon)) * np.cos(2 * np.radians(lat))
                
                # Random small-scale variations
                noise = np.random.normal(0, 0.5)
                
                # Combine all factors
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
    ds.temperature.attrs['units'] = '°C'
    ds.temperature.attrs['long_name'] = 'Surface Temperature'
    ds.precipitation.attrs['units'] = 'mm/day'
    ds.precipitation.attrs['long_name'] = 'Precipitation'
    ds.wind_speed.attrs['units'] = 'm/s'
    ds.wind_speed.attrs['long_name'] = 'Wind Speed'
    
    return ds

@st.cache_resource
def load_netcdf(file):
    """Load NetCDF file with error handling"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.nc') as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_path = tmp_file.name
        
        ds = xr.open_dataset(tmp_path)
        os.unlink(tmp_path)
        return ds
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

# Load data
if use_sample:
    with st.spinner("Generating sample climate data..."):
        ds = load_sample_data()
    st.sidebar.success("✅ Using sample data")
elif uploaded_file is not None:
    ds = load_netcdf(uploaded_file)
    if ds is not None:
        st.sidebar.success(f"✅ Loaded: {uploaded_file.name}")
else:
    ds = None
    st.info("👈 Please upload a NetCDF file or use sample data to begin")

if ds is not None:
    # Dataset overview
    with st.expander("📊 Dataset Overview", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Dimensions", len(ds.dims))
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Variables", len(ds.data_vars))
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            if 'time' in ds.dims:
                st.metric("Time Steps", len(ds.time))
            else:
                st.metric("Time Steps", "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Detailed info
        st.markdown("**Dimensions:**")
        for dim, size in ds.dims.items():
            st.text(f"  • {dim}: {size}")
        
        st.markdown("**Variables:**")
        for var in ds.data_vars:
            st.text(f"  • {var}: {ds[var].attrs.get('long_name', var)} ({ds[var].attrs.get('units', 'unknown')})")
    
    # Variable selection
    variables = list(ds.data_vars.keys())
    variable_labels = [f"{v} ({ds[v].attrs.get('units', '')})" for v in variables]
    
    selected_var_idx = st.sidebar.selectbox(
        "📈 Select variable",
        options=range(len(variables)),
        format_func=lambda x: variable_labels[x]
    )
    selected_var = variables[selected_var_idx]
    
    # Time selection
    has_time = 'time' in ds.dims
    if has_time:
        time_values = ds.time.values
        time_labels = [pd.Timestamp(t).strftime('%Y-%m-%d') for t in time_values]
        
        selected_time_idx = st.sidebar.select_slider(
            "⏱️ Select time",
            options=range(len(time_values)),
            value=len(time_values) // 2,
            format_func=lambda x: time_labels[x]
        )
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌐 3D Globe", 
        "🗺️ 2D Spatial View", 
        "📈 Time Series", 
        "📊 Statistics",
        "🔄 Comparison"
    ])
    
    with tab1:
        st.header("3D Globe Visualization")
        st.markdown('<div class="info-box">✨ 30fps optimized WebGL sphere with smooth data texturing. Click and drag to rotate, scroll to zoom.</div>', unsafe_allow_html=True)
        
        # Get data for selected time
        if has_time:
            data_3d = ds[selected_var].isel(time=selected_time_idx)
            current_time = time_labels[selected_time_idx]
        else:
            data_3d = ds[selected_var]
            current_time = "Static"
        
        # Prepare data for texturing
        data_3d = data_3d.sortby('lat', ascending=False).sortby('lon', ascending=True)
        
        # Create smooth colormap
        vmin, vmax = float(data_3d.min()), float(data_3d.max())
        
        # Handle potential all-NaN or constant data
        if np.isnan(vmin) or np.isnan(vmax) or vmin == vmax:
            vmin, vmax = 0, 100
        
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        
        # Create custom colormap if needed
        if cmap_name == 'turbo':
            cmap = plt.get_cmap('turbo')
        else:
            cmap = plt.get_cmap(cmap_name)
        
        # Convert data to RGBA
        rgba_pixels = cmap(norm(data_3d.values))
        
        # Handle NaN values (make transparent)
        mask = np.isnan(data_3d.values)
        rgba_pixels[mask] = [0, 0, 0, 0]
        
        # Create high-quality texture
        buf = io.BytesIO()
        
        # Use higher DPI for better quality
        fig, ax = plt.subplots(figsize=(20, 10), dpi=150)
        ax.imshow(rgba_pixels, extent=[-180, 180, -90, 90], aspect='auto')
        ax.axis('off')
        plt.tight_layout(pad=0)
        
        # Save with high quality
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', pad_inches=0, facecolor='black')
        plt.close()
        
        b64_img = base64.b64encode(buf.getvalue()).decode('utf-8')
        texture_data_uri = f"data:image/png;base64,{b64_img}"
        
        # Create colorbar
        fig_cbar, ax_cbar = plt.subplots(figsize=(8, 1), dpi=100)
        cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), 
                         cax=ax_cbar, orientation='horizontal', label=f'{selected_var} [{ds[selected_var].attrs.get("units", "")}]')
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
                    width: 100vw;
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
                    pointer-events: none;
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
                .fps-indicator {{
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
            <!-- Import Three.js and Globe.gl -->
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
            
            <div class="fps-indicator">
                🎮 30 FPS (Optimized)
            </div>
            
            <div class="controls-hint">
                🖱️ Drag to rotate | Scroll to zoom | Auto-rotation: {"ON" if st.session_state.globe_rotation_speed > 0 else "OFF"}
            </div>
            
            <script>
                // Initialize globe with custom texture
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
                    fetch('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson')
                        .then(res => res.json())
                        .then(countries => {{
                            globe.polygonsData(countries.features)
                                .polygonCapColor(() => 'rgba(0,0,0,0)')
                                .polygonSideColor(() => 'rgba(0,0,0,0)')
                                .polygonStrokeColor(() => 'rgba(255,255,255,0.6)')
                                .polygonAltitude(0.01)
                                .polygonLabel((d) => d.properties.NAME);
                        }});
                }}
                
                // FPS Throttling - Limit to 30fps
                let lastFrame = 0;
                const targetFPS = 30;
                const frameInterval = 1000 / targetFPS;
                
                function throttledAnimation(time) {{
                    requestAnimationFrame(throttledAnimation);
                    
                    // Throttle frame rate to targetFPS
                    if (time - lastFrame < frameInterval) return;
                    lastFrame = time;
                    
                    // Only update controls if needed
                    controls.update();
                }}
                
                // Start throttled animation
                throttledAnimation();
                
                // Handle window resize
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
    
    with tab2:
        st.header("2D Spatial Distribution")
        
        if has_time:
            data_slice = ds[selected_var].isel(time=selected_time_idx)
            title_time = time_labels[selected_time_idx]
        else:
            data_slice = ds[selected_var]
            title_time = ""
        
        # Create projection options
        projection = st.radio(
            "Map Projection",
            ["PlateCarree", "Mollweide", "Robinson", "Orthographic"],
            horizontal=True
        )
        
        if projection == "Orthographic":
            # Create 3D-like orthographic projection with cartopy
            fig = plt.figure(figsize=(15, 8))
            ax = fig.add_subplot(1, 1, 1, projection=ccrs.Orthographic(central_longitude=0, central_latitude=30))
            ax.set_global()
            ax.coastlines()
            ax.add_feature(cfeature.BORDERS, linestyle=':', alpha=0.5)
            ax.add_feature(cfeature.OCEAN, facecolor='black')
            ax.add_feature(cfeature.LAND, facecolor='black')
            ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)
            
            # Plot data
            im = ax.pcolormesh(
                ds.lon, ds.lat, data_slice.values,
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
            # Use plotly for interactive 2D maps
            fig = px.imshow(
                data_slice.values,
                x=ds.lon.values,
                y=ds.lat.values,
                labels=dict(x="Longitude", y="Latitude", color=selected_var),
                title=f"{selected_var} - {title_time}",
                aspect="auto",
                color_continuous_scale=cmap_name,
                origin='upper'
            )
            
            fig.update_layout(
                height=600,
                xaxis_title="Longitude",
                yaxis_title="Latitude",
                yaxis_autorange='reversed',
                template='plotly_dark'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Point selection for analysis - FIXED NaN issue with proper variable initialization
        st.subheader("📍 Point Analysis")
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
        
        # Find nearest grid point with NaN handling
        lat_idx = np.abs(ds.lat.values - selected_lat).argmin()
        lon_idx = np.abs(ds.lon.values - selected_lon).argmin()
        
        actual_lat = ds.lat.values[lat_idx]
        actual_lon = ds.lon.values[lon_idx]
        
        # Get value with NaN handling
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
        
        # FIXED: Initialize found_valid before using it
        found_valid = False
        
        # Handle NaN values properly
        if np.isnan(point_value):
            # Try to find nearest non-NaN value in a small neighborhood
            neighborhood_size = 3
            
            for i in range(max(0, lat_idx - neighborhood_size), min(len(ds.lat), lat_idx + neighborhood_size + 1)):
                for j in range(max(0, lon_idx - neighborhood_size), min(len(ds.lon), lon_idx + neighborhood_size + 1)):
                    if has_time:
                        test_value = ds[selected_var].isel(time=selected_time_idx, lat=i, lon=j).values
                    else:
                        test_value = ds[selected_var].isel(lat=i, lon=j).values
                    
                    if not np.isnan(test_value):
                        point_value = test_value
                        actual_lat = ds.lat.values[i]
                        actual_lon = ds.lon.values[j]
                        found_valid = True
                        break
                if found_valid:
                    break
            
            # If still NaN, calculate local average
            if np.isnan(point_value):
                # Get all valid values in a larger region
                valid_values = []
                weights = []
                
                for i in range(max(0, lat_idx - 5), min(len(ds.lat), lat_idx + 6)):
                    for j in range(max(0, lon_idx - 5), min(len(ds.lon), lon_idx + 6)):
                        if has_time:
                            test_value = ds[selected_var].isel(time=selected_time_idx, lat=i, lon=j).values
                        else:
                            test_value = ds[selected_var].isel(lat=i, lon=j).values
                        
                        if not np.isnan(test_value):
                            # Weight by inverse distance
                            dist = np.sqrt((i - lat_idx)**2 + (j - lon_idx)**2)
                            weight = 1.0 / (dist + 0.1)
                            valid_values.append(test_value)
                            weights.append(weight)
                
                if valid_values:
                    point_value = np.average(valid_values, weights=weights)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            
            # Display message if value is interpolated
            if np.isnan(point_value):
                st.metric(
                    "Value at selected point",
                    "No Data",
                    delta=f"Lat: {actual_lat:.2f}°, Lon: {actual_lon:.2f}°"
                )
                st.caption("⚠️ No valid data at this location")
            else:
                st.metric(
                    "Value at selected point",
                    f"{point_value:.2f} {ds[selected_var].attrs.get('units', '')}",
                    delta=f"Lat: {actual_lat:.2f}°, Lon: {actual_lon:.2f}°"
                )
                if found_valid:
                    st.caption("ℹ️ Nearest valid data point")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.header("Time Series Analysis")
        
        if has_time and len(time_values) > 1:
            # Time range selection
            time_range = st.select_slider(
                "Select time range",
                options=range(len(time_values)),
                value=(0, len(time_values)-1),
                format_func=lambda x: time_labels[x]
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
            
            # Extract time series with NaN handling
            time_series_data = ds[selected_var].isel(
                time=slice(t_start, t_end+1),
                lat=lat_idx_ts,
                lon=lon_idx_ts
            )
            
            # Handle NaN values in time series
            time_series_values = time_series_data.values
            time_subset = ds.time.values[t_start:t_end+1]
            
            # Remove NaN values for plotting if necessary
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
                
                # Add trend line if enough data points
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
                    title=f"{selected_var} at Lat={ds.lat.values[lat_idx_ts]:.2f}°, Lon={ds.lon.values[lon_idx_ts]:.2f}°",
                    xaxis_title="Time",
                    yaxis_title=f"{selected_var} [{ds[selected_var].attrs.get('units', '')}]",
                    height=500,
                    hovermode='x unified',
                    showlegend=True,
                    template='plotly_dark'
                )
                
                st.plotly_chart(fig_ts, use_container_width=True)
                
                # Statistics for the time series
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Mean", f"{np.nanmean(time_series_data.values):.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Std Dev", f"{np.nanstd(time_series_data.values):.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Min", f"{np.nanmin(time_series_data.values):.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                with col4:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Max", f"{np.nanmax(time_series_data.values):.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("No valid data points at selected location")
        else:
            st.warning("No time dimension found in dataset or only one time point available")
    
    with tab4:
        st.header("Statistical Analysis")
        
        # Flatten data for statistics with NaN handling
        data_flat = ds[selected_var].values.flatten()
        data_flat = data_flat[~np.isnan(data_flat)]
        
        if len(data_flat) > 0:
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Mean", f"{np.mean(data_flat):.2f}")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Median", f"{np.median(data_flat):.2f}")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Std Dev", f"{np.std(data_flat):.2f}")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col4:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Range", f"{np.ptp(data_flat):.2f}")
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
            
            # Zonal mean (by latitude) with NaN handling
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
                
                # Highlight equatorial vs polar regions with NaN handling
                col1, col2 = st.columns(2)
                
                with col1:
                    # Equatorial average (±15°)
                    equatorial_mask = np.abs(ds.lat.values) <= 15
                    equatorial_mean = np.nanmean(zonal_mean.values[equatorial_mask])
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Equatorial Mean (±15°)", f"{equatorial_mean:.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    # Polar average (60°-90°) with NaN handling
                    north_polar_mask = ds.lat.values >= 60
                    south_polar_mask = ds.lat.values <= -60
                    
                    north_mean = np.nanmean(zonal_mean.values[north_polar_mask])
                    south_mean = np.nanmean(zonal_mean.values[south_polar_mask])
                    
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("North Polar Mean (>60°)", f"{north_mean:.2f}")
                    st.metric("South Polar Mean (<-60°)", f"{south_mean:.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
    
    with tab5:
        st.header("Comparison Mode")
        st.markdown('<div class="info-box">📊 Compare two different time periods or variables</div>', unsafe_allow_html=True)
        
        comparison_type = st.radio(
            "Compare by:",
            ["Time Periods", "Variables"],
            horizontal=True
        )
        
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
            
            # Get data for both periods
            data1 = ds[selected_var].isel(time=t1_idx)
            data2 = ds[selected_var].isel(time=t2_idx)
            
            # Calculate difference with NaN handling
            diff = data2 - data1
            
            # Create comparison plots
            fig_comp = go.Figure()
            
            # Flatten with NaN handling
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
                xaxis_title=f"{time_labels[t1_idx]}",
                yaxis_title=f"{time_labels[t2_idx]}",
                height=500,
                template='plotly_dark'
            )
            
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Show difference statistics with NaN handling
            diff_values = diff.values.flatten()
            diff_values = diff_values[~np.isnan(diff_values)]
            
            if len(diff_values) > 0:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Mean Difference", f"{np.mean(diff_values):.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Max Difference", f"{np.max(diff_values):.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Min Difference", f"{np.min(diff_values):.2f}")
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
            
            # Flatten data for scatter plot with NaN handling
            d1_flat = data1.values.flatten()
            d2_flat = data2.values.flatten()
            mask = ~(np.isnan(d1_flat) | np.isnan(d2_flat))
            
            if len(d1_flat[mask]) > 0:
                # Calculate correlation
                correlation = np.corrcoef(d1_flat[mask], d2_flat[mask])[0, 1]
                
                # Create scatter plot
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

# Footer
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])

with footer_col2:
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p style='font-size: 0.9rem;'>
            🌍 PyClimaExplorer · Built for TECHNEX'26 Hackathon
        </p>
    </div>
    """, unsafe_allow_html=True)