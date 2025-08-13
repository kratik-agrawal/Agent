import os
from typing import List, Dict, Optional
from ..config import Config

class PromptService:
    """Service for managing prompts"""
    
    def __init__(self):
        self.prompts_dir = Config.PROMPTS_DIR
        os.makedirs(self.prompts_dir, exist_ok=True)
    
    def load_prompt(self, prompt_name: str) -> Optional[str]:
        """Load a prompt from the prompts directory"""
        prompt_path = os.path.join(self.prompts_dir, f"{prompt_name}.txt")
        if os.path.exists(prompt_path):
            try:
                with open(prompt_path, 'r') as f:
                    return f.read()
            except IOError as e:
                print(f"Error loading prompt {prompt_name}: {e}")
                return None
        return None
    
    def save_prompt(self, prompt_name: str, content: str) -> bool:
        """Save a prompt to the prompts directory"""
        prompt_path = os.path.join(self.prompts_dir, f"{prompt_name}.txt")
        try:
            with open(prompt_path, 'w') as f:
                f.write(content)
            return True
        except IOError as e:
            print(f"Error saving prompt {prompt_name}: {e}")
            return False
    
    def list_prompts(self) -> List[Dict[str, str]]:
        """List all available prompts"""
        prompts = []
        try:
            for filename in os.listdir(self.prompts_dir):
                if filename.endswith('.txt'):
                    prompt_name = filename[:-4]  # Remove .txt extension
                    prompts.append({
                        "name": prompt_name,
                        "filename": filename
                    })
        except OSError as e:
            print(f"Error listing prompts: {e}")
        
        return prompts
    
    def delete_prompt(self, prompt_name: str) -> bool:
        """Delete a prompt"""
        prompt_path = os.path.join(self.prompts_dir, f"{prompt_name}.txt")
        try:
            if os.path.exists(prompt_path):
                os.remove(prompt_path)
                return True
            return False
        except OSError as e:
            print(f"Error deleting prompt {prompt_name}: {e}")
            return False
    
    def prompt_exists(self, prompt_name: str) -> bool:
        """Check if a prompt exists"""
        prompt_path = os.path.join(self.prompts_dir, f"{prompt_name}.txt")
        return os.path.exists(prompt_path) 