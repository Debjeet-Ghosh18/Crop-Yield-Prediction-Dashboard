# Enhanced predictions.py - Replace your existing predictions.py with this
import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objects as go

def create_enhanced_prediction_cards():
    """Create stunning prediction result cards with advanced styling and animations"""
    return dbc.Row([
        # Yield Card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        # Icon with gradient background
                        html.Div([
                            html.I(className="fas fa-chart-line fa-3x", 
                                  style={'color': 'white'})
                        ], style={
                            'background': 'linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%)',
                            'borderRadius': '50%',
                            'width': '80px',
                            'height': '80px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'margin': '0 auto 20px auto',
                            'boxShadow': '0 10px 25px rgba(78, 205, 196, 0.3)'
                        }),
                        
                        html.H4("Predicted Yield", 
                               className="card-title text-dark fw-bold mb-3"),
                        
                        html.H2(id="yield-result", 
                               className="display-4 fw-bold mb-2",
                               style={'color': '#44a08d', 'textShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                        
                        html.P("kg/hectare", className="text-muted mb-3"),
                        
                        # Progress bar placeholder
                        html.Div(id="yield-confidence", className="mb-2"),
                        
                        # Trend indicator
                        html.Div(id="yield-trend", className="small text-muted")
                        
                    ], className="text-center")
                ])
            ], className="prediction-card yield-card h-100", style={
                'background': 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
                'borderRadius': '25px',
                'border': 'none',
                'boxShadow': '0 15px 35px rgba(0,0,0,0.1)',
                'transition': 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
                'position': 'relative',
                'overflow': 'hidden'
            })
        ], md=4),
        
        # Production Card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        # Icon with gradient background
                        html.Div([
                            html.I(className="fas fa-warehouse fa-3x", 
                                  style={'color': 'white'})
                        ], style={
                            'background': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                            'borderRadius': '50%',
                            'width': '80px',
                            'height': '80px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'margin': '0 auto 20px auto',
                            'boxShadow': '0 10px 25px rgba(79, 172, 254, 0.3)'
                        }),
                        
                        html.H4("Predicted Production", 
                               className="card-title text-dark fw-bold mb-3"),
                        
                        html.H2(id="production-result", 
                               className="display-4 fw-bold mb-2",
                               style={'color': '#00f2fe', 'textShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                        
                        html.P("Lakh Tonnes", className="text-muted mb-3"),
                        
                        # Progress bar placeholder
                        html.Div(id="production-confidence", className="mb-2"),
                        
                        # Market value estimate
                        html.Div(id="production-value", className="small text-muted")
                        
                    ], className="text-center")
                ])
            ], className="prediction-card production-card h-100", style={
                'background': 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
                'borderRadius': '25px',
                'border': 'none',
                'boxShadow': '0 15px 35px rgba(0,0,0,0.1)',
                'transition': 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
                'position': 'relative',
                'overflow': 'hidden'
            })
        ], md=4),
        
        # Productivity Card
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        # Icon with gradient background
                        html.Div([
                            html.I(className="fas fa-tachometer-alt fa-3x", 
                                  style={'color': 'white'})
                        ], style={
                            'background': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                            'borderRadius': '50%',
                            'width': '80px',
                            'height': '80px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'margin': '0 auto 20px auto',
                            'boxShadow': '0 10px 25px rgba(240, 147, 251, 0.3)'
                        }),
                        
                        html.H4("Productivity", 
                               className="card-title text-dark fw-bold mb-3"),
                        
                        html.H2(id="productivity-result", 
                               className="display-4 fw-bold mb-2",
                               style={'color': '#f5576c', 'textShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                        
                        html.P("Tonnes/Hectare", className="text-muted mb-3"),
                        
                        # Progress bar placeholder
                        html.Div(id="productivity-confidence", className="mb-2"),
                        
                        # Rating indicator
                        html.Div(id="productivity-rating", className="small text-muted")
                        
                    ], className="text-center")
                ])
            ], className="prediction-card productivity-card h-100", style={
                'background': 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
                'borderRadius': '25px',
                'border': 'none',
                'boxShadow': '0 15px 35px rgba(0,0,0,0.1)',
                'transition': 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
                'position': 'relative',
                'overflow': 'hidden'
            })
        ], md=4)
    ], className="mb-5")

