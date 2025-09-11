import dash
from dash import dcc, html, dash_table
import dash.dependencies as dd
import pandas as pd
import re
import glob
import os

# --------------------------
# Config
# --------------------------
DATA_PATH = "./sample_data"  # <--- your folder with parquet files

# --------------------------
# Helper Functions
# --------------------------

# Load option chain
def load_option_chain(file_path):
    expiry = os.path.basename(file_path).replace(".parquet", "")
    df = pd.read_parquet(file_path)

    # Ensure datetime is index
    if 'datetime' not in df.columns:
        raise ValueError("DataFrame must have a 'datetime' column")
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)

    option_data = []
    for col in df.columns:
        # Strike extraction fix (remove last 2 digits of expiry)
        match = re.match(r".*?(\d+)(CE|PE)$", col)
        if match:
            strike = int(match.group(1)[2:])  # remove last 2 digits of expiry
            opt_type = match.group(2)
            option_data.append({"col_name": col, "strike": strike, "optionType": opt_type})

    return df, option_data, expiry

# Get option chain for a datetime
def get_chain_for_datetime(df, option_data, selected_datetime):
    selected_datetime = pd.to_datetime(selected_datetime)
    if selected_datetime not in df.index:
        # nearest datetime
        nearest_idx = df.index.get_indexer([selected_datetime], method="nearest")[0]
        selected_datetime = df.index[nearest_idx]

    option_chain_rows = []
    for opt in option_data:
        col = opt['col_name']
        row = df.loc[selected_datetime, col]

        if isinstance(row, dict):
            o, h, l, c = row.get("open"), row.get("high"), row.get("low"), row.get("close")
        elif isinstance(row, (list, tuple)) and len(row) == 4:
            o, h, l, c = row
        else:
            o = h = l = c = row

        option_chain_rows.append({
            "strike": opt["strike"],
            "optionType": opt["optionType"],
            "open": o,
            "high": h,
            "low": l,
            "close": c
        })

    return pd.DataFrame(option_chain_rows), selected_datetime

# Make Sensibull-style table
def make_chain_table(option_chain_df, atm_strike=None):
    calls = option_chain_df[option_chain_df.optionType == "CE"]\
        .set_index("strike")[["close"]].rename(columns={"close": "CE"})
    puts = option_chain_df[option_chain_df.optionType == "PE"]\
        .set_index("strike")[["close"]].rename(columns={"close": "PE"})

    chain_table = pd.concat([calls, puts], axis=1).reset_index()
    chain_table = chain_table.sort_values("strike")

    style_data_conditional = [
        {"if": {"column_id": "strike"},
         "backgroundColor": "#f9f9f9", "fontWeight": "bold"}
    ]

    # Highlight ATM
    if atm_strike in chain_table['strike'].values:
        style_data_conditional.append({
            "if": {"filter_query": f"{{strike}} = {atm_strike}"},
            "backgroundColor": "#ffeb3b",
            "fontWeight": "bold"
        })

    return chain_table, style_data_conditional

# Calculate spot and ATM
def get_spot_and_atm(df, selected_datetime):
    spot_price = df.loc[selected_datetime, 'SPOT']
    atm_strike = round(spot_price / 50) * 50
    return spot_price, atm_strike

# --------------------------
# Load all expiries
# --------------------------
files = glob.glob(os.path.join(DATA_PATH, "*.parquet"))
expiries = [os.path.basename(f).replace(".parquet", "") for f in files]

# Cache loaded data
loaded_data = {}

# --------------------------
# Dash App
# --------------------------
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Option Chain Dashboard"),

    dcc.Dropdown(
        id="expiry-dropdown",
        options=[{"label": e, "value": e} for e in expiries],
        value=expiries[0] if expiries else None,
        style={"width": "300px"}
    ),

    dcc.Input(
        id="datetime-input",
        type="text",
        placeholder="YYYY-MM-DD HH:MM:SS",
        style={"width": "300px", "margin-top": "10px"}
    ),

    html.Div(id="datetime-suggestion", style={"color": "gray", "margin-bottom": "10px"}),

    dash_table.DataTable(
        id="option-chain-table",
        columns=[
            {"name": "CE", "id": "CE"},
            {"name": "strike", "id": "strike"},
            {"name": "PE", "id": "PE"},
        ],
        style_table={"overflowX": "auto", "height": "400px", "overflowY": "auto"},
        style_cell={"textAlign": "center", "padding": "5px"},
        style_header={"fontWeight": "bold"},
    ),

    html.Div(id="spot-display", style={"margin-top": "10px", "fontWeight": "bold"})
])

# --------------------------
# Callbacks
# --------------------------
@app.callback(
    [dd.Output("option-chain-table", "data"),
     dd.Output("option-chain-table", "style_data_conditional"),
     dd.Output("datetime-suggestion", "children"),
     dd.Output("spot-display", "children")],
    [dd.Input("expiry-dropdown", "value"),
     dd.Input("datetime-input", "value")]
)
def update_table(selected_expiry, selected_datetime):
    if selected_expiry not in loaded_data:
        file_path = os.path.join(DATA_PATH, f"{selected_expiry}.parquet")
        df, option_data, _ = load_option_chain(file_path)
        loaded_data[selected_expiry] = (df, option_data)
    else:
        df, option_data = loaded_data[selected_expiry]

    if not selected_datetime:
        selected_datetime = df.index[0]

    option_chain_df, actual_datetime = get_chain_for_datetime(df, option_data, selected_datetime)
    spot_price, atm_strike = get_spot_and_atm(df, actual_datetime)
    chain_table, style_conditional = make_chain_table(option_chain_df, atm_strike)

    # Show suggestion if typed datetime != actual
    suggestion = ""
    if selected_datetime != str(actual_datetime):
        suggestion = f"Nearest available datetime: {actual_datetime}"

    spot_text = f"Spot: {spot_price} | ATM Strike: {atm_strike}"

    return chain_table.to_dict("records"), style_conditional, suggestion, spot_text

# --------------------------
# Run App
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)
