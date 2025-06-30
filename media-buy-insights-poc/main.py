#!/usr/bin/env python3
"""
Media Buy AI Insights - Clean Main Entry Point
Pipeline: Database → KPI Analysis → Gemini JSON Insights → Power BI CSV
"""

import argparse
import sys
from datetime import datetime

from src.database import DatabaseManager
from src.kpi_calculator import KPICalculator
from src.core.gemini_client import GeminiInsightGenerator
from src.prompts.prompt_builder import CampaignPromptBuilder
from src.insights.insight_parser import InsightParser
from src.insights.insight_formatter import PowerBIInsightFormatter

def main():
    """Main entry point for AI-powered campaign insights"""
    
    parser = argparse.ArgumentParser(
        description='Generate AI insights for TV campaigns using Google Gemini',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py --client BARK --days 30        # Analyze BARK with Gemini
  python main.py --client OPOS --days 7         # Analyze OPOS, last 7 days  
  python main.py --list-clients                 # Show available clients
  python main.py --test-gemini                  # Test Gemini API connection
        '''
    )
    
    parser.add_argument('--client', type=str, help='Client name to analyze')
    parser.add_argument('--days', type=int, default=30, help='Lookback period in days (default: 30)')
    parser.add_argument('--list-clients', action='store_true', help='List available clients')
    parser.add_argument('--test-gemini', action='store_true', help='Test Gemini API connection')
    
    args = parser.parse_args()
    
    print("🚀 AI-Powered Media Buy Insights")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test Gemini if requested
        if args.test_gemini:
            print("\n🤖 Testing Gemini API...")
            client = GeminiInsightGenerator()
            if client.test_connection():
                print("✅ Gemini API connection successful")
            else:
                print("❌ Gemini API connection failed")
                print("💡 Check GEMINI_API_KEY in .env file")
            return
        
        # Initialize database
        print("\n📡 Connecting to database...")
        db = DatabaseManager()
        
        # List clients if requested
        if args.list_clients:
            print(f"\n📋 Available clients (last {args.days} days):")
            clients = db.get_available_clients(args.days)
            if clients:
                for i, client in enumerate(clients, 1):
                    print(f"   {i:2d}. {client}")
            else:
                print("   No clients found with attribution data")
            db.close()
            return
        
        # Validate client
        if not args.client:
            print("❌ Error: --client parameter required")
            print("💡 Use --list-clients to see options")
            sys.exit(1)
        
        # Get available clients and validate
        available_clients = db.get_available_clients(args.days)
        client_upper = args.client.upper()
        
        if client_upper not in [c.upper() for c in available_clients]:
            print(f"❌ Client '{args.client}' not found")
            print(f"💡 Available: {', '.join(available_clients[:5])}")
            db.close()
            sys.exit(1)
        
        # Get campaign data
        print(f"\n📊 Analyzing {client_upper} (last {args.days} days)")
        campaign_data = db.get_campaign_data(client=client_upper, days=args.days)
        
        if campaign_data.is_empty():
            print(f"❌ No data found for {client_upper}")
            db.close()
            sys.exit(1)
        
        print(f"✅ Found {len(campaign_data):,} TV spots")
        
        # Calculate KPIs
        print("\n🧮 Calculating KPIs...")
        kpi_calculator = KPICalculator()
        kpis = kpi_calculator.calculate_campaign_kpis(campaign_data)
        
        # Initialize Gemini components
        print("\n🤖 Generating AI insights...")
        gemini_client = GeminiInsightGenerator()
        prompt_builder = CampaignPromptBuilder()
        insight_parser = InsightParser()
        formatter = PowerBIInsightFormatter()
        
        # Build prompt and get insights
        prompt = prompt_builder.build_analysis_prompt(kpis, client_upper)
        raw_insights = gemini_client.generate_campaign_insights(prompt)
        
        # Parse and format insights
        parsed_insights = insight_parser.parse_gemini_response(raw_insights, client_upper)
        powerbi_rows = formatter.format_for_powerbi(parsed_insights)
        
        # Save CSV
        csv_path = formatter.save_to_csv(powerbi_rows)
        
        # Print summary
        print_insights_summary(parsed_insights, csv_path)
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ CRITICAL FAILURE: {e}")
        print("\n💡 Check:")
        print("   1. GEMINI_API_KEY in .env file")
        print("   2. Database connectivity")
        print("   3. Client has attribution data")
        sys.exit(1)

def print_insights_summary(insights: dict, csv_path: str):
    """Print clean insights summary"""
    
    metadata = insights['metadata']
    executive = insights.get('executive_summary', {})
    
    print(f"\n🎯 INSIGHTS GENERATED")
    print("=" * 50)
    print(f"📊 Client: {metadata['client_name']}")
    print(f"📈 Total Insights: {metadata['insight_count']}")
    
    # Executive summary
    if executive.get('summary'):
        print(f"\n📋 EXECUTIVE SUMMARY:")
        print(f"   {executive['summary']}")
        print(f"   Confidence: {executive.get('confidence')} | Urgency: {executive.get('urgency_level')}")
    
    # Top opportunities
    opportunities = insights.get('scaling_opportunities', [])
    if opportunities:
        print(f"\n🚀 TOP OPPORTUNITIES:")
        for i, opp in enumerate(opportunities[:3], 1):
            entity = opp.get('station') or opp.get('daypart') or 'Unknown'
            impact = opp.get('projected_impact', 'Performance improvement')
            print(f"   {i}. {entity}: {impact}")
    
    # Underperformers
    underperformers = insights.get('underperformers', [])
    if underperformers:
        print(f"\n⚠️  UNDERPERFORMERS:")
        for i, under in enumerate(underperformers[:2], 1):
            entity = under.get('entity', 'Unknown')
            action = under.get('recommended_action', 'investigate')
            print(f"   {i}. {entity}: {action}")
    
    # Budget moves
    reallocations = insights.get('budget_reallocations', [])
    if reallocations:
        print(f"\n💰 BUDGET MOVES:")
        for i, realloc in enumerate(reallocations[:2], 1):
            from_station = realloc.get('from_station', '')
            to_station = realloc.get('to_station', '')
            spots = realloc.get('spots_to_move', 'budget')
            if from_station and to_station:
                print(f"   {i}. Move {spots} spots: {from_station} → {to_station}")
    
    print(f"\n💾 Power BI CSV: {csv_path}")
    print("=" * 50)

if __name__ == "__main__":
    main()