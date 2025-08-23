import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_trend_chart(df, crop, metric):
    """Create trend chart for selected crop and metric"""
    crop_data = df[df['Crop'] == crop].groupby('Year')[metric].mean().reset_index()
    
    fig = px.line(crop_data, x='Year', y=metric, 
                  title=f'{metric} Trend for {crop}',
                  line_shape='spline')
    
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title=metric,
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig

def create_comparison_chart(df, season):
    """Create comparison chart across crops for selected season"""
    season_data = df[df['Season'] == season].groupby('Crop')[['Yield', 'Production']].mean().reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Yield (kg/ha)',
        x=season_data['Crop'],
        y=season_data['Yield'],
        yaxis='y',
        offsetgroup=1
    ))
    
    fig.add_trace(go.Bar(
        name='Production (Lakh Tonnes)',
        x=season_data['Crop'],
        y=season_data['Production'],
        yaxis='y2',
        offsetgroup=2
    ))
    
    fig.update_layout(
        title=f'Crop Comparison - {season} Season',
        xaxis=dict(title='Crops'),
        yaxis=dict(title='Yield (kg/ha)', side='left'),
        yaxis2=dict(title='Production (Lakh Tonnes)', side='right', overlaying='y'),
        barmode='group',
        template='plotly_white'
    )
    
    return fig