import dash
from dash import dcc, html, dash_table
import dash.dependencies as dd
import glob
import os
from data_loader import load_option_chain
from utils import get_chain_for_datetime, get_spot_and_atm, make_chain_table

# --------------------------
# Config
# --------------------------
DATA_PATH = "./sample_data"
files = glob.glob(os.path.join(DATA_PATH, "*.parquet"))
expiries = [os.path.basename(f).replace(".parquet", "") for f in files]

loaded_data = {}

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

    html.Div(id="datetime-suggestion", style={"color": "gray", "margin-bottom": "5px"}),
    html.Div(id="current-datetime-display", style={"margin-bottom": "10px", "fontWeight": "bold"}),

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
     dd.Output("current-datetime-display", "children"),
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

    suggestion = ""
    if selected_datetime != str(actual_datetime):
        suggestion = f"Nearest available datetime: {actual_datetime}"

    spot_text = f"Spot: {spot_price} | ATM Strike: {atm_strike}"
    current_dt_text = f"Currently Showing: {actual_datetime}"

    return chain_table.to_dict("records"), style_conditional, suggestion, current_dt_text, spot_text

# --------------------------
# Run App
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)
