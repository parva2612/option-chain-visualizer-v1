import plotly.express as px
import plotly.graph_objects as go

# def create_payoff_fig(spot_price, position_details_dict):
#     payoff_dict = create_plot_dict_2(spot_price, position_details_dict)
#     x_axis = list(payoff_dict.keys())
#     y_axis = list(payoff_dict.values())

#     fig = px.line(x=x_axis, y=y_axis,
#                 title=f"Payoff Chart")

#     fig.add_hline(y=0, line=dict(dash="dot", color="black"))
#     if spot_price is not None:
#         fig.add_vline(x=spot_price, line=dict(dash="dot", color="red"))

#     fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
#     return fig

def create_payoff_fig(spot_price, position_details_dict, fig_template = "plotly_white"):
    # Create payoff dict: keys=strikes, values=payoff
    payoff_dict = create_plot_dict_2(spot_price, position_details_dict)
    
    if not payoff_dict:
        return px.line(title="Payoff Chart")  # empty figure
    
    x_axis = list(payoff_dict.keys())
    y_axis = list(payoff_dict.values())

    fig = px.line(x=x_axis, y=y_axis, title="Payoff Chart")

    # Add horizontal line at y=0
    # fig.add_hline(y=0, line=dict(dash="dot", color="black"))

    # Add vertical line at spot price
    if spot_price is not None:
        fig.add_vline(x=spot_price, line=dict(dash="dot", color="red"))

    # Determine symmetric y-axis range
    if y_axis:
        if min(y_axis) < 0 and max(y_axis) > 0:
            min_y = min(y_axis)
            max_y = max(y_axis)
            upper_max_abs_y = abs(max_y)
            lower_max_abs_y = abs(min_y)
            

            if lower_max_abs_y > upper_max_abs_y:
                upper_lim = min(50*upper_max_abs_y, lower_max_abs_y/2)
                lower_lim = lower_max_abs_y
            else:
                upper_lim = upper_max_abs_y 
                lower_lim = min(upper_max_abs_y/2, lower_max_abs_y*50)
            
            max_abs = max(abs(min(y_axis)), abs(max(y_axis)))
            fig.update_yaxes(range=[-max_abs, max_abs])
        else:
            max_abs = max(abs(min(y_axis)), abs(max(y_axis)))
            upper_lim = max_abs
            lower_lim = max_abs
        fig.update_yaxes(range=[-lower_lim, upper_lim])

    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), template=fig_template)
    return fig


def create_plot_dict_2(underlying_ltp: float, position_dict: dict):

    if len(position_dict) == 0:
        return {}
    
    diff_ = max(abs(position_dict[key]['strike'] - underlying_ltp) for key in position_dict if position_dict[key]['option_type'].upper() in ['CE', 'PE'])
    lower_num = int((underlying_ltp - diff_)*0.98)
    upper_num = int((underlying_ltp + diff_)*1.02)
    # print(diff_, upper_num, underlying_ltp, lower_num, position_dict)
    

    
    payoff_dict = {}
    for x in range(lower_num, upper_num, 1):

        if x not in position_dict:
            payoff_dict[x] = 0
        
        for unique_sym in position_dict:
            if position_dict[unique_sym]['price'] != None:
                if position_dict[unique_sym]['option_type'] == 'FUT':
                    if position_dict[unique_sym]['buy_sell'].upper() == 'BUY':
                        payoff_dict[x] += (- position_dict[unique_sym]['price'] + x)*position_dict[unique_sym]['lots']
                    elif position_dict[unique_sym]['buy_sell'].upper() == 'SELL':
                        payoff_dict[x] += (position_dict[unique_sym]['entry_price'] - x)*position_dict[unique_sym]['lots']
                else:
                    try: 
                        if position_dict[unique_sym]['buy_sell'].upper() == "BUY":
                            if position_dict[unique_sym]['option_type'].upper() in ["CE", "C"]:
                                payoff_dict[x] += (max(x - position_dict[unique_sym]['strike'], 0) - position_dict[unique_sym]['price'])*position_dict[unique_sym]['lots']

                            elif position_dict[unique_sym]['option_type'].upper() in ["PE", "P"]:
                                payoff_dict[x] += (max(position_dict[unique_sym]['strike'] - x, 0) - position_dict[unique_sym]['price'])*position_dict[unique_sym]['lots']
                        else:
                            if position_dict[unique_sym]['option_type'].upper() in ["CE", "C"]:
                                payoff_dict[x] += -(max(x - position_dict[unique_sym]['strike'], 0) - position_dict[unique_sym]['price'])*position_dict[unique_sym]['lots']

                            elif position_dict[unique_sym]['option_type'].upper() in ["PE", "P"]:
                                payoff_dict[x] += -(max(position_dict[unique_sym]['strike'] - x, 0) - position_dict[unique_sym]['price'])*position_dict[unique_sym]['lots']
                    except Exception as e:
                        print(e)
                        raise e
            # else:
            #     print(f"{unique_sym} is none")
    return payoff_dict


# def plot