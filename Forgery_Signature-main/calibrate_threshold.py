import torch
import torch.nn.functional as F
from PIL import Image
import torchvision.transforms as transforms
from models.siamese_network import SiameseNetwork
import os

# Load model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = SiameseNetwork().to(device)
model.load_state_dict(torch.load('training/model_1.pt', map_location=device))
model.eval()

# Transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485], std=[0.229])
])

def process_image(image_path):
    img = Image.open(image_path).convert('L')
    img_tensor = transform(img).unsqueeze(0)
    return img_tensor

def calculate_distance(img1_path, img2_path):
    img1 = process_image(img1_path).to(device)
    img2 = process_image(img2_path).to(device)
    
    with torch.no_grad():
        output1, output2 = model(img1, img2)
        distance = F.pairwise_distance(output1, output2).item()
    
    return distance

# Test with your validation data
print("Testing Genuine Pairs (Same Person):")
genuine_distances = []

# Add paths to your genuine signature pairs
genuine_pairs = [
    ("test/049/01_049.png", "test/049/02_049.png"),
    # Add more genuine pairs
]

for img1, img2 in genuine_pairs:
    if os.path.exists(img1) and os.path.exists(img2):
        dist = calculate_distance(img1, img2)
        genuine_distances.append(dist)
        print(f"Distance: {dist:.4f}")

print("\n" + "="*50)
print("Testing Forged Pairs (Different People):")
forged_distances = []

# Add paths to your forged/different signature pairs
forged_pairs = [
    ("sign_data/test/049_forg/01_0114049.PNG", "sign_data/test/049_forg/01_0206049.PNG"),
    # Add more forged pairs
]

for img1, img2 in forged_pairs:
    if os.path.exists(img1) and os.path.exists(img2):
        dist = calculate_distance(img1, img2)
        forged_distances.append(dist)
        print(f"Distance: {dist:.4f}")

if genuine_distances and forged_distances:
    print("\n" + "="*50)
    print("STATISTICS:")
    print(f"Genuine pairs - Mean: {sum(genuine_distances)/len(genuine_distances):.4f}, "
          f"Max: {max(genuine_distances):.4f}, Min: {min(genuine_distances):.4f}")
    print(f"Forged pairs - Mean: {sum(forged_distances)/len(forged_distances):.4f}, "
          f"Max: {max(forged_distances):.4f}, Min: {min(forged_distances):.4f}")
    
    # Suggest optimal threshold
    max_genuine = max(genuine_distances)
    min_forged = min(forged_distances)
    suggested_threshold = (max_genuine + min_forged) / 2
    
    print(f"\nSUGGESTED THRESHOLD: {suggested_threshold:.4f}")
    print(f"Use this value in the predict_signature() function in app.py")
else:
    print("\nPlease add test image pairs to calculate optimal threshold")