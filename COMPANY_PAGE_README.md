# Company Detail Page Feature

## Overview

The company detail page provides a comprehensive view of each scraped company, displaying both web scraping results and AI research in an organized, actionable format.

## Features

### 🏢 Company Overview
- Company name and industry
- Creation and last updated dates
- Website URL with external link
- Last scraping timestamp
- Content item count

### 🔍 Key Insights
- AI research sections available
- Content analysis summary
- Data source indicators

### 🤖 AI Research & Analysis
- **Company Overview** - What they do, location, size
- **Products & Services** - Key offerings and differentiators
- **Target Customers** - Industries, geographies, company sizes
- **Pain Points** - Industry challenges and operational inefficiencies
- **Competitive Landscape** - Main competitors and positioning
- **Recent Developments** - Funding, partnerships, leadership changes
- **Industry Trends** - Macro and niche trends
- **Sales Opportunities** - Strategic angles for sales reps
- **Conversation Starters** - Context-rich opening lines

### 📄 Scraped Website Content
- Raw content from company website
- Content type classification (markdown, HTML, metadata)
- Source URL links
- Content previews with truncation

### 🎯 Right Panel Tools
- **Quick Actions** - Generate sales scripts, identify prospects
- **Data Sources** - Status of web scraping, AI research, manual pitch
- **Coming Soon** - Future features like target customer profiles

## Navigation

### From Home Page
- Click on any company name in the companies list
- Use the "View Details" button below each company card
- Navigate to `/company/[company-name]`

### Breadcrumb Navigation
- Home → Companies → [Company Name]
- Clickable breadcrumb trail for easy navigation

## URL Structure

```
/company/[company-name]
```

Example: `/company/Apple%20Inc` for "Apple Inc"

## Data Sources

The company page combines data from multiple sources:

1. **Manual Pitch Data** - User-entered company information
2. **Web Scraping** - Firecrawl website content extraction
3. **AI Research** - Perplexity AI market intelligence

## Responsive Design

- **Desktop**: 3-column layout with left panel (2/3) and right panel (1/3)
- **Mobile**: Single column layout with stacked cards
- **Tablet**: Adaptive grid layout

## Loading States

- Skeleton loaders during data fetching
- Smooth transitions between states
- Error handling with retry functionality

## Future Enhancements

### Planned Features
- Target customer profile generation
- Sample sales script creation
- Competitive analysis dashboard
- Market trends visualization
- Lead scoring tools
- Export functionality for reports

### Quick Actions
- Generate sales scripts based on AI research
- Identify prospect personas
- Market analysis reports
- Export company data

## Technical Implementation

### Components Used
- `Card` - Main content containers
- `Badge` - Status and category indicators
- `Button` - Interactive elements
- `Breadcrumb` - Navigation component
- `Separator` - Visual dividers

### State Management
- Company data loading and caching
- Error handling and retry logic
- Loading state management
- Responsive data display

### API Integration
- Fetches company data from Flask backend
- Handles both successful and failed responses
- Provides refresh functionality
- Error recovery mechanisms

## Usage Examples

### Viewing Company Data
1. Navigate to the home page
2. Click on a company name or "View Details" button
3. Explore the comprehensive company profile
4. Use the right panel for quick actions

### Refreshing Data
1. Click the "Refresh" button in the header
2. Data will be reloaded from the backend
3. Loading states will show during refresh

### Navigation
1. Use the "Back" button to return to home
2. Use breadcrumb navigation for multi-level navigation
3. Click external links to visit company websites

## Styling

### Color Scheme
- **Blue**: Company overview sections
- **Emerald**: Key insights and success states
- **Purple**: AI research sections
- **Orange**: Scraped content sections
- **Indigo**: Quick actions
- **Cyan**: Data sources
- **Amber**: Coming soon features

### Design Patterns
- Gradient headers for visual hierarchy
- Rounded corners and shadows for modern look
- Consistent spacing and typography
- Hover effects for interactive elements
- Responsive grid layouts

## Troubleshooting

### Common Issues
1. **Company not found**: Check company name spelling and encoding
2. **Loading errors**: Use refresh button or check backend connectivity
3. **Missing data**: Verify scraping jobs completed successfully
4. **Navigation issues**: Use breadcrumb or back button

### Error Recovery
- Automatic error display with retry options
- Graceful fallbacks for missing data
- User-friendly error messages
- Refresh functionality for data recovery 