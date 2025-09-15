import os
import glob
from dash import html, dcc

from src.config_loader import DATA_PATH

def create_layout():
    # fetch all parquet files
    files = glob.glob(os.path.join(DATA_PATH, "*.parquet"))
    expiries = [os.path.basename(f).replace(".parquet", "") for f in files]

    return html.Div([
        html.Div(
            style={
                "width": "100%",
                "maxHeight": "40vh",       # fixed height
                "overflowY": "auto",       # vertical scroll if needed
                "border": "1px solid black",
                "padding": "10px",
            },
            children=[
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
            html.Div(id="spot-display", style={"margin-top": "10px", "fontWeight": "bold"}),]

        ),
        

        # --- HTML Table appended here ---
        html.Div(
            style={
                "width": "100%",
                "maxHeight": "59vh",       # fixed height
                "overflowY": "auto",       # vertical scroll if needed
                "border": "1px solid black",
                # "padding": "10px",
            },
            children=[
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("SELL CE", style={"textAlign": "center", "position": "sticky", "top": 0, "backgroundColor": "#fff", "zIndex": 1}),
                            html.Th("BUY CE", style={"textAlign": "center", "position": "sticky", "top": 0, "backgroundColor": "#fff", "zIndex": 1}),
                            html.Th("CE", style={"textAlign": "center", "position": "sticky", "top": 0, "backgroundColor": "#fff", "zIndex": 1}),
                            html.Th("Strike", style={"textAlign": "center", "position": "sticky", "top": 0, "backgroundColor": "#fff", "zIndex": 1}),
                            html.Th("PE", style={"textAlign": "center", "position": "sticky", "top": 0, "backgroundColor": "#fff", "zIndex": 1}),
                            html.Th("BUY PE", style={"textAlign": "center", "position": "sticky", "top": 0, "backgroundColor": "#fff", "zIndex": 1}),
                            html.Th("SELL PE", style={"textAlign": "center", "position": "sticky", "top": 0, "backgroundColor": "#fff", "zIndex": 1}),
                        ])
                    ]),
                    html.Tbody(id="option-chain-table")
                ], style={
                    "width": "100%",
                    "borderCollapse": "collapse",
                    "tableLayout": "fixed"
                })
            ]
        )
        # html.Div(
        #     # style={
        #     #     "width": "100%",
        #     #     "maxHeight": "400px",       # fixed height
        #     #     "overflowY": "auto",       # vertical scroll if needed
        #     #     "border": "1px solid black",
        #     # },
        #     # childrean 
        #     html.Table([
        #         html.Thead([
        #             html.Tr([
        #                 html.Th("SELL CE"),
        #                 html.Th("BUY CE"),
        #                 html.Th("CE"),
        #                 html.Th("Strike"),
        #                 html.Th("PE"),
        #                 html.Th("BUY PE"),
        #                 html.Th("SELL PE"),
        #             ])
        #         ]),
        #         # Table Body
        #         html.Tbody(id="option-chain-table")
                
        #     ], style={
        #         "width": "100%",
        #         "border": "1px solid black",
        #         "borderCollapse": "collapse",
        #         "tableLayout": "fixed"  # ✅ fixed layout for proper column alignment
        #     })
        # )
    ])
