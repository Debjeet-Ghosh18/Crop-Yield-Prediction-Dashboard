import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import os
import sys
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from models.predictor import CropPredictor
    from config import Config
except ImportError:
    # Fallback for demo purposes
    class CropPredictor:
        def get_available_options(self):
            return {
                'crops': ['Rice', 'Wheat', 'Cotton', 'Sugarcane', 'Maize'],
                'seasons': ['Kharif', 'Rabi', 'Summer']
            }
        
        def predict(self, crop, season, area, year):
            import random
            yield_val = random.randint(2000, 5000)
            production = yield_val * area * 0.01
            productivity = production / area if area > 0 else 0
            
            return {
                'predicted_yield': yield_val,
                'predicted_production': production,
                'productivity': productivity,
                'confidence': random.uniform(0.8, 0.95)
            }
    
    class Config:
        DEBUG = True
        HOST = '0.0.0.0'
        PORT = 8050
        PROCESSED_DATA_DIR = 'dashboard/Data/Processed'
        MERGED_FILE = 'merged_data.csv'

# Initialize the Dash app with enhanced styling
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
    ]
)
server = app.server
app.title = "🌾 Smart Crop Analytics Dashboard"

# Initialize predictor and load data
config = Config()
predictor = CropPredictor()

# Load processed data for visualizations
try:
    df = pd.read_csv(os.path.join(config.PROCESSED_DATA_DIR, config.MERGED_FILE))
except:
    # Generate sample data for demo
    years = list(range(2015, 2025))
    crops = ['Rice', 'Wheat', 'Cotton', 'Sugarcane', 'Maize']
    seasons = ['Kharif', 'Rabi', 'Summer']
    
    data = []
    for year in years:
        for crop in crops:
            for season in seasons:
                import random
                data.append({
                    'Year': year,
                    'Crop': crop,
                    'Season': season,
                    'Yield': random.randint(1500, 6000),
                    'Production': random.randint(50, 500),
                    'Area': random.randint(50, 200)
                })
    
    df = pd.DataFrame(data)

# Get available options
options = predictor.get_available_options()

def create_enhanced_filters(crops, seasons):
    """Create beautiful filter components"""
    current_year = datetime.now().year
    
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.Label([
                    html.I(className="fas fa-seedling me-2 text-success"),
                    "Select Crop"
                ], className="fw-bold text-white mb-2"),
                dcc.Dropdown(
                    id='crop-dropdown',
                    options=[{'label': f"🌾 {crop}", 'value': crop} for crop in crops],
                    value=crops[0] if crops else None,
                    className="mb-3",
                    style={'borderRadius': '15px'}
                )
            ], style={'animation': 'fadeIn 1s'})
        ], md=3),
        
        dbc.Col([
            html.Div([
                html.Label([
                    html.I(className="fas fa-calendar-alt me-2 text-info"),
                    "Select Season"
                ], className="fw-bold text-white mb-2"),
                dcc.Dropdown(
                    id='season-dropdown',
                    options=[{'label': f"🌦️ {season}", 'value': season} for season in seasons],
                    value=seasons[0] if seasons else None,
                    className="mb-3",
                    style={'borderRadius': '15px'}
                )
            ], style={'animation': 'fadeIn 1s 0.2s both'})
        ], md=3),
        
        dbc.Col([
            html.Div([
                html.Label([
                    html.I(className="fas fa-map-marked-alt me-2 text-warning"),
                    "Area (Lakh Hectares)"
                ], className="fw-bold text-white mb-2"),
                dcc.Input(
                    id='area-input',
                    type='number',
                    value=100,
                    min=1,
                    max=1000,
                    className="form-control mb-3",
                    style={
                        'borderRadius': '15px', 
                        'border': '2px solid rgba(255,255,255,0.3)', 
                        'height': '50px',
                        'background': 'rgba(255,255,255,0.9)',
                        'textAlign': 'center',
                        'fontSize': '16px'
                    }
                )
            ], style={'animation': 'fadeIn 1s 0.4s both'})
        ], md=3),
        
        dbc.Col([
            html.Div([
                html.Label([
                    html.I(className="fas fa-clock me-2 text-primary"),
                    "Year"
                ], className="fw-bold text-white mb-2"),
                dcc.Input(
                    id='year-input',
                    type='number',
                    value=current_year + 1,
                    min=2000,
                    max=2035,
                    className="form-control mb-3",
                    style={
                        'borderRadius': '15px', 
                        'border': '2px solid rgba(255,255,255,0.3)', 
                        'height': '50px',
                        'background': 'rgba(255,255,255,0.9)',
                        'textAlign': 'center',
                        'fontSize': '16px'
                    }
                )
            ], style={'animation': 'fadeIn 1s 0.6s both'})
        ], md=3)
    ])

