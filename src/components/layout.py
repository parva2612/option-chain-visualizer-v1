import os
import glob
from dash import html, dcc

from src.config_loader import DATA_PATH

def create_layout():
    # fetch all parquet files
    files = glob.glob(os.path.join(DATA_PATH, "*.parquet"))
    expiries = [os.path.basename(f).replace(".parquet", "") for f in files]

    return html.Div([

        dcc.Store(id="checklist-ids-store", data=[]),
        dcc.Store(id="previous-outputs-store", storage_type="memory"),
        dcc.Store(id="buy-sell-state-store", storage_type="memory"),
        dcc.Store(id="buy-sell-state-payoff-format-store", storage_type="memory"),

        html.Div(
            style={
                "width": "98%",
                "maxHeight": "38vh",       # fixed height
                "overflowY": "auto",       # vertical scroll if needed
                "border": "1px solid black",
                "padding": "10px",
            },
            children=[
            html.H2("Option Chain Dashboard"),
            html.Div([    
                    html.Div([
                        html.Div([
                            dcc.Dropdown(
                                id="expiry-dropdown",
                                options=[{"label": e, "value": e} for e in expiries],
                                value=expiries[0] if expiries else None,
                                style={"width": "200px"}
                            )
                        ], style={"margin-right": "20px"}),

                        # Datetime input + suggestion
                        html.Div([
                            dcc.Input(
                                id="datetime-input",
                                type="text",
                                placeholder="YYYY-MM-DD HH:MM:SS",
                                style={"width": "220px"}
                            ),
                            html.Div(
                                id="datetime-suggestion",
                                style={"color": "gray", "fontSize": "12px", "margin-top": "2px"}
                            ),
                        ], style={"margin-right": "20px"}),

                        # Minus and plus buttons
                        html.Div([
                            html.Button("⏪ -1 min", id="minus-1min-btn", n_clicks=0, style={"margin-right": "5px"}),
                            html.Button("+1 min ⏩", id="plus-1min-btn", n_clicks=0)
                        ])
                    ], style={"display": "flex", "alignItems": "flex-start", "margin-bottom": "10px"}),

                    
                    html.Div([
                        html.Div(id="spot-display", style={"margin-right": "20px", "fontWeight": "bold"}),
                        html.Div(id="current-datetime-display", style={"fontWeight": "bold"})
                    ], style={"display": "flex", "alignItems": "center", "margin-bottom": "10px"})

                ])

            
            ]

        ),
        

        # --- HTML Table appended here ---
        html.Div(
            style={
                "width": "98%",
                "maxHeight": "59vh",       # fixed height
                "overflowY": "auto",       # vertical scroll if needed
                "border": "1px solid black",
                "padding": "10px",
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
        ),

        ################### POSITIONS DETAILS ###################
        html.Div(
            style={
                "display": "flex",
                "width": "98%",
                "marginTop": "10px",
                "gap": "10px"  # spacing between columns
            },
            children=[
                # Left column: open positions
                html.Div(
                    style={
                        "width": "48%",           # take about half width
                        "maxHeight": "40vh",      # fixed height
                        "overflowY": "auto",      # scroll if content exceeds height
                        "border": "1px solid black",
                        "padding": "10px"
                    },
                    children=[
                        html.H4("Open Positions"),
                        html.Table(
                            id="positions-table",
                            style={"width": "100%", "borderCollapse": "collapse"},
                            children=[
                                html.Thead([
                                    html.Tr([
                                        html.Th("Buy/Sell", style={"textAlign": "center"}),
                                        html.Th("Expiry", style={"textAlign": "center"}),
                                        html.Th("Strike", style={"textAlign": "center"}),
                                        html.Th("Type", style={"textAlign": "center"}),
                                        html.Th("Lots", style={"textAlign": "center"}),
                                        html.Th("Price", style={"textAlign": "center"}),
                                    ])
                                ]),
                                html.Tbody(id="positions-table-body")
                            ]
                        )
                    ]
                ),

                # Right column: payoff chart
                html.Div(
                    style={
                        "width": "50vw",
                        "height": "40vh",
                        "border": "1px solid black",
                        "padding": "5px"
                    },
                    children=[
                        dcc.Graph(id="payoff-graph")
                    ]
                )
            ]
        )

        # # --- Payoff Chart ---
        # html.Div(
        #     style={
        #         "width": "50vw",
        #         "height": "40vh",          # dedicated height for graph
        #         "border": "1px solid black",
        #         "padding": "1px",
        #         "marginTop": "1px",
        #     },
        #     children=[
        #         dcc.Graph(id="payoff-graph")
        #     ]
        # )
    ])
