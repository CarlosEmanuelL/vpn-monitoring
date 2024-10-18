from flask import Blueprint, render_template
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def monitor():
    log_file = '/app/openvpn-status/openvpn-status.log'
    users = []
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            for line in file:
                if 'CLIENT_LIST' in line:
                    data = line.split(',')
                    users.append({
                        'user': data[1],
                        'ip': data[2],
                        'connected_since': data[6]
                    })
    
    return render_template('monitor.html', users=users)
