from PIL import Image
import os

base = r"e:\embed_chatbot\embed_chatbot\apps\web\public\landing"
for f in os.listdir(base):
    if f.endswith(".png"):
        img = Image.open(os.path.join(base, f))
        print(f"{f}: size={img.size}, mode={img.mode}")
