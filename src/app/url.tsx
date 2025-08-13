"use client"
import React, { useState } from 'react';
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Copy, Link, ExternalLink, CheckCircle } from "lucide-react"

export default function Home() {
  const [originalUrl, setOriginalUrl] = useState('');
  const [shortenedUrl, setShortenedUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleShorten = async () => {
    if (!originalUrl) return;
    
    setIsLoading(true);
    try {
      // Connect to Flask backend API
      const response = await fetch('http://127.0.0.1:5000/shorten', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: originalUrl }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setShortenedUrl(data.shortened_url);
      } else {
        // Handle error response
        const errorData = await response.json();
        console.error('Error shortening URL:', errorData);
        // For demo purposes, create a mock shortened URL
        const mockShortUrl = `${window.location.origin}/s/${Math.random().toString(36).substr(2, 6)}`;
        setShortenedUrl(mockShortUrl);
      }
    } catch (error) {
      console.error('Error connecting to backend:', error);
      // Fallback for demo
      const mockShortUrl = `${window.location.origin}/s/${Math.random().toString(36).substr(2, 6)}`;
      setShortenedUrl(mockShortUrl);
    }
    setIsLoading(false);
  };

  const copyToClipboard = async () => {
    if (shortenedUrl) {
      await navigator.clipboard.writeText(shortenedUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="flex items-center justify-center mb-4">
              <Link className="w-8 h-8 text-blue-600 mr-3" />
              <h1 className="text-4xl font-bold text-gray-900">URL Shortener</h1>
            </div>
            <p className="text-lg text-gray-600">Create short, memorable links in seconds</p>
          </div>

          {/* Main Card */}
          <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="text-center pb-6">
              <CardTitle className="text-2xl text-gray-800">Shorten Your URL</CardTitle>
              <CardDescription className="text-gray-600">
                Enter a long URL and get a short, shareable link
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* URL Input */}
              <div className="space-y-2">
                <label htmlFor="url" className="text-sm font-medium text-gray-700">
                  Original URL
                </label>
                <div className="flex gap-2">
                  <Input
                    id="url"
                    type="url"
                    placeholder="https://example.com/very-long-url-that-needs-shortening"
                    value={originalUrl}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setOriginalUrl(e.target.value)}
                    className="flex-1"
                  />
                  <Button 
                    onClick={handleShorten}
                    disabled={!originalUrl || isLoading}
                    className="px-6"
                  >
                    {isLoading ? 'Shortening...' : 'Shorten'}
                  </Button>
                </div>
              </div>

              {/* Shortened URL Display */}
              {shortenedUrl && (
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    Shortened URL
                  </label>
                  <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border">
                    <ExternalLink className="w-4 h-4 text-gray-500" />
                    <span className="flex-1 text-sm text-gray-700 font-mono break-all">
                      {shortenedUrl}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={copyToClipboard}
                      className="shrink-0"
                    >
                      {copied ? (
                        <>
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4 mr-2" />
                          Copy
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-6 mt-12">
            <Card className="text-center border-0 bg-white/60 backdrop-blur-sm">
              <CardContent className="pt-6">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Link className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">Fast & Simple</h3>
                <p className="text-sm text-gray-600">Shorten URLs instantly with our lightning-fast service</p>
              </CardContent>
            </Card>

            <Card className="text-center border-0 bg-white/60 backdrop-blur-sm">
              <CardContent className="pt-6">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">Reliable</h3>
                <p className="text-sm text-gray-600">99.9% uptime ensures your links are always accessible</p>
              </CardContent>
            </Card>

            <Card className="text-center border-0 bg-white/60 backdrop-blur-sm">
              <CardContent className="pt-6">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Copy className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">Easy Sharing</h3>
                <p className="text-sm text-gray-600">One-click copy makes sharing your shortened links effortless</p>
              </CardContent>
            </Card>
          </div>

          {/* Footer */}
          <div className="text-center mt-12">
            <Badge variant="outline" className="text-xs">
              Powered by Next.js & Tailwind CSS
            </Badge>
          </div>
        </div>
      </div>
    </div>
  );
}
