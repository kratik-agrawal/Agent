// API client configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000'

// Types
export interface Company {
  id: string
  name: string
  industry: string
  pitch?: string
  scraped_data?: ScrapedData
  created_at: string
  updated_at: string
}

export interface CompanyFormData {
  company_name: string
  industry: string
  content: string
}

export interface ScrapeJob {
  job_id: string
  status: string
  company_name: string
  created_at: string
  error?: string | null
  result?: ScrapedData | null
}

export interface ScrapedData {
  job_id: string
  firecrawl_job_id: string
  url: string
  company_name: string
  scraped_at: string
  processed_content: ProcessedContent[]
  content_count: number
  perplexity_research?: PerplexityResearch
  status: string
}

export interface ProcessedContent {
  type: string
  url: string | null
  content: string
}

export interface PerplexityResearch {
  success: boolean
  content: string
  model: string
  usage: Record<string, unknown>
}

export interface BuyerPersona {
  id: string
  title: string
  role: string
  department: string
  priorities: string[]
  pain_points: string[]
  decision_criteria: string[]
  influence_level: 'high' | 'medium' | 'low'
  budget_authority: 'high' | 'medium' | 'low'
  technical_expertise: 'high' | 'medium' | 'low'
  company_name: string
  created_at: string
}

export interface PersonaGenerationRequest {
  company_name: string
  industry: string
  scraped_content?: string
  ai_research?: string
}

export interface PersonaGenerationResponse {
  personas: BuyerPersona[]
  analysis: string
  confidence_score: number
}

export interface ApiResponse<T> {
  data?: T
  error?: string
  status: number
}

// API client class
class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        return {
          error: errorData.error || `HTTP error! status: ${response.status}`,
          status: response.status,
        }
      }

      const data = await response.json()
      return {
        data,
        status: response.status,
      }
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      }
    }
  }

  // Company endpoints
  async getCompanies(): Promise<ApiResponse<Company[]>> {
    return this.request<Company[]>('/api/pitch/companies')
  }

  async getCompany(companyName: string): Promise<ApiResponse<Company>> {
    return this.request<Company>(`/api/pitch/companies/${encodeURIComponent(companyName)}`)
  }

  async createCompany(companyData: CompanyFormData): Promise<ApiResponse<Company>> {
    return this.request<Company>('/api/pitch/ingest/manual', {
      method: 'POST',
      body: JSON.stringify(companyData),
    })
  }

  async updateCompany(companyName: string, updates: Partial<Company>): Promise<ApiResponse<Company>> {
    return this.request<Company>(`/api/pitch/companies/${encodeURIComponent(companyName)}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    })
  }

  async deleteCompany(companyName: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/api/pitch/companies/${encodeURIComponent(companyName)}`, {
      method: 'DELETE',
    })
  }

  async getScrapedData(companyName: string): Promise<ApiResponse<ScrapedData>> {
    return this.request<ScrapedData>(`/api/pitch/companies/${encodeURIComponent(companyName)}/scraped-data`)
  }

  async researchCompany(companyName: string): Promise<ApiResponse<PerplexityResearch>> {
    return this.request<PerplexityResearch>(`/api/company/research/${encodeURIComponent(companyName)}`)
  }

  // Scraping endpoints
  async startScrape(url: string, companyName: string): Promise<ApiResponse<{ job_id: string; status: string; company_name: string }>> {
    return this.request<{ job_id: string; status: string; company_name: string }>('/api/pitch/ingest/scrape', {
      method: 'POST',
      body: JSON.stringify({ url, company_name: companyName }),
    })
  }

  async getScrapeStatus(jobId: string): Promise<ApiResponse<{ status: string; error?: string; result?: ScrapedData }>> {
    return this.request<{ status: string; error?: string; result?: ScrapedData }>(`/api/pitch/ingest/scrape/${jobId}/status`)
  }

  async getScrapeResult(jobId: string): Promise<ApiResponse<ScrapedData>> {
    return this.request<ScrapedData>(`/api/pitch/ingest/scrape/${jobId}/result`)
  }

  // Prompt endpoints
  async getPrompts(): Promise<ApiResponse<Array<{ name: string; filename: string }>>> {
    return this.request<Array<{ name: string; filename: string }>>('/api/prompts/')
  }

  async getPrompt(promptName: string): Promise<ApiResponse<{ name: string; content: string }>> {
    return this.request<{ name: string; content: string }>(`/api/prompts/${promptName}`)
  }

  async updatePrompt(promptName: string, content: string): Promise<ApiResponse<{ message: string; name: string }>> {
    return this.request<{ message:string; name: string }>(`/api/prompts/${promptName}`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    })
  }

  async deletePrompt(promptName: string): Promise<ApiResponse<{ message: string; name: string }>> {
    return this.request<{ message: string; name: string }>(`/api/prompts/${promptName}`, {
      method: 'DELETE',
    })
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    return this.request<{ status: string; timestamp: string }>('/health')
  }

  // Persona generation endpoints
  async generatePersonas(request: PersonaGenerationRequest): Promise<ApiResponse<PersonaGenerationResponse>> {
    return this.request<PersonaGenerationResponse>('/api/personas/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getPersonas(companyName: string): Promise<ApiResponse<BuyerPersona[]>> {
    return this.request<BuyerPersona[]>(`/api/personas/${encodeURIComponent(companyName)}`)
  }
}

// Export singleton instance
export const apiClient = new ApiClient(API_BASE_URL) 