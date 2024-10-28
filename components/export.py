import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import io

def export_device_data_csv(database, device_id, hours=24):
    # Get device details
    device = next((d for d in database.get_devices() if d['id'] == device_id), None)
    if not device:
        return None
    
    # Get monitoring data
    history = database.get_device_history(device_id, limit=None)
    df = pd.DataFrame(history)
    
    # Format the data
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Select relevant columns
    columns = ['timestamp', 'response_time', 'status', 'min_rtt', 'max_rtt', 
              'avg_rtt', 'jitter', 'packet_loss', 'threshold_violations']
    df = df[columns]
    
    # Create CSV in memory
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

def export_device_report_pdf(database, device_id, hours=24):
    # Get device details
    device = next((d for d in database.get_devices() if d['id'] == device_id), None)
    if not device:
        return None
    
    # Create PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title = Paragraph(f"Network Monitoring Report - {device['ip_address']}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Device Information
    device_info = [
        ["Device Information", ""],
        ["IP Address", device['ip_address']],
        ["Description", device['description']],
        ["Device Type", device['device_type']],
        ["Tags", ", ".join(device['tags'])],
    ]
    
    device_table = Table(device_info, colWidths=[200, 300])
    device_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    elements.append(device_table)
    elements.append(Spacer(1, 20))
    
    # Performance Metrics
    history = database.get_device_history(device_id, limit=24)  # Last 24 records
    if history:
        latest = history[0]
        metrics_data = [
            ["Current Performance Metrics", "", "", ""],
            ["Metric", "Current Value", "Threshold", "Status"],
            ["Response Time", f"{latest['response_time']*1000:.1f} ms", 
             f"{device['response_time_threshold']*1000:.1f} ms" if device['response_time_threshold'] else "N/A",
             "⚠️" if 'response_time' in latest['threshold_violations'] else "✓"],
            ["Packet Loss", f"{latest['packet_loss']:.1f}%",
             f"{device['packet_loss_threshold']:.1f}%" if device['packet_loss_threshold'] else "N/A",
             "⚠️" if 'packet_loss' in latest['threshold_violations'] else "✓"],
            ["Jitter", f"{latest['jitter']*1000:.1f} ms",
             f"{device['jitter_threshold']*1000:.1f} ms" if device['jitter_threshold'] else "N/A",
             "⚠️" if 'jitter' in latest['threshold_violations'] else "✓"],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[150, 150, 150, 50])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 12),
            ('BACKGROUND', (0, 2), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 2), (-1, -1), colors.black),
            ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 2), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        elements.append(metrics_table)
    
    # Generate PDF
    doc.build(elements)
    return buffer.getvalue()
