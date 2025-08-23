import dash_bootstrap_components as dbc
from dash import html

def create_prediction_cards():
    """Create prediction result cards"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Predicted Yield", className="card-title text-primary"),
                    html.H2(id="yield-result", className="text-success"),
                    html.P("kg/hectare", className="text-muted")
                ])
            ], className="mb-3")
        ], md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Predicted Production", className="card-title text-primary"),
                    html.H2(id="production-result", className="text-info"),
                    html.P("Lakh Tonnes", className="text-muted")
                ])
            ], className="mb-3")
        ], md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Productivity", className="card-title text-primary"),
                    html.H2(id="productivity-result", className="text-warning"),
                    html.P("Tonnes/Hectare", className="text-muted")
                ])
            ], className="mb-3")
        ], md=4)
    ])