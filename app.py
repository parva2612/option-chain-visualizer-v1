from dash import Dash
from src.components.layout import create_layout
from src.callbacks import register_callbacks

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Option Chain Dashboard"

# set layout
app.layout = create_layout()

# register callbacks
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
