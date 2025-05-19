from pathlib import Path
import yaml
import os


def get_config(config_filename="config.yaml"):
    """
    Read a configuration file from the ai-research root directory.
    
    Parameters:
    -----------
    config_filename : str
        Name of the config file (default: config.yaml)
        
    Returns:
    --------
    dict
        Configuration data
    """
    # Find the project root (ai-research directory)
    current_path = Path(os.getcwd()).resolve()
    
    # Traverse up until we find the ai-research directory
    # (assuming we're somewhere within the ai-research project)
    root_dir = None
    for path in [current_path] + list(current_path.parents):
        if (path / ".git").exists() and (path.name == "ai-research" or path.stem == "ai-research"):
            root_dir = path
            break
    
    if not root_dir:
        raise FileNotFoundError("Could not find ai-research root directory")
    
    # Construct path to the config file
    config_path = root_dir / config_filename
    
    # Open and read the file
    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_path}")
        raise
    except Exception as e:
        print(f"An error occurred while reading config: {e}")
        raise