import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from ..config import Config

class CompanyService:
    """Service for managing company data"""
    
    def __init__(self):
        self.companies_file = Config.COMPANIES_FILE
        self.scraped_dir = Config.SCRAPED_DIR
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.companies_file), exist_ok=True)
        os.makedirs(self.scraped_dir, exist_ok=True)
    
    def load_companies(self) -> List[Dict[str, Any]]:
        """Load companies data from file"""
        if os.path.exists(self.companies_file):
            try:
                with open(self.companies_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading companies: {e}")
                return []
        return []
    
    def save_companies(self, companies: List[Dict[str, Any]]) -> bool:
        """Save companies data to file"""
        try:
            with open(self.companies_file, 'w') as f:
                json.dump(companies, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving companies: {e}")
            return False
    
    def add_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new company"""
        companies = self.load_companies()
        
        # Check if company already exists
        existing_company = next(
            (c for c in companies if c['name'].lower() == company_data['name'].lower()), 
            None
        )
        
        if existing_company:
            # Update existing company
            existing_company.update(company_data)
            existing_company['updated_at'] = datetime.now().isoformat()
        else:
            # Add new company
            new_company = {
                'id': self._generate_company_id(),
                'name': company_data['name'],
                'industry': company_data.get('industry', ''),
                'pitch': company_data.get('pitch', ''),
                'scraped_data': company_data.get('scraped_data'),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            companies.append(new_company)
        
        if self.save_companies(companies):
            return companies[-1] if not existing_company else existing_company
        else:
            raise Exception("Failed to save company data")
    
    def get_company(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific company by name"""
        companies = self.load_companies()
        return next(
            (c for c in companies if c['name'].lower() == company_name.lower()), 
            None
        )
    
    def update_company(self, company_name: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a company"""
        companies = self.load_companies()
        company = self.get_company(company_name)
        
        if company:
            company.update(updates)
            company['updated_at'] = datetime.now().isoformat()
            
            if self.save_companies(companies):
                return company
        
        return None
    
    def delete_company(self, company_name: str) -> bool:
        """Delete a company"""
        companies = self.load_companies()
        companies = [c for c in companies if c['name'].lower() != company_name.lower()]
        
        return self.save_companies(companies)
    
    def save_scraped_data(self, company_name: str, data: Dict[str, Any]) -> str:
        """Save scraped data for a company"""
        company_dir = os.path.join(self.scraped_dir, company_name.lower().replace(' ', '_'))
        os.makedirs(company_dir, exist_ok=True)
        
        file_path = os.path.join(company_dir, "scraped_data.json")
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return file_path
    
    def load_scraped_data(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Load scraped data for a company"""
        company_dir = os.path.join(self.scraped_dir, company_name.lower().replace(' ', '_'))
        file_path = os.path.join(company_dir, "scraped_data.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading scraped data: {e}")
                return None
        return None
    
    def _generate_company_id(self) -> str:
        """Generate a unique company ID"""
        import uuid
        return str(uuid.uuid4()) 