import json
import gradio as gr
import time
import modal
import threading
import pyttsx3
import tempfile
import os
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import the visualization module
try:
    from ecosystem_viz import visualizer
    HAS_VISUALIZATION = True
    print("✅ Visualization module imported successfully")
except ImportError as e:
    HAS_VISUALIZATION = False
    print(f"⚠️ Visualization module not available: {e}")
    print("⚠️ Installing required packages may enable visualization")

print("Starting Agentic Ecosystem Simulator...")

# Initialize Modal app for simplified functions
app = modal.App("agentic-ecosystem-simple")

def simulate_ecosystem_step(environment):
    """Main orchestration function - runs the text-based ecosystem simulation using Modal"""
    
    if not environment or not environment.strip():
        return None, [], "Please provide an environment description.", None, None
    
    try:
        print(f"🌱 Simulating ecosystem for environment: {environment}")
        
        # Call deployed Modal function using the new API
        f = modal.Function.from_name("agentic-ecosystem-simple", "simulate_ecosystem")
        results = f.remote(environment)
            
        # Check for errors
        if 'error' in results and results['error']:
            print(f"❌ Error in simulation: {results['error']}")
            return None, [], f"Simulation error: {results['error']}", None, None
        
        # Process species data
        species_list = results['species']
        print(f"✓ Generated {len(species_list)} species")
        
        # Process events and summary
        events = results['events']
        summary = results['summary']
        print("✓ Generated events and summary")
        
        # Process audio if available
        audio = None
        if results['audio'] and results['audio'] != "base64_audio_data_placeholder":
            # In a real implementation, decode the audio data
            # For now, we'll skip this
            audio = None
        
        # Generate visualization if available
        visualization = None
        if HAS_VISUALIZATION:
            try:
                print("🎨 Generating ecosystem visualization...")
                print("⏳ This may take 2-5 minutes on first run (downloading model) or when using CPU...")
                
                # Generate visualization in background to avoid blocking
                def generate_viz():
                    return visualizer.generate_ecosystem_animation(environment)
                
                # Start in a separate thread with longer timeout for first-time model download
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(generate_viz)
                    try:
                        visualization = future.result(timeout=90000)  # Allow up to 5 minutes for model download + generation
                    except TimeoutError:
                        print("⚠️ Visualization generation timed out - this can happen on first run or with slow hardware")
                        visualization = None
                        
                if visualization and os.path.exists(visualization):
                    print(f"✓ Visualization generated successfully: {visualization}")
                    # Ensure we're returning the absolute path for Gradio
                    visualization = os.path.abspath(visualization)
                    print(f"✓ Returning absolute path: {visualization}")
                else:
                    print(f"⚠️ Visualization generation returned invalid file. Result: {visualization}")
                    if visualization:
                        print(f"⚠️ File exists check: {os.path.exists(visualization)}")
                    visualization = None
                    
            except Exception as viz_error:
                print(f"⚠️ Visualization error: {viz_error}")
                import traceback
                traceback.print_exc()
                visualization = None
        else:
            print("⚠️ Visualization module not available")
        
        print("🎉 Ecosystem simulation completed!")
        
        return (
            species_list,
            events,
            summary,
            audio,
            visualization
        )
        
    except Exception as e:
        print(f"Error in ecosystem simulation: {e}")
        return None, [], f"Simulation error: {str(e)}", None, None

def check_modal_deployment():
    """Check if Modal is properly configured"""
    try:
        # Try to lookup the deployed function using new API
        f = modal.Function.from_name("agentic-ecosystem-simple", "simulate_ecosystem")
        return "✅ Modal is properly configured and deployed!\n\nThe ecosystem simulator is ready to use."
    except Exception as e:
        return f"❌ Modal error: {str(e)}\nPlease run 'modal deploy modal_functions.py' to deploy the functions."

