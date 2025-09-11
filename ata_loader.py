import pandas as pd
import re
import os

def load_option_chain(file_path):
    """Load parquet and parse option columns"""
    expiry = os.path.basename(file_path).replace(".parquet", "")
    df = pd.read_parquet(file_path)

    # Ensure datetime is index
    if 'datetime' not in df.columns:
        raise ValueError("DataFrame must have a 'datetime' column")
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)

    option_data = []
    for col in df.columns:
        if col == 'SPOT':  # skip spot
            continue
        match = re.match(r".*?(\d+)(CE|PE)$", col)
        if match:
            # strike fix
            strike = int(match.group(1)[2:])
            opt_type = match.group(2)
            option_data.append({"col_name": col, "strike": strike, "optionType": opt_type})

    return df, option_data, expiry
