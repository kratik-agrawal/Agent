from flask import Blueprint, request, jsonify
from ..services.company_service import CompanyService
from ..services.perplexity_service import PerplexityService
from ..services.prompt_service import PromptService
from datetime import datetime

# Create blueprint
company_bp = Blueprint('company', __name__, url_prefix='/api/company')

# Initialize services
company_service = CompanyService()
perplexity_service = PerplexityService()
prompt_service = PromptService()

@company_bp.route('/companies', methods=['GET'])
def get_companies():
    """Get all companies"""
    try:
        companies = company_service.load_companies()
        return jsonify(companies)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@company_bp.route('/companies/<company_name>', methods=['GET'])
def get_company(company_name):
    """Get a specific company"""
    try:
        company = company_service.get_company(company_name)
        if company:
            return jsonify(company)
        else:
            return jsonify({"error": "Company not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@company_bp.route('/companies', methods=['POST'])
def create_company():
    """Create a new company"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"error": "Company name is required"}), 400
        
        company = company_service.add_company(data)
        return jsonify(company), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@company_bp.route('/companies/<company_name>', methods=['PUT'])
def update_company(company_name):
    """Update a company"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Update data is required"}), 400
        
        company = company_service.update_company(company_name, data)
        if company:
            return jsonify(company)
        else:
            return jsonify({"error": "Company not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@company_bp.route('/companies/<company_name>', methods=['DELETE'])
def delete_company(company_name):
    """Delete a company"""
    try:
        success = company_service.delete_company(company_name)
        if success:
            return jsonify({"message": "Company deleted successfully"})
        else:
            return jsonify({"error": "Company not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@company_bp.route('/companies/<company_name>/scraped-data', methods=['GET'])
def get_scraped_data(company_name):
    """Get scraped data for a company"""
    try:
        data = company_service.load_scraped_data(company_name)
        if data:
            return jsonify(data)
        else:
            return jsonify({"error": "Scraped data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@company_bp.route('/research/<company_name>', methods=['GET'])
def research_company(company_name):
    """Get Perplexity research for a specific company"""
    try:
        # Load the sales research prompt
        prompt_template = prompt_service.load_prompt("sales_research_prompt")
        if not prompt_template:
            return jsonify({"error": "Sales research prompt not found"}), 404
        
        # Get research from Perplexity
        result = perplexity_service.research_company(company_name, prompt_template)
        
        if result.get("success"):
            return jsonify({
                "status": "success",
                "company_name": company_name,
                "research": result.get("content"),
                "model": result.get("model", "unknown"),
                "usage": result.get("usage", {}),
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "error",
                "company_name": company_name,
                "error": result.get("error", "Unknown error")
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to research company",
            "error": str(e)
        }), 500 