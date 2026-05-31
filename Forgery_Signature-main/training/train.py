import torch
import torch.nn as nn
import torch.nn.functional as F
import os
import sys
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from PIL import Image

# Fix import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.siamese_network import SiameseNetwork

# -------------------------
# DATASET
# -------------------------
class SignatureDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.pairs = []

        persons = [f for f in os.listdir(data_dir)
                   if not f.endswith('_forg') and os.path.isdir(os.path.join(data_dir, f))]

        for person in persons:
            genuine_dir = os.path.join(data_dir, person)
            forged_dir = os.path.join(data_dir, f"{person}_forg")

            if not os.path.exists(forged_dir):
                continue

            genuine = [os.path.join(genuine_dir, f)
                       for f in os.listdir(genuine_dir) if f.endswith(('png','jpg','jpeg'))]

            forged = [os.path.join(forged_dir, f)
                      for f in os.listdir(forged_dir) if f.endswith(('png','jpg','jpeg'))]

            # Genuine pairs
            for i in range(len(genuine)):
                for j in range(i + 1, len(genuine)):
                    self.pairs.append((genuine[i], genuine[j], 0))  # similar

            # Forged pairs
            for g in genuine:
                for f in forged:
                    self.pairs.append((g, f, 1))  # dissimilar

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        img1_path, img2_path, label = self.pairs[idx]

        # ✅ FIX: Convert to RGB (3 channel)
        img1 = Image.open(img1_path).convert('RGB')
        img2 = Image.open(img2_path).convert('RGB')

        if self.transform:
            img1 = self.transform(img1)
            img2 = self.transform(img2)

        return img1, img2, torch.tensor(label, dtype=torch.float32)


# -------------------------
# TRANSFORMS WITH AUGMENTATION
# -------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomRotation(10),  # Add rotation augmentation
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),  # Add translation
    transforms.ColorJitter(brightness=0.1, contrast=0.1),  # Add color jitter
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# -------------------------  
# LOAD DATA
# -------------------------
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test')

dataset = SignatureDataset(data_dir, transform)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=0)  # Set to 0 for Windows compatibility

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -------------------------  
# LOSS FUNCTION WITH BETTER MARGIN
# -------------------------
class ContrastiveLoss(nn.Module):
    def __init__(self, margin=1.2):  # Increased margin for better separation
        super().__init__()
        self.margin = margin

    def forward(self, out1, out2, label):
        distance = F.pairwise_distance(out1, out2)

        loss = torch.mean(
            (1 - label) * torch.pow(distance, 2) +
            (label) * torch.pow(torch.clamp(self.margin - distance, min=0.0), 2)
        )
        return loss


# -------------------------  
# MODEL & OPTIMIZER
# -------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = SiameseNetwork(embedding_dim=256).to(device)  # Increased embedding dimension
criterion = ContrastiveLoss(margin=1.2)

# Better optimizer with weight decay
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)

# Learning rate scheduler
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

# -------------------------  
# TRAIN LOOP WITH VALIDATION
# -------------------------
epochs = 50  # Increased epochs for better training

best_loss = float('inf')
patience = 10
patience_counter = 0

for epoch in range(epochs):
    # Training phase
    model.train()
    total_loss = 0
    num_batches = 0

    for img1, img2, label in dataloader:
        img1, img2, label = img1.to(device), img2.to(device), label.to(device)

        out1, out2 = model(img1, img2)
        loss = criterion(out1, out2, label)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        num_batches += 1

    avg_loss = total_loss / num_batches

    # Learning rate scheduling
    scheduler.step()

    print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}, LR: {scheduler.get_last_lr()[0]:.6f}")

    # Early stopping
    if avg_loss < best_loss:
        best_loss = avg_loss
        patience_counter = 0
        # Save best model
        save_path = os.path.join(os.path.dirname(__file__), "model_best.pt")
        torch.save(model.state_dict(), save_path)
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"Early stopping at epoch {epoch+1}")
            break

if __name__ == '__main__':
    # Train the model
    best_loss = best_loss  # This will be available from the loop above
    
    # -------------------------  
    # SAVE FINAL MODEL
    # -------------------------
    save_path = os.path.join(os.path.dirname(__file__), "model_1.pt")
    torch.save(model.state_dict(), save_path)

    print("✅ Model trained & saved successfully!")
    print(f"Best model saved as 'model_best.pt' with loss: {best_loss:.4f}")