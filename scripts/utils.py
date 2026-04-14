"""
Utility functions for loading and working with Chicago crime data.

Common usage:
    from scripts.utils import load_data
    df = load_data()
"""
import pandas as pd
import os
try:
    from .config import *  # When imported as a module (Flask)
except ImportError:
    from config import * # When run directly from scripts/

def load_data(prefer_parquet=True):
    """
    Load cleaned Chicago crime data.
    
    Args:
        prefer_parquet: If True and parquet exists, load that. Otherwise CSV.
    
    Returns:
        pandas.DataFrame containing cleaned crime data
    """
    if prefer_parquet and os.path.exists(CLEANED_PARQUET):
        print(f"Loading from {CLEANED_PARQUET}...")
        return pd.read_parquet(CLEANED_PARQUET)
    
    if os.path.exists(CLEANED_CSV):
        print(f"Loading from {CLEANED_CSV}...")
        return pd.read_csv(CLEANED_CSV, low_memory=False)
    
    raise FileNotFoundError(
        f"No cleaned data found. Please run clean.py first.\n"
        f"Expected: {CLEANED_CSV} or {CLEANED_PARQUET}"
    )

def convert_to_parquet(force=False):
    """Convert cleaned CSV to parquet format for faster loading.
    
    Args:
        force: If True, regenerate parquet even if it already exists
    """
    if os.path.exists(CLEANED_PARQUET) and not force:
        print(f"Parquet already exists: {CLEANED_PARQUET}")
        print(f"Size: {os.path.getsize(CLEANED_PARQUET) / 1024**2:.1f} MB")
        return
    
    if not os.path.exists(CLEANED_CSV):
        raise FileNotFoundError(
            f"Cleaned CSV not found at {CLEANED_CSV}. Run clean.py first."
        )
    
    print(f"Converting {CLEANED_CSV} to parquet...")
    print(f"Original CSV size: {os.path.getsize(CLEANED_CSV) / 1024**2:.1f} MB")
    
    df = pd.read_csv(CLEANED_CSV, low_memory=False)
    df.to_parquet(CLEANED_PARQUET, index=False)
    
    print(f"Saved to {CLEANED_PARQUET}")
    print(f"Parquet size: {os.path.getsize(CLEANED_PARQUET) / 1024**2:.1f} MB")
    print(f"Space saved: {(1 - os.path.getsize(CLEANED_PARQUET) / os.path.getsize(CLEANED_CSV)) * 100:.1f}%")

def get_data_info():
    """Print information about available data files."""
    print("Chicago Crime Data Files:")
    print("-" * 60)
    
    files = [
        ("Raw CSV", RAW_CSV),
        ("Cleaned CSV", CLEANED_CSV),
        ("Cleaned Parquet", CLEANED_PARQUET)
    ]
    
    for name, path in files:
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / 1024**2
            print(f"✓ {name:20s} {size_mb:8.1f} MB  {path}")
        else:
            print(f"✗ {name:20s} {'(not found)':>10s}  {path}")

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth.
    
    Parameters:
        lat1, lon1: Latitude and longitude of point 1 (in decimal degrees)
        lat2, lon2: Latitude and longitude of point 2 (in decimal degrees)
    
    Returns:
        Distance in kilometers
    """
    import math
    
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Differences
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371  # Earth's radius in kilometers
    return R * c


def get_spatial_bounds(df):
    """
    Calculate spatial bounds and maximum distance for normalization.
    
    Parameters:
        df: DataFrame with 'latitude' and 'longitude' columns
    
    Returns:
        dict with 'max_distance' (km) and 'bounds' (lat/lon ranges)
    """
    max_lat, min_lat = df['latitude'].max(), df['latitude'].min()
    max_lon, min_lon = df['longitude'].max(), df['longitude'].min()
    max_distance = haversine(min_lat, min_lon, max_lat, max_lon)
    
    return {
        'max_distance': max_distance,
        'bounds': {
            'lat': (min_lat, max_lat),
            'lon': (min_lon, max_lon)
        }
    }

if __name__ == "__main__":
    print("=" * 60)
    print("CHICAGO CRIME DATA UTILITIES")
    print("=" * 60)
    print()
    
    get_data_info()
    print()
    
    if os.path.exists(CLEANED_CSV) and not os.path.exists(CLEANED_PARQUET):
        print("Converting CSV to parquet...")
        print()
        convert_to_parquet()
    elif os.path.exists(CLEANED_PARQUET):
        print("Parquet file already exists. Nothing to do.")
    else:
        print("No cleaned data found. Run clean.py first.")
