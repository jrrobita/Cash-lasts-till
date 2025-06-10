import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Start the app
app = dash.Dash(__name__)
server = app.server  # REQUIRED for Render/Gunicorn (hosting platform for Dash apps)

# Capital longevity function (no inflation/employment income yet)
def compute_years(C, W, R):
    try:
        ratio = R * C / W
        if ratio >= 1:
            return np.inf
        return -np.log(1 - ratio) / np.log(1 + R)
    except:
        return np.nan

# App layout
app.layout = html.Div([
    html.H1("Capital Longevity Dashboard", style={'textAlign': 'center'}),
    dcc.Store(id='prev-years-store', data=None),

    # TOP ROW: Inputs and result
    html.Div([
        html.Div([
            html.Label("Initial Capital ($):"),
            dcc.Dropdown(
                id='capital-dropdown',
                options=[{'label': f"${i:,}", 'value': i} for i in range(100000, 500001, 1000)],
                value=250000,
                clearable=False,
                style={'width': '150px'}
            )
        ], style={'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Annual Withdrawal ($):"),
            dcc.Dropdown(
                id='withdrawal-dropdown',
                options=[{'label': f"${i:,}", 'value': i} for i in range(10000, 30001, 250)],
                value=22000,
                clearable=False,
                style={'width': '150px'}
            )
        ], style={'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Real Rate of Return (%):"),
            dcc.Input(
                id='return-input',
                type='number',
                value=5.0,
                step=0.1,
                style={'width': '80px'}
            )
        ], style={'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label("Years Capital Lasts:"),
            html.H3(id='years-output', style={'margin': '0', 'color': 'blue'})
        ], style={'display': 'inline-block', 'padding': '10px', 'verticalAlign': 'bottom'}),
        
        html.Div([
            html.Label("Change from Previous:"),
            html.H4(id='years-delta-output', style={'margin': '0', 'color': 'green'})
        ], style={'display': 'inline-block', 'padding': '10px', 'verticalAlign': 'bottom'})

    ], style={'textAlign': 'center'}),

    # BOTTOM ROW: Graphs
    html.Div([
        html.Div([
            dcc.Graph(id='years-vs-capital')
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='years-vs-withdrawal')
        ], style={'width': '48%', 'display': 'inline-block'})
    ])
])



# Callback logic
from dash.dependencies import Input, Output, State

@app.callback(
    [Output('years-output', 'children'),
     Output('years-delta-output', 'children'),
     Output('prev-years-store', 'data'),
     Output('years-vs-capital', 'figure'),
     Output('years-vs-withdrawal', 'figure')],
    [Input('capital-dropdown', 'value'),
     Input('withdrawal-dropdown', 'value'),
     Input('return-input', 'value')],
    [State('prev-years-store', 'data')]
)
def update_output(C, W, R_percent, prev_years):
    R = R_percent / 100
    years = compute_years(C, W, R)

    # Compute deltas
    if prev_years is None or prev_years == "∞" or years == np.inf:
        delta_str = "–"
    else:
        delta = years - prev_years
        delta_str = f"{delta:+.2f} years"

    # Graphs
    capital_range = np.arange(100000, 500001, 5000)
    y_cap = [compute_years(c, W, R) for c in capital_range]

    withdrawal_range = np.arange(10000, 30001, 500)
    y_w = [compute_years(C, w, R) for w in withdrawal_range]

    capital_fig = go.Figure(data=go.Scatter(x=capital_range, y=y_cap, mode='lines'))
    capital_fig.update_layout(title='Years Capital Lasts vs Initial Capital',
                              xaxis_title='Initial Capital ($)', yaxis_title='Years')

    withdrawal_fig = go.Figure(data=go.Scatter(x=withdrawal_range, y=y_w, mode='lines'))
    withdrawal_fig.update_layout(title='Years Capital Lasts vs Annual Withdrawal',
                                 xaxis_title='Annual Withdrawal ($)', yaxis_title='Years')

    years_str = f"{'∞' if years == np.inf else f'{years:.2f}'}"

    return years_str, delta_str, (np.inf if years == np.inf else years), capital_fig, withdrawal_fig

# Run app
if __name__ == '__main__':
    app.run(debug=True)
