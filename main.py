from flask import Flask, request, render_template, session, jsonify, redirect, url_for
import math
from database import Db
import json
from aws_storage import AWSStorage

app = Flask(__name__)
app.secret_key = 'store'  # Set a secret key for session management

# Load user data
with open("data.json", 'r') as json_file:
    users = json.load(json_file)

db = Db(users['user'], users['password'])
aws = AWSStorage()

@app.route("/", methods=["GET"])
def index():
    # Page 1: Login page
    return render_template("mail.html")

@app.route("/calculator", methods=["POST"])
def calculator():
    # Page 2: Main application page after login
    email = request.form["email"]
    session['email'] = email
    if email in db.search():
        return render_template("index.html")
    else:
        return render_template("create.html")

@app.route('/submit_password', methods=['POST'])
def submit_password():
    password = request.form.get('password')
    email = session.get('email')
    if len(password) > 3:
        db.insert_table(email, password)
        aws.create_folder(email)
        return render_template('index.html')
    else:
        return render_template("create.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    if 'email' not in session:
        return redirect(url_for('index'))  # Ensure the user is redirected to the login page
    try:
        expression = request.form["expression"]
        is_degrees = request.form.get("isDegrees") == "true"
        email = session.get('email')
        
        if db.search_password(email, expression):
            return "yes"
        else:
            safe_dict = {
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'asin': math.asin,
                'acos': math.acos,
                'atan': math.atan,
                'log': math.log,
                'log10': math.log10,
                'sqrt': math.sqrt,
                'cbrt': lambda x: x ** (1/3),
                'pi': math.pi,
                'e': math.e,
                '**': pow
            }

            if is_degrees:
                safe_dict['sin'] = lambda x: math.sin(math.radians(x))
                safe_dict['cos'] = lambda x: math.cos(math.radians(x))
                safe_dict['tan'] = lambda x: math.tan(math.radians(x))
                safe_dict['asin'] = lambda x: math.degrees(math.asin(x))
                safe_dict['acos'] = lambda x: math.degrees(math.acos(x))
                safe_dict['atan'] = lambda x: math.degrees(math.atan(x))

            result = eval(expression, {"__builtins__": None}, safe_dict)
    except Exception as e:
        result = f"Error: {str(e)}"
    
    return str(result)

@app.route('/data', methods=["GET", "POST"])
def data():
    # Page 3: Additional content page
    if 'email' not in session:
        return redirect(url_for('index'))  # Ensure the user is redirected to the login page
    return render_template('data.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    folder_name = session.get('email')
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        try:
            result = aws.upload_file(file, folder_name)
            return result, 200
        except Exception as e:
            return str(e), 500

@app.route('/list_files', methods=['GET'])
def list_files():
    try:
        email = session.get('email')
        aws.refresh_file_list()
        files = [key for key in aws.file_keys if key.startswith(email)]
        files.remove(email+"/")
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/get_file_url', methods=['GET'])
def get_file_url():
    try:
        key = request.args.get('key')
        url = aws.get_signed_url(key, expiration=3600)
        return jsonify({'url': url}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/delete_file', methods=['DELETE'])
def delete_file():
    file_key = request.args.get('key')
    if not file_key:
        return 'No file key provided', 400
    try:
        message = aws.delete_file(file_key)
        return message, 200
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(debug=True)
