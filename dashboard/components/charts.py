# Enhanced charts.py - Replace your existing charts.py with this
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots
import numpy as np

def create_enhanced_trend_chart(df, crop, metric):
    """Create stunning trend chart with animations and enhanced visuals"""
    if df.empty or crop not in df['Crop'].values:
        return create_empty_chart("No data available for selected crop")
    
    crop_data = df[df['Crop'] == crop].groupby('Year')[metric].mean().reset_index()
    
    # Calculate moving average for smoother trend
    if len(crop_data) >= 3:
        crop_data['Moving_Avg'] = crop_data[metric].rolling(window=3, center=True).mean()
    
    fig = go.Figure()
    
    # Add area fill first (background layer)
    fig.add_trace(go.Scatter(
        x=crop_data['Year'],
        y=crop_data[metric],
        fill='tozeroy',
        mode='none',
        name='Area Fill',
        fillcolor='rgba(102, 126, 234, 0.1)',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add main trend line
    fig.add_trace(go.Scatter(
        x=crop_data['Year'],
        y=crop_data[metric],
        mode='lines+markers',
        name=f'{crop} {metric}',
        line=dict(
            color='#667eea',
            width=4,
            shape='spline',
            smoothing=0.3
        ),
        marker=dict(
            size=12,
            color='#764ba2',
            line=dict(color='white', width=2),
            symbol='circle'
        ),
        hovertemplate=f'<b>Year:</b> %{{x}}<br><b>{metric}:</b> %{{y:,.0f}}<br><extra></extra>',
        connectgaps=True
    ))
    
    # Add moving average if available
    if 'Moving_Avg' in crop_data.columns:
        fig.add_trace(go.Scatter(
            x=crop_data['Year'],
            y=crop_data['Moving_Avg'],
            mode='lines',
            name='Trend Line',
            line=dict(
                color='rgba(245, 87, 108, 0.8)',
                width=2,
                dash='dash'
            ),
            hovertemplate=f'<b>Year:</b> %{{x}}<br><b>Trend:</b> %{{y:,.0f}}<br><extra></extra>'
        ))
    
    # Add peak/valley annotations
    if len(crop_data) > 3:
        max_idx = crop_data[metric].idxmax()
        min_idx = crop_data[metric].idxmin()
        
        # Highest point
        fig.add_annotation(
            x=crop_data.loc[max_idx, 'Year'],
            y=crop_data.loc[max_idx, metric],
            text=f"Peak: {crop_data.loc[max_idx, metric]:,.0f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor='#44a08d',
            bgcolor='rgba(68, 160, 141, 0.8)',
            bordercolor='#44a08d',
            font=dict(color='white', size=10)
        )
        
        # Lowest point
        fig.add_annotation(
            x=crop_data.loc[min_idx, 'Year'],
            y=crop_data.loc[min_idx, metric],
            text=f"Low: {crop_data.loc[min_idx, metric]:,.0f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor='#f5576c',
            bgcolor='rgba(245, 87, 108, 0.8)',
            bordercolor='#f5576c',
            font=dict(color='white', size=10)
        )
    
    # Calculate growth rate
    if len(crop_data) >= 2:
        first_year = crop_data.iloc[0]
        last_year = crop_data.iloc[-1]
        years_diff = last_year['Year'] - first_year['Year']
        if years_diff > 0 and first_year[metric] > 0:
            growth_rate = ((last_year[metric] / first_year[metric]) ** (1/years_diff) - 1) * 100
            growth_text = f"Avg Annual Growth: {growth_rate:+.1f}%"
        else:
            growth_text = "Growth: N/A"
    else:
        growth_text = "Growth: N/A"
    
    fig.update_layout(
        title=dict(
            text=f'📈 {metric} Trend for {crop}<br><span style="font-size:14px; color:#666;">{growth_text}</span>',
            font=dict(size=18, color='#2c3e50', family='Inter'),
            x=0.5
        ),
        xaxis=dict(
            title=dict(text="Year", font=dict(size=14, color='#2c3e50')),
            gridcolor='rgba(0,0,0,0.05)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#666')
        ),
        yaxis=dict(
            title=dict(text=f"{metric} (kg/ha)" if metric == 'Yield' else f"{metric} (Lakh Tonnes)", 
                      font=dict(size=14, color='#2c3e50')),
            gridcolor='rgba(0,0,0,0.05)',
            showgrid=True,
            zeroline=False,
            tickfont=dict(color='#666')
        ),
        hovermode='x unified',
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        margin=dict(t=80, b=60, l=60, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1
        ),
        showlegend=True if 'Moving_Avg' in crop_data.columns else False
    )
    
    return fig

def create_enhanced_comparison_chart(df, season):
    """Create stunning comparison chart with multiple metrics"""
    if df.empty or season not in df['Season'].values:
        return create_empty_chart("No data available for selected season")
    
    season_data = df[df['Season'] == season].groupby('Crop')[['Yield', 'Production', 'Area']].mean().reset_index()
    season_data = season_data.sort_values('Yield', ascending=True)  # Sort for better visualization
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=1, cols=1,
        secondary_y=True,
        subplot_titles=[f'🌾 Crop Performance Comparison - {season} Season']
    )
    
    # Color palette
    colors = ['#667eea', '#4ecdc4', '#f093fb', '#4facfe', '#feca57', '#ff6b6b', '#4ecdc4', '#45b7d1']
    
    # Add yield bars
    fig.add_trace(
        go.Bar(
            name='Yield (kg/ha)',
            x=season_data['Crop'],
            y=season_data['Yield'],
            marker=dict(
                color=colors[:len(season_data)],
                line=dict(color='rgba(255,255,255,0.8)', width=2),
                opacity=0.8
            ),
            hovertemplate='<b>%{x}</b><br>Yield: %{y:,.0f} kg/ha<extra></extra>',
            text=season_data['Yield'].apply(lambda x: f'{x:,.0f}'),
            textposition='outside',
            textfont=dict(size=10, color='#2c3e50')
        ),
        secondary_y=False
    )
    
    # Add production line
    fig.add_trace(
        go.Scatter(
            name='Production (Lakh Tonnes)',
            x=season_data['Crop'],
            y=season_data['Production'],
            mode='lines+markers',
            line=dict(color='#f5576c', width=4),
            marker=dict(size=10, color='#f5576c', line=dict(color='white', width=2)),
            hovertemplate='<b>%{x}</b><br>Production: %{y:,.0f} Lakh Tonnes<extra></extra>'
        ),
        secondary_y=True
    )
    
    # Calculate efficiency (Yield per unit Area)
    season_data['Efficiency'] = season_data['Yield'] / (season_data['Area'] + 1)  # +1 to avoid division by zero
    
    # Add efficiency indicators as scatter points
    fig.add_trace(
        go.Scatter(
            name='Efficiency Index',
            x=season_data['Crop'],
            y=season_data['Efficiency'] * 50,  # Scale for visibility
            mode='markers',
            marker=dict(
                size=season_data['Efficiency'] / season_data['Efficiency'].max() * 30 + 10,
                color='rgba(102, 126, 234, 0.6)',
                line=dict(color='#667eea', width=2),
                symbol='diamond'
            ),
            hovertemplate='<b>%{x}</b><br>Efficiency: %{text}<extra></extra>',
            text=season_data['Efficiency'].apply(lambda x: f'{x:.2f}')
        ),
        secondary_y=False
    )
    
    # Update layout
    fig.update_xaxes(
        title_text="Crops",
        tickangle=45,
        tickfont=dict(size=12, color='#2c3e50')
    )
    
    fig.update_yaxes(
        title_text="<b>Yield (kg/ha)</b>",
        secondary_y=False,
        tickfont=dict(color='#2c3e50')
    )
    
    fig.update_yaxes(
        title_text="<b>Production (Lakh Tonnes)</b>",
        secondary_y=True,
        tickfont=dict(color='#f5576c')
    )
    
    fig.update_layout(
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        margin=dict(t=80, b=100, l=60, r=60),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1
        ),
        annotations=[
            dict(
                text="💡 Larger diamonds indicate higher efficiency (Yield/Area ratio)",
                showarrow=False,
                x=0.5,
                y=-0.15,
                xref="paper",
                yref="paper",
                font=dict(size=10, color='#666'),
                align="center"
            )
        ]
    )
    
    return fig

