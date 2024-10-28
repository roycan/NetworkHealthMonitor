import re

def validate_ip(ip_address):
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip_address):
        return False
    
    octets = ip_address.split('.')
    return all(0 <= int(octet) <= 255 for octet in octets)

def format_response_time(response_time):
    if response_time < 0:
        return "Timeout"
    return f"{response_time*1000:.1f} ms"

def calculate_uptime(history):
    if not history:
        return 0
    total = len(history)
    up = sum(1 for record in history if record['status'])
    return (up / total) * 100
