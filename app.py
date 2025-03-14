from __future__ import division, print_function
import numpy as np
import tensorflow as tf
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import nibabel as nib
import cv2

app = Flask(__name__)
app.secret_key = 'mynameisaffanhussain'

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

# Load TFLite model
TFLITE_MODEL_PATH = "model/brain_aneurysm_model.tflite"
interpreter = tf.lite.Interpreter(model_path=TFLITE_MODEL_PATH)
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def preprocess_nii(nii_path, img_size=(256, 256)):
    """Loads and preprocesses a .nii file for model prediction."""
    nii_img = nib.load(nii_path)
    nii_data = nii_img.get_fdata()
    
    # Extract middle slice
    mid_slice_idx = nii_data.shape[2] // 2
    mid_slice = nii_data[:, :, mid_slice_idx]
    
    # Normalize and resize
    normalized_slice = cv2.normalize(mid_slice, None, 0, 255, cv2.NORM_MINMAX)
    resized_slice = cv2.resize(normalized_slice, img_size)
    
    # Convert to 3-channel image (RGB format)
    final_img = np.stack([resized_slice] * 3, axis=-1)
    final_img = final_img / 255.0  # Normalize (0-1)
    final_img = np.expand_dims(final_img, axis=0)  # Add batch dimension
    
    return final_img.astype(np.float32)

def model_predict(nii_path):
    """Processes and predicts a .nii file using the TFLite model."""
    processed_img = preprocess_nii(nii_path)
    
    # Set input tensor
    interpreter.set_tensor(input_details[0]['index'], processed_img)
    
    # Run inference
    interpreter.invoke()
    
    # Get output tensor
    result = interpreter.get_tensor(output_details[0]['index'])
    
    predicted_class = np.argmax(result)
    
    return "Brain Aneurysm Detected!" if predicted_class == 1 else "No Brain Aneurysm"

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    if not file.filename.endswith('.nii'):
        return jsonify({"error": "Invalid file format. Please upload a .nii file."})
    
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)
    prediction = model_predict(file_path)
    
    return prediction

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['loggedin'] = True
            session['id'] = user.id
            session['username'] = user.username
            return redirect(url_for('preview'))
        msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        if User.query.filter_by(username=username).first():
            msg = 'Account already exists!'
        else:
            new_user = User(username=username, password=password, email=email)
            db.session.add(new_user)
            db.session.commit()
            msg = 'You have successfully registered!'
            return redirect(url_for('login'))
    return render_template('signup.html', msg=msg)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/preview', methods=['GET'])
def preview():
    return render_template("preview.html")

@app.route('/contact', methods=['GET'])
def contact():
    return render_template("contact.html")

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
