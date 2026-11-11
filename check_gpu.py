import torch
import sys

print("=" * 60)
print("🎮 GPU Detection Test")
print("=" * 60)

# Check PyTorch version
print(f"\n📦 PyTorch Version: {torch.__version__}")
print(f"🐍 Python Version: {sys.version}")

# Check CUDA
print(f"\n🔥 CUDA Available: {torch.cuda.is_available()}")
print(f"🔥 CUDA Version: {torch.version.cuda}")

if torch.cuda.is_available():
    print(f"🎮 GPU Count: {torch.cuda.device_count()}")
    print(f"🎮 Current GPU: {torch.cuda.current_device()}")
    print(f"🎮 GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
else:
    print("\n❌ GPU Not Detected!")
    print("\nPossible reasons:")
    print("1. PyTorch CPU version installed (not GPU version)")
    print("2. NVIDIA drivers not installed")
    print("3. CUDA toolkit not installed")

print("\n" + "=" * 60)