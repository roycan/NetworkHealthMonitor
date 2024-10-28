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

def create_detailed_metrics_chart(history, device):
    times = [record['timestamp'] for record in history]
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'RTT Metrics', 'Jitter',
            'Packet Loss', 'Moving Averages'
        )
    )
    
    # RTT Metrics
    fig.add_trace(
        go.Scatter(x=times, y=[r['min_rtt'] if r['min_rtt'] >= 0 else None for r in history],
                  name='Min RTT', line=dict(color='#2ECC71')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=times, y=[r['max_rtt'] if r['max_rtt'] >= 0 else None for r in history],
                  name='Max RTT', line=dict(color='#E74C3C')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=times, y=[r['avg_rtt'] if r['avg_rtt'] >= 0 else None for r in history],
                  name='Avg RTT', line=dict(color='#3498DB')),
        row=1, col=1
    )
    
    # Add response time threshold line if set
    if device['response_time_threshold']:
        fig.add_hline(
            y=device['response_time_threshold'],
            line_dash="dash",
            line_color="red",
            annotation_text="Threshold",
            row=1, col=1
        )
    
    # Jitter
    fig.add_trace(
        go.Scatter(x=times, y=[r['jitter'] if r['jitter'] >= 0 else None for r in history],
                  name='Jitter', line=dict(color='#9B59B6')),
        row=1, col=2
    )
    
    # Add jitter threshold line if set
    if device['jitter_threshold']:
        fig.add_hline(
            y=device['jitter_threshold'],
            line_dash="dash",
            line_color="red",
            annotation_text="Threshold",
            row=1, col=2
        )
    
    # Packet Loss
    fig.add_trace(
        go.Scatter(x=times, y=[r['packet_loss'] for r in history],
                  name='Packet Loss %', line=dict(color='#E67E22')),
        row=2, col=1
    )
    
    # Add packet loss threshold line if set
    if device['packet_loss_threshold']:
        fig.add_hline(
            y=device['packet_loss_threshold'],
            line_dash="dash",
            line_color="red",
            annotation_text="Threshold",
            row=2, col=1
        )
    
    # Moving Averages
    response_times = [r['response_time'] if r['response_time'] >= 0 else None for r in history]
    window = 5
    ma = []
    for i in range(len(response_times)):
        window_slice = [x for x in response_times[max(0, i-window+1):i+1] if x is not None]
        if window_slice:
            ma.append(sum(window_slice) / len(window_slice))
        else:
            ma.append(None)
    
    fig.add_trace(
        go.Scatter(x=times, y=ma,
                  name=f'{window}-point MA', line=dict(color='#F1C40F')),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

def create_trend_chart(trends):
    times = [record['time_bucket'] for record in trends]
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Average Response Time', 'Average Packet Loss',
            'Average Jitter', 'Availability'
        )
    )
    
    # Average Response Time
    fig.add_trace(
        go.Scatter(x=times, y=[r['avg_response_time'] for r in trends],
                  name='Avg Response Time', line=dict(color='#3498DB')),
        row=1, col=1
    )
    
    # Average Packet Loss
    fig.add_trace(
        go.Scatter(x=times, y=[r['avg_packet_loss'] for r in trends],
                  name='Avg Packet Loss', line=dict(color='#E67E22')),
        row=1, col=2
    )
    
    # Average Jitter
    fig.add_trace(
        go.Scatter(x=times, y=[r['avg_jitter'] for r in trends],
                  name='Avg Jitter', line=dict(color='#9B59B6')),
        row=2, col=1
    )
    
    # Availability
    fig.add_trace(
        go.Scatter(x=times, y=[r['availability'] for r in trends],
                  name='Availability %', line=dict(color='#2ECC71')),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig
