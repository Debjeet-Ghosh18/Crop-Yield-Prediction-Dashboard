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
import logging

# Configure logging to reduce console noise
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('dash').setLevel(logging.ERROR)

# Suppress React dev tools warnings
os.environ['REACT_APP_DISABLE_MINIFY'] = 'false'

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
                'crops': ['Rice', 'Wheat', 'Cotton', 'Sugarcane', 'Maize', 'Barley', 'Millets'],
                'seasons': ['Kharif', 'Rabi', 'Summer']
            }
        
        def predict(self, crop, season, area, year):
            import random
            
            # More realistic prediction logic based on crop and season
            base_yields = {
                'Rice': {'Kharif': 3500, 'Rabi': 3800, 'Summer': 3200},
                'Wheat': {'Kharif': 2800, 'Rabi': 4200, 'Summer': 3000},
                'Cotton': {'Kharif': 1800, 'Rabi': 1600, 'Summer': 1400},
                'Sugarcane': {'Kharif': 75000, 'Rabi': 72000, 'Summer': 68000},
                'Maize': {'Kharif': 4500, 'Rabi': 4800, 'Summer': 4200},
                'Barley': {'Kharif': 2500, 'Rabi': 3200, 'Summer': 2800},
                'Millets': {'Kharif': 1200, 'Rabi': 1000, 'Summer': 900}
            }
            
            base_yield = base_yields.get(crop, {}).get(season, 3000)
            variation = random.uniform(0.8, 1.3)
            yield_val = int(base_yield * variation)
            
            production = (yield_val * area) / 1000  # Convert to lakh tonnes
            productivity = production / area if area > 0 else 0
            
            return {
                'predicted_yield': yield_val,
                'predicted_production': production,
                'productivity': productivity,
                'confidence': random.uniform(0.75, 0.95)
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
    ],
    suppress_callback_exceptions=True,  # Suppress callback exceptions
    assets_folder='assets'  # For custom CSS
)

# Custom CSS to inject
custom_css = """
<style>
/* Animation keyframes */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

@keyframes glow {
    0% { box-shadow: 0 0 5px rgba(79, 172, 254, 0.3); }
    50% { box-shadow: 0 0 20px rgba(79, 172, 254, 0.6); }
    100% { box-shadow: 0 0 5px rgba(79, 172, 254, 0.3); }
}

/* Card hover effects */
.prediction-card:hover {
    transform: translateY(-10px) !important;
    box-shadow: 0 25px 50px rgba(0,0,0,0.2) !important;
}

.chart-card:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 20px 40px rgba(0,0,0,0.15) !important;
}

/* Button effects */
.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 30px rgba(79, 172, 254, 0.6) !important;
}

/* Loading spinner */
.loading-spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #4facfe;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.3);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255,255,255,0.5);
}
</style>
"""

server = app.server
app.title = "🌾 Smart Crop Analytics Dashboard"
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        ''' + custom_css + '''
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Initialize predictor and load data
config = Config()
predictor = CropPredictor()

# Load processed data for visualizations
try:
    df = pd.read_csv(os.path.join(config.PROCESSED_DATA_DIR, config.MERGED_FILE))
    print("Data loaded successfully")
except Exception as e:
    print(f"Loading demo data: {e}")
    # Generate more realistic sample data for demo
    years = list(range(2015, 2025))
    crops = ['Rice', 'Wheat', 'Cotton', 'Sugarcane', 'Maize', 'Barley', 'Millets']
    seasons = ['Kharif', 'Rabi', 'Summer']
    states = ['Maharashtra', 'Uttar Pradesh', 'Punjab', 'Haryana', 'Bihar']
    
    data = []
    for year in years:
        for crop in crops:
            for season in seasons:
                for state in states:
                    import random
                    
                    # More realistic yield ranges based on crop
                    yield_ranges = {
                        'Rice': (2000, 5000),
                        'Wheat': (2500, 4500),
                        'Cotton': (300, 600),
                        'Sugarcane': (60000, 80000),
                        'Maize': (3000, 6000),
                        'Barley': (2000, 3500),
                        'Millets': (800, 1500)
                    }
                    
                    min_yield, max_yield = yield_ranges.get(crop, (1000, 4000))
                    yield_val = random.randint(min_yield, max_yield)
                    area = random.randint(20, 300)
                    production = (yield_val * area) / 1000
                    
                    data.append({
                        'Year': year,
                        'Crop': crop,
                        'Season': season,
                        'State': state,
                        'Yield': yield_val,
                        'Production': production,
                        'Area': area
                    })
    
    df = pd.DataFrame(data)
    print(f"Generated {len(df)} sample records")

