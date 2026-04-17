# 🌍 Agentic Ecosystem Simulator

A sophisticated ecosystem simulator that connects multiple AI models through Modal cloud functions to create a dynamic simulation of an ecosystem based on your environmental description. Now with added visualization capabilities!

## 🎯 What This Does

This simulator creates a **complete ecosystem simulation** by chaining together AI models in the cloud:

1. **🧬 Species Generation** - Creates plants and animals specifically adapted to your environment
2. **🔄 Interaction Simulation** - Simulates ecological interactions specific to your environment
3. **📋 Ecosystem Summary** - Creates environment-aware summaries of key events
4. **🎵 Narration** - Converts ecosystem stories into natural speech narration
5. **🎬 Visualization** - Creates animated visualizations of your ecosystem (with GPU support)

All models run seamlessly through Modal cloud functions, demonstrating efficient **agentic orchestration**!

## 🚀 Quick Start

### Basic Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Deploy Modal functions
modal deploy modal_functions_fixed.py

# 3. Run the ecosystem simulator
python app_modal_deployed_clean.py
```

### Optional: Enable Visualization (Recommended)
For the visualization feature, additional dependencies are required:

**Windows:**
```bash
# Run the installer script
install_visualization.bat
```

**Linux/Mac:**
```bash
# Run the installer script
chmod +x install_visualization.sh
./install_visualization.sh
```

## 🌐 Usage

1. **Open your browser** to `http://127.0.0.1:7862` (or the provided shared URL)
2. **Enter an environment** like "tropical rainforest with morning mist"
3. **Click "Simulate Ecosystem Day"**
4. **Watch the magic happen**:
   - JSON of generated species appears
   - Daily interactions are simulated
   - Events are summarized intelligently
   - Visual animation of your ecosystem displays
   - Use the voice selector to generate audio narration

### 🎨 Example Environments to Try
- `tropical rainforest with high humidity and colorful birds`
- `desert oasis with palm trees and rocks at sunset`
- `temperate forest clearing in autumn with golden leaves`
- `alpine meadow with wildflowers and distant mountains`
- `wetland marsh with reeds and water on a misty morning`
- `volcanic island with unique flora adapting to the terrain`

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│                  Modal Cloud Functions                   │
│                                                          │
│  ┌─────────────────┐    ┌─────────────────┐             │
│  │  Species Gen    │    │  Interaction    │             │
│  │  (LLM)          │    │  Simulator      │             │
│  └─────────────────┘    │  (LLM)          │             │
│                         └─────────────────┘             │
│                                                          │
└──────────────────────────────────────────────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   Main App      │
                 │   Orchestrator  │
                 │   (Gradio)      │
                 │   Port 7862     │
                 └─────────────────┘
                          │
    ┌────────────────┬────┴─────────────┬───────────────┐
    ▼                ▼                  ▼               ▼
┌─────────────┐ ┌─────────────┐  ┌─────────────┐ ┌─────────────┐
│ Summarizer  │ │ TTS Narrator│  │ Ecosystem   │ │ Stable      │
│ (Cloud)     │ │ (Local)     │  │ Engine      │ │ Diffusion   │
└─────────────┘ └─────────────┘  └─────────────┘ └─────────────┘
```

## 📁 Project Structure

```
agentic_ecosystem/
├── requirements.txt         # Python dependencies
├── app_modal_deployed.py    # Main orchestrator (Gradio frontend)
├── modal_functions_fixed.py # Modal cloud functions for simulation
├── ecosystem_viz.py         # Visualization module using Stable Diffusion
├── install_visualization.bat # Windows installer for viz components
├── install_visualization.sh  # Linux/Mac installer for viz components
└── README.md                # This file
```

## 🔧 Technical Details

### System Components
- **Modal Cloud Functions**: Ecosystem simulation, species generation, interactions
- **Gradio Interface**: User-friendly web interface with real-time feedback
- **Local TTS Engine**: pyttsx3-powered voice narration with multiple voice options
- **Environment Analysis**: Detailed environment parsing for contextual simulation
- **Visualization Engine**: Stable Diffusion-powered ecosystem visualization

### Visualization System
- **Base Technology**: StableDiffusionPipeline from HuggingFace Diffusers
- **Animation**: Dynamic frame creation with subtle variations
- **Performance**: GPU acceleration (CUDA) for faster generation
- **Fallbacks**: Graceful degradation when GPU not available

### Modal Integration
- **Cloud-Based Processing**: Main simulation runs in the cloud via Modal
- **Local Processing**: TTS and visualization handled locally for efficiency

## 💻 Requirements

### Basic Features
- Python 3.8+
- Modal account and CLI
- Internet connection for Modal functions

### Visualization Features (Optional)
- CUDA-compatible GPU (highly recommended)
- PyTorch with CUDA support
- 8GB+ RAM for stable diffusion operations
- 4GB+ VRAM for optimal performance

## Authors
--ADITYA GUPTA

## 📜 License

MIT License
