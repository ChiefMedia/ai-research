# Simple PowerShell script to create Media Buy AI Insights PoC

Write-Host "Creating Media Buy AI Insights PoC..." -ForegroundColor Green

# Create root directory
$projectRoot = "media-buy-insights-poc"
New-Item -ItemType Directory -Path $projectRoot -Force | Out-Null

# Create subdirectories
$directories = @(
    "src",
    "queries", 
    "templates",
    "output",
    "output/reports",
    "output/data",
    "examples"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path $projectRoot $dir
    New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    Write-Host "Created: $dir" -ForegroundColor Yellow
}

# Create basic files
Write-Host "Creating files..." -ForegroundColor Green

# README.md
$readme = @"
# Media Buy AI Insights - Proof of Concept

## Setup
1. pip install -r requirements.txt
2. Copy .env.example to .env and add credentials
3. Update config.yaml with your settings
4. Run: python main.py --client YOUR_CLIENT

## Files
- main.py - Main entry point
- src/database.py - Database connection
- src/kpi_calculator.py - KPI calculations
- src/ai_insights.py - Gemini API integration
- src/report_generator.py - Report formatting
"@

Set-Content -Path (Join-Path $projectRoot "README.md") -Value $readme

# requirements.txt
$requirements = @"
pg8000==1.30.3
google-generativeai==0.3.2
pyyaml==6.0.1
python-dotenv==1.0.0
polars==0.20.2
"@

Set-Content -Path (Join-Path $projectRoot "requirements.txt") -Value $requirements

# .env.example
$envExample = @"
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
GEMINI_API_KEY=your_gemini_api_key_here
"@

Set-Content -Path (Join-Path $projectRoot ".env.example") -Value $envExample

# config.yaml
$config = @"
database:
  host: localhost
  port: 5432

kpi_targets:
  roas_target: 3.5
  cpo_target: 25.0
  cpm_benchmark: 15.0

ai_settings:
  model: gemini-pro
  temperature: 0.7
  max_tokens: 1000
"@

Set-Content -Path (Join-Path $projectRoot "config.yaml") -Value $config

# main.py
$main = @"
#!/usr/bin/env python3
"""
Media Buy AI Insights - Main Entry Point
Complete executive demo integrating database, KPI calculation, AI insights, and reporting
"""

import argparse
import sys
from datetime import datetime

from src.database import DatabaseManager
from src.kpi_calculator import KPICalculator
from src.ai_insights import InsightGenerator
from src.report_generator import ReportGenerator

