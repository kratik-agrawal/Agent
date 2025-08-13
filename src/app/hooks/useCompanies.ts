"use client"

import { useState, useEffect, useCallback } from 'react'
import { apiClient, Company, CompanyFormData } from '@/lib/api'

export function useCompanies() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load companies
  const loadCompanies = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.getCompanies()
      if (response.error) {
        setError(response.error)
      } else if (response.data) {
        setCompanies(response.data)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load companies')
    } finally {
      setLoading(false)
    }
  }, [])

  // Add company
  const addCompany = useCallback(async (companyData: CompanyFormData) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.createCompany(companyData)
      if (response.error) {
        setError(response.error)
        return false
      } else if (response.data) {
        setCompanies(prev => [...prev, response.data!])
        return true
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add company')
      return false
    } finally {
      setLoading(false)
    }
    return false
  }, [])

  // Delete company
  const deleteCompany = useCallback(async (companyName: string) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.deleteCompany(companyName)
      if (response.error) {
        setError(response.error)
        return false
      } else {
        setCompanies(prev => prev.filter(c => c.name !== companyName))
        return true
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete company')
      return false
    } finally {
      setLoading(false)
    }
    return false
  }, [])

  // Update company
  const updateCompany = useCallback(async (companyName: string, updates: Partial<Company>) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await apiClient.updateCompany(companyName, updates)
      if (response.error) {
        setError(response.error)
        return false
      } else if (response.data) {
        setCompanies(prev => 
          prev.map(c => c.name === companyName ? response.data! : c)
        )
        return true
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update company')
      return false
    } finally {
      setLoading(false)
    }
    return false
  }, [])

  // Load companies on mount
  useEffect(() => {
    loadCompanies()
  }, [loadCompanies])

  return {
    companies,
    loading,
    error,
    loadCompanies,
    addCompany,
    deleteCompany,
    updateCompany,
  }
} 