def get_available_voices():
    """Get available voices and categorize them by gender"""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        voice_options = {
            "🤖 Auto (Best Available)": "auto",
            "🔧 Default System Voice": "default"
        }
        
        premium_female_voices = []
        premium_male_voices = []
        standard_female_voices = []
        standard_male_voices = []
        
        if voices:
            for voice in voices:
                voice_name = voice.name
                voice_id = voice.id
                
                # Enhanced voice detection with Windows 10/11 premium voices
                is_premium_female = any(keyword in voice_name.lower() for keyword in [
                    'zira desktop', 'hazel desktop', 'eva desktop', 'aria', 'jenny', 
                    'michelle', 'joanna', 'salli', 'ivy', 'kimberly', 'kendra',
                    'microsoft zira', 'microsoft hazel', 'cortana'
                ])
                
                is_premium_male = any(keyword in voice_name.lower() for keyword in [
                    'david desktop', 'mark desktop', 'microsoft david', 'microsoft mark',
                    'matthew', 'justin', 'joey', 'brian', 'russell', 'aws neural'
                ])
                
                is_female = any(keyword in voice_name.lower() for keyword in [
                    'female', 'woman', 'zira', 'hazel', 'susan', 'karen', 'sarah', 
                    'anna', 'emma', 'jennifer', 'eva', 'samantha', 'linda', 'mary'
                ])
                
                is_male = any(keyword in voice_name.lower() for keyword in [
                    'male', 'man', 'david', 'mark', 'paul', 'richard', 'james',
                    'daniel', 'alex', 'tom', 'george', 'brian', 'michael', 'peter'
                ])
                
                # Categorize voices by quality and gender
                if is_premium_female:
                    premium_female_voices.append((f"✨ {voice_name} (Premium Female)", voice_id))
                elif is_premium_male:
                    premium_male_voices.append((f"✨ {voice_name} (Premium Male)", voice_id))
                elif is_female:
                    standard_female_voices.append((f"🚺 {voice_name}", voice_id))
                elif is_male:
                    standard_male_voices.append((f"🚹 {voice_name}", voice_id))
                else:
                    # For ambiguous voices, try to detect from other properties
                    if any(char in voice_name.lower() for char in ['f', '1']) and not any(char in voice_name.lower() for char in ['m', '0']):
                        standard_female_voices.append((f"🚺 {voice_name}", voice_id))
                    else:
                        standard_male_voices.append((f"🚹 {voice_name}", voice_id))
        
        # Build the final voice options in priority order
        # Premium voices first
        for name, voice_id in premium_female_voices:
            voice_options[name] = voice_id
        for name, voice_id in premium_male_voices:
            voice_options[name] = voice_id
            
        # Add separator if we have both premium and standard voices
        if (premium_female_voices or premium_male_voices) and (standard_female_voices or standard_male_voices):
            voice_options["━━━ Standard Voices ━━━"] = "separator"
            
        # Standard voices
        for name, voice_id in standard_female_voices:
            voice_options[name] = voice_id
        for name, voice_id in standard_male_voices:
            voice_options[name] = voice_id
            
        engine.stop()
        return voice_options
        
    except Exception as e:
        print(f"Error getting voices: {e}")
        return {"🤖 Auto (Best Available)": "auto", "🔧 Default System Voice": "default"}