def main():
    """Main application entry point"""
    
    parser = argparse.ArgumentParser(
        description='Generate AI-powered insights for TV media buy campaigns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py --client BARK --days 30        # Analyze BARK client, last 30 days
  python main.py --client OPOS --days 7         # Analyze OPOS client, last 7 days  
  python main.py --list-clients                 # Show available clients
  python main.py --client ALL --days 14         # Analyze all clients combined
        '''
    )
    
    parser.add_argument('--client', type=str, 
                       help='Client name to analyze (use --list-clients to see options)')
    parser.add_argument('--days', type=int, default=30,
                       help='Lookback period in days (default: 30)')
    parser.add_argument('--output', type=str, default='both', 
                       choices=['console', 'file', 'both'],
                       help='Output format (default: both)')
    parser.add_argument('--list-clients', action='store_true',
                       help='List available clients and exit')
    parser.add_argument('--save-detailed', action='store_true',
                       help='Save detailed JSON report in addition to executive summary')
    
    args = parser.parse_args()
    
    # Print header
    print("🚀 AI-Powered Media Buy Insights")
    print("=" * 60)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize database connection
        print("\n📡 Connecting to campaign database...")
        db = DatabaseManager()
        
        # Handle list clients request
        if args.list_clients:
            print(f"\n📋 Available clients with attribution data (last {args.days} days):")
            clients = db.get_available_clients(args.days)
            if clients:
                for i, client in enumerate(clients, 1):
                    print(f"   {i:2d}. {client}")
                print(f"\nTotal: {len(clients)} clients available")
            else:
                print("   No clients found with attribution data")
            db.close()
            return
        
        # Validate client parameter
        if not args.client:
            print("❌ Error: --client parameter is required")
            print("💡 Use --list-clients to see available options")
            sys.exit(1)
        
        # Get available clients
        available_clients = db.get_available_clients(args.days)
        
        if args.client.upper() == 'ALL':
            print(f"📊 Analyzing ALL clients combined (last {args.days} days)")
            client_name = 'ALL_CLIENTS'
            campaign_data = db.get_campaign_data(client=None, days=args.days)
        else:
            client_upper = args.client.upper()
            if client_upper not in available_clients:
                print(f"❌ Error: Client '{args.client}' not found")
                print(f"💡 Available clients: {', '.join(available_clients[:10])}")
                if len(available_clients) > 10:
                    print(f"   ... and {len(available_clients) - 10} more (use --list-clients for full list)")
                db.close()
                sys.exit(1)
            
            client_name = client_upper
            print(f"📊 Analyzing client: {client_name} (last {args.days} days)")
            campaign_data = db.get_campaign_data(client=client_name, days=args.days)
        
        # Check if we have data
        if campaign_data.is_empty():
            print(f"❌ No campaign data found for {client_name} in last {args.days} days")
            print("💡 Try a different client or longer time period")
            db.close()
            sys.exit(1)
        
        print(f"✅ Found {len(campaign_data):,} attributed TV spots for analysis")
        
        # Initialize analysis components
        print("\n🧮 Calculating campaign KPIs...")
        kpi_calculator = KPICalculator()
        kpis = kpi_calculator.calculate_campaign_kpis(campaign_data)
        
        print("🤖 Generating AI insights...")
        insight_generator = InsightGenerator()
        insights = insight_generator.generate_comprehensive_insights(kpis, client_name)
        
        print("📋 Generating executive report...")
        report_generator = ReportGenerator()
        report = report_generator.generate_report(campaign_data, kpis, insights)
        
        # Output results
        if args.output in ['console', 'both']:
            report_generator.print_to_console(report)
        
        if args.output in ['file', 'both']:
            # Always save executive summary
            summary_file = report_generator.save_executive_summary(report)
            
            # Save detailed report if requested
            if args.save_detailed:
                detailed_file = report_generator.save_to_file(report)
                print(f"📊 Detailed analysis: {detailed_file}")
        
        print(f"\n✅ Analysis complete for {client_name}!")
        
        # Close database connection
        db.close()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your .env file has correct database credentials")
        print("   2. Ensure GEMINI_API_KEY is set for AI insights")
        print("   3. Verify database connectivity and table access")
        sys.exit(1)

if __name__ == "__main__":
    main()
"@

Set-Content -Path (Join-Path $projectRoot "main.py") -Value $main

# Create empty source files
$sourceFiles = @("database.py", "kpi_calculator.py", "ai_insights.py", "report_generator.py")

foreach ($file in $sourceFiles) {
    $content = @"
# $file
# TODO: Implement $file functionality

class $(($file -replace '\.py','').Split('_') | ForEach-Object { (Get-Culture).TextInfo.ToTitleCase($_) } | Join-String):
    def __init__(self):
        pass
"@
    Set-Content -Path (Join-Path $projectRoot "src/$file") -Value $content
}

# Create basic SQL file
$sql = @"
-- Campaign performance query
SELECT 
    cpt.unique_key,
    cpt.client,
    cpt.revenue as cost,
    lam.overall_revenue,
    lam.overall_roas,
    lam.impressions
FROM core_post_time cpt
LEFT JOIN linear_attribution_metrics lam ON cpt.unique_key = lam.unique_key
WHERE cpt.date >= CURRENT_DATE - INTERVAL '%s days'
ORDER BY cpt.date DESC
"@

Set-Content -Path (Join-Path $projectRoot "queries/campaign_performance.sql") -Value $sql

# Create prompt template
$prompts = @"
You are a media buying expert. Analyze this campaign data and provide:

1. Performance summary
2. Key insights  
3. Optimization recommendations

Data: {data}
KPIs: {kpis}
"@

Set-Content -Path (Join-Path $projectRoot "templates/insight_prompts.txt") -Value $prompts

Write-Host ""
Write-Host "Project created successfully!" -ForegroundColor Green
Write-Host "Location: $projectRoot" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. cd $projectRoot"
Write-Host "2. pip install -r requirements.txt"
Write-Host "3. cp .env.example .env"
Write-Host "4. Edit .env with your credentials"
Write-Host "5. Implement the source files in src/"