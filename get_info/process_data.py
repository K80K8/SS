"""
Data Processing Script
----------------------
Processes raw text exports from the 'get info' script and produces
cleaned CSV outputs for system and listing data.

Python 3.8.10 environment
"""

import os
import re
import glob
import numpy as np
import pandas as pd
from datetime import datetime

# ============================================================
# 1. LOAD AND COMBINE RAW DATA
# ============================================================

folder_path = "raw_data"
file_paths = glob.glob(os.path.join(folder_path, "*vol*.txt"))

# Read all raw info files into DataFrames and concatenate
dfs = [pd.read_csv(path, sep=",", header=None, skiprows=1) for path in file_paths]
df_combined = pd.concat(dfs, ignore_index=True)

# ============================================================
# 2. MEMORY INFORMATION
# ============================================================

# Convert bytes to GB, always rounding UP, and format with 'GB'
df_combined["RAM"] = (
    np.ceil(df_combined[7] / (1024 ** 3))
    .astype(int)
    .astype(str)
    + "GB"
)

# RAM type lookup table
RAM_LOOKUP = {
    0: "Unknown", 1: "Other", 2: "DRAM", 3: "Synchronous DRAM", 4: "Cache DRAM",
    5: "EDO", 6: "EDRAM", 7: "VRAM", 8: "SRAM", 9: "RAM", 10: "ROM",
    11: "Flash", 12: "EEPROM", 13: "FEPROM", 14: "EPROM", 15: "CDRAM",
    16: "3DRAM", 17: "SDRAM", 18: "SGRAM", 19: "RDRAM", 20: "DDR",
    21: "DDR2", 22: "DDR2 FB-DIMM", 23: "Reserved", 24: "DDR3", 25: "FBD2",
    26: "DDR4", 27: "LPDDR", 28: "LPDDR2", 29: "LPDDR3", 30: "LPDDR4",
    31: "Logical non-volatile device", 32: "HBM", 33: "HBM2", 34: "DDR5"
}

# Combine RAM amount and type
df_combined["RAM Amount and Type"] = (
    df_combined["RAM"] + " " + df_combined[8].map(RAM_LOOKUP)
)

# ============================================================
# 3. CPU DETECTION AND CLEANUP
# ============================================================

