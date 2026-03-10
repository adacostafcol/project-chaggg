# this is how we cleaned the data
# ── Basic info ────────────────────────────────────────────────────────────────
print(df.describe())
print(df.shape)
print(df.dtypes)
print(df.columns.tolist())

# ── Filter to 2001-2025 ───────────────────────────────────────────────────────
df = df[df['year'].between(2001, 2025)]
print(df['year'].value_counts().sort_index())
print("\nTotal records (2001-2025):", len(df))

# ── Missing value summary ─────────────────────────────────────────────────────
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)

missing_summary = pd.DataFrame({
    "missing_count": missing,
    "missing_pct": missing_pct
}).sort_values("missing_pct", ascending=False)

missing_summary

# ── Data type checks ──────────────────────────────────────────────────────────
# fbi_code and iucr are strings, which is correct - they are category codes
print(df.dtypes)
df.info()

# Verify arrest and domestic are boolean
print("arrest unique values:", df["arrest"].unique())
print("domestic unique values:", df["domestic"].unique())
#ok good

# ── Type conversions ──────────────────────────────────────────────────────────

# date and updated_on should be datetime
# errors='coerce' turns unparseable values into NaT rather than crashing
df["date"]       = pd.to_datetime(df["date"], errors="coerce")
df["updated_on"] = pd.to_datetime(df["updated_on"], errors="coerce")

# district, ward, community_area should be integer
# Int64 (capital I) is used because these columns have missing values
# regular int64 cannot store NaN, Int64 can
df["district"]       = pd.to_numeric(df["district"], errors="coerce").astype("Int64")
df["ward"]           = pd.to_numeric(df["ward"], errors="coerce").astype("Int64")
df["community_area"] = pd.to_numeric(df["community_area"], errors="coerce").astype("Int64")

# Recode categorical text columns to save memory
df["primary_type"]        = df["primary_type"].astype("category")
df["description"]         = df["description"].astype("category")
df["location_description"] = df["location_description"].astype("category")

# Verify missing values did not increase after type conversions
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_summary = pd.DataFrame({
    "missing_count": missing,
    "missing_pct": missing_pct
}).sort_values("missing_pct", ascending=False)
missing_summary

# ── Remove coordinates outside Chicago ───────────────────────────────────────
# Valid Chicago latitude range: 41.6 - 42.1
# Valid Chicago longitude range: -87.9 - -87.5
#df.loc[~df["latitude"].between(41.6, 42.1), "latitude"] = None
#df.loc[~df["longitude"].between(-87.9, -87.5), "longitude"] = None

#print("Latitude range:", df["latitude"].min(), "-", df["latitude"].max())
#print("Longitude range:", df["longitude"].min(), "-", df["longitude"].max())
#commented out incase we don't want ot do it

# ── Missing data analysis ─────────────────────────────────────────────────────

# Total rows with at least one missing value
print("Rows with at least one missing value:", df.isnull().any(axis=1).sum())
print("That is", round(df.isnull().any(axis=1).sum() / len(df) * 100, 2), "% of the data")

# Which columns are driving the missing values
print("\nMissing values per column for incomplete rows:")
print(df[df.isnull().any(axis=1)][df.columns].isnull().sum())

# ── Is missing data concentrated in certain years? ────────────────────────────
df["has_missing"] = df.isnull().any(axis=1)

missing_by_year = df.groupby("year")["has_missing"].agg(["sum", "count"])
missing_by_year["pct"] = (missing_by_year["sum"] / missing_by_year["count"] * 100).round(2)
missing_by_year.columns = ["missing_count", "total_rows", "missing_pct"]
print(missing_by_year)
# Note: 2001 has high missing data - worth considering in analysis

# Which specific columns are missing by year
df.groupby("year")[["latitude", "longitude", "ward", "community_area"]].apply(lambda x: x.isnull().sum())

#double checking for things that may be considered full but just empty text, seems fine
# ── Check for empty strings masquerading as non-null ─────────────────────────
for col in df.select_dtypes(include="object").columns:
    empty_count = (df[col].astype(str).str.strip() == "").sum()
    nan_string  = (df[col].astype(str) == "nan").sum()
    if empty_count > 0 or nan_string > 0:
        print(col, "- empty strings:", empty_count, "| 'nan' strings:", nan_string)
