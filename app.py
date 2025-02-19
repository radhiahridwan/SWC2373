from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

WEBEX_API_URL = "https://webexapis.com/v1"
ROOMS_API_URL = f"{WEBEX_API_URL}/rooms"

# Home Page - Ask for Access Token
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        token = request.form.get('access_token')
        if not token:
            flash('❌ Access Token is required.', 'danger')
            return redirect(url_for('index'))

        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{WEBEX_API_URL}/people/me", headers=headers)

        if response.status_code == 200:
            return redirect(url_for('menu', access_token=token))
        else:
            flash('❌ Invalid Access Token. Please try again.', 'danger')

    return render_template('index.html')

# Menu Page
@app.route('/menu')
def menu():
    access_token = request.args.get('access_token')
    if not access_token:
        flash("Access token is required!", "danger")
        return redirect(url_for('index'))
    return render_template('menu.html', access_token=access_token)

# Test Webex Connection Page
@app.route('/test_connection', methods=['GET', 'POST'])
def test_connection():
    access_token = request.args.get('access_token') or request.form.get('access_token')
    if not access_token:
        flash("Access token is required!", "danger")
        return redirect(url_for('menu'))

    message = None  # Default: No message until button is clicked

    if request.method == 'POST':  # Run test only when the button is clicked
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{WEBEX_API_URL}/people/me", headers=headers)

        if response.status_code == 200:
            message = "✅ Connection successful! You are logged in to Webex."
        else:
            message = "❌ Connection failed! Please check your Webex login status."

    return render_template('test_connection.html', message=message, access_token=access_token)

# Fetch and Display User Information
@app.route('/user_info')
def user_info():
    access_token = request.args.get('access_token')
    if not access_token:
        flash("Access token is required!", "danger")
        return redirect(url_for('menu'))

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{WEBEX_API_URL}/people/me", headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        return render_template('user_info.html', user_info=user_info, access_token=access_token)
    else:
        flash("Invalid access token or API error!", "danger")
        return redirect(url_for('menu'))

# Fetch and Display Webex Rooms
@app.route('/rooms', methods=['GET', 'POST'])
def rooms():
    access_token = request.args.get('access_token') or request.form.get('access_token')
    if not access_token:
        flash("Access token is required!", "danger")
        return redirect(url_for('menu'))

    headers = {"Authorization": f"Bearer {access_token}"}

    # Handle Add Room Request
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        if room_name:
            room_data = {"title": room_name}
            create_response = requests.post(ROOMS_API_URL, headers=headers, json=room_data)

            if create_response.status_code == 200:
                flash("✅ Room created successfully!", "success")
            else:
                flash("❌ Failed to create room. Check your API access.", "danger")

    # Fetch all rooms
    response = requests.get(ROOMS_API_URL, headers=headers)
    if response.status_code == 200:
        rooms_data = response.json().get('items', [])
        return render_template('rooms.html', rooms=rooms_data, access_token=access_token)
    else:
        flash("Failed to retrieve rooms!", "danger")
        return redirect(url_for('user_info', access_token=access_token))

if __name__ == '__main__':
    app.run(debug=True)
