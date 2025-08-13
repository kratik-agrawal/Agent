"use client"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, Globe, Calendar } from "lucide-react"
import { Company } from "@/lib/api"

interface CompanyListProps {
  companies: Company[]
  onViewCompany?: (company: Company) => void
  onDeleteCompany?: (companyName: string) => void
}

export default function CompanyList({ companies, onViewCompany, onDeleteCompany }: CompanyListProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const truncateText = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + "..."
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Companies ({companies.length})</h2>
      </div>
      
      {companies.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">
              No companies added yet. Add your first company to get started.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {companies.map((company) => (
            <Card key={company.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-lg">{company.name}</CardTitle>
                    {company.industry && (
                      <Badge variant="secondary">{company.industry}</Badge>
                    )}
                  </div>
                  <div className="flex space-x-2">
                    {onViewCompany && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onViewCompany(company)}
                      >
                        <FileText className="h-4 w-4 mr-1" />
                        View
                      </Button>
                    )}
                    {onDeleteCompany && (
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => onDeleteCompany(company.name)}
                      >
                        Delete
                      </Button>
                    )}
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-3">
                {company.pitch && (
                  <div>
                    <p className="text-sm text-muted-foreground">
                      {truncateText(company.pitch)}
                    </p>
                  </div>
                )}
                
                <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                  <div className="flex items-center space-x-1">
                    <Calendar className="h-4 w-4" />
                    <span>Created: {formatDate(company.created_at)}</span>
                  </div>
                </div>
                
                {company.scraped_data && (
                  <div className="flex items-center space-x-1 text-sm text-muted-foreground">
                    <Globe className="h-4 w-4" />
                    <span>Web data available</span>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
} 