import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

def create_response_time_chart(history):
    times = [record['timestamp'] for record in history]
    response_times = [
        record['response_time'] if record['response_time'] >= 0 else None 
        for record in history
    ]
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=times,
            y=response_times,
            mode='lines+markers',
            name='Response Time',
            line=dict(color='#2E86C1')
        )
    )
    
    fig.update_layout(
        title='Response Time History',
        xaxis_title='Time',
        yaxis_title='Response Time (s)',
        height=300,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

def create_status_chart(history):
    times = [record['timestamp'] for record in history]
    status = [1 if record['status'] else 0 for record in history]
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=times,
            y=status,
            mode='lines',
            name='Status',
            line=dict(color='#27AE60'),
            fill='tozeroy'
        )
    )
    
    fig.update_layout(
        title='Status History',
        xaxis_title='Time',
        yaxis_title='Status',
        yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['Down', 'Up']),
        height=300,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig
