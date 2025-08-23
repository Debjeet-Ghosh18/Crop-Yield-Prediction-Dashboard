import dash_bootstrap_components as dbc
from dash import dcc, html

def create_filters(crops, seasons):
    """Create filter components"""
    return dbc.Row([
        dbc.Col([
            html.Label("Select Crop:", className="fw-bold"),
            dcc.Dropdown(
                id='crop-dropdown',
                options=[{'label': crop, 'value': crop} for crop in crops],
                value=crops[0] if crops else None,
                className="mb-3"
            )
        ], md=3),
        
        dbc.Col([
            html.Label("Select Season:", className="fw-bold"),
            dcc.Dropdown(
                id='season-dropdown',
                options=[{'label': season, 'value': season} for season in seasons],
                value=seasons[0] if seasons else None,
                className="mb-3"
            )
        ], md=3),
        
        dbc.Col([
            html.Label("Area (Lakh Hectares):", className="fw-bold"),
            dcc.Input(
                id='area-input',
                type='number',
                value=100,
                min=1,
                max=1000,
                className="form-control mb-3"
            )
        ], md=3),
        
        dbc.Col([
            html.Label("Year:", className="fw-bold"),
            dcc.Input(
                id='year-input',
                type='number',
                value=2025,
                min=2000,
                max=2030,
                className="form-control mb-3"
            )
        ], md=3)
    ])