from flask import Blueprint, request, jsonify
from ..services.prompt_service import PromptService

# Create blueprint
prompt_bp = Blueprint('prompt', __name__, url_prefix='/api/prompts')

# Initialize service
prompt_service = PromptService()

@prompt_bp.route('/', methods=['GET'])
def list_prompts():
    """List all available prompts"""
    try:
        prompts = prompt_service.list_prompts()
        return jsonify(prompts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prompt_bp.route('/<prompt_name>', methods=['GET'])
def get_prompt(prompt_name):
    """Get a specific prompt"""
    try:
        content = prompt_service.load_prompt(prompt_name)
        if content is None:
            return jsonify({"error": "Prompt not found"}), 404
        
        return jsonify({
            "name": prompt_name,
            "content": content
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prompt_bp.route('/<prompt_name>', methods=['POST'])
def update_prompt(prompt_name):
    """Update or create a prompt"""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"error": "Content is required"}), 400
        
        content = data['content']
        success = prompt_service.save_prompt(prompt_name, content)
        
        if success:
            return jsonify({
                "message": "Prompt updated successfully",
                "name": prompt_name
            })
        else:
            return jsonify({"error": "Failed to save prompt"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@prompt_bp.route('/<prompt_name>', methods=['DELETE'])
def delete_prompt(prompt_name):
    """Delete a prompt"""
    try:
        success = prompt_service.delete_prompt(prompt_name)
        if success:
            return jsonify({
                "message": "Prompt deleted successfully",
                "name": prompt_name
            })
        else:
            return jsonify({"error": "Prompt not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500 