def create_narrative_story(events, summary):
    """Create an ecosystem-specific 1-1.5 minute story using actual species and events"""
    
    # Target is approximately 180-270 words for 1-1.5 minutes at natural speech pace
    
    # Extract specific ecosystem information from summary and events
    environment_name = "this ecosystem"
    species_mentioned = []
    interactions_described = []
    environment_type = "natural habitat"
    
    # Parse the summary for environment context
    if summary and summary.strip():
        summary_lower = summary.lower()
        
        # Extract environment name from summary
        if "ecosystem summary for" in summary_lower:
            env_start = summary_lower.find("ecosystem summary for") + len("ecosystem summary for")
            env_end = summary_lower.find(":", env_start)
            if env_end == -1:
                env_end = summary_lower.find("\n", env_start)
            if env_end > env_start:
                environment_name = summary[env_start:env_end].strip()
        
        # Extract species names (look for patterns like "• SpeciesName (type):")
        import re
        species_pattern = r'[•\-\*]\s*([A-Z][a-zA-Z\s]+(?:Bird|Beetle|Fern|Moss|Flower|Grass|Tree|Fox|Mouse|Rabbit|Lizard|Spider|Butterfly|Ant|Fish|Frog|Snake))'
        found_species = re.findall(species_pattern, summary)
        species_mentioned = [species.strip() for species in found_species[:4]]  # Limit to first 4
        
        # Determine environment type
        if any(word in summary_lower for word in ['tropical', 'rainforest', 'jungle']):
            environment_type = "tropical rainforest"
        elif any(word in summary_lower for word in ['desert', 'arid', 'sand']):
            environment_type = "desert landscape"
        elif any(word in summary_lower for word in ['forest', 'woodland', 'trees']):
            environment_type = "forest ecosystem"
        elif any(word in summary_lower for word in ['alpine', 'mountain', 'peak']):
            environment_type = "mountain environment"
        elif any(word in summary_lower for word in ['marsh', 'wetland', 'water']):
            environment_type = "wetland habitat"
        elif any(word in summary_lower for word in ['cave', 'underground']):
            environment_type = "cave system"
    
    # Parse events for specific interactions
    if events and events.strip():
        event_lines = events.split('\n')
        for line in event_lines:
            if line.strip() and any(word in line.lower() for word in ['feeds on', 'competes with', 'grows', 'interacts', 'establishes', 'searches']):
                # Extract meaningful interaction descriptions
                clean_line = line.strip().replace('•', '').replace('-', '').strip()
                if len(clean_line) > 10:  # Only include substantial descriptions
                    interactions_described.append(clean_line)
        interactions_described = interactions_described[:3]  # Limit to first 3
    
    # Build the narrative story
    story_segments = []
    
    # Opening: Set the scene with the actual environment
    if environment_name != "this ecosystem":
        story_segments.append(f"In {environment_name}, a remarkable story unfolds.")
    else:
        story_segments.append(f"In this {environment_type}, a remarkable story unfolds.")
    
    # Introduction with species diversity
    if species_mentioned:
        if len(species_mentioned) == 1:
            story_segments.append(f"Here, the {species_mentioned[0]} has found its perfect home.")
        elif len(species_mentioned) == 2:
            story_segments.append(f"Here, the {species_mentioned[0]} and {species_mentioned[1]} share this vibrant space.")
        else:
            story_segments.append(f"Here, species like the {species_mentioned[0]}, {species_mentioned[1]}, and others create a living tapestry of life.")
    else:
        story_segments.append("Here, a diverse community of plants and animals has established itself.")
    
    # Main narrative with actual interactions
    if interactions_described:
        story_segments.append("Today's events tell a fascinating tale.")
        
        # Feature the most interesting interaction
        main_interaction = interactions_described[0]
        story_segments.append(f"We witness how {main_interaction.lower()}.")
        
        if len(interactions_described) > 1:
            story_segments.append(f"Meanwhile, {interactions_described[1].lower()}, showing the interconnected nature of this ecosystem.")
        
        if len(interactions_described) > 2:
            story_segments.append(f"And as the day progresses, {interactions_described[2].lower()}, completing a day full of natural activity.")
    else:
        # Fallback if no specific interactions
        story_segments.extend([
            "Today's events reveal the intricate dance of life.",
            "Each species plays its vital role in maintaining the delicate balance.",
            "From the smallest organisms to the most prominent features, every element contributes to this thriving ecosystem."
        ])
    
    # Environmental adaptation context
    if 'tropical' in environment_type:
        story_segments.append("The humid, warm conditions provide the perfect backdrop for rapid growth and vibrant interactions.")
    elif 'desert' in environment_type:
        story_segments.append("Despite the harsh conditions, life has found ingenious ways to thrive in this arid landscape.")
    elif 'forest' in environment_type:
        story_segments.append("The rich, layered habitat offers countless niches for different species to flourish.")
    elif 'mountain' in environment_type:
        story_segments.append("The challenging mountain environment has shaped hardy, resilient species.")
    elif 'wetland' in environment_type:
        story_segments.append("The water-rich environment supports an abundance of life in all its forms.")
    elif 'cave' in environment_type:
        story_segments.append("In this unique underground world, life has adapted to darkness in remarkable ways.")
    else:
        story_segments.append("The environmental conditions here have shaped each species' unique adaptations.")
    
    # Closing reflection
    story_segments.extend([
        "What we observe today is just one chapter in an ongoing story of survival, adaptation, and cooperation.",
        "This ecosystem reminds us that in nature, every day brings new challenges and new opportunities for life to flourish."
    ])
    
    # Join segments with natural pauses
    full_story = " ".join(story_segments)
    
    return full_story