def ordinal(n: int) -> str:
    """Convert integer to ordinal (1 → 1st, 2 → 2nd, etc.)."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def get_cpu_generation(cpu_name: str) -> str:
    """
    Determine CPU generation from a CPU name string.
    Supports:
      - Intel Core i3/i5/i7/i9
      - Intel Core Ultra
      - AMD Ryzen
    """
    if not isinstance(cpu_name, str):
        return "Unknown"

    cpu_lower = cpu_name.lower()

    # ---- Intel Core i3/i5/i7/i9 ----
    match = re.search(r"(i[3579])-([0-9]{3,5})", cpu_lower)
    if match:
        tier, digits = match.groups()
        num = int(digits)

        if num < 1000:
            gen = 1
        elif num < 10000:
            gen = int(str(num)[0])      # 2nd–9th gen
        else:
            gen = int(str(num)[:2])     # 10th gen+

        if "11th gen" in cpu_lower:
            return f"{tier} 11th Gen"
        elif "12th gen" in cpu_lower:
            return f"{tier} 12th Gen"
        return f"{tier} {ordinal(gen)} Gen"

    # ---- Intel Core Ultra ----
    if re.search(r"core(\(tm\))?\s+ultra\s+(\d)[-\s](\d+)([a-z]{0,3})?", cpu_lower):
        return "15th Gen"

    # ---- AMD Ryzen ----
    ryzen_match = re.search(r"ryzen\s+([3579])\s+([0-9]{4,5})", cpu_lower)
    if ryzen_match:
        tier, model = ryzen_match.groups()
        series = model[:1] + "000"
        return f"Ryzen {tier} {series} Series"

    return "Unknown"


# Apply CPU generation detection
df_combined["CPU Type"] = df_combined[5].apply(get_cpu_generation)

# Strip whitespace in string columns
for col in df_combined.select_dtypes(include=["object"]).columns:
    df_combined[col] = df_combined[col].str.strip()

# ---- CPU Name Cleanup ----
mask = df_combined[5].str.contains("AMD Ryzen", case=False, na=False)
df_combined["CPU"] = df_combined.apply(
    lambda row: " ".join(row[5].split()[:4]) if mask[row.name] else row[5],
    axis=1
)

# Replace “Intel(R) Core(TM)” with “Intel Core <Model>”
df_combined["CPU"] = df_combined["CPU"].str.replace(
    r".*Intel\(R\) Core\(TM\)\s+(\S+).*", r"Intel Core \1", regex=True
)

df_combined["CPU"] = (
    df_combined["CPU"] + " " + df_combined[6].astype(str) + " Core Processor"
)

# ============================================================
# 4. WINDOWS INFORMATION
# ============================================================

df_combined["Windows Type and Version"] = df_combined[10].str.replace(
    "Microsoft", "", regex=False
)

df_combined["Is Windows Activated?"] = df_combined[11].replace({
    "The machine is permanently activated.": "Yes",
    "n": "No"
})

# ============================================================
# 5. SPLIT DATAFRAMES: SYSTEM / LISTING
# ============================================================

df_system = df_combined[df_combined[0] == 1].reset_index(drop=True)
df_listing = df_combined[df_combined[0] == 0].reset_index(drop=True)

# Split disk info from column 13
disks = df_listing[13].str.split("|", expand=True)

# ============================================================
# 6. SYSTEM DATA CLEANUP
# ============================================================

df_system.rename(
    columns={
        1: "Barcode", 2: "Manufacturer", 3: "Model", 4: "Serial",
        9: "Corporate Supplier", 12: "Grade"
    },
    inplace=True
)

# Drop unused columns
df_system.drop(
    [0, 5, 6, 7, 8, 10, 11, 13,
     "RAM", "RAM Amount and Type", "CPU",
     "Windows Type and Version", "Is Windows Activated?"],
    axis=1, inplace=True
)

# Format grade
def map_grade(grade):
    grade = str(grade).strip().upper()
    return {"A": "Grade A", "B": "Grade B"}.get(grade, "Grade C")

df_system["Grade"] = df_system["Grade"].apply(map_grade)

# Clean up barcode and manufacturer
df_system["Barcode"] = df_system["Barcode"].str.upper()

MANUFACTURER_MAP = {
    "microsoft": "Microsoft", "acer": "Acer", "apple": "Apple", "asus": "Asus",
    "toshiba": "Toshiba", "dell": "Dell", "hp": "HP", "lenovo": "Lenovo",
    "msi": "MSI", "samsung": "Samsung", "sony": "Sony"
}

for keyword, name in MANUFACTURER_MAP.items():
    df_system.loc[
        df_system["Manufacturer"].str.contains(keyword, case=False, na=False),
        "Manufacturer"
    ] = name

df_system["Manufacturer"] = df_system["Manufacturer"].where(
    df_system["Manufacturer"].isin(MANUFACTURER_MAP.values()), "Other"
)

# Clean NaN, add ID column, and reorder
df_system.fillna("", inplace=True)
df_system = df_system.astype(str)
df_system.insert(0, "ID", None)

df_system = df_system.reindex(
    columns=["ID", "Manufacturer", "Model", "Serial", "CPU Type",
             "Barcode", "Grade", "Corporate Supplier"]
)

# ============================================================
# 7. LISTING DATA CLEANUP
# ============================================================

df_listing.rename(columns={1: "Listing Number", 3: "Model"}, inplace=True)
df_listing.drop(
    [0, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, "RAM", "CPU Type"],
    axis=1, inplace=True
)

# ============================================================
# 8. STORAGE DISK PROCESSING
# ============================================================

# Remove USB drives (serial number of all zeros)
disks.replace(r".*0{16}.*", np.nan, regex=True, inplace=True)

def push_nans_right(row):
    """Reorder each row so NaNs appear at the end."""
    return row.dropna().tolist() + [np.nan] * (len(row) - row.count())

disks = disks.apply(push_nans_right, axis=1, result_type="expand")
disks.dropna(axis=1, how="all", inplace=True)

# Define “nice” sizes (GB) for rounding
NICE_SIZES = [128, 256, 512, 1024, 2048, 4096, 8192]

def snap_to_nice(size_gb):
    """Round to nearest 'nice' storage size."""
    return min(NICE_SIZES, key=lambda x: abs(x - size_gb))

def format_storage(cell):
    """Convert raw disk info string into 'XXXGB TYPE'."""
    if pd.isna(cell):
        return np.nan
    parts = str(cell).split()
    if len(parts) < 2:
        return cell

    storage_type = parts[0]
    size_bytes = int(parts[1])
    size_gb = size_bytes / (1024 ** 3)
    snapped = snap_to_nice(size_gb)
    return f"{snapped}GB {storage_type}"

# Apply to every cell
disks_formatted = disks.applymap(format_storage)
disks_formatted.columns = [f"Disk{i+1}" for i in range(disks_formatted.shape[1])]

# Combine listing data with disk info
df_listing_final = pd.concat([df_listing, disks_formatted], axis=1).astype(str)

# ============================================================
# 9. EXPORT CLEANED DATA
# ============================================================

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
df_system.to_csv(f"system_data_{timestamp}.csv", index=False)
df_listing_final.to_csv(f"listing_data_{timestamp}.csv", index=False)
