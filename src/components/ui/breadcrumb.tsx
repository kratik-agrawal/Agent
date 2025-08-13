"use client"

import * as React from "react"
import { ChevronRight, Home } from "lucide-react"
import { cn } from "@/lib/utils"

interface BreadcrumbProps {
  items: Array<{
    label: string
    href?: string
  }>
  className?: string
}

const Breadcrumb = React.forwardRef<HTMLElement, BreadcrumbProps>(
  ({ items, className, ...props }, ref) => {
    return (
      <nav
        ref={ref}
        aria-label="Breadcrumb"
        className={cn("flex items-center space-x-1 text-sm text-gray-500", className)}
        {...props}
      >
        <a
          href="/"
          className="flex items-center hover:text-gray-700 transition-colors duration-200"
        >
          <Home className="h-4 w-4" />
        </a>
        
        {items.map((item, index) => (
          <React.Fragment key={index}>
            <ChevronRight className="h-4 w-4 text-gray-400" />
            {item.href ? (
              <a
                href={item.href}
                className="hover:text-gray-700 transition-colors duration-200"
              >
                {item.label}
              </a>
            ) : (
              <span className="text-gray-900 font-medium">{item.label}</span>
            )}
          </React.Fragment>
        ))}
      </nav>
    )
  }
)
Breadcrumb.displayName = "Breadcrumb"

export { Breadcrumb } 