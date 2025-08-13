"use client"

import { useState, useEffect } from "react"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Loader2, Globe, FileText, CheckCircle, AlertCircle, TreePine, ArrowRight } from "lucide-react"
import { useCompanies } from "./hooks/useCompanies"
import { CompanyFormData, Company, ScrapeJob } from "@/lib/api"

// Flask backend URL
const FLASK_BASE_URL = 'http://127.0.0.1:5000'

export default function Home() {
  const { companies, loading, error, addCompany, deleteCompany } = useCompanies()
  const [scrapeJobs, setScrapeJobs] = useState<ScrapeJob[]>([])
  const [testingFirecrawl, setTestingFirecrawl] = useState(false)
  const [firecrawlTestResult, setFirecrawlTestResult] = useState<string | null>(null)

  // Manual pitch form state
  const [manualForm, setManualForm] = useState({
    company_name: "",
    industry: "",
    content: ""
  })

  // Scrape form state
  const [scrapeForm, setScrapeForm] = useState({
    url: "",
    company_name: ""
  })

  // Auto-check status of pending jobs every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      const pendingJobs = scrapeJobs.filter(job => job.status === 'pending')
      pendingJobs.forEach(job => {
        checkScrapeStatus(job.job_id)
      })
    }, 10000) // Check every 10 seconds

    return () => clearInterval(interval)
  }, [scrapeJobs])

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const success = await addCompany(manualForm)
    if (success) {
      setManualForm({ company_name: "", industry: "", content: "" })
    }
  }

  const handleScrapeSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      // Validate URL format
      if (!scrapeForm.url.startsWith('http://') && !scrapeForm.url.startsWith('https://')) {
        alert('Please enter a valid URL starting with http:// or https://')
        return
      }
      
      const response = await fetch(`${FLASK_BASE_URL}/api/pitch/ingest/scrape`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(scrapeForm),
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('Scraping started:', result)
        setScrapeForm({ url: "", company_name: "" })
        
        // Add to scrape jobs list
        setScrapeJobs(prev => [...prev, {
          job_id: result.job_id,
          status: result.status,
          company_name: result.company_name || scrapeForm.company_name,
          created_at: new Date().toISOString()
        }])
      } else {
        const errorData = await response.json()
        console.error('Failed to start scraping:', errorData)
        alert(`Failed to start scraping: ${errorData.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Error:', error)
      alert(`Error starting scrape: ${error}`)
    }
  }

  const checkScrapeStatus = async (jobId: string) => {
    try {
      const response = await fetch(`${FLASK_BASE_URL}/api/pitch/ingest/scrape/${jobId}/status`)
      if (response.ok) {
        const result = await response.json()
        setScrapeJobs(prev => prev.map(job => 
          job.job_id === jobId ? { 
            ...job, 
            status: result.status,
            error: result.error || null,
            result: result.result || null
          } : job
        ))
        
        if (result.status === 'completed') {
          // Refresh companies list
          window.location.reload()
        }
      }
    } catch (error) {
      console.error('Error checking status:', error)
    }
  }

  const testFirecrawl = async () => {
    setTestingFirecrawl(true)
    setFirecrawlTestResult(null)
    
    try {
      const response = await fetch(`${FLASK_BASE_URL}/api/test/firecrawl`)
      const result = await response.json()
      
      if (response.ok) {
        setFirecrawlTestResult(`✅ ${result.message}`)
      } else {
        setFirecrawlTestResult(`❌ ${result.message}: ${result.error}`)
      }
    } catch (error) {
      setFirecrawlTestResult(`❌ Connection failed: ${error}`)
    } finally {
      setTestingFirecrawl(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-emerald-400" />
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-400" />
      case 'running':
        return <Loader2 className="h-4 w-4 text-teal-400 animate-spin" />
      case 'pending':
        return <Loader2 className="h-4 w-4 text-amber-400" />
      default:
        return <Loader2 className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200'
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'running':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'pending':
        return 'bg-amber-100 text-amber-800 border-amber-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50 to-slate-100">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23064714%22%20fill-opacity%3D%220.03%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%221%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-40"></div>
      
      <div className="relative z-10">
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-800 via-emerald-700 to-emerald-800 border-b border-emerald-600/30 shadow-lg">
          <div className="max-w-6xl mx-auto px-6 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
                  <TreePine className="h-7 w-7 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-white">Sylvan Pitch Agent</h1>
                  <p className="text-emerald-100 text-sm">AI-Powered Sales Pitch Customization</p>
                </div>
              </div>
              <div className="text-sm text-emerald-100 bg-white/10 px-4 py-2 rounded-lg backdrop-blur-sm border border-white/20">
                Revenue Intelligence Platform
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto px-6 py-12">
          {/* Hero Section */}
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-2 bg-emerald-100 text-emerald-800 text-sm font-semibold rounded-full mb-6">
              HOW IT WORKS
            </div>
            <h1 className="text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Take care of your
              <span className="block bg-gradient-to-r from-emerald-600 to-emerald-700 bg-clip-text text-transparent">
                farmers
              </span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Stop burning cash spending months on RevOps hiring and poorly integrated data systems. Your post-sales motion should be driving revenue.
            </p>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Input Forms */}
            <div className="lg:col-span-1 space-y-8">
              {/* Manual Pitch Input */}
              <Card className="bg-white border-0 shadow-xl rounded-2xl overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-emerald-50 to-emerald-100 border-b border-emerald-200/50 pb-6">
                  <CardTitle className="flex items-center gap-3 text-gray-900 text-xl">
                    <div className="p-2.5 bg-emerald-600 rounded-xl">
                      <FileText className="h-5 w-5 text-white" />
                    </div>
                    Manual Pitch Input
                  </CardTitle>
                  <CardDescription className="text-gray-600 text-base">
                    Enter your product pitch manually
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-8 px-8 pb-8">
                  <form onSubmit={handleManualSubmit} className="space-y-6">
                    <div>
                      <Label htmlFor="company_name" className="text-gray-700 font-medium mb-2 block">Company Name</Label>
                      <Input
                        id="company_name"
                        value={manualForm.company_name}
                        onChange={(e) => setManualForm(prev => ({ ...prev, company_name: e.target.value }))}
                        placeholder="e.g., Arkestro"
                        className="bg-gray-50 border-gray-200 text-gray-900 placeholder:text-gray-400 focus:border-emerald-500 focus:ring-emerald-500/20 rounded-xl h-12"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="industry" className="text-gray-700 font-medium mb-2 block">Industry</Label>
                      <Input
                        id="industry"
                        value={manualForm.industry}
                        onChange={(e) => setManualForm(prev => ({ ...prev, industry: e.target.value }))}
                        placeholder="e.g., Predictive Procurement Software"
                        className="bg-gray-50 border-gray-200 text-gray-900 placeholder:text-gray-400 focus:border-emerald-500 focus:ring-emerald-500/20 rounded-xl h-12"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="content" className="text-gray-700 font-medium mb-2 block">Pitch Content</Label>
                      <Textarea
                        id="content"
                        value={manualForm.content}
                        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setManualForm(prev => ({ ...prev, content: e.target.value }))}
                        placeholder="Enter your product pitch here..."
                        rows={6}
                        className="bg-gray-50 border-gray-200 text-gray-900 placeholder:text-gray-400 focus:border-emerald-500 focus:ring-emerald-500/20 rounded-xl resize-none"
                        required
                      />
                    </div>
                    <Button 
                      type="submit" 
                      disabled={loading} 
                      className="w-full bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 text-white border-0 shadow-lg rounded-xl h-12 font-semibold text-base transition-all duration-200"
                    >
                      {loading ? <Loader2 className="h-5 w-5 animate-spin mr-2" /> : null}
                      Submit Pitch
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Web Scraping */}
              <Card className="bg-white border-0 shadow-xl rounded-2xl overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-emerald-50 to-emerald-100 border-b border-emerald-200/50 pb-6">
                  <CardTitle className="flex items-center gap-3 text-gray-900 text-xl">
                    <div className="p-2.5 bg-emerald-600 rounded-xl">
                      <Globe className="h-5 w-5 text-white" />
                    </div>
                    Web Scraping
                  </CardTitle>
                  <CardDescription className="text-gray-600 text-base">
                    Scrape company website for pitch content
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-8 px-8 pb-8">
                  {/* Firecrawl Test Button */}
                  {/* <div className="mb-8 p-5 bg-gray-50 border border-gray-200 rounded-xl">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-medium text-gray-700">Test Firecrawl API</span>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={testFirecrawl}
                        disabled={testingFirecrawl}
                        className="border-emerald-200 text-emerald-700 hover:bg-emerald-50 hover:border-emerald-300 rounded-lg"
                      >
                        {testingFirecrawl ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                        Test Connection
                      </Button>
                    </div>
                    {firecrawlTestResult && (
                      <p className="text-sm text-gray-600">{firecrawlTestResult}</p>
                    )}
                  </div> */}
                  
                  <form onSubmit={handleScrapeSubmit} className="space-y-6">
                    <div>
                      <Label htmlFor="scrape_url" className="text-gray-700 font-medium mb-2 block">Website URL</Label>
                      <Input
                        id="scrape_url"
                        type="url"
                        value={scrapeForm.url}
                        onChange={(e) => setScrapeForm(prev => ({ ...prev, url: e.target.value }))}
                        placeholder="https://arkestro.com"
                        className="bg-gray-50 border-gray-200 text-gray-900 placeholder:text-gray-400 focus:border-emerald-500 focus:ring-emerald-500/20 rounded-xl h-12"
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="scrape_company" className="text-gray-700 font-medium mb-2 block">Company Name</Label>
                      <Input
                        id="scrape_company"
                        value={scrapeForm.company_name}
                        onChange={(e) => setScrapeForm(prev => ({ ...prev, company_name: e.target.value }))}
                        placeholder="e.g., Arkestro"
                        className="bg-gray-50 border-gray-200 text-gray-900 placeholder:text-gray-400 focus:border-emerald-500 focus:ring-emerald-500/20 rounded-xl h-12"
                        required
                      />
                    </div>
                    <Button 
                      type="submit" 
                      className="w-full bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 text-white border-0 shadow-lg rounded-xl h-12 font-semibold text-base transition-all duration-200"
                    >
                      Start Scraping
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Right Column - Results & Status */}
            <div className="lg:col-span-2 space-y-8">
              {/* Scrape Jobs Status */}
              {scrapeJobs.length > 0 && (
                <Card className="bg-white border-0 shadow-xl rounded-2xl overflow-hidden">
                  <CardHeader className="bg-gradient-to-r from-emerald-50 to-emerald-100 border-b border-emerald-200/50 pb-6">
                    <CardTitle className="text-gray-900 text-xl">Scraping Jobs</CardTitle>
                    <CardDescription className="text-gray-600 text-base">
                      Monitor the status of your web scraping jobs
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-8 px-8 pb-8">
                    <div className="space-y-4">
                      {scrapeJobs.map((job) => (
                        <div key={job.job_id} className="border border-gray-200 rounded-xl p-5 bg-gray-50/50">
                          <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                              {getStatusIcon(job.status)}
                              <div>
                                <p className="font-semibold text-gray-900">{job.company_name}</p>
                                <p className="text-sm text-gray-500">Job ID: {job.job_id.slice(0, 8)}...</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              <Badge className={`${getStatusColor(job.status)} border-0 font-medium`}>
                                {job.status}
                              </Badge>
                              {job.status === 'pending' && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => checkScrapeStatus(job.job_id)}
                                  className="border-emerald-200 text-emerald-700 hover:bg-emerald-50 hover:border-emerald-300 rounded-lg"
                                >
                                  Check Status
                                </Button>
                              )}
                            </div>
                          </div>
                          
                          {/* Show error if failed */}
                          {job.error && (
                            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                              <strong>Error:</strong> {job.error}
                            </div>
                          )}
                          
                          {/* Show result summary if completed */}
                          {job.result && job.status === 'completed' && (
                            <div className="mt-4 p-4 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-700">
                              <strong>Completed:</strong> {job.result.content_count || 0} content items scraped
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Companies List */}
              <Card className="bg-white border-0 shadow-xl rounded-2xl overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-emerald-50 to-emerald-100 border-b border-emerald-200/50 pb-6">
                  <CardTitle className="text-gray-900 text-xl">Companies & Pitches</CardTitle>
                  <CardDescription className="text-gray-600 text-base">
                    View all companies and their associated pitch data
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-8 px-8 pb-8">
                  {companies.length === 0 ? (
                    <div className="text-center py-16 text-gray-400">
                      <TreePine className="h-16 w-16 mx-auto mb-6 text-gray-300" />
                      <p className="text-xl font-medium text-gray-500">No companies added yet</p>
                      <p className="text-base text-gray-400">Start by submitting a pitch or scraping a website.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {companies.map((company, index) => (
                        <div key={index} className="border border-gray-200 rounded-xl p-5 bg-gray-50/50 hover:bg-gray-50 transition-colors duration-200">
                          <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900">
                              <a 
                                href={`/company/${encodeURIComponent(company.name)}`}
                                className="hover:text-emerald-600 transition-colors duration-200 cursor-pointer"
                              >
                                {company.name}
                              </a>
                            </h3>
                            <Badge variant="secondary" className="bg-emerald-100 text-emerald-800 border-emerald-200 font-medium">
                              {company.industry}
                            </Badge>
                          </div>
                          <div className="grid grid-cols-2 gap-4 text-sm text-gray-500 mb-4">
                            <div>
                              <span className="font-medium text-gray-600">Created:</span> {new Date(company.created_at).toLocaleDateString()}
                            </div>
                            <div>
                              <span className="font-medium text-gray-600">Updated:</span> {new Date(company.updated_at).toLocaleDateString()}
                            </div>
                          </div>
                          <div className="flex gap-2">
                            {company.pitch && (
                              <Badge variant="outline" className="text-emerald-700 border-emerald-300 bg-emerald-50 font-medium">
                                Manual Pitch ✓
                              </Badge>
                            )}
                            {company.scraped_data && (
                              <Badge variant="outline" className="text-emerald-700 border-emerald-300 bg-emerald-50 font-medium">
                                Scraped Data ✓
                              </Badge>
                            )}
                          </div>
                          <div className="mt-4">
                            <a 
                              href={`/company/${encodeURIComponent(company.name)}`}
                              className="inline-flex items-center gap-2 text-sm text-emerald-600 hover:text-emerald-800 font-medium hover:underline"
                            >
                              View Details
                              <ArrowRight className="h-3 w-3" />
                            </a>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
