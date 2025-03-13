import random
import time
import socket  # For detecting local IP
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'  # Replace with a secure, random key in production

###############################################################################
#                            IN-MEMORY STORAGE
###############################################################################
# For demonstration. In production, replace with a database.

approved_users = {
    "admin": "admin"  # Basic admin user
}
pending_users = {}

store_items = [
    {
        "id": 1,
        "name": "Bot Access Token",
        "unit_price": 9.99,
        "quantity": 10,
        "description": "Access for advanced bot features."
    },
    {
        "id": 2,
        "name": "VIP Server Upgrade",
        "unit_price": 19.99,
        "quantity": 5,
        "description": "Premium server performance upgrade."
    }
]
next_item_id = 3

# Basic server status (fake example)
server_info = {
    "Server 1": "Up",
    "Server 2": "Up",
    "Server 3": "Down"
}

# In-memory list of servers, so we can add new ones from admin page.
servers = []
next_server_id = 1

###############################################################################
#                               AUTH & USERS
###############################################################################

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Simple check
        if username in approved_users and approved_users[username] == password:
            session['logged_in'] = True
            session['username'] = username
            session['is_admin'] = (username == 'admin')
            return redirect(url_for('dashboard'))
        else:
            error_msg = "Invalid credentials or account not approved."
            return render_template('login.html', error=error_msg)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in approved_users or username in pending_users:
            return render_template('register.html', error="Username already exists.")
        
        # Add new user to pending list
        pending_users[username] = password
        return render_template('register.html', success="Account created; pending admin approval.")
    return render_template('register.html')

###############################################################################
#                               MAIN PAGES
###############################################################################

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Example data for the dashboard
    data = {
        "bots_online": 5,
        "bots_offline": 2,
        "servers_up": 3,
        "servers_down": 1
    }
    return render_template('dashboard.html', data=data)

@app.route('/store')
def store():
    # Public store page
    return render_template('store.html', products=store_items)

###############################################################################
#                           ADMIN: MAIN PANEL
###############################################################################

@app.route('/admin')
def admin_panel():
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))
    return render_template('admin.html', server_info=server_info)

###############################################################################
#                           ADMIN: STORE MGMT
###############################################################################

@app.route('/admin/store', methods=['GET', 'POST'])
def admin_store():
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))

    global next_item_id

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'add_item':
            # Create new store item
            item_name = request.form.get('item_name')
            item_unit_price = request.form.get('item_unit_price')
            item_quantity = request.form.get('item_quantity')
            item_desc = request.form.get('item_desc', '')

            if item_name and item_unit_price and item_quantity:
                try:
                    unit_price = float(item_unit_price)
                    quantity = int(item_quantity)
                except ValueError:
                    # Invalid numeric input
                    pass
                else:
                    new_item = {
                        "id": next_item_id,
                        "name": item_name,
                        "unit_price": unit_price,
                        "quantity": quantity,
                        "description": item_desc
                    }
                    store_items.append(new_item)
                    next_item_id += 1
            return redirect(url_for('admin_store'))

        elif form_type == 'remove_item':
            item_id_str = request.form.get('item_id')
            if item_id_str:
                try:
                    item_id = int(item_id_str)
                    for item in store_items:
                        if item['id'] == item_id:
                            store_items.remove(item)
                            break
                except ValueError:
                    pass
            return redirect(url_for('admin_store'))

    return render_template('admin_store.html', products=store_items)

###############################################################################
#                          ADMIN: USER MGMT
###############################################################################

@app.route('/admin/users', methods=['GET', 'POST'])
def admin_users():
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'approve_accounts':
            selected_accounts = request.form.getlist('pending_users')
            for user in selected_accounts:
                if user in pending_users:
                    # Move from pending to approved
                    approved_users[user] = pending_users[user]
                    del pending_users[user]
            return redirect(url_for('admin_users'))

    return render_template('admin_users.html',
                           approved_users=approved_users,
                           pending_users=pending_users)

###############################################################################
#                           ADMIN: SERVER MGMT
###############################################################################

@app.route('/admin/servers', methods=['GET', 'POST'])
def admin_servers():
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))

    global next_server_id

    if request.method == 'POST':
        ip = request.form.get('ip')
        port_str = request.form.get('port')
        login_user = request.form.get('login_user')
        login_pass = request.form.get('login_pass')

        # Basic parse for port
        try:
            port = int(port_str)
        except ValueError:
            port = 80

        servers.append({
            "id": next_server_id,
            "ip": ip,
            "port": port,
            "login_user": login_user,
            "login_pass": login_pass
        })
        next_server_id += 1
        return redirect(url_for('admin_servers'))

    return render_template('admin_servers.html', servers=servers)

###############################################################################
#                          API ROUTE: SERVERS
###############################################################################

@app.route('/api/servers')
def servers_api():
    """
    Returns JSON list of servers for the bot script to consume.
    In production, secure this route properly.
    """
    return jsonify(servers)

###############################################################################
#                        IP DETECTION & FLASK RUN
###############################################################################

def get_local_ip():
    """
    Returns the local IP address of this computer by attempting a connection
    to a well-known address (Google DNS), then reading which IP is used.
    This helps us avoid defaulting to 127.0.0.1 on Windows.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        # Fallback if detection fails
        return "127.0.0.1"

if __name__ == '__main__':
    # Force Flask to bind to your Hamachi IP
    app.run(host='0.0.0.0', port=5000, debug=True)