def generate_narration_with_voice(summary, voice_selection, events=None):
    """Generate narration audio from summary text and events with voice selection"""
    if not summary or summary.strip() == "":
        return None
    
    # Create a compelling 1.5-minute narrative story
    narrative_text = create_narrative_story(events, summary)
    
    try:
        # Initialize the text-to-speech engine
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        
        # Set voice based on selection
        if voice_selection and voice_selection != "auto" and voice_selection != "default" and voice_selection != "separator":
            # Use the selected voice
            engine.setProperty('voice', voice_selection)
        elif voice_selection == "auto" and voices:
            # Auto-select the best available high-quality voice
            best_voice = None
            
            # Priority 1: Premium Windows voices
            for voice in voices:
                voice_name = voice.name.lower()
                if any(keyword in voice_name for keyword in ['zira desktop', 'hazel desktop', 'eva desktop']):
                    best_voice = voice.id
                    break
            
            # Priority 2: Microsoft premium voices
            if not best_voice:
                for voice in voices:
                    voice_name = voice.name.lower()
                    if 'microsoft' in voice_name and any(keyword in voice_name for keyword in ['zira', 'david', 'hazel', 'mark']):
                        best_voice = voice.id
                        break
            
            # Priority 3: Any female voice (generally more pleasant)
            if not best_voice:
                for voice in voices:
                    voice_name = voice.name.lower()
                    if any(keyword in voice_name for keyword in ['female', 'woman', 'zira', 'hazel', 'eva']):
                        best_voice = voice.id
                        break
            
            # Priority 4: Any male voice
            if not best_voice:
                for voice in voices:
                    voice_name = voice.name.lower()
                    if any(keyword in voice_name for keyword in ['male', 'man', 'david', 'mark']):
                        best_voice = voice.id
                        break
            
            if best_voice:
                engine.setProperty('voice', best_voice)
        
        # Enhanced speech properties for more natural sound
        current_rate = engine.getProperty('rate')
        current_volume = engine.getProperty('volume')
        
        # Optimize speech parameters for natural delivery (targeting 1.5 minutes)
        engine.setProperty('rate', max(140, min(current_rate * 0.9, 170)))  # Moderate pace for storytelling
        engine.setProperty('volume', min(current_volume * 1.1, 1.0))  # Slightly louder
        
        # Try to set additional properties for better quality (Windows SAPI specific)
        try:
            # Some Windows SAPI voices support these
            engine.setProperty('pitch', 0)  # Neutral pitch
            engine.setProperty('inflection', 50)  # Natural inflection
        except:
            pass
        
        # Preprocess narrative text for better pronunciation
        processed_narrative = narrative_text
        
        # Replace common abbreviations and technical terms for better pronunciation
        replacements = {
            'ecosystem': 'eco-system',
            'species': 'species',
            'biodiversity': 'bio-diversity',
            'symbiosis': 'sym-bi-o-sis',
            'photosynthesis': 'photo-synthesis',
            'decomposition': 'de-com-po-si-tion',
            'adaptation': 'a-dap-ta-tion',
            'evolution': 'e-vo-lu-tion'
        }
        
        for word, replacement in replacements.items():
            processed_narrative = processed_narrative.replace(word, replacement)
        
        # Add natural pauses for better storytelling rhythm
        processed_narrative = processed_narrative.replace('. ', '. ... ')
        processed_narrative = processed_narrative.replace(', ', ', .. ')
        processed_narrative = processed_narrative.replace(' ... ', ' ... ')  # Enhanced dramatic pauses
        
        # Create a temporary file for the audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_filename = temp_file.name
        temp_file.close()
        
        # Save the speech to file
        engine.save_to_file(processed_narrative, temp_filename)
        engine.runAndWait()
        
        # Clean up engine
        engine.stop()
        
        return temp_filename
        
    except Exception as e:
        print(f"Error generating narration: {e}")
        return None

def generate_narration(summary):
    """Backward compatibility wrapper"""
    return generate_narration_with_voice(summary, "auto", None)

