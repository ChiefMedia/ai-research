#!/usr/bin/env python3
"""
Media Buy AI Insights - Main Entry Point
Complete executive demo integrating database, KPI calculation, AI insights, and reporting
Enhanced version with automatic CSV export for Power BI integration
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
        description='Generate AI-powered insights for TV media buy campaigns with Power BI CSV export',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py --client BARK --days 30        # Analyze BARK client, save all reports + CSV
  python main.py --client OPOS --days 7         # Analyze OPOS client, last 7 days  
  python main.py --list-clients                 # Show available clients
  python main.py --client ALL --days 14         # Analyze all clients combined
  python main.py --client BARK --no-console     # Generate reports without console output
  python main.py --client OPOS --csv-only       # Generate only CSV for Power BI import
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
    parser.add_argument('--no-console', action='store_true',
                       help='Skip console output, save reports only')
    parser.add_argument('--csv-only', action='store_true',
                       help='Generate only CSV file for Power BI import')
    parser.add_argument('--executive-only', action='store_true',
                       help='Save only executive summary, skip detailed reports')
    parser.add_argument('--include-json', action='store_true',
                       help='Include raw JSON data file in addition to formatted reports')
    
    args = parser.parse_args()
    
    # Handle flag combinations
    if args.no_console:
        args.output = 'file'
    elif args.csv_only:
        args.output = 'file'
    
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
        
        print("📋 Generating comprehensive reports...")
        report_generator = ReportGenerator()
        report = report_generator.generate_report(campaign_data, kpis, insights)
        
        # Output results based on user preferences
        saved_files = {}
        
        # Console output (unless suppressed or CSV-only)
        if args.output in ['console', 'both'] and not args.csv_only:
            report_generator.print_to_console(report)
        
        # File output
        if args.output in ['file', 'both'] or args.csv_only:
            print(f"\n💾 Saving reports to output/reports/...")
            
            if args.csv_only:
                # Save only CSV for Power BI
                csv_file = report_generator.save_ai_insights_csv(report)
                if csv_file:
                    saved_files['ai_insights_csv'] = csv_file
                    print(f"\n📊 Power BI CSV Export Complete!")
                    print(f"   📁 File: {csv_file}")
                    print(f"   💡 Import this CSV into Power BI for dashboard insights")
                
            elif args.executive_only:
                # Save only executive summary
                exec_file = report_generator.save_executive_summary(report)
                if exec_file:
                    saved_files['executive_summary'] = exec_file
                
                # Always include CSV for Power BI integration
                csv_file = report_generator.save_ai_insights_csv(report)
                if csv_file:
                    saved_files['ai_insights_csv'] = csv_file
                
            else:
                # Save all reports by default
                if args.include_json:
                    # Save all report types including JSON
                    saved_files = report_generator.save_all_reports(report)
                else:
                    # Save detailed, executive, and CSV reports (skip JSON)
                    base_filename = f"{client_name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    detailed_file = report_generator.save_detailed_report(report, f"{base_filename}_detailed")
                    exec_file = report_generator.save_executive_summary(report, f"{base_filename}_executive")
                    csv_file = report_generator.save_ai_insights_csv(report, f"{base_filename}_ai_insights")
                    
                    if detailed_file:
                        saved_files['detailed_analysis'] = detailed_file
                    if exec_file:
                        saved_files['executive_summary'] = exec_file
                    if csv_file:
                        saved_files['ai_insights_csv'] = csv_file
        
        # Report what was saved
        if saved_files:
            if not args.csv_only:
                print(f"\n📁 Reports saved successfully:")
                for report_type, filepath in saved_files.items():
                    report_name = report_type.replace('_', ' ').title()
                    print(f"   • {report_name}: {filepath}")
                
                # Show file sizes
                print(f"\n📊 Report Summary:")
                total_size = 0
                for filepath in saved_files.values():
                    try:
                        import os
                        size = os.path.getsize(filepath) / 1024  # KB
                        total_size += size
                        filename = os.path.basename(filepath)
                        print(f"   • {filename}: {size:.1f} KB")
                    except:
                        pass
                
                if total_size > 0:
                    print(f"   📦 Total: {total_size:.1f} KB")
            
            # Highlight CSV file for Power BI
            if 'ai_insights_csv' in saved_files:
                print(f"\n🎯 Power BI Integration Ready!")
                print(f"   📊 CSV File: {saved_files['ai_insights_csv']}")
                print(f"   💡 Import this CSV into your Power BI dashboard for AI insights")
        
        print(f"\n✅ Analysis complete for {client_name}!")
        
        # Provide quick summary of key insights (unless CSV-only)
        if not args.csv_only:
            if insights.get('key_findings'):
                print(f"\n🔍 Quick Insights:")
                for i, finding in enumerate(insights['key_findings'][:3], 1):
                    print(f"   {i}. {finding}")
            
            # Show top optimization priority
            priorities = insights.get('optimization_priorities', [])
            if priorities:
                top_priority = priorities[0]
                impact_emoji = "🔥" if top_priority.get('impact') == 'High' else "📈"
                print(f"\n⚡ Top Priority: {top_priority.get('recommendation', 'Review detailed reports')} {impact_emoji}")
        
        # CSV-specific success message
        if args.csv_only:
            print(f"\n🎉 CSV export successful! Ready for Power BI import.")
            print(f"📝 Next steps:")
            print(f"   1. Open Power BI Desktop")
            print(f"   2. Get Data → Text/CSV")
            print(f"   3. Import: {saved_files.get('ai_insights_csv', 'CSV file')}")
            print(f"   4. Create relationships using client + product keys")
        
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
        print("   4. Try with --list-clients to verify data availability")
        print("   5. Use --csv-only flag to skip console output if needed")
        sys.exit(1)

def print_version_info():
    """Print system information"""
    print("System Components:")
    print("  • Database: PostgreSQL with Polars analytics")
    print("  • AI Engine: Google Gemini 1.5")
    print("  • Analytics: Campaign KPI calculation")
    print("  • Reports: Console + Detailed Text + Executive Summary + CSV")
    print("  • Power BI: CSV export for dashboard integration")

if __name__ == "__main__":
    main()