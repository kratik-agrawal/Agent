"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { Breadcrumb } from "@/components/ui/breadcrumb"
import { 
  ArrowLeft, 
  Building2, 
  Users, 
  DollarSign, 
  MapPin, 
  Globe, 
  Linkedin, 
  Target, 
  MessageSquare, 
  TrendingUp,
  FileText,
  Lightbulb,
  UserCheck,
  BarChart3,
  Calendar,
  ExternalLink,
  AlertCircle,
  RefreshCw,
  Loader2
} from "lucide-react"

// Flask backend URL
const FLASK_BASE_URL = 'http://127.0.0.1:5000'

interface Company {
  name: string
  industry: string
  pitch?: any
  scraped_data?: any
  created_at: string
  updated_at: string
}

interface ScrapedData {
  job_id: string
  firecrawl_job_id: string
  url: string
  company_name: string
  scraped_at: string
  processed_content: any[]
  content_count: number
  perplexity_research: any
  status: string
}

export default function CompanyPage() {
  const params = useParams()
  const router = useRouter()
  const [company, setCompany] = useState<Company | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [generatingPersonas, setGeneratingPersonas] = useState(false)
  const [personas, setPersonas] = useState<any[]>([])
  const [personaError, setPersonaError] = useState<string | null>(null)
  const [generatingMarketAnalysis, setGeneratingMarketAnalysis] = useState(false)
  const [marketAnalysis, setMarketAnalysis] = useState<any[]>([])
  const [marketAnalysisError, setMarketAnalysisError] = useState<string | null>(null)

  const companyName = decodeURIComponent(params.name as string)

  useEffect(() => {
    loadCompany()
  }, [companyName])

  const loadCompany = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${FLASK_BASE_URL}/api/pitch/companies/${encodeURIComponent(companyName)}`)
      
      if (response.ok) {
        const data = await response.json()
        setCompany(data)
        
        // Load existing personas if available
        if (data.personas) {
          setPersonas(data.personas)
        }
      } else if (response.status === 404) {
        setError("Company not found")
      } else {
        setError("Failed to load company data")
      }
    } catch (error) {
      console.error('Error loading company:', error)
      setError("Failed to load company data")
    } finally {
      setLoading(false)
    }
  }

  const generatePersonas = async () => {
    if (!company) return
    
    try {
      setGeneratingPersonas(true)
      setPersonaError(null)
      
      // Send minimal data - just company name and industry
      const requestData = {
        company_name: company.name,
        industry: company.industry
      }
      
      console.log('Generating personas for:', company.name, 'in industry:', company.industry)
      
      const response = await fetch(`${FLASK_BASE_URL}/api/personas/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('Persona generation result:', result)
        
        if (result.success) {
          // Just store the text content
          setPersonas([{ content: result.content }])
          // Refresh company data to get updated personas
          loadCompany()
        } else {
          setPersonaError(result.content || 'Failed to generate personas')
        }
      } else {
        const errorData = await response.json()
        setPersonaError(errorData.error || 'Failed to generate personas')
      }
    } catch (error) {
      console.error('Error generating personas:', error)
      setPersonaError('Error generating personas')
    } finally {
      setGeneratingPersonas(false)
    }
  }

  const generateMarketAnalysis = async () => {
    if (!company) return
    
    try {
      setGeneratingMarketAnalysis(true)
      setMarketAnalysisError(null)
      
      // Send minimal data - just company name and industry
      const requestData = {
        company_name: company.name,
        industry: company.industry
      }
      
      console.log('Generating market analysis for:', company.name, 'in industry:', company.industry)
      
      const response = await fetch(`${FLASK_BASE_URL}/api/market/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('Market analysis result:', result)
        
        if (result.success) {
          // Just store the text content
          setMarketAnalysis([{ content: result.content }])
          // Refresh company data to get updated market analysis
          loadCompany()
        } else {
          setMarketAnalysisError(result.content || 'Failed to generate market analysis')
        }
      } else {
        const errorData = await response.json()
        setMarketAnalysisError(errorData.error || 'Failed to generate market analysis')
      }
    } catch (error) {
      console.error('Error generating market analysis:', error)
      setMarketAnalysisError('Error generating market analysis')
    } finally {
      setGeneratingMarketAnalysis(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const extractKeyInsights = (scrapedData: ScrapedData) => {
    const insights = []
    
    if (scrapedData.perplexity_research?.success) {
      const research = scrapedData.perplexity_research.content
      
      // Extract key insights from Perplexity research
      if (research.includes('Company Overview')) insights.push('Company Overview')
      if (research.includes('Products & Services')) insights.push('Products & Services')
      if (research.includes('Target Customers')) insights.push('Target Customers')
      if (research.includes('Pain Points')) insights.push('Pain Points')
      if (research.includes('Competitive Landscape')) insights.push('Competitive Landscape')
      if (research.includes('Recent Developments')) insights.push('Recent Developments')
      if (research.includes('Industry Trends')) insights.push('Industry Trends')
      if (research.includes('Sales Opportunities')) insights.push('Sales Opportunities')
      if (research.includes('Conversation Starters')) insights.push('Conversation Starters')
    }
    
    // Add insights from scraped content
    if (scrapedData.content_count > 0) {
      insights.push(`${scrapedData.content_count} Content Items`)
    }
    
    return insights
  }

  const renderPerplexityResearch = (research: any) => {
    if (!research?.success) {
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">AI research failed: {research?.error || 'Unknown error'}</p>
        </div>
      )
    }

    const content = research.content
    const sections = content.split(/(?=^[A-Z][^:]*:)/m).filter(Boolean)

    return (
      <div className="space-y-6">
        {sections.map((section: string, index: number) => {
          const [title, ...contentParts] = section.split('\n')
          const content = contentParts.join('\n').trim()
          
          if (!content) return null
          
          return (
            <div key={index} className="space-y-3">
              <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                {getSectionIcon(title)}
                {title.replace(':', '')}
              </h4>
              <div className="text-sm text-gray-700 leading-relaxed">
                {content.split('\n').map((line: string, lineIndex: number) => {
                  if (line.trim().startsWith('-') || line.trim().startsWith('•')) {
                    return (
                      <div key={lineIndex} className="flex items-start gap-2 ml-4">
                        <span className="text-emerald-500 mt-1">•</span>
                        <span>{line.trim().substring(1).trim()}</span>
                      </div>
                    )
                  }
                  return <p key={lineIndex} className="mb-2">{line}</p>
                })}
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  const getSectionIcon = (title: string) => {
    const lowerTitle = title.toLowerCase()
    if (lowerTitle.includes('overview')) return <Building2 className="h-4 w-4" />
    if (lowerTitle.includes('products') || lowerTitle.includes('services')) return <FileText className="h-4 w-4" />
    if (lowerTitle.includes('customers') || lowerTitle.includes('personas')) return <Users className="h-4 w-4" />
    if (lowerTitle.includes('pain points')) return <Lightbulb className="h-4 w-4" />
    if (lowerTitle.includes('competitive')) return <BarChart3 className="h-4 w-4" />
    if (lowerTitle.includes('recent') || lowerTitle.includes('developments')) return <Calendar className="h-4 w-4" />
    if (lowerTitle.includes('trends')) return <TrendingUp className="h-4 w-4" />
    if (lowerTitle.includes('opportunities')) return <Target className="h-4 w-4" />
    if (lowerTitle.includes('conversation')) return <MessageSquare className="h-4 w-4" />
    return <FileText className="h-4 w-4" />
  }

  const renderScrapedContent = (scrapedData: ScrapedData) => {
    if (!scrapedData.processed_content || scrapedData.processed_content.length === 0) {
      return <p className="text-gray-500 text-sm">No content available</p>
    }

    return (
      <div className="space-y-4">
        {scrapedData.processed_content.map((item: any, index: number) => (
          <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50/50">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline" className="text-xs">
                {item.type}
              </Badge>
              {item.url && (
                <a 
                  href={item.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-xs text-emerald-600 hover:text-emerald-800 flex items-center gap-1"
                >
                  <ExternalLink className="h-3 w-3" />
                  View Source
                </a>
              )}
            </div>
            <div className="text-sm text-gray-700">
              {item.content.length > 300 
                ? `${item.content.substring(0, 300)}...` 
                : item.content
              }
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header Skeleton */}
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center gap-4">
              <div className="h-10 w-20 bg-gray-200 rounded animate-pulse"></div>
              <div>
                <div className="h-8 w-48 bg-gray-200 rounded animate-pulse mb-2"></div>
                <div className="h-4 w-32 bg-gray-200 rounded animate-pulse"></div>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Panel Skeleton */}
            <div className="lg:col-span-2 space-y-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white rounded-2xl p-8 shadow-xl">
                  <div className="h-6 w-48 bg-gray-200 rounded animate-pulse mb-4"></div>
                  <div className="h-4 w-32 bg-gray-200 rounded animate-pulse mb-6"></div>
                  <div className="space-y-3">
                    {[1, 2, 3].map((j) => (
                      <div key={j} className="h-4 bg-gray-200 rounded animate-pulse"></div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Right Panel Skeleton */}
            <div className="space-y-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-white rounded-2xl p-6 shadow-xl">
                  <div className="h-6 w-32 bg-gray-200 rounded animate-pulse mb-4"></div>
                  <div className="space-y-3">
                    {[1, 2, 3].map((j) => (
                      <div key={j} className="h-4 bg-gray-200 rounded animate-pulse"></div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error || !company) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 mb-4">
            <AlertCircle className="h-16 w-16 mx-auto" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Error</h1>
          <p className="text-gray-600 mb-6">{error || 'Company not found'}</p>
          <Button onClick={() => router.push('/')} variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
        </div>
      </div>
    )
  }

  const scrapedData = company.scraped_data
  const keyInsights = scrapedData ? extractKeyInsights(scrapedData) : []

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-4">
            <Button 
              onClick={() => router.push('/')} 
              variant="ghost" 
              size="sm"
              className="text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{company.name}</h1>
              <p className="text-gray-600">{company.industry}</p>
            </div>
            <div className="ml-auto">
              <Button 
                onClick={loadCompany} 
                variant="outline" 
                size="sm"
                className="text-gray-600 hover:text-gray-900"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
          <div className="mt-4">
            <Breadcrumb 
              items={[
                { label: 'Companies', href: '/' },
                { label: company.name }
              ]} 
            />
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Company Overview & Key Insights */}
          <div className="lg:col-span-2 space-y-6">
            {/* Company Overview */}
            <Card className="bg-white border-0 shadow-xl rounded-2xl overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-blue-100 border-b border-blue-200/50 pb-6">
                <CardTitle className="text-gray-900 text-xl flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Company Overview
                </CardTitle>
                <CardDescription className="text-gray-600 text-base">
                  Key company information and insights
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-8 px-8 pb-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <Building2 className="h-5 w-5 text-blue-600" />
                      <div>
                        <p className="text-sm font-medium text-gray-500">Company Name</p>
                        <p className="text-gray-900">{company.name}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Target className="h-5 w-5 text-blue-600" />
                      <div>
                        <p className="text-sm font-medium text-gray-500">Industry</p>
                        <p className="text-gray-900">{company.industry}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Calendar className="h-5 w-5 text-blue-600" />
                      <div>
                        <p className="text-sm font-medium text-gray-500">Created</p>
                        <p className="text-gray-900">{formatDate(company.created_at)}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Calendar className="h-5 w-5 text-blue-600" />
                      <div>
                        <p className="text-sm font-medium text-gray-500">Last Updated</p>
                        <p className="text-gray-900">{formatDate(company.updated_at)}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    {scrapedData?.url && (
                      <div className="flex items-center gap-3">
                        <Globe className="h-5 w-5 text-blue-600" />
                        <div>
                          <p className="text-sm font-medium text-gray-500">Website</p>
                          <a 
                            href={scrapedData.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-emerald-600 hover:text-emerald-800 flex items-center gap-1"
                          >
                            {scrapedData.url}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        </div>
                      </div>
                    )}
                    {scrapedData?.scraped_at && (
                      <div className="flex items-center gap-3">
                        <Calendar className="h-5 w-5 text-blue-600" />
                        <div>
                          <p className="text-sm font-medium text-gray-500">Last Scraped</p>
                          <p className="text-gray-900">{formatDate(scrapedData.scraped_at)}</p>
                        </div>
                      </div>
                    )}
                    {scrapedData?.content_count && (
                      <div className="flex items-center gap-3">
                        <FileText className="h-5 w-5 text-blue-600" />
                        <div>
                          <p className="text-sm font-medium text-gray-500">Content Items</p>
                          <p className="text-gray-900">{scrapedData.content_count}</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Key Insights */}
            {keyInsights.length > 0 && (
              <Card className="bg-white border-0 shadow-xl rounded-2xl overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-emerald-50 to-emerald-100 border-b border-emerald-200/50 pb-6">
                  <CardTitle className="text-gray-900 text-xl flex items-center gap-2">
                    <Lightbulb className="h-5 w-5" />
                    Key Insights Available
                  </CardTitle>
                  <CardDescription className="text-gray-600 text-base">
                    AI-powered research and analysis results
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-8 px-8 pb-8">
                  <div className="flex flex-wrap gap-2">
                    {keyInsights.map((insight, index) => (
                      <Badge 
                        key={index} 
                        variant="secondary" 
                        className="bg-emerald-100 text-emerald-800 border-emerald-200 font-medium"
                      >
                        {insight}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* AI Research Results */}
            {scrapedData?.perplexity_research && (
              <Card className="bg-white border-0 shadow-xl rounded-2xl overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-purple-50 to-purple-100 border-b border-purple-200/50 pb-6">
                  <CardTitle className="text-gray-900 text-xl flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    AI Research & Analysis
                  </CardTitle>
                  <CardDescription className="text-gray-600 text-base">
                    Comprehensive market intelligence from Perplexity AI
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-8 px-8 pb-8">
                  {renderPerplexityResearch(scrapedData.perplexity_research)}
                </CardContent>
              </Card>
            )}

            {/* Scraped Content */}
            {scrapedData?.processed_content && (
              <Card className="bg-white border-0 shadow-xl rounded-2xl overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-orange-50 to-orange-100 border-b border-orange-200/50 pb-6">
                  <CardTitle className="text-gray-900 text-xl flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Scraped Website Content
                  </CardTitle>
                  <CardDescription className="text-gray-600 text-base">
                    Raw content extracted from the company website
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-8 px-8 pb-8">
                  {renderScrapedContent(scrapedData)}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Panel - Actionable Insights & Tools */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card className="bg-white border-0 shadow-xl rounded-2xl overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-indigo-50 to-indigo-100 border-b border-indigo-200/50 pb-6">
                <CardTitle className="text-gray-900 text-xl flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-8 px-6 pb-6">
                <div className="space-y-3">
                  <Button 
                    onClick={generatePersonas}
                    disabled={generatingPersonas}
                    className="w-full justify-start" 
                    variant="outline"
                  >
                    {generatingPersonas ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Users className="h-4 w-4 mr-2" />
                    )}
                    {generatingPersonas ? 'Generating Personas...' : 'Generate Buyer Personas'}
                  </Button>
                  
                  {personaError && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                      {personaError}
                    </div>
                  )}
                  
                  <Button 
                    onClick={generateMarketAnalysis}
                    disabled={generatingMarketAnalysis}
                    className="w-full justify-start" 
                    variant="outline"
                  >
                    {generatingMarketAnalysis ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <TrendingUp className="h-4 w-4 mr-2" />
                    )}
                    {generatingMarketAnalysis ? 'Analyzing Market...' : 'Market Analysis'}
                  </Button>
                  
                  {marketAnalysisError && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                      {marketAnalysisError}
                    </div>
                  )}
                  
                  <Button className="w-full justify-start" variant="outline">
                    <MessageSquare className="h-4 w-4 mr-2" />
                    Generate Sales Script
                  </Button>
                  {/* <Button className="w-full justify-start" variant="outline">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Market Analysis
                  </Button>
                  <Button className="w-full justify-start" variant="outline">
                    <FileText className="h-4 w-4 mr-2" />
                    Export Report
                  </Button> */}
                </div>
              </CardContent>
            </Card>

            {/* Buyer Personas */}
            {personas.length > 0 && (
              <Card className="bg-white border-0 shadow-xl rounded-2xl overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-emerald-50 to-emerald-100 border-b border-emerald-200/50 pb-6">
                  <CardTitle className="text-gray-900 text-xl flex items-center gap-2">
                    <UserCheck className="h-5 w-5" />
                    Buyer Personas
                  </CardTitle>
                  <CardDescription className="text-gray-600 text-base">
                    AI-generated buyer personas for sales targeting
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-8 px-6 pb-6">
                  <div className="space-y-4">
                    {personas.map((persona, index) => (
                      <div key={index} className="prose prose-sm max-w-none">
                        <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                          {persona.content}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Market Analysis */}
            {marketAnalysis.length > 0 && (
              <Card className="bg-white border-0 shadow-xl rounded-2xl overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-blue-50 to-blue-100 border-b border-blue-200/50 pb-6">
                  <CardTitle className="text-gray-900 text-xl flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Market Analysis
                  </CardTitle>
                  <CardDescription className="text-gray-600 text-base">
                    Market landscape and similar companies for prospecting
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-8 px-6 pb-6">
                  <div className="space-y-4">
                    {marketAnalysis.map((analysis, index) => (
                      <div key={index} className="prose prose-sm max-w-none">
                        <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                          {analysis.content}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Data Sources */}
            <Card className="bg-white border-0 shadow-xl rounded-2xl overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-cyan-50 to-cyan-100 border-b border-cyan-200/50 pb-6">
                <CardTitle className="text-gray-900 text-xl flex items-center gap-2">
                  <Globe className="h-5 w-5" />
                  Data Sources
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-8 px-6 pb-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Web Scraping</span>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      {scrapedData ? '✓ Available' : '✗ Not Available'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">AI Research</span>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      {scrapedData?.perplexity_research?.success ? '✓ Available' : '✗ Not Available'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Manual Pitch</span>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      {company.pitch ? '✓ Available' : '✗ Not Available'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Buyer Personas</span>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      {personas.length > 0 ? `✓ ${personas.length} Generated` : '✗ Not Generated'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Placeholder for Future Features */}
            <Card className="bg-white border-0 shadow-xl rounded-2xl overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-amber-50 to-amber-100 border-b border-amber-200/50 pb-6">
                <CardTitle className="text-gray-900 text-xl flex items-center gap-2">
                  <Lightbulb className="h-5 w-5" />
                  Coming Soon
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-8 px-6 pb-6">
                <div className="space-y-3 text-sm text-gray-600">
                  <p>• Target Customer Profiles</p>
                  <p>• Sample Sales Scripts</p>
                  <p>• Competitive Analysis</p>
                  <p>• Market Trends Dashboard</p>
                  <p>• Lead Scoring Tools</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
} 