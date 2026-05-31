import torch
import torch.nn.functional as F
from PIL import Image
import torchvision.transforms as transforms
from models.siamese_network import SiameseNetwork

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Load model
model = SiameseNetwork().to(device)
model.load_state_dict(torch.load('training/model_1.pt', map_location=device))
model.eval()
print("Model loaded successfully!")

# Transform
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485], std=[0.229])
])

def test_prediction(img1_path, img2_path):
    # Process images
    img1 = Image.open(img1_path).convert('L')
    img2 = Image.open(img2_path).convert('L')
    
    img1_tensor = transform(img1).unsqueeze(0).to(device)
    img2_tensor = transform(img2).unsqueeze(0).to(device)
    
    # Predict
    with torch.no_grad():
        output1, output2 = model(img1_tensor, img2_tensor)
        distance = F.pairwise_distance(output1, output2).item()
    
    print(f"\nEuclidean Distance: {distance:.4f}")
    print(f"Interpretation: {'GENUINE (Similar)' if distance < 0.75 else 'FORGED (Different)'}")
    return distance

# Test with your images
print("\n" + "="*50)
print("TEST YOUR IMAGES:")
print("Replace these paths with your actual test images")
print("="*50)

# Uncomment and replace with your test images
test_prediction("test/049/01_049.png", "test/049_forg/01_0206049.PNG")