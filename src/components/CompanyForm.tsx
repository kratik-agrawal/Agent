"use client"

import { useState } from "react"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface CompanyFormProps {
  onSubmit: (data: { company_name: string; industry: string; content: string }) => Promise<void>
  loading?: boolean
}

export default function CompanyForm({ onSubmit, loading = false }: CompanyFormProps) {
  const [formData, setFormData] = useState({
    company_name: "",
    industry: "",
    content: ""
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onSubmit(formData)
    setFormData({ company_name: "", industry: "", content: "" })
  }

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Add Company Manually</CardTitle>
        <CardDescription>
          Enter company information and pitch content manually
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="company_name">Company Name</Label>
            <Input
              id="company_name"
              value={formData.company_name}
              onChange={(e) => handleChange('company_name', e.target.value)}
              placeholder="Enter company name"
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="industry">Industry</Label>
            <Input
              id="industry"
              value={formData.industry}
              onChange={(e) => handleChange('industry', e.target.value)}
              placeholder="Enter industry"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="content">Pitch Content</Label>
            <Textarea
              id="content"
              value={formData.content}
              onChange={(e) => handleChange('content', e.target.value)}
              placeholder="Enter pitch content or company description"
              rows={4}
            />
          </div>
          
          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Adding..." : "Add Company"}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
} 