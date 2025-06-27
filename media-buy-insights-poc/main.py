#!/usr/bin/env python3
"""
Enhanced Media Buy AI Insights - Main Entry Point
Complete executive demo with comprehensive granular insights for Power BI dashboard
"""

import argparse
import sys
from datetime import datetime

from src.database import DatabaseManager
from src.kpi_calculator import KPICalculator
from src.ai_insights import InsightGenerator
from src.report_generator import ReportGenerator

def main():
    """Main application entry point with enhanced insights"""
    
    parser = argparse.ArgumentParser(
        description='Generate comprehensive AI-powered insights for TV media buy campaigns with Power BI integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py --client BARK --days 30        # Generate comprehensive insights for BARK
  python main.py --client OPOS --days 7         # Analyze OPOS with granular station/daypart insights  
  python main.py --list-clients                 # Show available clients
  python main.py --client ALL --days 14         # Analyze all clients with full insight matrix
  python main.py --client BARK --powerbi-ready  # Generate Power BI optimized insights
  python main.py --client OPOS --insights-only  # Generate only enhanced insights CSV
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
    parser.add_argument('--powerbi-ready', action='store_true',
                       help='Generate Power BI optimized reports with comprehensive insights')
    parser.add_argument('--insights-only', action='store_true',
                       help='Generate only enhanced insights CSV for Power BI import')
    parser.add_argument('--no-console', action='store_true',
                       help='Skip console output, save reports only')
    parser.add_argument('--include-quadrants', action='store_true',
                       help='Include performance quadrant analysis in outputs')
    parser.add_argument('--detailed-combinations', action='store_true',
                       help='Generate detailed station+daypart combination insights')
    
    args = parser.parse_args()
    
    # Handle flag combinations
    if args.no_console or args.insights_only:
        args.output = 'file'
    elif args.powerbi_ready:
        args.output = 'both'
        args.include_quadrants = True
        args.detailed_combinations = True
    
    # Print header
    print("🚀 Enhanced AI-Powered Media Buy Insights")
    print("=" * 70)
    print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.powerbi_ready:
        print("🎯 Power BI Dashboard Mode: Comprehensive insights enabled")
    
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
        
        # Initialize enhanced analysis components
        print("\n🧮 Calculating comprehensive campaign KPIs...")
        kpi_calculator = KPICalculator()
        kpis = kpi_calculator.calculate_campaign_kpis(campaign_data)
        
        print("🤖 Generating comprehensive AI insights with granular analysis...")
        insight_generator = InsightGenerator()
        comprehensive_insights = insight_generator.generate_comprehensive_insights(kpis, client_name)
        
        print(f"📊 Generated {comprehensive_insights['metadata']['total_insights_generated']} total insights")
        
        # Generate reports
        print("📋 Generating comprehensive reports...")
        report_generator = ReportGenerator()
        
        # Create enhanced report structure
        report = report_generator.generate_report(campaign_data, kpis, comprehensive_insights)
        
        # Output results based on user preferences
        saved_files = {}
        
        # Console output (unless suppressed or insights-only)
        if args.output in ['console', 'both'] and not args.insights_only:
            if args.powerbi_ready:
                print("\n" + "="*70)
                print("📊 POWER BI DASHBOARD INSIGHTS PREVIEW")
                print("="*70)
                report_generator.print_insights_summary(comprehensive_insights)
            else:
                report_generator.print_to_console(report)
        
        # File output
        if args.output in ['file', 'both'] or args.insights_only or args.powerbi_ready:
            print(f"\n💾 Saving enhanced reports to output/reports/...")
            
            base_filename = f"{client_name.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if args.insights_only:
                # Save only comprehensive insights CSV
                csv_file = insight_generator.save_insights_csv(comprehensive_insights, f"{base_filename}_insights")
                if csv_file:
                    saved_files['insights_csv'] = csv_file
                    print(f"\n📊 Comprehensive Insights CSV Export Complete!")
                    print(f"   📁 File: {csv_file}")
                    print(f"   💡 Import this CSV into Power BI for comprehensive dashboard insights")
                
            elif args.powerbi_ready:
                # Save all Power BI optimized reports
                detailed_file = report_generator.save_detailed_report(report, f"{base_filename}_powerbi_detailed")
                exec_file = report_generator.save_executive_summary(report, f"{base_filename}_powerbi_executive")
                insights_csv = insight_generator.save_insights_csv(comprehensive_insights, f"{base_filename}_powerbi_insights")
                
                # Additional Power BI specific exports
                station_csv = report_generator.save_station_performance_csv(report, f"{base_filename}_station_performance")
                daypart_csv = report_generator.save_daypart_performance_csv(report, f"{base_filename}_daypart_performance")
                combination_csv = report_generator.save_combination_performance_csv(report, f"{base_filename}_combination_performance")
                
                if detailed_file:
                    saved_files['powerbi_detailed'] = detailed_file
                if exec_file:
                    saved_files['powerbi_executive'] = exec_file
                if insights_csv:
                    saved_files['powerbi_insights'] = insights_csv
                if station_csv:
                    saved_files['station_performance'] = station_csv
                if daypart_csv:
                    saved_files['daypart_performance'] = daypart_csv
                if combination_csv:
                    saved_files['combination_performance'] = combination_csv
                
            else:
                # Save standard reports
                detailed_file = report_generator.save_detailed_report(report, f"{base_filename}_detailed")
                exec_file = report_generator.save_executive_summary(report, f"{base_filename}_executive")
                insights_csv = insight_generator.save_insights_csv(comprehensive_insights, f"{base_filename}_insights")
                
                if detailed_file:
                    saved_files['detailed'] = detailed_file
                if exec_file:
                    saved_files['executive'] = exec_file
                if insights_csv:
                    saved_files['insights'] = insights_csv
        
        # Report what was saved
        if saved_files:
            if not args.insights_only:
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
        
        # Power BI integration guidance
        if args.powerbi_ready or args.insights_only:
            print(f"\n🎯 Power BI Dashboard Integration Ready!")
            
            if args.powerbi_ready:
                print(f"📊 Complete dataset exported:")
                print(f"   • AI Insights: {saved_files.get('powerbi_insights', 'N/A')}")
                print(f"   • Station Performance: {saved_files.get('station_performance', 'N/A')}")
                print(f"   • Daypart Performance: {saved_files.get('daypart_performance', 'N/A')}")
                print(f"   • Combination Analysis: {saved_files.get('combination_performance', 'N/A')}")
            else:
                print(f"📊 AI Insights: {saved_files.get('insights_csv', 'N/A')}")
            
            print(f"\n📝 Power BI Import Instructions:")
            print(f"   1. Open Power BI Desktop")
            print(f"   2. Get Data → Text/CSV")
            print(f"   3. Import all CSV files from output/reports/")
            print(f"   4. Create relationships using client + station + daypart keys")
            print(f"   5. Build visualizations using the insight categories and performance metrics")
        
        # Provide quick summary of key insights (unless insights-only)
        if not args.insights_only:
            print(f"\n🔍 Quick Insights Preview:")
            
            # Show key findings
            key_findings = comprehensive_insights.get('key_findings', [])
            for i, finding in enumerate(key_findings[:3], 1):
                print(f"   {i}. {finding}")
            
            # Show top station insight
            station_insights = comprehensive_insights.get('station_insights', [])
            if station_insights:
                top_station_insight = station_insights[0]
                impact_emoji = "🔥" if top_station_insight.get('priority', 999) <= 2 else "📈"
                print(f"\n⚡ Top Station Opportunity: {top_station_insight.get('recommendation', 'See detailed reports')} {impact_emoji}")
            
            # Show top daypart insight
            daypart_insights = comprehensive_insights.get('daypart_insights', [])
            if daypart_insights:
                top_daypart_insight = daypart_insights[0]
                print(f"⏰ Top Daypart Opportunity: {top_daypart_insight.get('recommendation', 'See detailed reports')}")
            
            # Show quadrant analysis if included
            if args.include_quadrants:
                quadrants = comprehensive_insights.get('performance_quadrants', {})
                if quadrants:
                    champions = quadrants.get('high_volume_high_efficiency', [])
                    hidden_gems = quadrants.get('low_volume_high_efficiency', [])
                    print(f"\n🏆 Performance Quadrants:")
                    print(f"   • Champions (Scale these): {len(champions)} stations")
                    print(f"   • Hidden Gems (Test these): {len(hidden_gems)} stations")
        
        print(f"\n✅ Comprehensive analysis complete for {client_name}!")
        print(f"📈 Total insights generated: {comprehensive_insights['metadata']['total_insights_generated']}")
        
        # Close database connection
        db.close()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Comprehensive analysis failed: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your .env file has correct database credentials")
        print("   2. Ensure GEMINI_API_KEY is set for AI insights")
        print("   3. Verify database connectivity and table access")
        print("   4. Try with --list-clients to verify data availability")
        print("   5. Use --insights-only flag to generate only CSV exports")
        print("   6. Try --powerbi-ready for complete Power BI integration")
        sys.exit(1)

def print_version_info():
    """Print system information"""
    print("System Components:")
    print("  • Database: PostgreSQL with Polars analytics")
    print("  • AI Engine: Google Gemini 2.0 Flash")
    print("  • Analytics: Comprehensive KPI calculation with quadrant analysis")
    print("  • Insights: Granular station, daypart, and combination analysis")
    print("  • Reports: Console + Detailed Text + Executive Summary + CSV")
    print("  • Power BI: Multi-table CSV export for advanced dashboard integration")
    print("  • Visualizations: Performance quadrants, opportunity matrix, budget reallocation")

if __name__ == "__main__":
    main()