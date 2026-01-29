#git add .
#git commit -m "Python Change 2"
#git push origin main

from flask import Flask, request, render_template_string, redirect, url_for, session, send_file
from datetime import datetime
import os
from zoneinfo import ZoneInfo
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from openpyxl import Workbook
from datetime import datetime
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError
from zoneinfo import ZoneInfo
from datetime import datetime

app = Flask(__name__)
app.secret_key = '9f3e8c2b5d7a4f9cbb8e1d0a3f7c6e4520d93f4a1b6c7e8d9f1a2b3c4d5e6f7a'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_EDkMvy5q7PcV@ep-delicate-art-a2qhgk2m-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_ZhAg3xEcs1dB@ep-wandering-smoke-agbn8re8-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "poolclass": QueuePool,
    "pool_pre_ping": True,      # Checks if connection is alive before using
    "pool_recycle": 280,        # Recycles connections after ~5 min idle
    "pool_timeout": 30          # Wait up to 30 sec for a free connection
}

db = SQLAlchemy(app)

USERS = {
    "NEX ADMIN":{"password": "Admin@379", "role": "admin"},
    "Holfontein Diesel": {"password":"Diesel@149", "role": "user"}
}

### DATABASE MODELS ###
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' or 'user'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class FuelLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    site = db.Column(db.String(50), nullable=False)
    vehicle = db.Column(db.String(100), nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    odometer = db.Column(db.Float, nullable=False)
    start_reading = db.Column(db.Float, nullable=False)
    end_reading = db.Column(db.Float, nullable=False)
    pumped = db.Column(db.Float, nullable=False)
    consumption = db.Column(db.Float, nullable=True)   # km per litre


HTML_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Fuel Log Entry</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-size: 20px;             /* Larger base font size */
            font-family: Arial, sans-serif;
            padding: 30px;
            max-width: 700px;            /* Wider container */
            margin: auto;
        }
        label {
            display: block;
            margin-top: 25px;
            font-weight: bold;
        }
        input, textarea {
            width: 100%;
            padding: 20px 20px;          /* Bigger padding */
            font-size: 22px;             /* Bigger font */
            box-sizing: border-box;
            border-radius: 30px;
            border: 2px solid #ccc;
        }
        textarea {
            height: 100px;               /* Taller textarea */
        }
        button {
            margin-top: 30px;
            padding: 70px;
            font-size: 28px;             /* Bigger button text */
            width: 100%;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #45a049;
        }
        .result {
            font-weight: bold;
            margin-top: 26px;
            font-size: 26px;             /* Larger pumped display */
        }
        img.logo {
            max-width: 200px;
            display: block;
            margin: 0 auto 20px auto;
        }
        .logout {
            position: absolute;
            top: 20px;
            right: 30px;
            font-size: 18px;
        }
        .logout a {
            text-decoration: none;
            color: red;
            font-weight: bold;
        }
        .logout a:hover {
            text-decoration: underline;
        }

        select {
            width: 100%;
            padding: 20px;
            font-size: 22px;
            border-radius: 12px;
            border: 2px solid #ccc;
            margin-top: 15px;
            appearance: none;
            background-color: #fff;
        }

        select option {
            font-size: 22px;
            padding: 10px;
        }
        
    </style>

    <script>
        function calculateEnd() {
            var start = parseFloat(document.getElementById('start').value) || 0;
            var pumped = parseFloat(document.getElementById('pumped_input').value) || 0;
            var end = start + pumped;
            document.getElementById('calculated_end').textContent = end.toFixed(2);
        }
    </script>
