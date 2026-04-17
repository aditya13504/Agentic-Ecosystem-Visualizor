import modal
import json
import random

# Create a Modal app
app = modal.App("agentic-ecosystem-simple")

# Simple image without image processing dependencies
simple_image = modal.Image.debian_slim().pip_install("requests")

# ------------------------------------------------------
# LOCAL HELPER FUNCTIONS (Not Modal functions)
# ------------------------------------------------------
def analyze_environment(environment_text):
    """Extract detailed features from the environment description."""
    env_features = {
        "type": "temperate",  # default
        "climate": "moderate",
        "moisture": "medium",
        "light": "bright",
        "terrain": "flat",
        "time_of_day": "day",
        "season": "spring", 
        "keywords": []
    }
    
    text_lower = environment_text.lower()
    
    # Environment types
    env_types = {
        "tropical": ["tropical", "rainforest", "jungle", "humid"],
        "desert": ["desert", "arid", "sand", "dry", "cactus"],
        "arctic": ["arctic", "cold", "snow", "ice", "frozen"],
        "aquatic": ["lake", "pond", "river", "stream", "water"],
        "mountain": ["mountain", "alpine", "peak", "high altitude"],
        "grassland": ["grassland", "prairie", "meadow", "plain"],
        "forest": ["forest", "woodland", "trees", "canopy"],
        "cave": ["cave", "underground", "dark", "cavern"]
    }
    
    for env_type, keywords in env_types.items():
        if any(keyword in text_lower for keyword in keywords):
            env_features["type"] = env_type
            break
    
    # Climate assessment
    if any(word in text_lower for word in ["hot", "warm", "tropical", "humid"]):
        env_features["climate"] = "hot"
    elif any(word in text_lower for word in ["cold", "cool", "arctic", "frozen"]):
        env_features["climate"] = "cold"
    else:
        env_features["climate"] = "moderate"
    
    # Moisture levels
    if any(word in text_lower for word in ["humid", "wet", "moist", "rain", "water"]):
        env_features["moisture"] = "high"
    elif any(word in text_lower for word in ["dry", "arid", "desert"]):
        env_features["moisture"] = "low"
    else:
        env_features["moisture"] = "medium"
    
    # Light conditions
    if any(word in text_lower for word in ["dark", "cave", "underground", "night"]):
        env_features["light"] = "dim"
    elif any(word in text_lower for word in ["bright", "sunny", "open"]):
        env_features["light"] = "bright"
    else:
        env_features["light"] = "moderate"
    
    # Extract keywords for species generation
    env_features["keywords"] = [word for word in text_lower.split() if len(word) > 3]
    
    return env_features

def local_generate_species(environment: str, count: int = 6):
    """Generate species based on environment analysis (local version)."""
    
    env_features = analyze_environment(environment)
    species_list = []
    
    # Generate plants (60% of species)
    plant_count = max(1, int(count * 0.6))
    
    # Environment-specific plant templates
    plant_templates = {
        "tropical": [
            {"name": "Broad-leaf Fern", "type": "plant", "description": "Large tropical fern with broad fronds"},
            {"name": "Jungle Vine", "type": "plant", "description": "Climbing vine with colorful flowers"},
            {"name": "Palm Frond", "type": "plant", "description": "Tall palm with fan-shaped leaves"}
        ],
        "desert": [
            {"name": "Barrel Cactus", "type": "plant", "description": "Round cactus that stores water"},
            {"name": "Desert Sage", "type": "plant", "description": "Hardy shrub with silver leaves"},
            {"name": "Prickly Pear", "type": "plant", "description": "Flat-padded cactus with bright flowers"}
        ],
        "arctic": [
            {"name": "Arctic Moss", "type": "plant", "description": "Low-growing moss adapted to cold"},
            {"name": "Tundra Grass", "type": "plant", "description": "Hardy grass that survives freezing"},
            {"name": "Ice Flower", "type": "plant", "description": "Small flower that blooms in snow"}
        ],
        "forest": [
            {"name": "Oak Sapling", "type": "plant", "description": "Young oak tree with broad leaves"},
            {"name": "Forest Moss", "type": "plant", "description": "Soft moss covering forest floor"},
            {"name": "Wild Fern", "type": "plant", "description": "Delicate fern growing in shade"}
        ]
    }
    
    # Get templates for environment type
    templates = plant_templates.get(env_features["type"], plant_templates["forest"])
    
    # Generate plants
    for i in range(plant_count):
        base_template = templates[i % len(templates)]
        plant = {
            "name": f"{env_features['climate'].title()} {base_template['name']}",
            "type": "plant",
            "description": f"{base_template['description']} adapted to {env_features['climate']} {env_features['type']} conditions",
            "habitat": f"{env_features['type']} with {env_features['moisture']} moisture and {env_features['light']} light",
            "behavior": f"Grows in {env_features['climate']} conditions, thrives in {env_features['light']} light",
            "need": f"{env_features['moisture']} moisture levels"
        }
        species_list.append(plant)
    
    # Generate animals (40% of species)
    animal_count = count - plant_count
    
    animal_templates = {
        "tropical": [
            {"name": "Colorful Bird", "type": "animal", "description": "Bright tropical bird"},
            {"name": "Tree Frog", "type": "animal", "description": "Small amphibian living in trees"}
        ],
        "desert": [
            {"name": "Desert Lizard", "type": "animal", "description": "Heat-adapted reptile"},
            {"name": "Sand Mouse", "type": "animal", "description": "Small rodent that burrows"}
        ],
        "arctic": [
            {"name": "Snow Hare", "type": "animal", "description": "White rabbit adapted to cold"},
            {"name": "Arctic Fox", "type": "animal", "description": "Small predator with thick fur"}
        ],
        "forest": [
            {"name": "Forest Squirrel", "type": "animal", "description": "Agile tree-dwelling rodent"},
            {"name": "Woodland Bird", "type": "animal", "description": "Small songbird living in trees"}
        ]
    }
    
    animal_temps = animal_templates.get(env_features["type"], animal_templates["forest"])
    
    for i in range(animal_count):
        base_template = animal_temps[i % len(animal_temps)]
        animal = {
            "name": f"{env_features['season'].title()} {base_template['name']}",
            "type": "animal", 
            "description": f"{base_template['description']} active during {env_features['time_of_day']}",
            "habitat": f"{env_features['type']} environment with {env_features['terrain']} terrain",
            "behavior": f"Forages during {env_features['time_of_day']}, seeks {env_features['climate']} conditions",
            "need": f"shelter and food in {env_features['type']} habitat"
        }
        species_list.append(animal)
    
    return species_list