def create_enhanced_prediction_cards():
    """Create stunning prediction cards"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-chart-line fa-4x text-white")
                        ], style={
                            'background': 'linear-gradient(135deg, #4ecdc4, #44a08d)',
                            'borderRadius': '50%',
                            'width': '100px',
                            'height': '100px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'margin': '0 auto 20px',
                            'boxShadow': '0 10px 30px rgba(78, 205, 196, 0.3)',
                            'animation': 'pulse 2s infinite'
                        }),
                        html.H4("Predicted Yield", className="card-title text-dark fw-bold"),
                        html.H2(id="yield-result", className="display-3 fw-bold text-success mb-2"),
                        html.P("kg/hectare", className="text-muted"),
                        html.Div(id="yield-status", className="mt-2")
                    ], className="text-center")
                ])
            ], style={
                'background': 'linear-gradient(135deg, #ffffff, #f8f9fa)',
                'borderRadius': '25px',
                'border': 'none',
                'boxShadow': '0 15px 35px rgba(0,0,0,0.1)',
                'transition': 'transform 0.3s ease, box-shadow 0.3s ease'
            }, className="h-100 prediction-card")
        ], md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-warehouse fa-4x text-white")
                        ], style={
                            'background': 'linear-gradient(135deg, #4facfe, #00f2fe)',
                            'borderRadius': '50%',
                            'width': '100px',
                            'height': '100px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'margin': '0 auto 20px',
                            'boxShadow': '0 10px 30px rgba(79, 172, 254, 0.3)',
                            'animation': 'pulse 2s infinite 0.5s'
                        }),
                        html.H4("Predicted Production", className="card-title text-dark fw-bold"),
                        html.H2(id="production-result", className="display-3 fw-bold text-info mb-2"),
                        html.P("Lakh Tonnes", className="text-muted"),
                        html.Div(id="production-status", className="mt-2")
                    ], className="text-center")
                ])
            ], style={
                'background': 'linear-gradient(135deg, #ffffff, #f8f9fa)',
                'borderRadius': '25px',
                'border': 'none',
                'boxShadow': '0 15px 35px rgba(0,0,0,0.1)',
                'transition': 'transform 0.3s ease, box-shadow 0.3s ease'
            }, className="h-100 prediction-card")
        ], md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-tachometer-alt fa-4x text-white")
                        ], style={
                            'background': 'linear-gradient(135deg, #f093fb, #f5576c)',
                            'borderRadius': '50%',
                            'width': '100px',
                            'height': '100px',
                            'display': 'flex',
                            'alignItems': 'center',
                            'justifyContent': 'center',
                            'margin': '0 auto 20px',
                            'boxShadow': '0 10px 30px rgba(240, 147, 251, 0.3)',
                            'animation': 'pulse 2s infinite 1s'
                        }),
                        html.H4("Productivity", className="card-title text-dark fw-bold"),
                        html.H2(id="productivity-result", className="display-3 fw-bold text-warning mb-2"),
                        html.P("Tonnes/Hectare", className="text-muted"),
                        html.Div(id="productivity-status", className="mt-2")
                    ], className="text-center")
                ])
            ], style={
                'background': 'linear-gradient(135deg, #ffffff, #f8f9fa)',
                'borderRadius': '25px',
                'border': 'none',
                'boxShadow': '0 15px 35px rgba(0,0,0,0.1)',
                'transition': 'transform 0.3s ease, box-shadow 0.3s ease'
            }, className="h-100 prediction-card")
        ], md=4)
    ], className="mb-5")

def create_enhanced_trend_chart(df, crop, metric):
    """Create enhanced trend chart"""
    if df.empty or crop not in df['Crop'].values:
        return go.Figure()
    
    crop_data = df[df['Crop'] == crop].groupby('Year')[metric].mean().reset_index()
    
    fig = go.Figure()
    
    # Add area fill
    fig.add_trace(go.Scatter(
        x=crop_data['Year'],
        y=crop_data[metric],
        fill='tozeroy',
        mode='none',
        name='Area',
        fillcolor='rgba(102, 126, 234, 0.1)',
        showlegend=False
    ))
    
    # Add main line
    fig.add_trace(go.Scatter(
        x=crop_data['Year'],
        y=crop_data[metric],
        mode='lines+markers',
        name=f'{crop} {metric}',
        line=dict(color='#667eea', width=4, shape='spline'),
        marker=dict(size=12, color='#764ba2', line=dict(color='white', width=2)),
        hovertemplate=f'<b>Year:</b> %{{x}}<br><b>{metric}:</b> %{{y:,.0f}}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f'📈 {metric} Trend for {crop}',
            font=dict(size=20, color='#2c3e50', family='Inter'),
            x=0.5
        ),
        xaxis=dict(
            title="Year",
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True
        ),
        yaxis=dict(
            title=metric,
            gridcolor='rgba(0,0,0,0.1)',
            showgrid=True
        ),
        hovermode='x unified',
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter"),
        margin=dict(t=60, b=40, l=40, r=40)
    )
    
    return fig

def create_enhanced_comparison_chart(df, season):
    """Create enhanced comparison chart"""
    if df.empty or season not in df['Season'].values:
        return go.Figure()
    
    season_data = df[df['Season'] == season].groupby('Crop')[['Yield', 'Production']].mean().reset_index()
    
    fig = go.Figure()
    
    colors = ['#667eea', '#4ecdc4', '#f093fb', '#4facfe', '#feca57']
    
    fig.add_trace(go.Bar(
        name='Yield (kg/ha)',
        x=season_data['Crop'],
        y=season_data['Yield'],
        marker=dict(
            color=colors[:len(season_data)],
            line=dict(color='rgba(255,255,255,0.8)', width=2),
            opacity=0.8
        ),
        hovertemplate='<b>%{x}</b><br>Yield: %{y:,.0f} kg/ha<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text=f'🌾 Crop Performance - {season} Season',
            font=dict(size=20, color='#2c3e50', family='Inter'),
            x=0.5
        ),
        xaxis=dict(
            title='Crops',
            tickangle=45
        ),
        yaxis=dict(
            title='Yield (kg/ha)'
        ),
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter"),
        margin=dict(t=60, b=80, l=40, r=40)
    )
    
    return fig

# Define the layout
app.layout = html.Div([
    html.Div([
        dbc.Container([
            # Header Section
            html.Div([
                html.H1([
                    html.I(className="fas fa-seedling me-3"),
                    "Smart Crop Analytics Dashboard"
                ], className="display-3 fw-bold text-white mb-3 text-center",
                   style={'textShadow': '0 4px 15px rgba(0,0,0,0.2)'}),
                html.P("Predict crop yield and production using advanced machine learning", 
                       className="lead text-white text-center mb-2",
                       style={'opacity': '0.9'}),
                html.P(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                       className="text-white text-center small mb-5",
                       style={'opacity': '0.7'})
            ], className="mb-5"),
            
            # Filters Section
            dbc.Card([
                dbc.CardBody([
                    create_enhanced_filters(options['crops'], options['seasons'])
                ])
            ], style={
                'background': 'rgba(255, 255, 255, 0.15)',
                'backdropFilter': 'blur(15px)',
                'border': '1px solid rgba(255, 255, 255, 0.2)',
                'borderRadius': '25px',
                'boxShadow': '0 15px 35px rgba(0,0,0,0.1)'
            }, className="mb-5"),
            
            # Prediction Button
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dbc.Button([
                            html.I(className="fas fa-magic me-2"),
                            "Generate Prediction"
                        ], id="predict-button", 
                           color="primary", 
                           size="lg",
                           className="w-100",
                           style={
                               'background': 'linear-gradient(135deg, #4facfe, #00f2fe)',
                               'border': 'none',
                               'borderRadius': '30px',
                               'padding': '18px 40px',
                               'fontSize': '18px',
                               'fontWeight': '700',
                               'textTransform': 'uppercase',
                               'letterSpacing': '1px',
                               'boxShadow': '0 8px 25px rgba(79, 172, 254, 0.4)',
                               'transition': 'all 0.3s ease'
                           },
                           n_clicks=0),
                        html.Div(id="prediction-status", className="mt-3 text-center")
                    ])
                ], md={'size': 6, 'offset': 3})
            ], className="mb-5"),
            
            # Results Section
            html.Div(id="results-container", children=[
                create_enhanced_prediction_cards()
            ]),
            
            # Charts Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-line me-2 text-white"),
                            html.H4("Trend Analysis", className="mb-0 d-inline text-white")
                        ], style={
                            'background': 'linear-gradient(135deg, #667eea, #764ba2)',
                            'borderRadius': '25px 25px 0 0',
                            'border': 'none'
                        }),
                        dbc.CardBody([
                            dcc.Graph(id="trend-chart", config={'displayModeBar': False})
                        ], style={'padding': '30px'})
                    ], style={
                        'background': 'white',
                        'borderRadius': '25px',
                        'border': 'none',
                        'boxShadow': '0 15px 35px rgba(0,0,0,0.1)',
                        'transition': 'transform 0.3s ease, box-shadow 0.3s ease'
                    }, className="chart-card")
                ], md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-bar me-2 text-white"),
                            html.H4("Crop Comparison", className="mb-0 d-inline text-white")
                        ], style={
                            'background': 'linear-gradient(135deg, #4ecdc4, #44a08d)',
                            'borderRadius': '25px 25px 0 0',
                            'border': 'none'
                        }),
                        dbc.CardBody([
                            dcc.Graph(id="comparison-chart", config={'displayModeBar': False})
                        ], style={'padding': '30px'})
                    ], style={
                        'background': 'white',
                        'borderRadius': '25px',
                        'border': 'none',
                        'boxShadow': '0 15px 35px rgba(0,0,0,0.1)',
                        'transition': 'transform 0.3s ease, box-shadow 0.3s ease'
                    }, className="chart-card")
                ], md=6)
            ], className="mb-5"),
            
            # Footer
            html.Hr(style={'border': '1px solid rgba(255,255,255,0.2)', 'margin': '50px 0 20px 0'}),
            html.Div([
                html.P([
                    html.I(className="fas fa-leaf me-2"),
                    "Powered by Advanced Machine Learning & Agricultural Data Science"
                ], className="text-center text-white mb-0",
                   style={'opacity': '0.7', 'fontSize': '14px'})
            ])
            
        ], fluid=True)
    ], style={
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'minHeight': '100vh',
        'padding': '20px 0',
        'fontFamily': 'Inter, sans-serif'
    }),
    
    # Store for results
    dcc.Store(id='prediction-store'),
    dcc.Interval(id='interval-component', interval=30*1000, n_intervals=0)
])

# Enhanced callbacks
@app.callback(
    [Output('yield-result', 'children'),
     Output('production-result', 'children'),
     Output('productivity-result', 'children'),
     Output('prediction-store', 'data'),
     Output('prediction-status', 'children'),
     Output('yield-status', 'children'),
     Output('production-status', 'children'),
     Output('productivity-status', 'children')],
    [Input('predict-button', 'n_clicks')],
    [State('crop-dropdown', 'value'),
     State('season-dropdown', 'value'),
     State('area-input', 'value'),
     State('year-input', 'value')]
)
def make_enhanced_prediction(n_clicks, crop, season, area, year):
    if not n_clicks:
        return ("Ready to predict", "Ready to predict", "Ready to predict", {}, 
                "", "", "", "")
    
    if not all([crop, season, area, year]):
        error_msg = html.Div([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Please fill in all fields"
        ], className="alert alert-warning text-center", style={'borderRadius': '15px'})
        return ("Missing data", "Missing data", "Missing data", {}, 
                error_msg, "", "", "")
    
    try:
        result = predictor.predict(crop, season, area, year)
        
        if 'error' in result:
            error_msg = html.Div([
                html.I(className="fas fa-times-circle me-2"),
                f"Prediction failed: {result['error']}"
            ], className="alert alert-danger text-center", style={'borderRadius': '15px'})
            return ("Error", "Error", "Error", {}, error_msg, "", "", "")
        
        success_msg = html.Div([
            html.I(className="fas fa-check-circle me-2"),
            "Prediction completed successfully!"
        ], className="alert alert-success text-center", style={'borderRadius': '15px'})
        
        # Create confidence indicators
        confidence = result.get('confidence', 0.85)
        
        yield_status = create_confidence_bar(confidence, 'success')
        production_status = create_confidence_bar(confidence, 'info') 
        productivity_status = create_confidence_bar(confidence, 'warning')
        
        return (
            f"{result['predicted_yield']:,.0f}",
            f"{result['predicted_production']:,.0f}",
            f"{result['productivity']:.2f}",
            result,
            success_msg,
            yield_status,
            production_status,
            productivity_status
        )
    
    except Exception as e:
        error_msg = html.Div([
            html.I(className="fas fa-exclamation-circle me-2"),
            f"System error: {str(e)}"
        ], className="alert alert-danger text-center", style={'borderRadius': '15px'})
        return ("System Error", "System Error", "System Error", {}, 
                error_msg, "", "", "")

def create_confidence_bar(confidence, color_type):
    """Create confidence indicator bar"""
    confidence_percent = confidence * 100
    
    color_map = {
        'success': 'success',
        'info': 'info', 
        'warning': 'warning'
    }
    
    return html.Div([
        html.Small(f"Confidence: {confidence_percent:.1f}%", 
                  className="text-muted fw-bold"),
        dbc.Progress(
            value=confidence_percent,
            color=color_map.get(color_type, 'primary'),
            style={'height': '6px', 'borderRadius': '10px'},
            striped=True,
            animated=confidence_percent > 70
        )
    ])

@app.callback(
    Output('trend-chart', 'figure'),
    [Input('crop-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_trend_chart(crop, n_intervals):
    if not crop:
        return go.Figure()
    return create_enhanced_trend_chart(df, crop, 'Yield')

@app.callback(
    Output('comparison-chart', 'figure'),
    [Input('season-dropdown', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_comparison_chart(season, n_intervals):
    if not season:
        return go.Figure()
    return create_enhanced_comparison_chart(df, season)

# Quick area selection callbacks
@app.callback(
    Output('area-input', 'value'),
    [Input('area-small', 'n_clicks'),
     Input('area-medium', 'n_clicks'), 
     Input('area-large', 'n_clicks')],
    prevent_initial_call=True
)
def update_area_quick_select(small, medium, large):
    ctx = callback_context
    if not ctx.triggered:
        return 100
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'area-small':
        return 50
    elif button_id == 'area-medium':
        return 150
    elif button_id == 'area-large':
        return 300
    
    return 100

# Quick year selection callbacks  
@app.callback(
    Output('year-input', 'value'),
    [Input('year-next', 'n_clicks'),
     Input('year-next2', 'n_clicks'),
     Input('year-next5', 'n_clicks')],
    prevent_initial_call=True
)
def update_year_quick_select(next1, next2, next5):
    ctx = callback_context
    if not ctx.triggered:
        return datetime.now().year + 1
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    current_year = datetime.now().year
    
    if button_id == 'year-next':
        return current_year + 1
    elif button_id == 'year-next2':
        return current_year + 2
    elif button_id == 'year-next5':
        return current_year + 5
    
    return current_year + 1

if __name__ == '__main__':
    try:
        app.run_server(debug=config.DEBUG, host=config.HOST, port=config.PORT)
    except:
        app.run_server(debug=True, host='0.0.0.0', port=8050)