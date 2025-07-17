from flask import Flask, request, render_template_string, redirect, url_for, session, send_file
from datetime import datetime
import os
import csv
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '9f3e8c2b5d7a4f9cbb8e1d0a3f7c6e4520d93f4a1b6c7e8d9f1a2b3c4d5e6f7a'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

USERNAME = 'Marnus'
PASSWORD = 'NEX@test149'  # Change this!

CSV_FILE = 'fuel_log.csv'

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
        <select id="site" name="site" onchange="toggleVehicleField()">
            <option value="">--Select Site--</option>
            <option value="Holfontein">Holfontein</option>
            <option value="Plank">Plank</option>
        </select>

        <!-- Holfontein Vehicle Dropdown -->
        <div id="vehicle_dropdown" style="display:none;">
            <label for="vehicle_select">Vehicle:</label>
            <select id="vehicle_select" name="vehicle_select">
                <option value="">--Select Vehicle--</option>
                <option>Geni 1</option>
                <option>Geni 2</option>
                <option>Geni3 Hopper</option>
                <option>Landini 1</option>
                <option>Landini 2</option>
                <option>Landini 3</option>
                <option>Landini 4</option>
                <option>Landini 5</option>
                <option>Mahindra Bakkie</option>
                <option>MF DHS856FS</option>
                <option>MF DHS872FS</option>
                <option>MF DHS879FS</option>
                <option>MF DHS885FS</option>
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
            if (site === "Holfontein") {
                document.getElementById("vehicle_dropdown").style.display = "block";
                document.getElementById("vehicle_input").style.display = "none";
            } else if (site === "Plank") {
                document.getElementById("vehicle_dropdown").style.display = "none";
                document.getElementById("vehicle_input").style.display = "block";
            } else {
                document.getElementById("vehicle_dropdown").style.display = "none";
                document.getElementById("vehicle_input").style.display = "none";
            }
        }
        </script>


        <label for="driver_name">Driver Name:</label>
        <input id="driver_name" name="driver_name" type="text" required>

        <label for="odometer">Vehicle Odometer:</label>
        <input id="odometer" name="odometer" type="number" step="0.1" required>


        <label for="start">Pump Start Reading:</label>
        <input id="start" name="start" type="number" step="0.1" required oninput="calculateEnd()">
        {% if error %}
        <div style="color:red; font-size:18px; font-weight:bold; margin-top:5px;">{{ error }}</div>
        {% endif %}


        <label for="pumped_input">Pumped (Litres):</label>
        <input id="pumped_input" name="pumped" type="number" step="0.1" required oninput="calculateEnd()">

        <div class="result">End Reading: <span id="calculated_end">0.00</span></div>

        <label for="photo">Upload Photo:</label>
        <input id="photo" name="photo" type="file" accept="image/*">

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

def write_to_csv(timestamp, site, vehicle, driver_name, odometer, start, end, pumped, photo_path):
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Timestamp', 'Site', 'Vehicle', 'Driver Name', 'Odometer', 'Start Reading', 'End Reading', 'Pumped', 'Photo'])
        writer.writerow([timestamp, site, vehicle, driver_name, odometer, start, end, pumped, photo_path])


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
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Vehicle logic
        vehicle = request.form.get('vehicle_text') if site == "Plank" else request.form.get('vehicle_select')

        # ✅ Handle image upload
        photo = request.files.get('photo')
        photo_filename = ''
        if photo and photo.filename != '':
            photo_filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
            photo.save(photo_path)

        # ✅ Validate previous reading
        previous = get_last_readings()
        if previous:
            _, prev_end = previous
            if round(start, 1) != round(prev_end, 1):
                error = f"❌ Invalid entry: Start reading ({start:.1f}) must equal previous end reading ({prev_end:.1f})."
                return render_template_string(HTML_FORM, error=error)

        # ✅ Save data to CSV with photo filename as last column
        photo_file = request.files.get('photo')
        photo_path = ''
        if photo_file and allowed_file(photo_file.filename):
            filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo_file.save(photo_path)

        write_to_csv(timestamp, site, vehicle, driver_name, odometer, start, end, pumped, photo_path)

        return render_template_string(HTML_FORM + "<p style='color:green; font-weight:bold;'>✅ Logged successfully!</p>")

    return render_template_string(HTML_FORM)



@app.route('/download')
def download():
    if not os.path.exists(CSV_FILE):
        return "No data to download yet.", 404

    df = pd.read_csv(CSV_FILE)
    excel_file = 'fuel_log.xlsx'
    with pd.ExcelWriter(excel_file, engine='openpyxl', date_format='YYYY-MM-DD HH:MM:SS') as writer:
        df.to_excel(writer, index=False)

    return send_file(excel_file, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)