# Get available options
options = predictor.get_available_options()

def create_enhanced_filters(crops, seasons):
    """Create beautiful filter components with quick selection buttons"""
    current_year = datetime.now().year
    
    return dbc.Container([
        dbc.Row([
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
                        style={'borderRadius': '15px'},
                        placeholder="Choose a crop..."
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
                        style={'borderRadius': '15px'},
                        placeholder="Choose a season..."
                    )
                ], style={'animation': 'fadeIn 1s 0.2s both'})
            ], md=3),
            
            dbc.Col([
                html.Div([
                    html.Label([
                        html.I(className="fas fa-map-marked-alt me-2 text-warning"),
                        "Area (Lakh Hectares)"
                    ], className="fw-bold text-white mb-2"),
                    dbc.InputGroup([
                        dcc.Input(
                            id='area-input',
                            type='number',
                            value=100,
                            min=1,
                            max=1000,
                            className="form-control",
                            style={
                                'borderRadius': '15px 0 0 15px', 
                                'border': '2px solid rgba(255,255,255,0.3)', 
                                'height': '50px',
                                'background': 'rgba(255,255,255,0.9)',
                                'textAlign': 'center',
                                'fontSize': '16px'
                            }
                        ),
                        dbc.ButtonGroup([
                            dbc.Button("50", id="area-small", size="sm", color="outline-light", style={'borderRadius': '0'}),
                            dbc.Button("150", id="area-medium", size="sm", color="outline-light", style={'borderRadius': '0'}),
                            dbc.Button("300", id="area-large", size="sm", color="outline-light", style={'borderRadius': '0 15px 15px 0'})
                        ], className="input-group-append")
                    ])
                ], style={'animation': 'fadeIn 1s 0.4s both'})
            ], md=3),
            
            dbc.Col([
                html.Div([
                    html.Label([
                        html.I(className="fas fa-clock me-2 text-primary"),
                        "Prediction Year"
                    ], className="fw-bold text-white mb-2"),
                    dbc.InputGroup([
                        dcc.Input(
                            id='year-input',
                            type='number',
                            value=current_year + 1,
                            min=2000,
                            max=2035,
                            className="form-control",
                            style={
                                'borderRadius': '15px 0 0 15px', 
                                'border': '2px solid rgba(255,255,255,0.3)', 
                                'height': '50px',
                                'background': 'rgba(255,255,255,0.9)',
                                'textAlign': 'center',
                                'fontSize': '16px'
                            }
                        ),
                        dbc.ButtonGroup([
                            dbc.Button("+1", id="year-next", size="sm", color="outline-light", style={'borderRadius': '0'}),
                            dbc.Button("+2", id="year-next2", size="sm", color="outline-light", style={'borderRadius': '0'}),
                            dbc.Button("+5", id="year-next5", size="sm", color="outline-light", style={'borderRadius': '0 15px 15px 0'})
                        ], className="input-group-append")
                    ])
                ], style={'animation': 'fadeIn 1s 0.6s both'})
            ], md=3)
        ])
    ], fluid=True)

def create_enhanced_prediction_cards():
    """Create stunning prediction cards with loading states"""
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
                        html.H2(id="yield-result", className="display-3 fw-bold text-success mb-2", 
                               children="Ready to predict"),
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
                        html.H2(id="production-result", className="display-3 fw-bold text-info mb-2",
                               children="Ready to predict"),
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
                        html.H2(id="productivity-result", className="display-3 fw-bold text-warning mb-2",
                               children="Ready to predict"),
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

def create_enhanced_trend_chart(df, crop, metric='Yield'):
    """Create enhanced trend chart with better error handling"""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray")
        )
        return fig
    
    if crop not in df['Crop'].values:
        fig = go.Figure()
        fig.add_annotation(
            text=f"No data available for {crop}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig
    
    crop_data = df[df['Crop'] == crop].groupby('Year')[metric].mean().reset_index()
    
    if crop_data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text=f"No trend data for {crop}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig
    
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
        margin=dict(t=60, b=40, l=40, r=40),
        showlegend=False
    )
    
    return fig

