import xml.etree.ElementTree as ET
import yaml
import sys

def modify_sdf(sdf_path, config_path, output_path):
    # 1. Load the Configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # 2. Parse the SDF (XML)
    tree = ET.parse(sdf_path)
    root = tree.getroot()
    world = root.find('world')

    if world is None:
        print("Error: No <world> tag found in SDF.")
        sys.exit(1)

    # --- RULE 1: Remove Specific Models ---
    models_to_remove = config.get('remove_models', [])
    for model in world.findall('model'):
        if model.get('name') in models_to_remove:
            world.remove(model)
            print(f"Removed model: {model.get('name')}")

    # --- RULE 2: Adjust Light Intensity ---
    intensity_multiplier = config.get('light_intensity_multiplier', 1.0)
    if intensity_multiplier != 1.0:
        for light in world.findall('light'):
            intensity_tag = light.find('intensity')
            if intensity_tag is not None and intensity_tag.text:
                # 1. Read the existing value and convert it to a float
                existing_val = float(intensity_tag.text)

                # 2. Multiply by your config multiplier
                new_val = existing_val * intensity_multiplier

                # 3. Write it back as a string (formatting to 3 decimal places keeping the SDF clean)
                intensity_tag.text = f"{new_val:.2f}"
                print(f"Updated light '{light.get('name')}' intensity to {intensity_tag.text}")

    # --- RULE 3: Convert .glb to .dae in URIs ---
    if config.get('convert_glb_to_dae', True):
        # root.iter('uri') finds <uri> tags anywhere in the entire XML tree
        for uri in root.iter('uri'):
            # Check if the tag has text and if it ends with the target extension
            if uri.text and uri.text.endswith('.glb'):
                old_text = uri.text
            
                # Replace the extension safely
                uri.text = old_text.replace('.glb', '.dae')
            
                print(f"Updated URI extension: {old_text} -> {uri.text}")

    # 3. Save the Modified SDF
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print(f"Modified SDF saved to {output_path}")

if __name__ == "__main__":
    # Example usage: python3 sdf_modifier.py /tmp/aic.sdf config.yaml /tmp/aic_modified.sdf
    if len(sys.argv) != 4:
        print("Usage: python3 sdf_modifier.py <input.sdf> <config.yaml> <output.sdf>")
        sys.exit(1)
    
    modify_sdf(sys.argv[1], sys.argv[2], sys.argv[3])