def test_voice_sample(voice_selection):
    """Generate a test audio sample with the selected voice"""
    test_text = "Hello! This is a preview of how your ecosystem narration will sound. The voice will describe the fascinating interactions between species in your simulated environment."
    
    try:
        # Initialize the text-to-speech engine
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        
        # Set voice based on selection
        if voice_selection and voice_selection != "auto" and voice_selection != "default" and voice_selection != "separator":
            # Use the selected voice
            engine.setProperty('voice', voice_selection)
        elif voice_selection == "auto" and voices:
            # Auto-select the best available high-quality voice
            best_voice = None
            
            # Priority 1: Premium Windows voices
            for voice in voices:
                voice_name = voice.name.lower()
                if any(keyword in voice_name for keyword in ['zira desktop', 'hazel desktop', 'eva desktop']):
                    best_voice = voice.id
                    break
            
            # Priority 2: Microsoft premium voices
            if not best_voice:
                for voice in voices:
                    voice_name = voice.name.lower()
                    if 'microsoft' in voice_name and any(keyword in voice_name for keyword in ['zira', 'david', 'hazel', 'mark']):
                        best_voice = voice.id
                        break
            
            # Priority 3: Any female voice (generally more pleasant)
            if not best_voice:
                for voice in voices:
                    voice_name = voice.name.lower()
                    if any(keyword in voice_name for keyword in ['female', 'woman', 'zira', 'hazel', 'eva']):
                        best_voice = voice.id
                        break
            
            # Priority 4: Any male voice
            if not best_voice:
                for voice in voices:
                    voice_name = voice.name.lower()
                    if any(keyword in voice_name for keyword in ['male', 'man', 'david', 'mark']):
                        best_voice = voice.id
                        break
            
            if best_voice:
                engine.setProperty('voice', best_voice)
        
        # Enhanced speech properties for more natural sound
        current_rate = engine.getProperty('rate')
        current_volume = engine.getProperty('volume')
        
        # Optimize speech parameters for natural delivery
        engine.setProperty('rate', max(140, min(current_rate * 0.9, 170)))
        engine.setProperty('volume', min(current_volume * 1.1, 1.0))
        
        # Create a temporary file for the audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_filename = temp_file.name
        temp_file.close()
        
        # Save the speech to file
        engine.save_to_file(test_text, temp_filename)
        engine.runAndWait()
        
        # Clean up engine
        engine.stop()
        
        return temp_filename
        
    except Exception as e:
        print(f"Error generating test voice: {e}")
        return None

# Create the main Gradio interface
print("🚀 Creating main interface...")

# Get available voices for the dropdown
voice_options = get_available_voices()
voice_choices = [choice for choice in voice_options.keys() if choice != "separator"]
voice_values = [voice_options[choice] for choice in voice_choices]

# Create custom nature-themed color scheme with darker green and light blue mix
nature_theme = gr.themes.Soft().set(
    body_background_fill="#d4edda",  # Darker light green background
    background_fill_primary="#e8f5e8",  # Medium light green
    background_fill_secondary="#d6ebf5",  # Darker light blue
    block_background_fill="#f8f9fa",  # Off-white for content blocks
    button_primary_background_fill="#1e7e34",  # Darker forest green for primary buttons
    button_primary_background_fill_hover="#28a745",  # Medium green on hover
    button_primary_text_color="#ffffff",
    button_secondary_background_fill="#c3e6cb",  # Darker light green for secondary buttons
    button_secondary_background_fill_hover="#b3d7e6",  # Darker light blue on hover
    button_secondary_text_color="#155724"  # Darker green text
)

