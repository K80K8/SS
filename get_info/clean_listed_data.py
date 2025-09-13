# python 3.8.10 environment
import pandas as pd
import numpy as np
import glob
import os

# file_paths = ['list_data.txt']
folder_path = "."

# Get all .txt files in the folder that contain listed data
file_paths = glob.glob(os.path.join(folder_path, "list*.txt"))

dfs = []
for i, path in enumerate(file_paths):
    if i == 0:
        df = pd.read_csv(path, sep=',')
    else:
        df = pd.read_csv(path, sep=',', skiprows=1, header=None)
        df.columns = dfs[0].columns
    dfs.append(df)

df_combined = pd.concat(dfs, ignore_index=True)

# Convert bytes to GB, always rounding UP, and format with 'GB'
df_combined['RAM'] = (np.ceil(df_combined['RAMAmount'] / (1024**3))).astype(int).astype(str) + 'GB'
df_combined.drop('RAMAmount', axis=1)


# Define RAM lookup table
ram_lookup_table = {
    0: "Unknown",
    1: "Other",
    2: "DRAM",
    3: "Synchronous DRAM",
    4: "Cache DRAM",
    5: "EDO",
    6: "EDRAM",
    7: "VRAM",
    8: "SRAM",
    9: "RAM",
    10: "ROM",
    11: "Flash",
    12: "EEPROM",
    13: "FEPROM",
    14: "EPROM",
    15: "CDRAM",
    16: "3DRAM",
    17: "SDRAM",
    18: "SGRAM",
    19: "RDRAM",
    20: "DDR",
    21: "DDR2",
    22: "DDR2 FB-DIMM",
    23: "Reserved",
    24: "DDR3",
    25: "FBD2",
    26: "DDR4",
    27: "LPDDR",
    28: "LPDDR2",
    29: "LPDDR3",
    30: "LPDDR4",
    31: "Logical non-volatile device",
    32: "HBM",
    33: "HBM2",
    34: "DDR5"
}

# Map the numeric codes to names and add to new column for ram amount and type
df_combined['RAM Amount and Type'] = df_combined['RAM'] + ' ' + df_combined['RAMType'].map(ram_lookup_table)


# List of columns to drop
columns_to_drop = ['RAM', 'RAMType', 'RAMAmount']

# Drop multiple columns
df_new = df_combined.drop(columns=columns_to_drop)

# Convert bytes to GB
sizes_gb = df_new['StorageAmount'] / (1024**3)

# Common marketed capacities in GB
common_sizes = np.array([64, 128, 256, 512, 1024, 2048, 4096])

# Snap each size to nearest common capacity
def snap_to_common(x):
    return common_sizes[np.argmin(np.abs(common_sizes - x))]

df_new['Storage_Snapped_GB'] = sizes_gb.apply(snap_to_common)

# Format as string with GB or TB
def format_size(x):
    if x >= 1024:
        return f"{int(x/1024)}TB"
    else:
        return f"{int(x)}GB"

df_new['Storage_Display'] = df_new['Storage_Snapped_GB'].apply(format_size)
df_new['Storage Amount and Type'] = df_new['Storage_Display'] + ' ' + df_new['StorageType']

# List of columns to drop
columns_to_drop = ['StorageAmount', 'StorageType', 'Storage_Snapped_GB', 'Storage_Display']

# Drop multiple columns
df_newer = df_new.drop(columns=columns_to_drop)

df_converted = df_newer.astype(str)

df_converted.insert(loc=0, column='ID', value=None) # can change value

for col in df_converted.select_dtypes(include=['object']).columns:
    df_converted[col] = df_converted[col].str.strip()

# Only keep first 4 words for Ryzen
keyword = 'AMD Ryzen'
mask = df_converted['CPU'].str.contains(keyword, case=False, na=False)

df_converted['CPU'] = df_converted.apply(
    lambda row: ' '.join(row['CPU'].split()[:4]) if mask[row.name] else row['CPU'],
    axis=1
)

# Replace Intel(R) Core(TM) with Intel Core and keep the next word (model)
df_converted['CPU'] = df_converted['CPU'].str.replace(
    r'^Intel\(R\) Core\(TM\)\s+(\S+).*',
    r'Intel Core \1',
    regex=True
)

df_converted['CPU'] = df_converted['CPU'] + ' ' + df_converted['CPUCores'] + ' Core Processor'
df = df_converted.drop('CPUCores', axis=1)

df['Windows Type and Version'] = df['Windows']
df = df.drop('Windows', axis=1)

# Replace 'y' with 'Yes' and 'n' with 'No' in Windows Activated
df['Is Windows Activated?'] = df['WindowsActivated'].replace({'y': 'Yes', 'n': 'No'})
df = df.drop('WindowsActivated', axis=1)
print(df)
df.to_csv('output_listed.csv', index=False)