</head>
<body>
    <img class="logo" src="/static/logo.png" alt="Logo">
    <h2>⛽ Fuel Log Entry</h2>
    <form method="POST" enctype="multipart/form-data">
        <!-- Site Dropdown -->
        <label for="site">Select Organisation:</label>
        <select id="site" name="site" onchange="toggleVehicleField()" required>
            <option value="">--Select Site--</option>
            <option value="Holfontein" {% if site == 'Holfontein' %}selected{% endif %}>Holfontein</option>
            <option value="Plank" {% if site == 'Plank' %}selected{% endif %}>Plank</option>
            <option value="Abantu" {% if site == 'Abantu' %}selected{% endif %}>Abantu</option>
            <option value="Edwin Carriers" {% if site == 'Edwin Carriers' %}selected{% endif %}>Edwin Carriers</option>
            <option value="CBI" {% if site == 'CBI' %}selected{% endif %}>CBI</option>
        </select>

        <!-- Holfontein Vehicle Dropdown -->
        <div id="vehicle_dropdown" style="display:none;">
            <label for="vehicle_select">Vehicle:</label>
            <select id="vehicle_select" name="vehicle_select">
                <option value="">--Select Vehicle--</option>
                <option {% if vehicle_select == 'Geni 1' %}selected{% endif %}>Geni 1</option>
                <option {% if vehicle_select == 'Geni 2' %}selected{% endif %}>Geni 2</option>
                <option {% if vehicle_select == 'Geni3 Hopper' %}selected{% endif %}>Geni3 Hopper</option>
                <option {% if vehicle_select == 'Geni4 Color Sorter' %}selected{% endif %}>Geni4 Color Sorter</option>
                <option value="Landini KY63 NP GP" {% if vehicle_select == 'Landini KY63 NP GP' %}selected{% endif %}>Landini KY63 NP GP</option>
                <option value="Landini KY63 PR GP" {% if vehicle_select == 'Landini KY63 PR GP' %}selected{% endif %}>Landini KY63 PR GP</option>
                <option value="Landini KY63 LK GP" {% if vehicle_select == 'Landini KY63 LK GP' %}selected{% endif %}>Landini KY63 LK GP</option>
                <option value="Landini KY63 MR GP" {% if vehicle_select == 'Landini KY63 MR GP' %}selected{% endif %}>Landini KY63 MR GP</option>
                <option value="Landini Hire" {% if vehicle_select == 'Landini Hire' %}selected{% endif %}>Landini Hire</option>
                <option {% if vehicle_select == 'Mahindra Bakkie' %}selected{% endif %}>Mahindra Bakkie</option>
                <option {% if vehicle_select == 'MF DHS856FS' %}selected{% endif %}>MF DHS856FS</option>
                <option {% if vehicle_select == 'MF DHS872FS' %}selected{% endif %}>MF DHS872FS</option>
                <option {% if vehicle_select == 'MF DHS879FS' %}selected{% endif %}>MF DHS879FS</option>
                <option {% if vehicle_select == 'MF DHS885FS' %}selected{% endif %}>MF DHS885FS</option>
                <option {% if vehicle_select == 'Forklift F1' %}selected{% endif %}>Forklift F1</option>
            </select>
        </div>

        <!-- Plank Vehicle Text Input -->
        <div id="vehicle_input" style="display:none;">
            <label for="vehicle_text">Vehicle:</label>
            <input id="vehicle_text" name="vehicle_text" type="text">
        </div>

        <script>
        function toggleVehicleField() {
            var site = document.getElementById("site").value;
            var vehicleDropdown = document.getElementById("vehicle_dropdown");
            var vehicleInput = document.getElementById("vehicle_input");
            var vehicleSelect = document.getElementById("vehicle_select");
            var vehicleText = document.getElementById("vehicle_text");

            if (site === "Holfontein") {
                vehicleDropdown.style.display = "block";
                vehicleInput.style.display = "none";

                vehicleSelect.setAttribute("required", "true");
                vehicleText.removeAttribute("required");

            } else if (["Plank", "Abantu", "Edwin Carriers","CBI"].includes(site)) {
                vehicleDropdown.style.display = "none";
                vehicleInput.style.display = "block";

                vehicleText.setAttribute("required", "true");
                vehicleSelect.removeAttribute("required");

            } else {
                vehicleDropdown.style.display = "none";
                vehicleInput.style.display = "none";

                vehicleSelect.removeAttribute("required");
                vehicleText.removeAttribute("required");
            }
        }

        // ✅ Run on page load to restore state after error
        document.addEventListener("DOMContentLoaded", toggleVehicleField);
        </script>


        <label for="driver_name">Driver Name:</label>
        <input id="driver_name" name="driver_name" type="text" value="{{ driver_name | default('') }}" required>

        <label for="odometer">Vehicle Odometer:</label>
        <input id="odometer" name="odometer" type="number" step="0.1" min="1" 
            value="{{ odometer | default('') }}" required>
        {% if error_odometer %}
        <div style="color:red; font-size:18px; font-weight:bold; margin-top:5px;">
            {{ error_odometer }}
        </div>
        {% endif %}


        <label for="start">Pump Start Reading:</label>
        <input id="start" name="start" type="number" step="0.1" min="1" 
            value="{{ start | default('') }}" required oninput="calculateEnd()">
        {% if error_start %}
        <div style="color:red; font-size:18px; font-weight:bold; margin-top:5px;">
            {{ error_start }}
        </div>
        {% endif %}


        <label for="pumped_input">Pumped (Litres):</label>
        <input id="pumped_input" name="pumped" type="number" step="0.1" min="1" value="{{ pumped | default('') }}" required oninput="calculateEnd()">

        <div class="result">End Reading: <span id="calculated_end">0.00</span></div>

        <button type="submit">Log Fuel</button>
        </form>

        {% if session.get('role') == 'admin' %}
        <form method="POST" action="/clear_db" onsubmit="return confirm('Are you sure you want to clear all records?');" style="margin-bottom: 20px;">
            <button type="submit" style="background-color: #d9534f;">⚠️ Clear All Records (Admin Only)</button>
        </form>
        {% endif %}
    
    <div class="logout"><a href="/logout">Logout</a></div>
    <a href="/download" style="display:block; margin-top: 20px; font-size:18px;">⬇️ Download Fuel Log Excel</a>
    
    {% if success %}
    <script>
        // Show success popup
        alert("{{ success }}");
    </script>
    {% endif %}

