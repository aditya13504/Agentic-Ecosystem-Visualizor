import torch
from diffusers import StableDiffusionPipeline
from PIL import Image, ImageEnhance
import imageio
import os
import random
import tempfile
import time

class EcosystemVisualizer:
    def __init__(self):
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.initialized = False
        print(f"🎨 EcosystemVisualizer will use device: {self.device}")
        
    def initialize_model(self):
        """Lazy initialization of the model to avoid loading it until needed"""
        if not self.initialized:
            try:
                print("🔄 Initializing Stable Diffusion model...")
                print("📥 This may take several minutes on first run to download the model (~4GB)")
                model_id = "CompVis/stable-diffusion-v1-4"
                
                # Load with appropriate settings based on device
                if self.device == "cuda":
                    print("🚀 Using GPU acceleration")
                    self.pipe = StableDiffusionPipeline.from_pretrained(
                        model_id, 
                        torch_dtype=torch.float16,
                        revision="fp16",
                    ).to(self.device)
                else:
                    print("🐌 Using CPU (this will be slower - consider using GPU for faster generation)")
                    self.pipe = StableDiffusionPipeline.from_pretrained(
                        model_id
                    ).to(self.device)
                    
                self.initialized = True
                print("✅ Stable Diffusion model initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing Stable Diffusion: {e}")
                raise

    def create_variants(self, img, n=8):
        """Create animated frames with slight variations using the exact pipeline logic"""
        frames = []
        for i in range(n):
            # Apply slight zoom, brightness or shift to simulate motion
            enhancer = ImageEnhance.Brightness(img)
            bright_img = enhancer.enhance(1 + random.uniform(-0.03, 0.03))

            shift_x = random.randint(-2, 2)
            shift_y = random.randint(-2, 2)
            shifted_img = bright_img.transform(
                img.size, Image.AFFINE, (1, 0, shift_x, 0, 1, shift_y)
            )
            frames.append(shifted_img)
        return frames
    
    def generate_ecosystem_animation(self, environment_description):
        """Generate an animated GIF of the ecosystem based on description using your exact pipeline"""
        try:
            # Make sure model is initialized
            self.initialize_model()
            
            # Enhance the prompt for better visualization
            enhanced_prompt = self._enhance_prompt(environment_description)
            print(f"🖼️ Generating visualization for: {enhanced_prompt}")
            
            # === Step 1: Generate base image ===
            num_steps = 50 if self.device == "cuda" else 35  # Use 50 steps as in your pipeline
            base_image = self.pipe(
                enhanced_prompt, 
                num_inference_steps=num_steps
            ).images[0]
            
            # === Step 2: Create animated frames with slight variations ===
            frames = self.create_variants(base_image, n=8)
            
            # === Step 3: Save as GIF ===
            # Use a unique filename to avoid browser caching issues
            gif_filename = f"ecosystem_viz_{int(time.time() * 1000)}.gif"
            gif_path = os.path.join(os.getcwd(), gif_filename)
            
            frames[0].save(
                gif_path, 
                save_all=True, 
                append_images=frames[1:], 
                duration=150,  # 150ms per frame as in your pipeline
                loop=0  # 0 = infinite loop
            )
            time.sleep(0.1)  # Ensure file is flushed to disk
            
            # Ensure file is flushed and closed (Windows safety)
            with open(gif_path, "rb") as f:
                f.read()  # Force OS to flush file buffers
            time.sleep(0.1)  # Give the OS a moment to flush the file
            print(f"✅ Generated animation saved to {gif_path}")
            
            # Return the absolute path for Gradio
            return os.path.abspath(gif_path)
            
        except Exception as e:
            print(f"❌ Error generating visualization: {e}")
            import traceback
            traceback.print_exc()
            # Return None on error
            return None
            
    def _enhance_prompt(self, environment_description):
        """Enhance the environment description for better visualization"""
        # Add details for better image generation
        enhanced = environment_description.strip()
        
        # Add style and quality enhancers if not already present
        enhancers = [
            "detailed ecosystem", "nature", "4k", "high quality", 
            "detailed", "realistic", "landscape"
        ]
        
        for enhancer in enhancers:
            if enhancer.lower() not in enhanced.lower():
                enhanced += f", {enhancer}"
                
        return enhanced

# Create a singleton instance
visualizer = EcosystemVisualizer()
