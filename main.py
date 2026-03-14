# app.py
import streamlit as st
import xarray as xr
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import matplotlib.pyplot as plt
from datetime import datetime
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="PyClimaExplorer",
    page_icon="🌍",
    layout="wide"
)

# Title and description
st.title("🌍 PyClimaExplorer")
st.markdown("### Interactive Climate Data Visualizer")
st.markdown("Upload NetCDF files to explore climate variables in 2D, 3D, and time series.")

# Sidebar for controls
st.sidebar.header("Controls")

# File upload
uploaded_file = st.sidebar.file_uploader(
    "Upload NetCDF file", 
    type=['nc'],
    help="Upload a NetCDF file containing climate variables (temperature, precipitation, etc.)"
)

# Sample data option
use_sample = st.sidebar.checkbox("Use sample data", value=False)

@st.cache_data
def load_sample_data():
    """Create a sample dataset for demonstration"""
    # Create synthetic climate data
    lats = np.linspace(-90, 90, 45)
    lons = np.linspace(-180, 180, 90)
    times = pd.date_range('2020-01-01', '2020-12-31', freq='M')
    
    # Create synthetic temperature data (in Kelvin)
    data = np.random.randn(len(times), len(lats), len(lons)) * 5 + 280
    
    # Add realistic patterns
    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            # Temperature decreases with latitude
            lat_factor = np.cos(np.radians(lat))
            data[:, i, j] += 15 * lat_factor
            
            # Seasonal variation
            for t, time in enumerate(times):
                month = time.month
                if month in [12, 1, 2]:  # Northern winter
                    data[t, i, j] -= 5 * lat_factor
                elif month in [6, 7, 8]:  # Northern summer
                    data[t, i, j] += 5 * lat_factor
    
    ds = xr.Dataset(
        {
            'temperature': (['time', 'lat', 'lon'], data),
        },
        coords={
            'time': times,
            'lat': lats,
            'lon': lons,
        }
    )
    return ds