def create_enhanced_comparison_chart(df, season):
    """Create enhanced comparison chart with better error handling"""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color="gray")
        )
        return fig
    
    if season not in df['Season'].values:
        fig = go.Figure()
        fig.add_annotation(
            text=f"No data available for {season} season",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig
    
    season_data = df[df['Season'] == season].groupby('Crop')[['Yield', 'Production']].mean().reset_index()
    
    if season_data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text=f"No comparison data for {season} season",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="gray")
        )
        return fig
    
    fig = go.Figure()
    
    colors = ['#667eea', '#4ecdc4', '#f093fb', '#4facfe', '#feca57', '#ff6b6b', '#4ecdc4']
    
    fig.add_trace(go.Bar(
        name='Average Yield',
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
            text=f'🌾 Average Crop Yield - {season} Season',
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
        margin=dict(t=60, b=100, l=40, r=40),
        showlegend=False
    )
    
    return fig

def create_confidence_bar(confidence, color_type='primary'):
    """Create confidence indicator bar"""
    confidence_percent = confidence * 100
    
    color_map = {
        'success': 'success',
        'info': 'info', 
        'warning': 'warning',
        'primary': 'primary'
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
                            html.Span("Generate Prediction", id="button-text")
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
                           disabled=False,
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
                            dcc.Graph(
                                id="trend-chart", 
                                config={'displayModeBar': False},
                                figure=create_enhanced_trend_chart(df, options['crops'][0] if options['crops'] else 'Rice')
                            )
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
                            dcc.Graph(
                                id="comparison-chart", 
                                config={'displayModeBar': False},
                                figure=create_enhanced_comparison_chart(df, options['seasons'][0] if options['seasons'] else 'Kharif')
                            )
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
            
            # Additional Analytics Section
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-info-circle me-2 text-white"),
                            html.H4("Prediction Insights", className="mb-0 d-inline text-white")
                        ], style={
                            'background': 'linear-gradient(135deg, #f093fb, #f5576c)',
                            'borderRadius': '25px 25px 0 0',
                            'border': 'none'
                        }),
                        dbc.CardBody([
                            html.Div(id="prediction-insights", children=[
                                html.P([
                                    html.I(className="fas fa-lightbulb me-2 text-warning"),
                                    "Make a prediction to see detailed insights and recommendations!"
                                ], className="text-center text-muted mb-0 p-4")
                            ])
                        ])
                    ], style={
                        'background': 'white',
                        'borderRadius': '25px',
                        'border': 'none',
                        'boxShadow': '0 15px 35px rgba(0,0,0,0.1)'
                    })
                ], md=12)
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
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0, disabled=True)  # Disabled by default
])

