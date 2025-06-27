"""
Report Generator - Format campaign insights for console and Power BI consumption
Streamlined version focused on essential outputs without redundancy
"""

import json
import os
import csv
from datetime import datetime
from typing import Dict, Any, List

class ReportGenerator:
    def __init__(self, output_dir: str = "output/reports"):
        """Initialize report generator with output directory"""
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_report(self, campaign_data: Any, kpis: Dict[str, Any], insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive report structure from campaign analysis
        Input: Campaign data (DataFrame), KPIs, and AI insights
        Output: Structured report ready for output
        """
        
        # Extract key information
        metadata = kpis.get('metadata', {})
        totals = kpis.get('totals', {})
        efficiency = kpis.get('efficiency', {})
        performance = kpis.get('performance_vs_targets', {})
        dimensional = kpis.get('dimensional_analysis', {})
        
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'client_name': insights.get('metadata', {}).get('client_name', 'Unknown'),
                'analysis_period': metadata.get('date_range', {}),
                'spots_analyzed': metadata.get('spots_analyzed', 0),
                'data_quality_score': metadata.get('data_quality_score', 0),
                'ai_confidence': insights.get('metadata', {}).get('analysis_confidence', 0),
                'total_insights_generated': insights.get('metadata', {}).get('total_insights_generated', 0)
            },
            
            'executive_summary': {
                'ai_summary': insights.get('executive_summary', 'Summary not available'),
                'key_findings': insights.get('key_findings', []),
                'overall_performance': self._assess_overall_performance(totals, efficiency)
            },
            
            'campaign_metrics': {
                'totals': totals,
                'efficiency_metrics': efficiency,
                'performance_vs_targets': performance
            },
            
            'performance_data': {
                'station_performance': dimensional.get('station_performance', []),
                'daypart_performance': dimensional.get('daypart_performance', []),
                'station_daypart_combinations': dimensional.get('station_daypart_combinations', [])
            },
            
            'ai_insights': {
                'station_insights': insights.get('station_insights', []),
                'daypart_insights': insights.get('daypart_insights', []),
                'combination_insights': insights.get('station_daypart_insights', []),
                'performance_quadrants': insights.get('performance_quadrants', {}),
                'opportunity_matrix': insights.get('opportunity_matrix', []),
                'optimization_priorities': insights.get('optimization_priorities', [])
            }
        }
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print concise summary to console"""
        
        metadata = report['metadata']
        executive = report['executive_summary']
        metrics = report['campaign_metrics']
        ai_insights = report['ai_insights']
        
        print(f"\n📊 CLIENT: {metadata['client_name'].upper()}")
        print(f"📅 Period: {metadata.get('analysis_period', {}).get('start_date', 'N/A')} to {metadata.get('analysis_period', {}).get('end_date', 'N/A')}")
        print(f"📺 Spots Analyzed: {metadata['spots_analyzed']:,}")
        print(f"🎯 Data Quality: {metadata['data_quality_score']:.0f}% | AI Confidence: {metadata['ai_confidence']:.0%}")
        
        # Executive Summary
        print(f"\n📋 EXECUTIVE SUMMARY:")
        print(f"{executive['ai_summary']}")
        
        # Key Findings
        if executive['key_findings']:
            print(f"\n🔍 KEY FINDINGS:")
            for i, finding in enumerate(executive['key_findings'], 1):
                print(f"   {i}. {finding}")
        
        # Performance Metrics
        totals = metrics['totals']
        efficiency = metrics['efficiency_metrics']
        
        print(f"\n📈 CAMPAIGN METRICS:")
        print(f"   Revenue: ${totals.get('total_revenue', 0):,.2f}")
        print(f"   Visits: {totals.get('total_visits', 0):,}")
        print(f"   Orders: {totals.get('total_orders', 0):,}")
        
        visit_rate = totals.get('total_visits', 0) / max(totals.get('total_spots', 1), 1)
        print(f"   Visits per Spot: {visit_rate:.2f}")
        
        if efficiency.get('roas'):
            print(f"   ROAS: {efficiency['roas']:.2f}x")
        if efficiency.get('cpo'):
            print(f"   Cost per Order: ${efficiency['cpo']:.2f}")
        
        # Top Insights
        station_insights = ai_insights.get('station_insights', [])
        if station_insights:
            print(f"\n🎯 TOP STATION OPPORTUNITIES:")
            for insight in station_insights[:3]:
                station = insight.get('station', 'Unknown')
                opportunity = insight.get('opportunity_type', 'Monitor')
                print(f"   • {station}: {opportunity}")
        
        # Performance Quadrants
        quadrants = ai_insights.get('performance_quadrants', {})
        if quadrants:
            champions = quadrants.get('high_volume_high_efficiency', [])
            hidden_gems = quadrants.get('low_volume_high_efficiency', [])
            print(f"\n📊 PERFORMANCE QUADRANTS:")
            print(f"   • Champions (Scale These): {len(champions)} stations")
            print(f"   • Hidden Gems (Test These): {len(hidden_gems)} stations")
        
        print(f"\n✅ Analysis complete - {metadata['total_insights_generated']} total insights generated")
    
    def save_executive_summary(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save executive summary"""
        
        if filename is None:
            client_name = report['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_executive_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.txt")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                metadata = report['metadata']
                executive = report['executive_summary']
                
                file.write(f"EXECUTIVE SUMMARY - {metadata['client_name'].upper()}\n")
                file.write("="*70 + "\n\n")
                
                file.write(f"Analysis Period: {metadata.get('analysis_period', {}).get('start_date', 'N/A')} to {metadata.get('analysis_period', {}).get('end_date', 'N/A')}\n")
                file.write(f"Spots Analyzed: {metadata['spots_analyzed']:,}\n")
                file.write(f"Data Quality: {metadata['data_quality_score']:.0f}%\n")
                file.write(f"AI Insights Generated: {metadata.get('total_insights_generated', 0):,}\n\n")
                
                file.write("EXECUTIVE SUMMARY:\n")
                file.write(f"{executive['ai_summary']}\n\n")
                
                if executive['key_findings']:
                    file.write("KEY FINDINGS:\n")
                    for i, finding in enumerate(executive['key_findings'], 1):
                        file.write(f"{i}. {finding}\n")
                    file.write("\n")
                
                # Add top optimization opportunities (fix encoding issue)
                ai_insights = report.get('ai_insights', {})
                opportunities = ai_insights.get('opportunity_matrix', [])
                if opportunities:
                    file.write("TOP OPTIMIZATION OPPORTUNITIES:\n")
                    for i, opp in enumerate(opportunities[:3], 1):
                        from_station = opp.get('from_station', 'Unknown')
                        to_station = opp.get('to_station', 'Unknown')
                        projected_gain = opp.get('projected_visit_gain', 0)
                        confidence = opp.get('confidence', 'Medium')
                        # Replace Unicode arrow with ASCII equivalent
                        file.write(f"{i}. {from_station} -> {to_station}: ")
                        file.write(f"+{projected_gain} visits ({confidence} confidence)\n")
                
                file.write(f"\nGenerated: {metadata['generated_at']}\n")
            
            print(f"📄 Executive summary saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving executive summary: {e}")
            return ""
    
    def save_detailed_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save detailed report with comprehensive insights"""
        
        if filename is None:
            client_name = report['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_detailed_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.txt")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                metadata = report['metadata']
                executive = report['executive_summary']
                metrics = report['campaign_metrics']
                ai_insights = report['ai_insights']
                
                # Write report header
                file.write("="*80 + "\n")
                file.write("🎯 DETAILED CAMPAIGN ANALYSIS REPORT\n")
                file.write("="*80 + "\n")
                
                # Header Information
                file.write(f"\n📊 CLIENT: {metadata['client_name'].upper()}\n")
                file.write(f"📅 Period: {metadata.get('analysis_period', {}).get('start_date', 'N/A')} to {metadata.get('analysis_period', {}).get('end_date', 'N/A')}\n")
                file.write(f"📺 Spots Analyzed: {metadata['spots_analyzed']:,}\n")
                file.write(f"🎯 Data Quality: {metadata['data_quality_score']:.0f}% | AI Confidence: {metadata['ai_confidence']:.0%}\n")
                file.write(f"🤖 Total Insights Generated: {metadata['total_insights_generated']:,}\n")
                
                # Executive Summary
                file.write(f"\n" + "="*60 + "\n")
                file.write("📋 EXECUTIVE SUMMARY\n")
                file.write("="*60 + "\n")
                file.write(f"\n{executive['ai_summary']}\n")
                
                # Key Findings
                if executive['key_findings']:
                    file.write(f"\n🔍 KEY FINDINGS:\n")
                    for i, finding in enumerate(executive['key_findings'], 1):
                        file.write(f"   {i}. {finding}\n")
                
                # Performance Metrics
                self._write_performance_metrics_section(file, metrics)
                
                # Station Analysis
                file.write(f"\n" + "="*60 + "\n")
                file.write("📺 STATION ANALYSIS\n")
                file.write("="*60 + "\n")
                
                station_insights = ai_insights.get('station_insights', [])
                if station_insights:
                    file.write(f"\n🎯 STATION-SPECIFIC AI INSIGHTS:\n")
                    for insight in station_insights[:5]:  # Top 5 only
                        station = insight.get('station', 'Unknown')
                        tier = insight.get('performance_tier', 'Unknown')
                        opportunity = insight.get('opportunity_type', 'Monitor')
                        recommendation = insight.get('recommendation', 'No recommendation')
                        
                        file.write(f"\n   • {station} ({tier}):\n")
                        file.write(f"     Type: {opportunity}\n")
                        file.write(f"     Recommendation: {recommendation}\n")
                
                # Performance Quadrants
                quadrants = ai_insights.get('performance_quadrants', {})
                if quadrants:
                    file.write(f"\n" + "="*60 + "\n")
                    file.write("🎯 PERFORMANCE QUADRANTS\n")
                    file.write("="*60 + "\n")
                    
                    quadrant_labels = {
                        'high_volume_high_efficiency': 'CHAMPIONS (Scale These)',
                        'low_volume_high_efficiency': 'HIDDEN GEMS (Test These)',
                        'high_volume_low_efficiency': 'INEFFICIENT GIANTS (Optimize These)',
                        'low_volume_low_efficiency': 'UNDERPERFORMERS (Consider Eliminating)'
                    }
                    
                    for quadrant_key, stations in quadrants.items():
                        if stations:
                            label = quadrant_labels.get(quadrant_key, quadrant_key)
                            file.write(f"\n🔸 {label}:\n")
                            for station in stations[:3]:  # Top 3 per quadrant
                                name = station.get('station', 'Unknown')
                                volume = station.get('volume', 0)
                                efficiency = station.get('efficiency', 0)
                                action = station.get('action', 'Monitor')
                                file.write(f"   • {name}: {volume:,} visits, {efficiency:.1f} avg/spot → {action}\n")
                
                # Budget Reallocation Opportunities
                opportunities = ai_insights.get('opportunity_matrix', [])
                if opportunities:
                    file.write(f"\n" + "="*60 + "\n")
                    file.write("💡 BUDGET REALLOCATION OPPORTUNITIES\n")
                    file.write("="*60 + "\n")
                    
                    for i, opportunity in enumerate(opportunities[:3], 1):  # Top 3 only
                        from_station = opportunity.get('from_station', 'Unknown')
                        to_station = opportunity.get('to_station', 'Unknown')
                        efficiency_gain = opportunity.get('efficiency_gain', 0)
                        projected_gain = opportunity.get('projected_visit_gain', 0)
                        confidence = opportunity.get('confidence', 'Medium')
                        
                        # Replace Unicode arrow with ASCII equivalent
                        file.write(f"\n   {i}. {from_station} -> {to_station}\n")
                        file.write(f"      Efficiency Gain: +{efficiency_gain:.1f} visits/spot\n")
                        file.write(f"      Projected Impact: +{projected_gain} visits\n")
                        file.write(f"      Confidence: {confidence}\n")
                
                file.write(f"\n" + "="*80 + "\n")
                file.write("END OF REPORT\n")
                file.write("="*80 + "\n")
            
            print(f"📊 Detailed report saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving detailed report: {e}")
            return ""
    
    def save_station_performance_csv(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save station performance data as CSV for Power BI"""
        
        if filename is None:
            client_name = report['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_stations_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        
        try:
            performance_data = report.get('performance_data', {})
            ai_insights = report.get('ai_insights', {})
            station_performance = performance_data.get('station_performance', [])
            station_insights = ai_insights.get('station_insights', [])
            
            # Create a lookup for insights by station
            insights_lookup = {insight.get('station'): insight for insight in station_insights}
            
            station_data = []
            for station in station_performance:
                station_name = station.get('station', 'Unknown')
                insight = insights_lookup.get(station_name, {})
                
                station_data.append({
                    'client': report['metadata']['client_name'],
                    'station': station_name,
                    'total_visits': station.get('total_visits', 0),
                    'total_spots': station.get('spots', 0),
                    'avg_visits_per_spot': station.get('avg_visits_per_spot', 0),
                    'total_cost': station.get('total_cost', 0),
                    'cpm': station.get('cpm', 0),
                    'performance_tier': insight.get('performance_tier', 'Unknown'),
                    'opportunity_type': insight.get('opportunity_type', 'Monitor'),
                    'ai_recommendation': insight.get('recommendation', ''),
                    'confidence': insight.get('confidence', 'Medium'),
                    'action_type': insight.get('action_type', 'monitor'),
                    'priority': insight.get('priority', 999),
                    'generated_date': report['metadata']['generated_at'][:10]
                })
            
            if station_data:
                fieldnames = ['client', 'station', 'total_visits', 'total_spots', 'avg_visits_per_spot', 
                             'total_cost', 'cpm', 'performance_tier', 'opportunity_type', 
                             'ai_recommendation', 'confidence', 'action_type', 'priority', 'generated_date']
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(station_data)
                
                print(f"📺 Station CSV saved: {filepath}")
                return filepath
            else:
                print("⚠️  No station performance data available")
                return ""
                
        except Exception as e:
            print(f"❌ Error saving station CSV: {e}")
            return ""
    
    def save_daypart_performance_csv(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save daypart performance data as CSV for Power BI"""
        
        if filename is None:
            client_name = report['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_dayparts_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        
        try:
            performance_data = report.get('performance_data', {})
            ai_insights = report.get('ai_insights', {})
            daypart_performance = performance_data.get('daypart_performance', [])
            daypart_insights = ai_insights.get('daypart_insights', [])
            
            # Create a lookup for insights by daypart
            insights_lookup = {insight.get('daypart'): insight for insight in daypart_insights}
            
            daypart_data = []
            for daypart in daypart_performance:
                daypart_name = daypart.get('daypart', 'Unknown')
                insight = insights_lookup.get(daypart_name, {})
                
                daypart_data.append({
                    'client': report['metadata']['client_name'],
                    'daypart': daypart_name,
                    'total_visits': daypart.get('total_visits', 0),
                    'total_spots': daypart.get('spots', 0),
                    'avg_visits_per_spot': daypart.get('avg_visits_per_spot', 0),
                    'total_cost': daypart.get('total_cost', 0),
                    'cpm': daypart.get('cpm', 0),
                    'efficiency_rating': insight.get('efficiency_rating', 'Unknown'),
                    'recommendation_priority': insight.get('recommendation_priority', 'Low'),
                    'ai_recommendation': insight.get('recommendation', ''),
                    'confidence': insight.get('confidence', 'Medium'),
                    'action_type': insight.get('action_type', 'monitor'),
                    'priority': insight.get('priority', 999),
                    'generated_date': report['metadata']['generated_at'][:10]
                })
            
            if daypart_data:
                fieldnames = ['client', 'daypart', 'total_visits', 'total_spots', 'avg_visits_per_spot', 
                             'total_cost', 'cpm', 'efficiency_rating', 'recommendation_priority', 
                             'ai_recommendation', 'confidence', 'action_type', 'priority', 'generated_date']
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(daypart_data)
                
                print(f"⏰ Daypart CSV saved: {filepath}")
                return filepath
            else:
                print("⚠️  No daypart performance data available")
                return ""
                
        except Exception as e:
            print(f"❌ Error saving daypart CSV: {e}")
            return ""
    
    def _write_performance_metrics_section(self, file, metrics: Dict[str, Any]):
        """Write performance metrics section to file"""
        
        file.write(f"\n" + "="*60 + "\n")
        file.write("📈 CAMPAIGN PERFORMANCE METRICS\n")
        file.write("="*60 + "\n")
        
        totals = metrics['totals']
        efficiency = metrics['efficiency_metrics']
        
        # Core Metrics
        file.write(f"\n💰 CAMPAIGN TOTALS:\n")
        file.write(f"   Total Spend: ${totals.get('total_cost', 0):,.2f}\n")
        file.write(f"   Website Visits: {totals.get('total_visits', 0):,}\n")
        file.write(f"   Orders: {totals.get('total_orders', 0):,}\n")
        file.write(f"   Revenue: ${totals.get('total_revenue', 0):,.2f}\n")
        file.write(f"   Impressions: {totals.get('total_impressions', 0):,}\n")
        
        # Efficiency Metrics
        file.write(f"\n📊 EFFICIENCY METRICS:\n")
        if efficiency.get('roas'):
            file.write(f"   ROAS: {efficiency['roas']:.2f}x\n")
        if efficiency.get('cpm'):
            file.write(f"   CPM: ${efficiency['cpm']:.2f}\n")
        if efficiency.get('cpo'):
            file.write(f"   Cost per Order: ${efficiency['cpo']:.2f}\n")
        if totals.get('total_visits', 0) > 0 and totals.get('total_cost', 0) > 0:
            cpv = totals['total_cost'] / totals['total_visits']
            file.write(f"   Cost per Visit: ${cpv:.2f}\n")
        
        visit_rate = totals.get('total_visits', 0) / max(totals.get('total_spots', 1), 1)
        file.write(f"   Visits per Spot: {visit_rate:.2f}\n")
    
    def _assess_overall_performance(self, totals: Dict, efficiency: Dict) -> str:
        """Generate overall performance assessment"""
        
        visit_rate = totals.get('total_visits', 0) / max(totals.get('total_spots', 1), 1)
        
        if visit_rate >= 2.0:
            return "Excellent engagement with strong optimization opportunities"
        elif visit_rate >= 1.5:
            return "Strong performance with clear optimization paths"
        elif visit_rate >= 1.0:
            return "Solid performance with improvement opportunities"
        elif visit_rate >= 0.5:
            return "Moderate performance with optimization potential"
        else:
            return "Needs improvement - optimization strategy required"


# Test the Report Generator
if __name__ == "__main__":
    print("🧪 Testing Report Generator...")
    print("=" * 50)
    
    try:
        import sys
        sys.path.append('.')
        from src.database import DatabaseManager
        from src.kpi_calculator import KPICalculator
        from src.ai_insights import InsightGenerator
        
        with DatabaseManager() as db:
            clients = db.get_available_clients(30)
            if clients:
                client = clients[0]
                print(f"📊 Testing report generation for client: {client}")
                
                # Get data and generate analysis
                df = db.get_campaign_data(client=client, days=30)
                if not df.is_empty():
                    calculator = KPICalculator()
                    kpis = calculator.calculate_campaign_kpis(df)
                    
                    insight_generator = InsightGenerator()
                    insights = insight_generator.generate_comprehensive_insights(kpis, client)
                    
                    # Generate reports
                    reporter = ReportGenerator()
                    report = reporter.generate_report(df, kpis, insights)
                    
                    # Print to console
                    reporter.print_summary(report)
                    
                    print(f"\n✅ Report generation test completed!")
                        
                else:
                    print("❌ No campaign data available")
            else:
                print("❌ No clients available")
                
    except ImportError as e:
        print(f"❌ Cannot import required modules: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")