@st.cache_data
def load_netcdf(file):
    """Load NetCDF file"""
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.nc') as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_path = tmp_file.name
        
        # Load with xarray
        ds = xr.open_dataset(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return ds
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

# Load data
if use_sample:
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
    # Display dataset info
    with st.expander("Dataset Information", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Dimensions:**", dict(ds.dims))
        with col2:
            st.write("**Variables:**", list(ds.data_vars.keys()))
        
        st.write("**Coordinates:**", list(ds.coords.keys()))
    
    # Select variable
    variables = list(ds.data_vars.keys())
    selected_var = st.sidebar.selectbox("Select variable", variables)
    
    # Check if time dimension exists
    has_time = 'time' in ds.dims
    
    # Time selection
    if has_time:
        time_values = ds.time.values
        time_indices = range(len(time_values))
        time_labels = [pd.Timestamp(t).strftime('%Y-%m-%d') for t in time_values]
        
        selected_time_idx = st.sidebar.selectbox(
            "Select time slice",
            options=time_indices,
            format_func=lambda x: time_labels[x]
        )
        
        # Time range for time series
        if len(time_values) > 1:
            time_range = st.sidebar.select_slider(
                "Time range for analysis",
                options=time_indices,
                value=(time_indices[0], time_indices[-1]),
                format_func=lambda x: time_labels[x]
            )
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ 2D Spatial View", "📈 Time Series", "🌐 3D Globe", "📊 Statistics"])
    
    with tab1:
        st.header("Spatial Distribution")
        
        if has_time:
            # Get data for selected time
            data_slice = ds[selected_var].isel(time=selected_time_idx)
            title_time = pd.Timestamp(time_values[selected_time_idx]).strftime('%Y-%m-%d')
        else:
            data_slice = ds[selected_var]
            title_time = ""
        
        # Create 2D heatmap using plotly
        fig = px.imshow(
            data_slice.values,
            x=ds.lon.values,
            y=ds.lat.values,
            labels=dict(x="Longitude", y="Latitude", color=selected_var),
            title=f"{selected_var} - {title_time}",
            aspect="auto",
            color_continuous_scale="RdYlBu_r"
        )
        
        fig.update_layout(
            height=600,
            xaxis_title="Longitude",
            yaxis_title="Latitude",
            yaxis_autorange='reversed'  # Fix orientation
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add lat/lon selection for point analysis
        st.subheader("Point Analysis")
        col1, col2 = st.columns(2)
        with col1:
            selected_lat = st.slider("Select Latitude", float(ds.lat.min()), float(ds.lat.max()), float(ds.lat.mean()))
        with col2:
            selected_lon = st.slider("Select Longitude", float(ds.lon.min()), float(ds.lon.max()), float(ds.lon.mean()))
        
        # Find nearest indices
        lat_idx = np.abs(ds.lat.values - selected_lat).argmin()
        lon_idx = np.abs(ds.lon.values - selected_lon).argmin()
        
        st.write(f"Nearest grid point: Lat={ds.lat.values[lat_idx]:.2f}, Lon={ds.lon.values[lon_idx]:.2f}")
    
    with tab2:
        st.header("Time Series Analysis")
        
        if has_time and len(time_values) > 1:
            # Get time range data
            t_start, t_end = time_range
            time_subset = ds.time.values[t_start:t_end+1]
            
            # Select location for time series
            st.subheader("Select Location")
            col1, col2 = st.columns(2)
            with col1:
                lat_ts = st.select_slider("Latitude", ds.lat.values, value=float(ds.lat.values[len(ds.lat)//2]))
            with col2:
                lon_ts = st.select_slider("Longitude", ds.lon.values, value=float(ds.lon.values[len(ds.lon)//2]))
            
            # Get data at selected point
            lat_idx_ts = np.abs(ds.lat.values - lat_ts).argmin()
            lon_idx_ts = np.abs(ds.lon.values - lon_ts).argmin()
            
            time_series_data = ds[selected_var].isel(
                time=slice(t_start, t_end+1),
                lat=lat_idx_ts,
                lon=lon_idx_ts
            )
            
            # Create time series plot
            fig_ts = px.line(
                x=time_subset,
                y=time_series_data.values,
                labels={"x": "Time", "y": selected_var},
                title=f"{selected_var} at Lat={ds.lat.values[lat_idx_ts]:.2f}, Lon={ds.lon.values[lon_idx_ts]:.2f}"
            )
            
            fig_ts.update_layout(height=500)
            st.plotly_chart(fig_ts, use_container_width=True)
            
            # Show data table
            with st.expander("View Data"):
                df_ts = pd.DataFrame({
                    'Time': time_subset,
                    selected_var: time_series_data.values
                })
                st.dataframe(df_ts)
        else:
            st.warning("No time dimension found in dataset or only one time point available")
    
    with tab3:
        st.header("3D Globe Visualization")
        st.info("🌐 3D visualization using PyDeck")
        
        if has_time:
            # Prepare data for 3D visualization
            data_3d = ds[selected_var].isel(time=selected_time_idx)
        else:
            data_3d = ds[selected_var]
        
        # Create a DataFrame for PyDeck
        lats, lons = np.meshgrid(ds.lat.values, ds.lon.values, indexing='ij')
        values = data_3d.values
        
        # Flatten arrays for PyDeck
        df_3d = pd.DataFrame({
            'lat': lats.flatten(),
            'lon': lons.flatten(),
            'value': values.flatten()
        })
        
        # Filter out NaN values
        df_3d = df_3d.dropna()
        
        # Normalize values for color scaling
        df_3d['value_norm'] = (df_3d['value'] - df_3d['value'].min()) / (df_3d['value'].max() - df_3d['value'].min())
        
        # Define a color scale
        def get_color(val_norm):
            # Blue (low) to Red (high)
            return [int(255 * val_norm), 100, int(255 * (1 - val_norm)), 200]
        
        df_3d['color'] = df_3d['value_norm'].apply(get_color)
        
        # Create PyDeck layer
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_3d,
            get_position=["lon", "lat"],
            get_color="color",
            get_radius=200000,  # 200km radius
            radius_min_pixels=5,
            radius_max_pixels=50,
            pickable=True,
            auto_highlight=True
        )
        
        # Set viewport
        view_state = pdk.ViewState(
            latitude=0,
            longitude=0,
            zoom=1,
            pitch=45,
            bearing=0
        )
        
        # Render
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "Lat: {lat}\nLon: {lon}\nValue: {value}"}
        )
        
        st.pydeck_chart(r)
        
        # Add explanation
        st.markdown("""
        **3D Visualization Notes:**
        - Points are colored from blue (low values) to red (high values)
        - Hover over points to see exact values
        - Use mouse to rotate, zoom, and explore the globe
        """)
    
    with tab4:
        st.header("Statistical Summary")
        
        # Calculate statistics
        data_flat = ds[selected_var].values.flatten()
        data_flat = data_flat[~np.isnan(data_flat)]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mean", f"{np.mean(data_flat):.2f}")
        with col2:
            st.metric("Std Dev", f"{np.std(data_flat):.2f}")
        with col3:
            st.metric("Min", f"{np.min(data_flat):.2f}")
        with col4:
            st.metric("Max", f"{np.max(data_flat):.2f}")
        
        # Histogram
        fig_hist = px.histogram(
            x=data_flat,
            nbins=50,
            labels={"x": selected_var},
            title=f"Distribution of {selected_var}"
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Zonal mean (by latitude)
        if 'lat' in ds.dims:
            st.subheader("Zonal Mean (Average by Latitude)")
            zonal_mean = ds[selected_var].mean(dim=['lon', 'time'] if 'time' in ds.dims else ['lon'])
            
            fig_zonal = px.line(
                x=ds.lat.values,
                y=zonal_mean.values,
                labels={"x": "Latitude", "y": selected_var},
                title=f"Zonal Mean of {selected_var}"
            )
            st.plotly_chart(fig_zonal, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>PyClimaExplorer - Built for TECHNEX'26 Hackathon</p>
    <p>Upload NetCDF files to explore climate data in 2D, 3D, and time series</p>
</div>
""", unsafe_allow_html=True)