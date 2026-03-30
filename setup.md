# Environment Setup

## 1. Install Python 3.11
Download from https://www.python.org/downloads/
Make sure to check "Add Python to PATH" during install.

## 2. Create a virtual environment
```bash
python -m venv venv
```

Activate it:
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

## 3. Install PyTorch (machine-specific)

**RTX 4050 (CUDA 12.1):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**RTX 5070 (CUDA 12.8):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

## 4. Install remaining dependencies
```bash
pip install -r requirements.txt
```

## 5. Verify GPU is detected
```bash
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```
Should print `True` and your GPU name. If it prints `False`, PyTorch is not seeing your GPU — check CUDA drivers.

## Transferring to a new machine
1. Clone the repo
2. Create a new virtual environment (Step 2)
3. Run the correct PyTorch install command for that machine (Step 3)
4. Run `pip install -r requirements.txt` (Step 4)
5. Verify GPU (Step 5)
