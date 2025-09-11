from dash import Input, Output
from .data_loader import load_option_chain
from .utils import get_chain_for_datetime, get_spot_and_atm, make_chain_table
import os, glob
from src.config_loader import DATA_PATH

loaded_data = {}

def register_callbacks(app):

    @app.callback(
        [Output("option-chain-table", "data"),
         Output("option-chain-table", "style_data_conditional"),
         Output("datetime-suggestion", "children"),
         Output("current-datetime-display", "children"),
         Output("spot-display", "children")],
        [Input("expiry-dropdown", "value"),
         Input("datetime-input", "value")]
    )
    def update_table(selected_expiry, selected_datetime):
        if not selected_expiry:
            # fallback empty outputs
            return [], [], "", "", ""

        # load data if not cached
        if selected_expiry not in loaded_data:
            file_path = os.path.join(DATA_PATH, f"{selected_expiry}.parquet")
            df, option_data, _ = load_option_chain(file_path)
            loaded_data[selected_expiry] = (df, option_data)
        else:
            df, option_data = loaded_data[selected_expiry]

        # fallback datetime
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

    def populate_expiries(_):
        files = glob.glob(os.path.join(DATA_PATH, "*.parquet"))
        expiries = [os.path.basename(f).replace(".parquet", "") for f in files]
        return [{"label": e, "value": e} for e in expiries]