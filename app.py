#git add .
#git commit -m "Python Change 2"
#git push origin main

from flask import Flask, request, render_template_string, redirect, url_for, session, send_file
from datetime import datetime
import os
import csv
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime
from zoneinfo import ZoneInfo
import os
from openpyxl.utils.dataframe import dataframe_to_rows



app = Flask(__name__)
app.secret_key = '9f3e8c2b5d7a4f9cbb8e1d0a3f7c6e4520d93f4a1b6c7e8d9f1a2b3c4d5e6f7a'


USERNAME = 'Marnus'
PASSWORD = 'NEX@test149'  # Change this!

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'fuel_log.csv')
EXCEL_FILE = os.path.join(BASE_DIR, 'fuel_log.xlsx')

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')    # Absolute path for uploads
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        <label for="site">Select Site:</label>
        <select id="site" name="site" onchange="toggleVehicleField()" required>
            <option value="">--Select Site--</option>
            <option value="Holfontein" {% if site == 'Holfontein' %}selected{% endif %}>Holfontein</option>
            <option value="Plank" {% if site == 'Plank' %}selected{% endif %}>Plank</option>
        </select>

        <!-- Holfontein Vehicle Dropdown -->
        <div id="vehicle_dropdown" style="display:none;">
            <label for="vehicle_select">Vehicle:</label>
            <select id="vehicle_select" name="vehicle_select">
                <option value="">--Select Vehicle--</option>
                <option {% if vehicle_select == 'Geni 1' %}selected{% endif %}>Geni 1</option>
                <option {% if vehicle_select == 'Geni 2' %}selected{% endif %}>Geni 2</option>
                <option {% if vehicle_select == 'Geni3 Hopper' %}selected{% endif %}>Geni3 Hopper</option>
                <option {% if vehicle_select == 'Landini 1' %}selected{% endif %}>Landini 1</option>
                <option {% if vehicle_select == 'Landini 2' %}selected{% endif %}>Landini 2</option>
                <option {% if vehicle_select == 'Landini 3' %}selected{% endif %}>Landini 3</option>
                <option {% if vehicle_select == 'Landini 4' %}selected{% endif %}>Landini 4</option>
                <option {% if vehicle_select == 'Landini 5' %}selected{% endif %}>Landini 5</option>
                <option {% if vehicle_select == 'Mahindra Bakkie' %}selected{% endif %}>Mahindra Bakkie</option>
                <option {% if vehicle_select == 'MF DHS856FS' %}selected{% endif %}>MF DHS856FS</option>
                <option {% if vehicle_select == 'MF DHS872FS' %}selected{% endif %}>MF DHS872FS</option>
                <option {% if vehicle_select == 'MF DHS879FS' %}selected{% endif %}>MF DHS879FS</option>
                <option {% if vehicle_select == 'MF DHS885FS' %}selected{% endif %}>MF DHS885FS</option>
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

            } else if (site === "Plank") {
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
        <input id="odometer" name="odometer" type="number" step="0.1" min="1" value="{{ odometer | default('') }}" required>


        <label for="start">Pump Start Reading:</label>
        <input id="start" name="start" type="number" step="0.1" min="1" value="{{ start | default('') }}" required oninput="calculateEnd()">
        {% if error %}
        <div style="color:red; font-size:18px; font-weight:bold; margin-top:5px;">{{ error }}</div>
        {% endif %}


        <label for="pumped_input">Pumped (Litres):</label>
        <input id="pumped_input" name="pumped" type="number" step="0.1" min="1" value="{{ pumped | default('') }}" required oninput="calculateEnd()">

        <div class="result">End Reading: <span id="calculated_end">0.00</span></div>

        <button type="submit">Log Fuel</button>
    </form>
    <div class="logout"><a href="/logout">Logout</a></div>
    <a href="/download" style="display:block; margin-top: 20px; font-size:18px;">⬇️ Download Fuel Log Excel</a>

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

def write_to_csv(timestamp, site, vehicle, driver_name, odometer, start, end, pumped):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Timestamp', 'Site', 'Vehicle', 'Driver Name', 'Odometer', 'Start Reading', 'End Reading', 'Pumped'])
        writer.writerow([timestamp, site, vehicle, driver_name, odometer, start, end, pumped])




def get_last_readings():
    if not os.path.exists(CSV_FILE):
        return None
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return None
    last_row = df.iloc[-1]
    last_start = float(last_row['Start Reading'])
    last_end = float(last_row['End Reading'])
    return last_start, last_end


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('log_fuel'))
        else:
            error = "Invalid username or password"
    return render_template_string(LOGIN_FORM, error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def log_fuel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Existing form fields
        site = request.form.get('site')
        driver_name = request.form.get('driver_name')
        odometer = float(request.form.get('odometer'))
        start = float(request.form.get('start'))
        pumped = float(request.form.get('pumped'))
        end = start + pumped
        tz = ZoneInfo("Africa/Johannesburg")  # or your local timezone
        timestamp = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')

        # Vehicle logic
        vehicle = request.form.get('vehicle_text') if site == "Plank" else request.form.get('vehicle_select')

        # ✅ Validate previous reading
        previous = get_last_readings()
        if previous:
            _, prev_end = previous
            if round(start, 1) != round(prev_end, 1):
                error = f"❌ Invalid entry: Start reading ({start:.1f}) must equal previous end reading ({prev_end:.1f})."
                return render_template_string(
                    HTML_FORM,
                    error=error,
                    site=site,
                    vehicle_text=request.form.get('vehicle_text', ''),
                    vehicle_select=request.form.get('vehicle_select', ''),
                    driver_name=driver_name,
                    odometer=odometer,
                    start=start,
                    pumped=pumped
                )
        if odometer <= 0 or start <= 0 or pumped <= 0:
            error = "❌ All numeric values must be greater than zero."
            return render_template_string(HTML_FORM, error=error, site=site, driver_name=driver_name, odometer=odometer, start=start, pumped=pumped)

        write_to_csv(timestamp, site, vehicle, driver_name, odometer, start, end, pumped)

        return render_template_string(HTML_FORM + "<p style='color:green; font-weight:bold;'>✅ Logged successfully!</p>")

    return render_template_string(HTML_FORM)



from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenPyxlImage
from openpyxl.utils import get_column_letter

@app.route('/download')
def download():
    if not os.path.exists(CSV_FILE):
        return "No data to download yet.", 404

    df = pd.read_csv(CSV_FILE)

    wb = Workbook()
    ws = wb.active
    ws.title = "Fuel Log"

    # Write headers and data
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    wb.save(EXCEL_FILE)
    return send_file(EXCEL_FILE, as_attachment=True)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)