def create_productivity_radar_chart(df, crops_list, season):
    """Create radar chart for crop productivity comparison"""
    if df.empty or season not in df['Season'].values:
        return create_empty_chart("No data available")
    
    season_data = df[df['Season'] == season]
    metrics = ['Yield', 'Production', 'Area']
    
    fig = go.Figure()
    
    colors = ['#667eea', '#4ecdc4', '#f093fb', '#4facfe', '#feca57']
    
    for i, crop in enumerate(crops_list[:5]):  # Limit to 5 crops for clarity
        if crop in season_data['Crop'].values:
            crop_metrics = season_data[season_data['Crop'] == crop][metrics].mean()
            
            # Normalize values (0-100 scale)
            normalized_values = []
            for metric in metrics:
                max_val = season_data[metric].max()
                min_val = season_data[metric].min()
                if max_val > min_val:
                    norm_val = ((crop_metrics[metric] - min_val) / (max_val - min_val)) * 100
                else:
                    norm_val = 50
                normalized_values.append(norm_val)
            
            fig.add_trace(go.Scatterpolar(
                r=normalized_values + [normalized_values[0]],  # Close the polygon
                theta=metrics + [metrics[0]],
                fill='toself',
                name=crop,
                line=dict(color=colors[i % len(colors)]),
                fillcolor=f'rgba({",".join(map(str, px.colors.hex_to_rgb(colors[i % len(colors)])))}, 0.1)'
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10)
            )
        ),
        title=dict(
            text=f'📊 Crop Performance Radar - {season} Season',
            font=dict(size=16, color='#2c3e50'),
            x=0.5
        ),
        template='plotly_white',
        font=dict(family="Inter"),
        margin=dict(t=60, b=40, l=40, r=40)
    )
    
    return fig

def create_correlation_heatmap(df):
    """Create correlation heatmap for agricultural metrics"""
    if df.empty:
        return create_empty_chart("No data available")
    
    # Select numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) < 2:
        return create_empty_chart("Insufficient numeric data")
    
    corr_matrix = df[numeric_cols].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False,
        hovertemplate='<b>%{x} vs %{y}</b><br>Correlation: %{z:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text='🔗 Agricultural Metrics Correlation Matrix',
            font=dict(size=16, color='#2c3e50'),
            x=0.5
        ),
        template='plotly_white',
        font=dict(family="Inter"),
        margin=dict(t=60, b=40, l=40, r=40),
        width=500,
        height=500
    )
    
    return fig

def create_empty_chart(message="No data available"):
    """Create an empty chart with a message"""
    fig = go.Figure()
    
    fig.add_annotation(
        text=f"📊<br>{message}",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color='#666'),
        align="center"
    )
    
    fig.update_layout(
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        margin=dict(t=40, b=40, l=40, r=40)
    )
    
    return fig

# Legacy function names for backward compatibility
def create_trend_chart(df, crop, metric):
    """Backward compatibility wrapper"""
    return create_enhanced_trend_chart(df, crop, metric)

def create_comparison_chart(df, season):
    """Backward compatibility wrapper"""
    return create_enhanced_comparison_chart(df, season)