# Enhanced filters.py - Replace your existing filters.py with this
import dash_bootstrap_components as dbc
from dash import dcc, html
from datetime import datetime

def create_enhanced_filters(crops, seasons):
    """Create beautiful filter components with icons and enhanced styling"""
    current_year = datetime.now().year
    
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.Label([
                    html.Div([
                        html.I(className="fas fa-seedling", style={'fontSize': '18px'}),
                    ], style={'marginRight': '10px', 'color': '#4ecdc4'}),
                    "Select Crop"
                ], className="fw-bold text-white mb-3 d-flex align-items-center",
                   style={'fontSize': '16px', 'textShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                
                dcc.Dropdown(
                    id='crop-dropdown',
                    options=[{
                        'label': html.Div([
                            get_crop_icon(crop),
                            html.Span(crop, style={'marginLeft': '8px'})
                        ], style={'display': 'flex', 'alignItems': 'center'}),
                        'value': crop
                    } for crop in crops],
                    value=crops[0] if crops else None,
                    className="mb-3 custom-dropdown enhanced-dropdown",
                    placeholder="Choose a crop...",
                    style={
                        'borderRadius': '15px',
                        'fontWeight': '500'
                    },
                    clearable=False
                )
            ], style={'animation': 'fadeInUp 0.8s ease-out 0.1s both'})
        ], md=3),
        
        dbc.Col([
            html.Div([
                html.Label([
                    html.Div([
                        html.I(className="fas fa-calendar-alt", style={'fontSize': '18px'}),
                    ], style={'marginRight': '10px', 'color': '#4facfe'}),
                    "Select Season"
                ], className="fw-bold text-white mb-3 d-flex align-items-center",
                   style={'fontSize': '16px', 'textShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                
                dcc.Dropdown(
                    id='season-dropdown',
                    options=[{
                        'label': html.Div([
                            get_season_icon(season),
                            html.Span(season, style={'marginLeft': '8px'})
                        ], style={'display': 'flex', 'alignItems': 'center'}),
                        'value': season
                    } for season in seasons],
                    value=seasons[0] if seasons else None,
                    className="mb-3 custom-dropdown enhanced-dropdown",
                    placeholder="Choose a season...",
                    style={
                        'borderRadius': '15px',
                        'fontWeight': '500'
                    },
                    clearable=False
                )
            ], style={'animation': 'fadeInUp 0.8s ease-out 0.2s both'})
        ], md=3),
        
        dbc.Col([
            html.Div([
                html.Label([
                    html.Div([
                        html.I(className="fas fa-map-marked-alt", style={'fontSize': '18px'}),
                    ], style={'marginRight': '10px', 'color': '#f093fb'}),
                    "Area (Lakh Hectares)"
                ], className="fw-bold text-white mb-3 d-flex align-items-center",
                   style={'fontSize': '16px', 'textShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                
                dcc.Input(
                    id='area-input',
                    type='number',
                    value=100,
                    min=1,
                    max=1000,
                    step=1,
                    className="form-control mb-3 custom-input enhanced-input",
                    placeholder="Enter area...",
                    style={
                        'borderRadius': '15px',
                        'border': '2px solid rgba(255, 255, 255, 0.3)',
                        'background': 'rgba(255, 255, 255, 0.9)',
                        'height': '55px',
                        'fontSize': '16px',
                        'fontWeight': '500',
                        'textAlign': 'center'
                    }
                ),
                
                # Area suggestions
                html.Div([
                    html.Small("💡 Typical ranges: Small (10-50), Medium (50-200), Large (200+)", 
                             className="text-white-50")
                ])
            ], style={'animation': 'fadeInUp 0.8s ease-out 0.3s both'})
        ], md=3),
        
        dbc.Col([
            html.Div([
                html.Label([
                    html.Div([
                        html.I(className="fas fa-clock", style={'fontSize': '18px'}),
                    ], style={'marginRight': '10px', 'color': '#feca57'}),
                    "Year"
                ], className="fw-bold text-white mb-3 d-flex align-items-center",
                   style={'fontSize': '16px', 'textShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                
                dcc.Input(
                    id='year-input',
                    type='number',
                    value=current_year + 1,
                    min=2000,
                    max=2035,
                    step=1,
                    className="form-control mb-3 custom-input enhanced-input",
                    placeholder="Enter year...",
                    style={
                        'borderRadius': '15px',
                        'border': '2px solid rgba(255, 255, 255, 0.3)',
                        'background': 'rgba(255, 255, 255, 0.9)',
                        'height': '55px',
                        'fontSize': '16px',
                        'fontWeight': '500',
                        'textAlign': 'center'
                    }
                ),
                
                # Year info
                html.Div([
                    html.Small(f"📅 Current: {current_year}, Prediction range: 2000-2035", 
                             className="text-white-50")
                ])
            ], style={'animation': 'fadeInUp 0.8s ease-out 0.4s both'})
        ], md=3)
    ])

def get_crop_icon(crop):
    """Return appropriate icon for each crop type"""
    crop_icons = {
        'Rice': html.I(className="fas fa-seedling", style={'color': '#4ecdc4'}),
        'Wheat': html.I(className="fas fa-wheat", style={'color': '#f39c12'}),
        'Cotton': html.I(className="fas fa-cloud", style={'color': '#ecf0f1'}),
        'Sugarcane': html.I(className="fas fa-candy-cane", style={'color': '#e67e22'}),
        'Maize': html.I(className="fas fa-corn", style={'color': '#f1c40f'}),
        'Soybean': html.I(className="fas fa-circle", style={'color': '#27ae60'}),
        'Groundnut': html.I(className="fas fa-circle-dot", style={'color': '#8b4513'}),
        'Sunflower': html.I(className="fas fa-sun", style={'color': '#ff6b35'}),
        'Default': html.I(className="fas fa-leaf", style={'color': '#2ecc71'})
    }
    return crop_icons.get(crop, crop_icons['Default'])

def get_season_icon(season):
    """Return appropriate icon for each season"""
    season_icons = {
        'Kharif': html.I(className="fas fa-cloud-rain", style={'color': '#3498db'}),
        'Rabi': html.I(className="fas fa-snowflake", style={'color': '#74b9ff'}),
        'Summer': html.I(className="fas fa-sun", style={'color': '#fdcb6e'}),
        'Zaid': html.I(className="fas fa-thermometer-half", style={'color': '#e17055'}),
        'Default': html.I(className="fas fa-calendar", style={'color': '#6c5ce7'})
    }
    return season_icons.get(season, season_icons['Default'])

def create_advanced_filters_with_search(crops, seasons, states=None):
    """Create advanced filters with search functionality and state selection"""
    current_year = datetime.now().year
    
    return html.Div([
        # Primary Filters Row
        dbc.Row([
            dbc.Col([
                create_filter_group(
                    icon="fas fa-seedling",
                    icon_color="#4ecdc4",
                    label="Select Crop",
                    component=dcc.Dropdown(
                        id='crop-dropdown',
                        options=[{
                            'label': crop,
                            'value': crop
                        } for crop in crops],
                        value=crops[0] if crops else None,
                        className="enhanced-dropdown",
                        placeholder="🌾 Choose a crop...",
                        clearable=False,
                        searchable=True
                    ),
                    tooltip="Select the crop type for prediction"
                )
            ], md=6),
            
            dbc.Col([
                create_filter_group(
                    icon="fas fa-calendar-alt",
                    icon_color="#4facfe",
                    label="Select Season",
                    component=dcc.Dropdown(
                        id='season-dropdown',
                        options=[{
                            'label': season,
                            'value': season
                        } for season in seasons],
                        value=seasons[0] if seasons else None,
                        className="enhanced-dropdown",
                        placeholder="🌦️ Choose a season...",
                        clearable=False
                    ),
                    tooltip="Select the growing season"
                )
            ], md=6),
        ], className="mb-4"),
        
        # Secondary Filters Row
        dbc.Row([
            dbc.Col([
                create_filter_group(
                    icon="fas fa-map-marked-alt",
                    icon_color="#f093fb",
                    label="Area (Lakh Hectares)",
                    component=html.Div([
                        dcc.Input(
                            id='area-input',
                            type='number',
                            value=100,
                            min=1,
                            max=1000,
                            step=1,
                            className="enhanced-input",
                            placeholder="Enter cultivation area..."
                        ),
                        html.Div([
                            dbc.ButtonGroup([
                                dbc.Button("Small (50)", id="area-small", size="sm", outline=True, color="light"),
                                dbc.Button("Medium (150)", id="area-medium", size="sm", outline=True, color="light"),
                                dbc.Button("Large (300)", id="area-large", size="sm", outline=True, color="light")
                            ], size="sm", className="mt-2 w-100")
                        ])
                    ]),
                    tooltip="Enter the cultivation area in lakh hectares"
                )
            ], md=6),
            
            dbc.Col([
                create_filter_group(
                    icon="fas fa-clock",
                    icon_color="#feca57",
                    label="Prediction Year",
                    component=html.Div([
                        dcc.Input(
                            id='year-input',
                            type='number',
                            value=current_year + 1,
                            min=2000,
                            max=2035,
                            step=1,
                            className="enhanced-input",
                            placeholder="Enter year..."
                        ),
                        html.Div([
                            dbc.ButtonGroup([
                                dbc.Button(str(current_year + 1), id="year-next", size="sm", outline=True, color="light"),
                                dbc.Button(str(current_year + 2), id="year-next2", size="sm", outline=True, color="light"),
                                dbc.Button(str(current_year + 5), id="year-next5", size="sm", outline=True, color="light")
                            ], size="sm", className="mt-2 w-100")
                        ])
                    ]),
                    tooltip=f"Select year for prediction (Current: {current_year})"
                )
            ], md=6)
        ])
    ])

def create_filter_group(icon, icon_color, label, component, tooltip=None):
    """Create a styled filter group with icon and tooltip"""
    return html.Div([
        html.Label([
            html.Div([
                html.I(className=icon, style={'fontSize': '18px', 'color': icon_color}),
            ], style={'marginRight': '10px'}),
            label,
            html.I(className="fas fa-info-circle ms-2", 
                  style={'fontSize': '12px', 'opacity': '0.7'}) if tooltip else None
        ], className="fw-bold text-white mb-3 d-flex align-items-center",
           style={'fontSize': '16px', 'textShadow': '0 2px 4px rgba(0,0,0,0.1)'},
           title=tooltip if tooltip else ""),
        
        component
    ], className="filter-group")

# Backward compatibility
def create_filters(crops, seasons):
    """Backward compatibility wrapper"""
    return create_enhanced_filters(crops, seasons)