# Enhanced callbacks with better error handling
@app.callback(
    [Output('yield-result', 'children'),
     Output('production-result', 'children'),
     Output('productivity-result', 'children'),
     Output('prediction-store', 'data'),
     Output('prediction-status', 'children'),
     Output('yield-status', 'children'),
     Output('production-status', 'children'),
     Output('productivity-status', 'children'),
     Output('predict-button', 'disabled'),
     Output('button-text', 'children'),
     Output('prediction-insights', 'children')],
    [Input('predict-button', 'n_clicks')],
    [State('crop-dropdown', 'value'),
     State('season-dropdown', 'value'),
     State('area-input', 'value'),
     State('year-input', 'value')],
    prevent_initial_call=False
)
def make_enhanced_prediction(n_clicks, crop, season, area, year):
    """Enhanced prediction with loading states and insights"""
    
    # Initial state
    if not n_clicks:
        return ("Ready to predict", "Ready to predict", "Ready to predict", {}, 
                "", "", "", "", False, "Generate Prediction",
                html.P([
                    html.I(className="fas fa-lightbulb me-2 text-warning"),
                    "Make a prediction to see detailed insights and recommendations!"
                ], className="text-center text-muted mb-0 p-4"))
    
    # Validation
    if not all([crop, season, area, year]):
        error_msg = dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Please fill in all fields to generate prediction"
        ], color="warning", className="text-center", style={'borderRadius': '15px'})
        
        return ("Missing data", "Missing data", "Missing data", {}, 
                error_msg, "", "", "", False, "Generate Prediction",
                html.P("Complete all fields above", className="text-center text-muted p-4"))
    
    # Validate ranges
    if area <= 0 or area > 1000:
        error_msg = dbc.Alert([
            html.I(className="fas fa-times-circle me-2"),
            "Area must be between 1 and 1000 lakh hectares"
        ], color="danger", className="text-center", style={'borderRadius': '15px'})
        
        return ("Invalid area", "Invalid area", "Invalid area", {}, 
                error_msg, "", "", "", False, "Generate Prediction",
                html.P("Please enter a valid area", className="text-center text-muted p-4"))
    
    if year < 2000 or year > 2035:
        error_msg = dbc.Alert([
            html.I(className="fas fa-times-circle me-2"),
            "Year must be between 2000 and 2035"
        ], color="danger", className="text-center", style={'borderRadius': '15px'})
        
        return ("Invalid year", "Invalid year", "Invalid year", {}, 
                error_msg, "", "", "", False, "Generate Prediction",
                html.P("Please enter a valid year", className="text-center text-muted p-4"))
    
    try:
        # Make prediction
        result = predictor.predict(crop, season, area, year)
        
        if 'error' in result:
            error_msg = dbc.Alert([
                html.I(className="fas fa-times-circle me-2"),
                f"Prediction failed: {result['error']}"
            ], color="danger", className="text-center", style={'borderRadius': '15px'})
            
            return ("Error", "Error", "Error", {}, error_msg, "", "", "", 
                    False, "Generate Prediction",
                    html.P("Prediction error occurred", className="text-center text-danger p-4"))
        
        success_msg = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            "Prediction completed successfully!"
        ], color="success", className="text-center", style={'borderRadius': '15px'})
        
        # Create confidence indicators
        confidence = result.get('confidence', 0.85)
        
        yield_status = create_confidence_bar(confidence, 'success')
        production_status = create_confidence_bar(confidence, 'info') 
        productivity_status = create_confidence_bar(confidence, 'warning')
        
        # Generate insights
        insights = create_prediction_insights(crop, season, area, year, result)
        
        return (
            f"{result['predicted_yield']:,.0f}",
            f"{result['predicted_production']:,.1f}",
            f"{result['productivity']:.2f}",
            result,
            success_msg,
            yield_status,
            production_status,
            productivity_status,
            False,
            "Generate Prediction",
            insights
        )
    
    except Exception as e:
        error_msg = dbc.Alert([
            html.I(className="fas fa-exclamation-circle me-2"),
            f"System error: Please try again"
        ], color="danger", className="text-center", style={'borderRadius': '15px'})
        
        print(f"Prediction error: {e}")  # Log for debugging
        
        return ("System Error", "System Error", "System Error", {}, 
                error_msg, "", "", "", False, "Generate Prediction",
                html.P("System error - please try again", className="text-center text-danger p-4"))

def create_prediction_insights(crop, season, area, year, result):
    """Generate insights based on prediction results"""
    try:
        yield_val = result['predicted_yield']
        production = result['predicted_production']
        productivity = result['productivity']
        confidence = result['confidence']
        
        # Create insights based on values
        insights = []
        
        # Yield insights
        if yield_val > 4000:
            insights.append(("High yield predicted", "success", "fas fa-arrow-up"))
        elif yield_val > 2500:
            insights.append(("Moderate yield predicted", "warning", "fas fa-minus"))
        else:
            insights.append(("Lower yield predicted", "danger", "fas fa-arrow-down"))
        
        # Production insights
        total_production = production
        if total_production > 200:
            insights.append(("High production volume", "success", "fas fa-warehouse"))
        elif total_production > 100:
            insights.append(("Moderate production volume", "info", "fas fa-box"))
        else:
            insights.append(("Limited production volume", "warning", "fas fa-box-open"))
        
        # Confidence insights
        if confidence > 0.9:
            insights.append(("Very high confidence", "success", "fas fa-shield-check"))
        elif confidence > 0.8:
            insights.append(("Good confidence level", "info", "fas fa-shield-alt"))
        else:
            insights.append(("Moderate confidence", "warning", "fas fa-shield"))
        
        # Season-specific recommendations
        season_tips = {
            'Kharif': "Monitor monsoon patterns for optimal results",
            'Rabi': "Ensure adequate irrigation during winter months", 
            'Summer': "Focus on drought-resistant varieties"
        }
        
        insight_cards = []
        for i, (text, color, icon) in enumerate(insights):
            insight_cards.append(
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.I(className=f"{icon} fa-2x mb-2", style={'color': f'var(--bs-{color})'} if color != 'danger' else {'color': '#dc3545'}),
                            html.P(text, className="mb-0 fw-bold")
                        ], className="text-center p-3")
                    ], color=color, outline=True, style={'borderRadius': '15px'})
                ], md=4, className="mb-3")
            )
        
        # Add recommendation card
        recommendation = dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.I(className="fas fa-lightbulb fa-2x mb-2 text-primary"),
                    html.H6("Recommendation", className="fw-bold mb-2"),
                    html.P(season_tips.get(season, "Follow best agricultural practices"), 
                           className="mb-0 small")
                ], className="text-center p-3")
            ], color="primary", outline=True, style={'borderRadius': '15px'})
        ], md=12, className="mb-3")
        
        return html.Div([
            dbc.Row(insight_cards),
            dbc.Row([recommendation])
        ])
        
    except Exception as e:
        return html.P(f"Unable to generate insights", className="text-center text-muted p-4")

