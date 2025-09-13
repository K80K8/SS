#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process listed hardware data from text files and output a cleaned CSV.

Environment: Python 3.8.10
"""

import os
import glob
import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
FOLDER_PATH = "."
OUTPUT_FILE = "output_listed.csv"

# Lookup table for RAM types
RAM_LOOKUP = {
    0: "Unknown", 1: "Other", 2: "DRAM", 3: "Synchronous DRAM", 4: "Cache DRAM",
    5: "EDO", 6: "EDRAM", 7: "VRAM", 8: "SRAM", 9: "RAM", 10: "ROM",
    11: "Flash", 12: "EEPROM", 13: "FEPROM", 14: "EPROM", 15: "CDRAM",
    16: "3DRAM", 17: "SDRAM", 18: "SGRAM", 19: "RDRAM", 20: "DDR",
    21: "DDR2", 22: "DDR2 FB-DIMM", 23: "Reserved", 24: "DDR3", 25: "FBD2",
    26: "DDR4", 27: "LPDDR", 28: "LPDDR2", 29: "LPDDR3", 30: "LPDDR4",
    31: "Logical non-volatile device", 32: "HBM", 33: "HBM2", 34: "DDR5"
}

# Common marketed storage capacities (GB)
COMMON_SIZES = np.array([64, 128, 256, 512, 1024, 2048, 4096])


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
def snap_to_common(x: float) -> int:
    """Snap a raw storage size in GB to the nearest marketed capacity."""
    return COMMON_SIZES[np.argmin(np.abs(COMMON_SIZES - x))]


def format_size(x: int) -> str:
    """Format storage size as GB or TB string."""
    return f"{int(x / 1024)}TB" if x >= 1024 else f"{int(x)}GB"


# -----------------------------------------------------------------------------
# Main processing
# -----------------------------------------------------------------------------
def main() -> None:
    # Collect all text files starting with "list"
    file_paths = glob.glob(os.path.join(FOLDER_PATH, "list*.txt"))

    # Read and merge files
    dfs = []
    for i, path in enumerate(file_paths):
        if i == 0:
            df = pd.read_csv(path, sep=",")
        else:
            df = pd.read_csv(path, sep=",", skiprows=1, header=None)
            df.columns = dfs[0].columns
        dfs.append(df)

    df_combined = pd.concat(dfs, ignore_index=True)

    # -------------------------------------------------------------------------
    # RAM processing
    # -------------------------------------------------------------------------
    df_combined["RAM"] = (
        np.ceil(df_combined["RAMAmount"] / (1024 ** 3))
        .astype(int)
        .astype(str) + "GB"
    )

    df_combined["RAM Amount and Type"] = (
        df_combined["RAM"] + " " + df_combined["RAMType"].map(RAM_LOOKUP)
    )

    df = df_combined.drop(columns=["RAM", "RAMType", "RAMAmount"])

    # -------------------------------------------------------------------------
    # Storage processing
    # -------------------------------------------------------------------------
    sizes_gb = df["StorageAmount"] / (1024 ** 3)
    df["Storage_Snapped_GB"] = sizes_gb.apply(snap_to_common)
    df["Storage_Display"] = df["Storage_Snapped_GB"].apply(format_size)

    df["Storage Amount and Type"] = df["Storage_Display"] + " " + df["StorageType"]

    df = df.drop(columns=["StorageAmount", "StorageType",
                          "Storage_Snapped_GB", "Storage_Display"])

    # -------------------------------------------------------------------------
    # General cleaning
    # -------------------------------------------------------------------------
    df = df.astype(str)
    df.insert(loc=0, column="ID", value=None)

    # Strip whitespace
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()

    # -------------------------------------------------------------------------
    # CPU processing
    # -------------------------------------------------------------------------
    # Keep only first 4 words for AMD Ryzen
    keyword = "AMD Ryzen"
    mask = df["CPU"].str.contains(keyword, case=False, na=False)
    df["CPU"] = df.apply(
        lambda row: " ".join(row["CPU"].split()[:4]) if mask[row.name] else row["CPU"],
        axis=1,
    )

    # Simplify Intel naming
    df["CPU"] = df["CPU"].str.replace(
        r"^Intel\(R\) Core\(TM\)\s+(\S+).*",
        r"Intel Core \1",
        regex=True,
    )

    # Append core count
    df["CPU"] = df["CPU"] + " " + df["CPUCores"] + " Core Processor"
    df = df.drop(columns=["CPUCores"])

    # -------------------------------------------------------------------------
    # Windows processing
    # -------------------------------------------------------------------------
    df["Windows Type and Version"] = df["Windows"]
    df = df.drop(columns=["Windows"])

    df["Is Windows Activated?"] = df["WindowsActivated"].replace({"y": "Yes", "n": "No"})
    df = df.drop(columns=["WindowsActivated"])

    # -------------------------------------------------------------------------
    # Output
    # -------------------------------------------------------------------------
    df.to_csv(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    main()
