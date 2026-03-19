import os
import shutil

# --- CONFIGURATION ---
SOURCE_DIR = "/home/xxfactionsxx/Downloads" # Change this to where you download new files
HUB_DIR = "/srv/ai/models/comfyui"

# Map extensions/keywords to ComfyUI subfolders
MAPPING = {
    "checkpoints": [".ckpt", ".safetensors"],
    "loras": ["_lora", "lora"],
    "vae": ["vae"],
    "diffusion_models": ["wan2", "diffusion"],
    "clip": ["t5", "clip", "umt5"],
    "clip_vision": ["clip_vision"]
}

def organize():
    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getsize(file_path) < 100 * 1024 * 1024: # Skip files < 100MB
                continue
            
            moved = False
            for folder, triggers in MAPPING.items():
                if any(t in file.lower() for t in triggers):
                    dest_folder = os.path.join(HUB_DIR, folder)
                    os.makedirs(dest_folder, exist_ok=True)
                    print(f"📦 Moving {file} to {folder}...")
                    shutil.move(file_path, os.path.join(dest_folder, file))
                    moved = True
                    break
            
            if not moved:
                print(f"❓ Could not categorize {file}. Manual move required.")

if __name__ == "__main__":
    organize()