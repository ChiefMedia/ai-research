#!/usr/bin/env python3
"""
Media Buy AI Insights - Main Entry Point
Clean, focused application for generating AI-powered TV campaign insights
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
  python main.py --client BARK --output csv     # Generate only CSV for Power BI
        '''
    )
    
    parser.add_argument('--client', type=str, 
                       help='Client name to analyze (use --list-clients to see options)')
    parser.add_argument('--days', type=int, default=30,
                       help='Lookback period in days (default: 30)')
    parser.add_argument('--output', type=str, default='console', 
                       choices=['console', 'csv', 'reports', 'all'],
                       help='Output format: console=screen only, csv=Power BI export, reports=files, all=everything (default: console)')
    parser.add_argument('--list-clients', action='store_true',
                       help='List available clients and exit')
    
    args = parser.parse_args()
    
    # Print header
    print("🚀 Media Buy AI Insights")
    print("=" * 50)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize database connection
        print("\n📡 Connecting to database...")
        db = DatabaseManager()
        
        # Handle list clients request
        if args.list_clients:
            print(f"\n📋 Available clients (last {args.days} days):")
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
                print(f"💡 Available clients: {', '.join(available_clients[:5])}")
                if len(available_clients) > 5:
                    print(f"   ... and {len(available_clients) - 5} more (use --list-clients for full list)")
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
        
        print(f"✅ Found {len(campaign_data):,} TV spots for analysis")
        
        # Calculate KPIs
        print("\n🧮 Calculating campaign KPIs...")
        kpi_calculator = KPICalculator()
        kpis = kpi_calculator.calculate_campaign_kpis(campaign_data)
        
        # Generate AI insights
        print("🤖 Generating AI insights...")
        insight_generator = InsightGenerator()
        insights = insight_generator.generate_comprehensive_insights(kpis, client_name)
        
        # Generate reports
        print("📋 Generating reports...")
        report_generator = ReportGenerator()
        report = report_generator.generate_report(campaign_data, kpis, insights)
        
        # Output based on user preference
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_filename = f"{client_name.lower()}_{timestamp}"
        
        if args.output in ['console', 'all']:
            print("\n" + "="*60)
            print("📊 CAMPAIGN ANALYSIS RESULTS")
            print("="*60)
            report_generator.print_summary(report)
        
        if args.output in ['csv', 'all']:
            print(f"\n💾 Saving Power BI CSV exports...")
            csv_files = []
            
            # Main insights CSV
            insights_csv = insight_generator.save_insights_csv(insights, f"{base_filename}_insights")
            if insights_csv:
                csv_files.append(insights_csv)
            
            # Performance data CSVs
            station_csv = report_generator.save_station_performance_csv(report, f"{base_filename}_stations")
            if station_csv:
                csv_files.append(station_csv)
            
            daypart_csv = report_generator.save_daypart_performance_csv(report, f"{base_filename}_dayparts")
            if daypart_csv:
                csv_files.append(daypart_csv)
            
            if csv_files:
                print(f"\n📊 Power BI CSV files ready:")
                for csv_file in csv_files:
                    print(f"   📁 {csv_file}")
                print(f"\n💡 Import these CSV files into Power BI for dashboard visualization")
        
        if args.output in ['reports', 'all']:
            print(f"\n💾 Saving detailed reports...")
            
            # Executive summary
            exec_file = report_generator.save_executive_summary(report, f"{base_filename}_executive")
            if exec_file:
                print(f"   📄 Executive Summary: {exec_file}")
            
            # Detailed analysis
            detailed_file = report_generator.save_detailed_report(report, f"{base_filename}_detailed")
            if detailed_file:
                print(f"   📊 Detailed Report: {detailed_file}")
        
        # Show key insights preview
        if args.output == 'console':
            key_findings = insights.get('key_findings', [])
            if key_findings:
                print(f"\n🔍 Key Insights:")
                for i, finding in enumerate(key_findings[:3], 1):
                    print(f"   {i}. {finding}")
        
        print(f"\n✅ Analysis complete for {client_name}!")
        print(f"📈 Total insights generated: {insights['metadata']['total_insights_generated']}")
        
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
        print("   4. Use --list-clients to verify data availability")
        sys.exit(1)

if __name__ == "__main__":
    main()