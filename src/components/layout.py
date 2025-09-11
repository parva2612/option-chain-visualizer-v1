from dash import html, dcc, dash_table
import glob
import os
from src.config_loader import DATA_PATH

def create_layout():
    # fetch all parquet files
    files = glob.glob(os.path.join(DATA_PATH, "*.parquet"))
    expiries = [os.path.basename(f).replace(".parquet", "") for f in files]

    return html.Div([
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
        html.Div(id="spot-display", style={"margin-top": "10px", "fontWeight": "bold"}),

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
        )
    ])
