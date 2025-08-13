# Architecture Overview

This document outlines the clean, organized architecture of our Company Research Platform.

## Project Structure

```
├── api/                          # Backend API (Flask)
│   ├── config.py                # Configuration management
│   ├── app.py                   # Main Flask application
│   ├── services/                # Business logic layer
│   │   ├── company_service.py   # Company data management
│   │   ├── prompt_service.py    # Prompt management
│   │   └── perplexity_service.py # Perplexity API integration
│   ├── routes/                  # API route definitions
│   │   ├── company_routes.py    # Company-related endpoints
│   │   └── prompt_routes.py     # Prompt-related endpoints
│   ├── data/                    # Data storage
│   ├── prompts/                 # Prompt templates
│   └── requirements.txt         # Python dependencies
├── src/                         # Frontend (Next.js)
│   ├── app/                     # Next.js app directory
│   │   ├── page.tsx            # Main page component
│   │   ├── hooks/              # Custom React hooks
│   │   │   └── useCompanies.ts # Company management hook
│   │   └── layout.tsx          # Root layout
│   ├── components/              # Reusable UI components
│   │   ├── ui/                 # Base UI components
│   │   ├── CompanyForm.tsx     # Company creation form
│   │   └── CompanyList.tsx     # Company list display
│   └── lib/                     # Utility libraries
│       └── api.ts              # API client layer
├── package.json                 # Frontend dependencies
└── README.md                    # Project documentation
```

## Backend Architecture

### 1. Configuration Management (`config.py`)
- Centralized configuration using environment variables
- Support for different environments (dev, staging, prod)
- Validation of required configuration values
- CORS configuration management

### 2. Service Layer (`services/`)
- **CompanyService**: Handles all company-related operations
  - CRUD operations for companies
  - Scraped data management
  - File I/O operations
  
- **PromptService**: Manages prompt templates
  - Load, save, list, and delete prompts
  - File-based storage system
  
- **PerplexityService**: Integrates with Perplexity AI API
  - Company research functionality
  - API error handling and retry logic
  - Connection testing

### 3. Route Layer (`routes/`)
- **Company Routes**: `/api/company/*`
  - GET `/companies` - List all companies
  - POST `/companies` - Create new company
  - GET `/companies/<name>` - Get specific company
  - PUT `/companies/<name>` - Update company
  - DELETE `/companies/<name>` - Delete company
  - GET `/companies/<name>/scraped-data` - Get scraped data
  - GET `/research/<name>` - Research company with Perplexity
  
- **Prompt Routes**: `/api/prompts/*`
  - GET `/` - List all prompts
  - GET `/<name>` - Get specific prompt
  - POST `/<name>` - Create/update prompt
  - DELETE `/<name>` - Delete prompt

### 4. Application Factory (`app.py`)
- Uses Flask factory pattern for better testing and configuration
- Registers blueprints for organized routing
- Configures CORS and error handling
- Health check endpoint

## Frontend Architecture

### 1. Component Structure
- **CompanyForm**: Handles company creation and updates
- **CompanyList**: Displays companies in a grid layout
- **UI Components**: Reusable base components using shadcn/ui

### 2. State Management
- **useCompanies Hook**: Custom hook for company state management
  - Loading states
  - Error handling
  - CRUD operations
  - Automatic data refresh

### 3. API Layer (`lib/api.ts`)
- Centralized API client with TypeScript interfaces
- Consistent error handling
- Request/response typing
- Environment-based configuration

### 4. Routing
- Tab-based navigation between companies list and add company form
- Clean URL structure
- Responsive design

## Key Benefits of This Architecture

### 1. **Separation of Concerns**
- Backend logic separated into services
- Frontend components are focused and reusable
- API layer abstracts backend communication

### 2. **Maintainability**
- Clear file organization
- Consistent naming conventions
- Modular service architecture

### 3. **Scalability**
- Easy to add new services
- Blueprint-based routing
- Component-based frontend

### 4. **Testing**
- Services can be tested independently
- Frontend components are isolated
- API layer can be mocked

### 5. **Configuration Management**
- Environment-based configuration
- Centralized API keys and settings
- Easy deployment configuration

## Environment Variables

Create a `.env` file in the `api/` directory:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
FLASK_PORT=5000

# API Keys
PERPLEXITY_API_KEY=your-perplexity-api-key-here
FIRECRAWL_API_KEY=your-firecrawl-api-key-here

# Data Directories
DATA_DIR=data
PROMPTS_DIR=prompts

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Getting Started

### Backend
```bash
cd api
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
npm install
npm run dev
```

## Future Enhancements

1. **Database Integration**: Replace file-based storage with PostgreSQL
2. **Authentication**: Add user management and JWT tokens
3. **Caching**: Implement Redis for performance optimization
4. **Monitoring**: Add logging and metrics collection
5. **Testing**: Comprehensive test suite for all layers
6. **Deployment**: Docker containerization and CI/CD pipeline 