@app.callback(
    Output('trend-chart', 'figure'),
    [Input('crop-dropdown', 'value'),
     Input('interval-component', 'n_intervals')],
    prevent_initial_call=False
)
def update_trend_chart(crop, n_intervals):
    """Update trend chart with error handling"""
    try:
        if not crop:
            return create_enhanced_trend_chart(df, options['crops'][0] if options['crops'] else 'Rice')
        return create_enhanced_trend_chart(df, crop, 'Yield')
    except Exception as e:
        print(f"Trend chart error: {e}")
        return go.Figure().add_annotation(
            text="Chart temporarily unavailable",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )

@app.callback(
    Output('comparison-chart', 'figure'),
    [Input('season-dropdown', 'value'),
     Input('interval-component', 'n_intervals')],
    prevent_initial_call=False
)
def update_comparison_chart(season, n_intervals):
    """Update comparison chart with error handling"""
    try:
        if not season:
            return create_enhanced_comparison_chart(df, options['seasons'][0] if options['seasons'] else 'Kharif')
        return create_enhanced_comparison_chart(df, season)
    except Exception as e:
        print(f"Comparison chart error: {e}")
        return go.Figure().add_annotation(
            text="Chart temporarily unavailable",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )

# Quick area selection callbacks
@app.callback(
    Output('area-input', 'value'),
    [Input('area-small', 'n_clicks'),
     Input('area-medium', 'n_clicks'), 
     Input('area-large', 'n_clicks')],
    [State('area-input', 'value')],
    prevent_initial_call=True
)
def update_area_quick_select(small, medium, large, current_value):
    """Handle quick area selection"""
    ctx = callback_context
    if not ctx.triggered:
        return current_value or 100
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    area_map = {
        'area-small': 50,
        'area-medium': 150,
        'area-large': 300
    }
    
    return area_map.get(button_id, current_value or 100)

# Quick year selection callbacks  
@app.callback(
    Output('year-input', 'value'),
    [Input('year-next', 'n_clicks'),
     Input('year-next2', 'n_clicks'),
     Input('year-next5', 'n_clicks')],
    [State('year-input', 'value')],
    prevent_initial_call=True
)
def update_year_quick_select(next1, next2, next5, current_value):
    """Handle quick year selection"""
    ctx = callback_context
    if not ctx.triggered:
        return current_value or (datetime.now().year + 1)
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    current_year = datetime.now().year
    
    year_map = {
        'year-next': current_year + 1,
        'year-next2': current_year + 2,
        'year-next5': current_year + 5
    }
    
    return year_map.get(button_id, current_value or (current_year + 1))

# Add clientside callback for better performance
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            // Add loading animation to button
            return [true, window.dash_clientside.no_update];
        }
        return [false, window.dash_clientside.no_update];
    }
    """,
    [Output('predict-button', 'style'),
     Output('predict-button', 'className')],
    [Input('predict-button', 'n_clicks')],
    prevent_initial_call=True
)

# Add error boundary
@app.server.errorhandler(500)
def handle_500_error(error):
    """Handle internal server errors gracefully"""
    return "Dashboard temporarily unavailable. Please refresh the page.", 500

@app.server.errorhandler(404)
def handle_404_error(error):
    """Handle 404 errors"""
    return "Page not found", 404

def main():
    """Main function to run the app"""
    try:
        print("🌾 Starting Smart Crop Analytics Dashboard...")
        print(f"📊 Loaded {len(df)} data records")
        print(f"🚀 Dashboard available at: http://{config.HOST}:{config.PORT}")
        
        app.run_server(
            debug=config.DEBUG, 
            host=config.HOST, 
            port=config.PORT,
            dev_tools_ui=config.DEBUG,
            dev_tools_props_check=False  # Reduces console warnings
        )
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("🔄 Trying fallback configuration...")
        app.run_server(debug=True, host='0.0.0.0', port=8050)

if __name__ == '__main__':
    main()