def create_confidence_indicator(confidence_score, metric_type="yield"):
    """Create confidence indicator with progress bar"""
    if not confidence_score:
        return html.Div()
    
    confidence_percent = confidence_score * 100
    
    # Determine color based on confidence level
    if confidence_percent >= 90:
        color = "#44a08d"  # Green
        icon = "fas fa-check-circle"
        text = "Very High Confidence"
    elif confidence_percent >= 80:
        color = "#4facfe"  # Blue
        icon = "fas fa-thumbs-up"
        text = "High Confidence"
    elif confidence_percent >= 70:
        color = "#feca57"  # Yellow
        icon = "fas fa-exclamation-triangle"
        text = "Moderate Confidence"
    else:
        color = "#f5576c"  # Red
        icon = "fas fa-exclamation-circle"
        text = "Low Confidence"
    
    return html.Div([
        html.Div([
            html.I(className=f"{icon} me-2"),
            html.Span(f"{text} ({confidence_percent:.1f}%)", 
                     style={'fontSize': '12px', 'fontWeight': '600'})
        ], style={'color': color, 'marginBottom': '8px'}),
        
        dbc.Progress(
            value=confidence_percent,
            color="success" if confidence_percent >= 80 else "warning" if confidence_percent >= 70 else "danger",
            style={'height': '8px', 'borderRadius': '10px'},
            striped=True,
            animated=True
        )
    ])

def create_trend_indicator(current_value, historical_avg):
    """Create trend indicator showing if value is above/below historical average"""
    if not current_value or not historical_avg:
        return html.Div()
    
    difference = ((current_value - historical_avg) / historical_avg) * 100
    
    if abs(difference) < 1:
        icon = "fas fa-equals"
        color = "#666"
        text = "Similar to average"
        arrow = ""
    elif difference > 0:
        icon = "fas fa-arrow-up"
        color = "#44a08d"
        text = f"{difference:+.1f}% above average"
        arrow = "↗️"
    else:
        icon = "fas fa-arrow-down"
        color = "#f5576c"
        text = f"{abs(difference):.1f}% below average"
        arrow = "↘️"
    
    return html.Div([
        html.I(className=f"{icon} me-2", style={'color': color}),
        html.Span(f"{arrow} {text}", style={
            'fontSize': '11px',
            'color': color,
            'fontWeight': '500'
        })
    ])

def create_performance_gauge(value, max_value, title, color_scheme="blue"):
    """Create a gauge chart for performance metrics"""
    
    color_maps = {
        "blue": {"low": "#e3f2fd", "mid": "#4facfe", "high": "#00f2fe"},
        "green": {"low": "#e8f5e8", "mid": "#4ecdc4", "high": "#44a08d"},
        "purple": {"low": "#f3e5f5", "mid": "#f093fb", "high": "#f5576c"}
    }
    
    colors = color_maps.get(color_scheme, color_maps["blue"])
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 14}},
        delta={'reference': max_value * 0.7},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': colors["high"]},
            'steps': [
                {'range': [0, max_value * 0.3], 'color': colors["low"]},
                {'range': [max_value * 0.3, max_value * 0.7], 'color': colors["mid"]},
                {'range': [max_value * 0.7, max_value], 'color': colors["high"]}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(
        template='plotly_white',
        font=dict(family="Inter"),
        margin=dict(t=60, b=40, l=40, r=40),
        height=300
    )
    
    return fig

# Backward compatibility
def create_prediction_cards():
    """Backward compatibility wrapper"""
    return create_enhanced_prediction_cards()