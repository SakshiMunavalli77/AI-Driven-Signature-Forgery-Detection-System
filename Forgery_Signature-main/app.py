from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import torch
import torch.nn.functional as F
from PIL import Image
import torchvision.transforms as transforms
from models.siamese_network import SiameseNetwork
from bson.objectid import ObjectId

# ================= INIT =================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/signature_forgery_db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ================= MODEL =================
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Initialize model with correct embedding dimension
model = SiameseNetwork(embedding_dim=256).to(device)

# Try loading the best trained model
model_path = 'training/model_best.pt'
try:
    model.load_state_dict(torch.load(model_path, map_location=device), strict=False)
    print(f"✅ Model loaded successfully from {model_path}!")
except Exception as e:
    print(f"❌ Model load failed from {model_path}")
    print(f"Error: {str(e)[:200]}...")
    print("\n🔧 SOLUTIONS:")
    print("1. Retrain the model: python training/train.py")
    print("2. Check that training/model_best.pt exists")
    raise RuntimeError("Model not loaded! Cannot start application without trained model.")

model.eval()

# ================= TRANSFORM =================
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# ================= USER =================
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    return User(user_data) if user_data else None

# ================= HELPERS =================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_image(path):
    try:
        img = Image.open(path).convert('RGB')
        img = transform(img)
        return img.unsqueeze(0)
    except Exception as e:
        print("Image error:", e)
        return None

# ================= PREDICTION =================
def predict_signature(img1_path, img2_path):
    img1 = process_image(img1_path)
    img2 = process_image(img2_path)

    if img1 is None or img2 is None:
        return None

    img1, img2 = img1.to(device), img2.to(device)

    with torch.no_grad():
        out1, out2 = model(img1, img2)
        distance = F.pairwise_distance(out1, out2).item()

    # 🔥 FINAL THRESHOLD (tune after testing)
    threshold = 0.75

    is_genuine = distance < threshold
    result_label = "Genuine Signature" if is_genuine else "Forged Signature"

    # 🔥 FIXED CONFIDENCE
    if is_genuine:
        confidence = max(50, 100 - (distance / threshold) * 100)
    else:
        confidence = max(50, (distance / threshold) * 100)

    confidence = min(100, max(0, confidence))

    print(f"[DEBUG] Distance: {distance}, Threshold: {threshold}")

    return {
        "is_genuine": is_genuine,
        "distance": round(distance, 4),
        "confidence": round(confidence, 2),
        "result": result_label
    }

# ================= ROUTES =================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if mongo.db.users.find_one({'email': email}):
            flash("Email exists", "danger")
            return redirect(url_for('register'))

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "password": hashed
        })

        flash("Registered!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = mongo.db.users.find_one({'email': request.form['email']})
        if user and bcrypt.check_password_hash(user['password'], request.form['password']):
            login_user(User(user))
            return redirect(url_for('predict'))
        flash("Invalid login", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        file1 = request.files['signature1']
        file2 = request.files['signature2']

        if not file1 or not file2:
            flash("Upload both images", "danger")
            return redirect(url_for('predict'))

        f1 = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file1.filename))
        f2 = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file2.filename))

        file1.save(f1)
        file2.save(f2)

        result = predict_signature(f1, f2)

        # Save prediction to database
        if result:
            prediction_record = {
                "user_id": ObjectId(current_user.id),
                "image1": os.path.basename(f1),
                "image2": os.path.basename(f2),
                "is_genuine": result["is_genuine"],
                "distance": result["distance"],
                "confidence": result["confidence"],
                "result": result["result"],
                "timestamp": datetime.now()
            }
            mongo.db.predictions.insert_one(prediction_record)

        return render_template("predict.html",
                               result=result,
                               image1=os.path.basename(f1),
                               image2=os.path.basename(f2))

    return render_template('predict.html')

@app.route('/history')
@login_required
def history():
    predictions = list(mongo.db.predictions.find(
        {'user_id': ObjectId(current_user.id)}
    ).sort('timestamp', -1))
    return render_template('history.html', predictions=predictions)

@app.route('/delete_history/<prediction_id>', methods=['POST'])
@login_required
def delete_history(prediction_id):
    try:
        prediction = mongo.db.predictions.find_one({
            '_id': ObjectId(prediction_id),
            'user_id': ObjectId(current_user.id)
        })
        
        if prediction:
            # Delete the prediction record
            mongo.db.predictions.delete_one({'_id': ObjectId(prediction_id)})
            flash("Prediction deleted", "success")
        else:
            flash("Prediction not found", "danger")
    except Exception as e:
        print(f"Error deleting prediction: {e}")
        flash("Error deleting prediction", "danger")
    
    return redirect(url_for('history'))

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)