</body>
</html>
'''

LOGIN_FORM = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">  <!-- ✅ Important for mobile scaling -->
    <style>
        body {
            font-size: 22px;
            font-family: Arial, sans-serif;
            padding: 20px;
            margin: 0;
            background-color: #f9f9f9;
        }
        .container {
            max-width: 500px;
            margin: auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        label {
            display: block;
            margin-top: 20px;
        }
        input {
            width: 100%;
            padding: 15px;
            font-size: 22px;
            box-sizing: border-box;
            border: 1.5px solid #ccc;
            border-radius: 6px;
        }
        button {
            margin-top: 30px;
            padding: 18px;
            font-size: 24px;
            width: 100%;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0069d9;
        }
        .error {
            color: red;
            margin-top: 20px;
            font-size: 20px;
        }
        img.logo {
            max-width: 200px;
            display: block;
            margin: 0 auto 20px auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <img class="logo" src="/static/logo.png" alt="Logo">
        <h2>🔐 Login</h2>
        <form method="POST">
            <label for="username">Username:</label>
            <input id="username" name="username" required autofocus>

            <label for="password">Password:</label>
            <input id="password" name="password" type="password" required>
            <input type="checkbox" onclick="togglePassword()"> Show Password

            <script>
            function togglePassword() {
                var pass = document.getElementById("password");
                pass.type = (pass.type === "password") ? "text" : "password";
            }
            </script>


            <button type="submit">Login</button>
        </form>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = USERS.get(username)
        if user and user['password'] == password:
            session['logged_in'] = True
            session['username'] = username
            session['role'] = user['role']   # store role in session
            return redirect(url_for('log_fuel'))
        else:
            error = "Invalid username or password"
    return render_template_string(LOGIN_FORM, error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def log_fuel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Separate errors
    error_odometer = None
    error_start = None
    success = None

    if request.method == 'POST':
        site = request.form.get('site')

        # Determine vehicle field based on site
        if site == "Holfontein":
            vehicle = request.form.get('vehicle_select')
        elif site in ["Plank", "Abantu", "Edwin Carriers","CBI"]:
            vehicle = request.form.get('vehicle_text')
        else:
            error_start = "❌ Invalid site selected."
            return render_template_string(HTML_FORM, error_start=error_start)

        driver_name = request.form.get('driver_name')
        odometer = round(float(request.form.get('odometer', 0)), 1)
        start = round(float(request.form.get('start', 0)), 1)
        pumped = round(float(request.form.get('pumped', 0)), 1)
        end = round(start + pumped, 1)

        # 🚗 Holfontein odometer validation
        if site == "Holfontein":
            last_vehicle_entry = (
                FuelLog.query
                .filter(FuelLog.site == "Holfontein", FuelLog.vehicle == vehicle)
                .order_by(FuelLog.timestamp.desc())
                .first()
            )
            if last_vehicle_entry and odometer <= last_vehicle_entry.odometer:
                error_odometer = (
                    f"❌ Odometer reading ({odometer}) must be greater than "
                    f"last reading for this vehicle."
                )
                return render_template_string(
                    HTML_FORM,
                    error_odometer=error_odometer,
                    error_start=None,
                    site=site,
                    vehicle_select=vehicle,
                    driver_name=driver_name,
                    odometer=odometer,
                    start=start,
                    pumped=pumped
                )

        # 🛢 Pump start reading validation (last overall entry)
        last_entry = FuelLog.query.order_by(FuelLog.timestamp.desc()).first()
        if last_entry:
            expected_start = round(last_entry.end_reading, 2)
            if round(start, 2) != expected_start:
                error_start = (
                    f"❌ Start Reading ({start}) does NOT match previous End Reading "
                    
                )
                return render_template_string(
                    HTML_FORM,
                    error_odometer=None,
                    error_start=error_start,
                    site=site,
                    vehicle_select=vehicle if site == "Holfontein" else "",
                    driver_name=driver_name,
                    odometer=odometer,
                    start=start,
                    pumped=pumped
                )
            
        # 🛢 Pump start reading validation
        # last_entry = FuelLog.query.order_by(FuelLog.timestamp.desc()).first()

        # 🚗 Holfontein odometer validation
        if site == "Holfontein":
            last_vehicle_entry = (
                FuelLog.query
                .filter(FuelLog.site == "Holfontein", FuelLog.vehicle == vehicle)
                .order_by(FuelLog.timestamp.desc())
                .first()
            )

            if last_vehicle_entry and odometer <= last_vehicle_entry.odometer:
                error_odometer = (
                    f"❌ Odometer reading ({odometer}) must be greater than "
                    f"last reading."
                )
                return (...)

        # ➕ NEW: Consumption calculation
        if site == "Holfontein" and last_vehicle_entry:
            consumption = round((odometer - last_vehicle_entry.odometer) / pumped, 2)
        else:
            consumption = None


        # ✅ Insert only if validation passed
        tz = ZoneInfo("Africa/Johannesburg")
        timestamp = datetime.now(tz).replace(tzinfo=None)
        new_entry = FuelLog(
            timestamp=timestamp,
            site=site,
            vehicle=vehicle,
            driver_name=driver_name,
            odometer=odometer,
            start_reading=start,
            end_reading=end,
            pumped=pumped,
            consumption=consumption
        )

        # 🔄 Safe DB commit with retry
        try:
            db.session.add(new_entry)
            db.session.commit()
        except OperationalError:
            db.session.rollback()
            try:
                db.session.add(new_entry)
                db.session.commit()
            except OperationalError as e:
                error_start = f"⚠️ Database error: {str(e)}. Please try again."
                return render_template_string(
                    HTML_FORM,
                    error_odometer=None,
                    error_start=error_start,
                    site=site,
                    vehicle_select=vehicle if site == "Holfontein" else "",
                    driver_name=driver_name,
                    odometer=odometer,
                    start=start,
                    pumped=pumped,
                    consumption=consumption
                )

        success = "✅ Fuel log added successfully!"

    return render_template_string(
        HTML_FORM,
        error_odometer=error_odometer,
        error_start=error_start,
        success=success
    )






@app.route('/clear_db', methods=['POST'])
def clear_db():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return "Unauthorized", 403

    # Delete all rows from FuelLog table
    FuelLog.query.delete()
    db.session.commit()
    return redirect(url_for('log_fuel'))

@app.route('/download')
def download():
    entries = FuelLog.query.order_by(FuelLog.timestamp.asc()).all()
    if not entries:
        return "No data to download yet.", 404

    wb = Workbook()
    ws = wb.active
    ws.title = "Fuel Log"
    ws.append(['Timestamp', 'Site', 'Vehicle', 'Driver Name', 'Odometer', 'Start', 'End', 'Pumped', 'Consumption (km/l|h/l)'])
    for e in entries:
        ws.append([
            e.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            e.site,
            e.vehicle,
            e.driver_name,
            round(e.odometer, 1) if e.odometer is not None else '',
            round(e.start_reading, 1) if e.start_reading is not None else '',
            round(e.end_reading, 1) if e.end_reading is not None else '',
            round(e.pumped, 1) if e.pumped is not None else '',
            round(e.consumption, 2) if e.consumption is not None else ''
        ])

    today = datetime.today().strftime("%Y-%m-%d")
    file_path = f"Holfontein Diesel {today}.xlsx"
    wb.save(file_path)
    return send_file(file_path, as_attachment=True)

### Initialize DB ###
with app.app_context():
    db.create_all()
    # Ensure at least one admin exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='admin')
        admin.set_password('Admin123')  # Default password
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
    