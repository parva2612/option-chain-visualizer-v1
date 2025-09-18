from dash import Input, Output, html, dcc, State, ctx, MATCH, ALL
import dash
from .data_loader import load_option_chain
from .utils import get_chain_for_datetime, get_spot_and_atm, make_chain_table
import os, glob
from src.config_loader import DATA_PATH
import pandas as pd
from datetime import timedelta

loaded_data = {}
previous_outputs = {
    "data": [],
    "suggestion": "",
    "current_datetime": "",
    "spot_text": "",
    "current_dt": ""
}


def register_callbacks(app):

    """
        ==========================================================================
        BOTH ARE FOR REFERANCE FOR FUTURE
        ==========================================================================

        Function with old format of previous_outputs

        def generate_checklist_ids(previous_outputs):
        ids = []
        if len(previous_outputs['data']) > 0:
            for tr in previous_outputs['data']:
                if isinstance(tr, html.Tr):
                    for td in tr.children:
                        if isinstance(td, html.Td) and isinstance(td.children, dcc.Checklist):
                            ids.append(td.children.id)
                        break
                break

        return ids
        
        ==========================================================================

        Function with new format of previous outputs

        def generate_checklist_ids(previous_outputs):
            print(f'into generate_checklist_ids FUNCTION')
            ids = []
            if len(previous_outputs['data']) > 0:

                for tr in previous_outputs['data']:
                    if 'props' in tr.keys() and 'type' in tr.keys() and tr['type'] == 'Tr' and 'children' in tr['props']:
                        for td in tr['props']['children']:
                            if 'props' in td and 'type' in td and td['type'] == 'Td' and 'children' in td['props']:
                                if type(td['props']['children']) == dict:
                                    ids.append(td['props']['children']['props']['id'])
            return ids
    """
    
    

    
    
    @app.callback(
        Output({"type": "checklist-buy-ce", "strike": MATCH}, "value"),
        Output({"type": "checklist-sell-ce", "strike": MATCH}, "value"),
        Input({"type": "checklist-buy-ce", "strike": MATCH}, "value"),
        Input({"type": "checklist-sell-ce", "strike": MATCH}, "value"),
        prevent_initial_call=True
    )
    def toggle_ce(buy_value, sell_value):
        """Keep BUY CE and SELL CE mutually exclusive per strike."""
        ctx = dash.callback_context
        if not ctx.triggered:
            return buy_value, sell_value
        triggered = ctx.triggered_id
        if triggered["type"] == "checklist-buy-ce" and buy_value:
            return buy_value, []  # clear SELL
        elif triggered["type"] == "checklist-sell-ce" and sell_value:
            return [], sell_value  # clear BUY
        return buy_value, sell_value



    @app.callback(
        Output({"type": "checklist-buy-pe", "strike": MATCH}, "value"),
        Output({"type": "checklist-sell-pe", "strike": MATCH}, "value"),
        Input({"type": "checklist-buy-pe", "strike": MATCH}, "value"),
        Input({"type": "checklist-sell-pe", "strike": MATCH}, "value"),
        prevent_initial_call=True
    )

    
    def toggle_ce(buy_value, sell_value):
        """Keep BUY PE and SELL PE mutually exclusive per strike."""
        ctx = dash.callback_context
        if not ctx.triggered:
            return buy_value, sell_value
        triggered = ctx.triggered_id
        if triggered["type"] == "checklist-buy-pe" and buy_value:
            return buy_value, []  # clear SELL
        elif triggered["type"] == "checklist-sell-pe" and sell_value:
            return [], sell_value  # clear BUY
        return buy_value, sell_value
    
    
    @app.callback(
        Output("buy-sell-state-store", "data"),
        Input({"type": "checklist-buy-ce", "strike": ALL}, "value"),
        Input({"type": "checklist-sell-ce", "strike": ALL}, "value"),
        Input({"type": "checklist-buy-pe", "strike": ALL}, "value"),
        Input({"type": "checklist-sell-pe", "strike": ALL}, "value"),
        State("buy-sell-state-store", "data"),
    )
    def update_buy_sell_state(buy_ce_vals, sell_ce_vals, buy_pe_vals, sell_pe_vals, current_state):
        # Initialize store if empty
        if current_state is None:
            current_state = {"ce": {"buy": [], "sell": []}, "pe": {"buy": [], "sell": []}}

        # Collect selected strikes
        ce_buy_strikes = [i["id"]["strike"] for i, val in zip(ctx.inputs_list[0], buy_ce_vals) if val]
        ce_sell_strikes = [i["id"]["strike"] for i, val in zip(ctx.inputs_list[1], sell_ce_vals) if val]
        pe_buy_strikes  = [i["id"]["strike"] for i, val in zip(ctx.inputs_list[2], buy_pe_vals) if val]
        pe_sell_strikes = [i["id"]["strike"] for i, val in zip(ctx.inputs_list[3], sell_pe_vals) if val]

        updated_state = {
            "ce": {"buy": ce_buy_strikes, "sell": ce_sell_strikes},
            "pe": {"buy": pe_buy_strikes, "sell": pe_sell_strikes},
        }

        # print(updated_state)

        return updated_state
    
    @app.callback(
        [
            Output("option-chain-table", "children"),
            Output("datetime-suggestion", "children"),
            Output("current-datetime-display", "children"),
            Output("spot-display", "children"),
            Output("datetime-input", "value"),
            Output("previous-outputs-store", "data"),
            # Output("buy-sell-state-store", "data"),
            
        ],

        [
            Input("expiry-dropdown", "value"),
            Input("datetime-input", "value"),
            Input("minus-1min-btn", "n_clicks"),
            Input("plus-1min-btn", "n_clicks"),
            Input("buy-sell-state-store", "data"),
        ],

        State("previous-outputs-store", "data"),
        # State("buy-sell-state-store", "data"),
        
    )
    
    def update_table(*args):

        # global previous_outputs
        # print(args)
        
        selected_expiry, selected_datetime, minus_clicks, plus_clicks = args[:4]

        buy_sell_state = args[-2]
        previous_outputs = args[-1]
        print(buy_sell_state)
        # print(args)
        
        if previous_outputs is None:
            print("parva: previous_outputs is None")
            previous_outputs = {
                "data": [],
                "suggestion": "",
                "current_datetime": "",
                "spot_text": "",
                "current_dt": ""
            }
        else:
            print("parva: previous_outputs is not None")
        
        trigger = ctx.triggered_id
        print(f"TRIGGER ID = {trigger}")
        output_datetime_str = selected_datetime
        
        if not selected_expiry:
            # fallback empty outputs
            print(f"return ins is as not selected_expiry: {selected_expiry}")
            return (
                previous_outputs["data"],
                previous_outputs["suggestion"],
                previous_outputs["current_datetime"],
                previous_outputs["spot_text"],
                output_datetime_str,
                previous_outputs,
                # buy_sell_state

            )

        # load data if not cached
        if selected_expiry not in loaded_data:
            file_path = os.path.join(DATA_PATH, f"{selected_expiry}.parquet")
            df, option_data, _ = load_option_chain(file_path)
            loaded_data[selected_expiry] = (df, option_data)
        else:
            df, option_data = loaded_data[selected_expiry]

        # fallback datetime
        # print(f"selected datetime = {selected_datetime}")
        if not selected_datetime:
            selected_datetime = df.index[0]
        elif trigger in ["minus-1min-btn", "plus-1min-btn"]:
            try:
                # print(selected_datetime)
                selected_datetime = pd.to_datetime(selected_datetime)
                if trigger == "minus-1min-btn":
                    selected_datetime -= timedelta(minutes=1)
                elif trigger == "plus-1min-btn":
                    selected_datetime += timedelta(minutes=1)
                
                selected_datetime = selected_datetime.strftime("%Y-%m-%d %H:%M:%S")
            except:
                selected_datetime = df.index[0]
        

        # if not selected_datetime:
        #     selected_datetime = df.index[0]
        # print(f"selected datetime: {selected_datetime}")
        option_chain_df, actual_datetime = get_chain_for_datetime(df, option_data, selected_datetime)
        
        
        
        # print(f"actual datetime: {actual_datetime}")
        if option_chain_df is None:
            previous_outputs["current_dt"] = output_datetime_str
            return (
                previous_outputs["data"],
                previous_outputs["suggestion"],
                previous_outputs["current_datetime"],
                previous_outputs["spot_text"],
                previous_outputs["current_dt"],
                previous_outputs,
                # buy_sell_state
            )

        if trigger in ["minus-1min-btn", "plus-1min-btn"]:
            output_datetime_str = actual_datetime.strftime('%Y-%m-%d %H:%M:%S')
        # print(option_chain_df)
        spot_price, atm_strike = get_spot_and_atm(df, actual_datetime)
        chain_table, style_conditional = make_chain_table(option_chain_df, atm_strike)

        rows = []
        
        for item in chain_table.to_dict("records"):
            row_style = {}

            # Conditional background for 'strike' column
            if item["strike"] == atm_strike:
                row_style = {"textAlign": "center", "backgroundColor": "#ffeb3b", "fontWeight": "bold"}
            elif item["strike"] % 5 == 0:  # example: alternate styling
                row_style = {"textAlign": "center","backgroundColor": "#f9f9f9"}

            rows.append(
                html.Tr([
                    html.Td(dcc.Checklist(
                        # id=f'checklist-sell-ce-{item["strike"]}',
                        id={"type": "checklist-sell-ce", "strike": item["strike"]},
                        options=[{"label": "S", "value": "selected"}],
                        # value=[],
                        value = (["selected"] if item["strike"] in buy_sell_state["ce"]["sell"] else []),
                        inline=True,
                        style={"margin": "0"}
                    ), style=row_style),
                    html.Td(dcc.Checklist(
                        # id=f'checklist-buy-ce-{item["strike"]}',
                        id={"type": "checklist-buy-ce", "strike": item["strike"]},
                        options=[{"label": "B", "value": "selected"}],
                        # value=[],
                        value = (["selected"] if item["strike"] in buy_sell_state["ce"]["buy"] else []),
                        inline=True,
                        style={"margin": "0"}
                    ), style=row_style),
                    html.Td(item["CE"], style=row_style),
                    html.Td(item["strike"], style=row_style),
                    html.Td(item["PE"], style=row_style),
                    html.Td(dcc.Checklist(
                        # id=f'checklist-buy-pe-{item["strike"]}',
                        id={"type": "checklist-buy-pe", "strike": item["strike"]},
                        options=[{"label": "B", "value": "selected"}],
                        # value=[],
                        value = (["selected"] if item["strike"] in buy_sell_state["pe"]["buy"] else []),
                        inline=True,
                        style={"margin": "0"}
                    ), style=row_style),
                    html.Td(dcc.Checklist(
                        # id=f'checklist-sell-pe-{item["strike"]}',
                        id={"type": "checklist-sell-pe", "strike": item["strike"]},
                        options=[{"label": "S", "value": "selected"}],
                        # value=[],
                        value = (["selected"] if item["strike"] in buy_sell_state["pe"]["sell"] else []),
                        inline=True,
                        style={"margin": "0"}
                    ), style=row_style),
                ]))
    
        suggestion = ""
        if selected_datetime != str(actual_datetime):
            suggestion = f"Nearest available datetime: {actual_datetime}"

        spot_text = f"Spot: {spot_price} | ATM Strike: {atm_strike}"
        current_dt_text = f"Currently Showing: {actual_datetime}"

        # print(rows)
        previous_outputs = {
            "data": rows,
            "suggestion": suggestion,
            "current_datetime": current_dt_text,
            "spot_text": spot_text,
            "current_dt": output_datetime_str
        }
        # print()
        # print(f"====================>\n\n{previous_outputs}\n<====================\n")
        return (
            previous_outputs["data"],
            previous_outputs["suggestion"],
            previous_outputs["current_datetime"],
            previous_outputs["spot_text"],
            previous_outputs["current_dt"],
            previous_outputs,
            # buy_sell_state
        )

    def populate_expiries(_):
        files = glob.glob(os.path.join(DATA_PATH, "*.parquet"))
        expiries = [os.path.basename(f).replace(".parquet", "") for f in files]
        return [{"label": e, "value": e} for e in expiries]