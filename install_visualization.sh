#!/bin/bash

echo "======================================================"
echo "    Installing Ecosystem Simulator Visualization Tools"
echo "======================================================"

echo
echo "This script will install the required packages for the"
echo "ecosystem visualization component."
echo
echo "Requirements:"
echo "- Python 3.8+ with pip"
echo "- CUDA compatible GPU (recommended)"
echo

read -p "Press Enter to continue..."

echo
echo "[1/4] Installing base requirements..."
pip install -r requirements.txt

echo
echo "[2/4] Installing PyTorch with CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo
echo "[3/4] Installing visualization components..."
pip install diffusers>=0.24.0 transformers>=4.34.0 accelerate>=0.23.0 imageio>=2.31.0 Pillow>=10.0.0

echo
echo "[4/4] Testing visualization module..."
python -c "import torch; print(f'PyTorch available: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); from diffusers import StableDiffusionPipeline; print('Diffusers module loaded successfully')"

echo
echo "======================================================"
echo "Installation Complete!"
echo
echo "To use the visualization features:"
echo "1. Run the simulator: python app_modal_deployed.py"
echo "2. Fill in an environment description"
echo "3. Click \"Simulate Ecosystem Day\""
echo "======================================================"

read -p "Press Enter to exit..."
