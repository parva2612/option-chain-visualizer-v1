import pandas as pd
from datetime import datetime

def get_chain_for_datetime(df, option_data, selected_datetime):
    print(f"{datetime.now()}: into start of src/utils -> get_chain_for_datetime")
    selected_datetime = pd.to_datetime(selected_datetime)
    if selected_datetime not in df.index:
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

def get_spot_and_atm(df, selected_datetime):
    print(f"{datetime.now()}: into start of src/utils -> get_spot_and_atm")
    spot_price = df.loc[selected_datetime, 'SPOT']
    atm_strike = round(spot_price / 50) * 50
    return spot_price, atm_strike

def make_chain_table(option_chain_df, atm_strike=None):
    print(f"{datetime.now()}: into start of src/utils -> make_chain_table")

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

    if atm_strike in chain_table['strike'].values:
        style_data_conditional.append({
            "if": {"filter_query": f"{{strike}} = {atm_strike}"},
            "backgroundColor": "#ffeb3b",
            "fontWeight": "bold"
        })

    return chain_table, style_data_conditional