def local_simulate_interactions(species_list, environment):
    """Simulate realistic interactions between species."""
    
    interactions = []
    env_features = analyze_environment(environment)
    
    # Create interaction scenarios based on environment
    if len(species_list) < 2:
        return ["The ecosystem is too sparse for meaningful interactions."]
    
    plants = [s for s in species_list if s["type"] == "plant"]
    animals = [s for s in species_list if s["type"] == "animal"]
    
    # Plant-animal interactions
    if plants and animals:
        plant = random.choice(plants)
        animal = random.choice(animals)
        interactions.append(f"The {animal['name']} finds shelter beneath the {plant['name']}, creating a symbiotic relationship.")
    
    # Environmental interactions
    if env_features["climate"] == "hot":
        interactions.append(f"During the hot {env_features['time_of_day']}, species seek shade and conserve energy.")
    elif env_features["climate"] == "cold":
        interactions.append(f"The cold conditions force species to cluster together for warmth.")
    
    # Competition for resources
    if len(species_list) >= 3:
        competitors = random.sample(species_list, 2)
        interactions.append(f"The {competitors[0]['name']} and {competitors[1]['name']} compete for limited resources in the {env_features['type']} habitat.")
    
    # Seasonal behaviors
    interactions.append(f"As {env_features['season']} progresses, species adapt their behavior to the changing {env_features['type']} environment.")
    
    # Random positive interaction
    if len(species_list) >= 2:
        pair = random.sample(species_list, 2)
        interactions.append(f"The {pair[0]['name']} and {pair[1]['name']} form an unexpected alliance, helping each other survive in the {env_features['climate']} conditions.")
    
    return interactions

def local_generate_summary(species_list, interactions, environment):
    """Generate a narrative summary of the ecosystem."""
    
    env_features = analyze_environment(environment)
    
    summary = f"In this {env_features['climate']} {env_features['type']} environment, "
    summary += f"a diverse ecosystem has emerged with {len(species_list)} unique species. "
    
    plants = [s for s in species_list if s["type"] == "plant"]
    animals = [s for s in species_list if s["type"] == "animal"]
    
    if plants:
        summary += f"The {len(plants)} plant species form the foundation of this ecosystem, "
        summary += f"adapted to {env_features['light']} light and {env_features['moisture']} moisture conditions. "
    
    if animals:
        summary += f"The {len(animals)} animal species have evolved behaviors suited to the {env_features['terrain']} terrain "
        summary += f"and {env_features['time_of_day']} activity patterns. "
    
    summary += f"Throughout the {env_features['season']} season, these species engage in {len(interactions)} "
    summary += f"different types of interactions, creating a complex web of relationships that sustains the ecosystem."
    
    return summary

# Removed visual components (Google Images Search Integration)

# ------------------------------------------------------
# MODAL FUNCTIONS (These are the deployed functions)
# ------------------------------------------------------

@app.function(image=simple_image)
def simulate_ecosystem(environment: str):
    """Main function to simulate a complete text-based ecosystem."""
    
    try:
        print(f"Starting ecosystem simulation for: {environment}")
        
        # Step 1: Generate species (using local function)
        print("Generating species...")
        species_list = local_generate_species(environment, 6)
        
        # Step 2: Simulate interactions (using local function)
        print("Simulating interactions...")
        interactions = local_simulate_interactions(species_list, environment)
        
        # Step 3: Generate summary (using local function)
        print("Generating summary...")
        summary = local_generate_summary(species_list, interactions, environment)
        
        # Format events as text
        events_text = "🌿 Daily Ecosystem Events:\n\n"
        for i, interaction in enumerate(interactions, 1):
            events_text += f"{i}. {interaction}\n\n"
        
        print("Ecosystem simulation completed successfully!")
        
        return {
            'species': species_list,
            'images': [],  # No images in text-only version
            'events': events_text,
            'summary': summary,
            'audio': None,  # No audio generation in simple version
            'error': None
        }
        
    except Exception as e:
        print(f"Error in ecosystem simulation: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'species': [],
            'images': [],
            'events': f"Error: {str(e)}",
            'summary': f"Simulation failed: {str(e)}",
            'audio': None,
            'error': str(e)
        }

@app.function(image=simple_image)
def generate_species(environment: str, count: int = 6):
    """Generate species based on environment analysis."""
    return local_generate_species(environment, count)

@app.function(image=simple_image)
def simulate_interactions(species_list, environment):
    """Simulate interactions between species."""
    return local_simulate_interactions(species_list, environment)

@app.function(image=simple_image)
def generate_summary(species_list, interactions, environment):
    """Generate a narrative summary of the ecosystem."""
    return local_generate_summary(species_list, interactions, environment)
