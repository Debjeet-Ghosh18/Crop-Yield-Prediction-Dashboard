import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.predictor import CropPredictor
from dashboard.components.filters import create_filters
from dashboard.components.predictions import create_prediction_cards
from dashboard.components.charts import create_trend_chart, create_comparison_chart
from config import Config

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "Crop Prediction Dashboard"

# Initialize predictor and load data
config = Config()
predictor = CropPredictor()

# Load processed data for visualizations
try:
    df = pd.read_csv(os.path.join(config.PROCESSED_DATA_DIR, config.MERGED_FILE))
except:
    df = pd.DataFrame()
    print("Warning: Could not load processed data for visualizations")

# Get available options
options = predictor.get_available_options()

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("🌾 Crop Prediction Dashboard", className="text-center mb-4 text-primary"),
            html.P("Predict crop yield and production using machine learning", 
                   className="text-center text-muted mb-5")
        ])
    ]),
    
    # Filters
    dbc.Card([
        dbc.CardHeader(html.H4("Input Parameters", className="mb-0")),
        dbc.CardBody([
            create_filters(options['crops'], options['seasons'])
        ])
    ], className="mb-4"),
    
    # Prediction Button
    dbc.Row([
        dbc.Col([
            dbc.Button("Predict", id="predict-button", color="primary", size="lg", 
                      className="w-100 mb-4")
        ], md={'size': 6, 'offset': 3})
    ]),
    
    # Results
    create_prediction_cards(),
    
    # Charts (only show if data is available)
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Trend Analysis", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id="trend-chart") if not df.empty else html.P("Data loading...", className="text-center")
                ])
            ])
        ], md=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H4("Crop Comparison", className="mb-0")),
                dbc.CardBody([
                    dcc.Graph(id="comparison-chart") if not df.empty else html.P("Data loading...", className="text-center")
                ])
            ])
        ], md=6)
    ], className="mt-4"),
    
    # Store for results
    dcc.Store(id='prediction-store')
    
], fluid=True)

# Callbacks
@app.callback(
    [Output('yield-result', 'children'),
     Output('production-result', 'children'),
     Output('productivity-result', 'children'),
     Output('prediction-store', 'data')],
    [Input('predict-button', 'n_clicks')],
    [State('crop-dropdown', 'value'),
     State('season-dropdown', 'value'),
     State('area-input', 'value'),
     State('year-input', 'value')]
)
def make_prediction(n_clicks, crop, season, area, year):
    if not n_clicks or not all([crop, season, area, year]):
        return "Click Predict", "Click Predict", "Click Predict", {}
    
    result = predictor.predict(crop, season, area, year)
    
    if 'error' in result:
        return f"Error: {result['error']}", "Error", "Error", {}
    
    return (
        f"{result['predicted_yield']:,.0f}",
        f"{result['predicted_production']:,.0f}",
        f"{result['productivity']:.2f}",
        result
    )

# Only add chart callbacks if data is available
if not df.empty:
    @app.callback(
        Output('trend-chart', 'figure'),
        [Input('crop-dropdown', 'value')]
    )
    def update_trend_chart(crop):
        if not crop:
            return {}
        return create_trend_chart(df, crop, 'Yield')

    @app.callback(
        Output('comparison-chart', 'figure'),
        [Input('season-dropdown', 'value')]
    )
    def update_comparison_chart(season):
        if not season:
            return {}
        return create_comparison_chart(df, season)

# Make sure this works for both old and new Dash versions
if __name__ == '__main__':
    try:
        app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
    except AttributeError:
        app.run_server(debug=config.DEBUG, host=config.HOST, port=config.PORT)