with gr.Blocks(title="Agentic Ecosystem Simulator", theme=nature_theme, css="""
/* Additional custom CSS for darker nature theme */
.gradio-container {
    background: linear-gradient(135deg, #c8e6c8 0%, #b8d4e8 50%, #d0e2f0 100%);
    min-height: 100vh;
}

/* Card-like styling for content blocks with darker accents */
.block {
    background: rgba(248, 249, 250, 0.95);
    border-radius: 8px;
    border: 1px solid #6c9a6c;
    box-shadow: 0 2px 8px rgba(28, 126, 52, 0.1);
}

/* Nature-themed headers with darker colors */
h1, h2, h3 {
    color: #155724;
    text-shadow: 1px 1px 2px rgba(28, 126, 52, 0.15);
}
""") as demo:
    gr.Markdown("""
    # 🌍 Agentic Ecosystem Simulator
    
    Welcome to the Text-Based Ecosystem Simulator! This application uses multiple AI models working together 
    through Modal cloud functions to create and simulate a living ecosystem through text.
    
    **How it works:**
    1. **Environment Analysis** - Your input is analyzed for environment type, climate, time, season & more
    2. **Species Generation** - AI creates plants and animals specifically adapted to your environment
    3. **Interaction Simulation** - AI simulates ecological interactions specific to your environment
    4. **Smart Summary** - Key events are summarized with environmental context
    5. **Audio Narration** - Natural voice synthesis brings your ecosystem to life
    
    **The more detailed your environment description, the more tailored your ecosystem will be!**
    
    🚀 **Status**: Using Modal deployment with enhanced visualization capabilities
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            environment_input = gr.Textbox(
                label="🌿 Room Environment Description (be specific and detailed!)",
                placeholder="e.g., 'tropical rainforest with morning mist and flowering vines', 'desert oasis with palm trees and rocky outcrops at sunset'",
                lines=3,
                value="temperate meadow in spring morning with wildflowers and gentle breeze"
            )
            
            simulate_btn = gr.Button("🚀 Simulate Ecosystem Day", variant="primary", size="lg")
            
            modal_status = gr.Textbox(
                label="🖥️ Modal Status",
                value="Click 'Check Modal' to see status",
                lines=4,
                interactive=False
            )
            check_modal_btn = gr.Button("🔍 Check Modal", variant="secondary")
            
        with gr.Column(scale=3):
            species_output = gr.JSON(
                label="🧬 Generated Species",
                show_label=True
            )
    
    # Visualization section - always show
    with gr.Row():
        visualization_output = gr.Image(
            label="🎬 Ecosystem Visualization Animation",
            show_label=True,
            interactive=False,
            height=400,
            type="filepath"  # Ensure Gradio treats the output as a file path
        )
    
    with gr.Row():
        with gr.Column():
            events_output = gr.Textbox(
                label="📅 Day's Events", 
                lines=8,
                show_label=True
            )
        
        with gr.Column():
            summary_output = gr.Textbox(
                label="📋 Ecosystem Summary",
                lines=4,
                show_label=True
            )
            
            voice_selection = gr.Dropdown(
                choices=voice_choices,
                value=voice_choices[0] if voice_choices else "🤖 Auto (Best Available)",
                label="🎭 Voice Selection",
                info="Choose between male and female voices for natural-sounding narration. Premium voices offer the most human-like quality."
            )
            with gr.Row():
                narrate_btn = gr.Button("🎙️ Generate Narration", variant="primary", size="sm")
                test_voice_btn = gr.Button("🔊 Test Voice", variant="secondary", size="sm")
            
            audio_output = gr.Audio(
                label="🎵 Narration",
                show_label=True
            )
    
    # Event handlers
    simulate_btn.click(
        fn=simulate_ecosystem_step,
        inputs=[environment_input],
        outputs=[species_output, events_output, summary_output, audio_output, visualization_output]
    )
    
    narrate_btn.click(
        fn=lambda summary, voice, events: generate_narration_with_voice(summary, voice_options.get(voice, "auto"), events),
        inputs=[summary_output, voice_selection, events_output],
        outputs=[audio_output]
    )
    
    test_voice_btn.click(
        fn=lambda voice: test_voice_sample(voice_options.get(voice, "auto")),
        inputs=[voice_selection],
        outputs=[audio_output]
    )
    
    check_modal_btn.click(
        fn=check_modal_deployment,
        outputs=[modal_status]
    )
    
    # Add example environments
    gr.Markdown("""
    ### 💡 Detailed Environments to Try:
    
    **Try adding environmental details like:**
    - Time of day: morning, afternoon, evening, night
    - Season: spring, summer, autumn, winter
    - Weather: misty, sunny, rainy, cloudy, stormy
    - Features: rocky, sandy, flowering, foggy, lush, sparse
    
    **Example environments with rich details:**
    - tropical rainforest with morning mist and flowering plants
    - desert oasis with palm trees and rocky outcrops at sunset  
    - temperate forest clearing in autumn with golden leaves
    - alpine meadow with wildflowers on a spring morning
    - wetland marsh with reeds and shallow water during summer evening
    - volcanic island with unique flora adapting to the harsh terrain
    - underground cave system with phosphorescent fungi and still pools
    """)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌍 AGENTIC ECOSYSTEM SIMULATOR - ENHANCED VERSION")
    print("="*60)
    print("\n🚀 Starting cloud-based orchestrator interface...")
    print("\n📋 SETUP STATUS:")
    print("✅ Modal functions deployed to cloud")
    print("✅ Enhanced version with environment-aware features")
    
    if HAS_VISUALIZATION:
        print("✅ Visualization module loaded - animated simulations enabled")
    else:
        print("⚠️ Visualization module not available - install diffusers, torch, etc. to enable")
        
    print("\n✨ Ready to simulate! Try: 'temperate meadow in spring'")
    print("="*60)
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7862,
        share=True,
        show_error=True
    )
