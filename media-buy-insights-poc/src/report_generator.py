"""
Report Generator - Format campaign insights for executive consumption
Creates console, file, and structured outputs from KPI and AI analysis
Enhanced version with CSV export capability for Power BI integration
"""

import json
import os
import csv
from datetime import datetime
from typing import Dict, Any

class ReportGenerator:
    def __init__(self, output_dir: str = "output/reports"):
        """Initialize report generator with output directory"""
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_report(self, campaign_data: Any, kpis: Dict[str, Any], insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive report structure from campaign analysis
        Input: Campaign data (DataFrame), KPIs, and AI insights
        Output: Structured report ready for consumption
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
                'ai_confidence': insights.get('metadata', {}).get('analysis_confidence', 0)
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
            'optimization_insights': {
                'station_performance': dimensional.get('station_performance', []),
                'daypart_performance': dimensional.get('daypart_performance', []),
                'station_daypart_combinations': dimensional.get('station_daypart_combinations', []),
                'ai_recommendations': insights.get('prescriptive_recommendations', 'Recommendations not available'),
                'optimization_priorities': insights.get('optimization_priorities', [])
            },
            'ai_analysis': {
                'descriptive_analysis': insights.get('descriptive_analysis', 'Analysis not available'),
                'prescriptive_recommendations': insights.get('prescriptive_recommendations', {}),
                'model_used': insights.get('metadata', {}).get('ai_model', 'Unknown')
            }
        }
        
        return report
    
    def save_ai_insights_csv(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save AI insights as CSV for Power BI import"""
        
        if filename is None:
            client_name = report['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_ai_insights_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        
        try:
            ai_analysis = report.get('ai_analysis', {})
            prescriptive_data = ai_analysis.get('prescriptive_recommendations', {})
            
            # Extract structured insights from the AI analysis
            insights_data = []
            
            # Process optimization recommendations
            if isinstance(prescriptive_data, dict) and 'optimization_recommendations' in prescriptive_data:
                for rec in prescriptive_data['optimization_recommendations']:
                    insights_data.append({
                        'client': report['metadata']['client_name'],
                        'product': 'DEFAULT',  # Add product logic if needed
                        'insight_type': 'optimization',
                        'priority': rec.get('priority', 999),
                        'impact_level': rec.get('impact_level', 'Medium'),
                        'area': rec.get('area', 'Unknown'),
                        'station': rec.get('station'),
                        'daypart': rec.get('daypart'),
                        'recommendation': rec.get('recommendation', ''),
                        'expected_impact': rec.get('expected_impact', ''),
                        'confidence': rec.get('confidence', 'Unknown'),
                        'action_type': rec.get('action_type', 'optimize'),
                        'generated_date': report['metadata']['generated_at'][:10]  # Just date part
                    })
            
            # Process key findings
            if isinstance(prescriptive_data, dict) and 'key_findings' in prescriptive_data:
                for finding in prescriptive_data['key_findings']:
                    insights_data.append({
                        'client': report['metadata']['client_name'],
                        'product': 'DEFAULT',
                        'insight_type': 'finding',
                        'priority': finding.get('priority', 999),
                        'impact_level': finding.get('impact_level', 'Medium'),
                        'area': finding.get('finding_type', 'Analysis'),
                        'station': finding.get('station'),
                        'daypart': finding.get('daypart'),
                        'recommendation': finding.get('description', ''),
                        'expected_impact': 'N/A',
                        'confidence': 'N/A',
                        'action_type': 'insight',
                        'generated_date': report['metadata']['generated_at'][:10]
                    })
            
            # Fallback: If no structured data, create basic insights from optimization_priorities
            if not insights_data:
                optimization_priorities = report['optimization_insights'].get('optimization_priorities', [])
                for i, priority in enumerate(optimization_priorities, 1):
                    insights_data.append({
                        'client': report['metadata']['client_name'],
                        'product': 'DEFAULT',
                        'insight_type': 'optimization',
                        'priority': i,
                        'impact_level': priority.get('impact', 'Medium'),
                        'area': priority.get('area', 'Unknown'),
                        'station': None,
                        'daypart': None,
                        'recommendation': priority.get('recommendation', ''),
                        'expected_impact': 'Manual analysis required',
                        'confidence': 'N/A',
                        'action_type': 'optimize',
                        'generated_date': report['metadata']['generated_at'][:10]
                    })
            
            # Write CSV
            if insights_data:
                fieldnames = ['client', 'product', 'insight_type', 'priority', 'impact_level', 
                             'area', 'station', 'daypart', 'recommendation', 'expected_impact', 
                             'confidence', 'action_type', 'generated_date']
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(insights_data)
                
                print(f"📊 AI insights CSV saved to: {filepath}")
                print(f"📝 Exported {len(insights_data)} insights to CSV")
                return filepath
            else:
                print("⚠️  No structured insights available for CSV export")
                return ""
                
        except Exception as e:
            print(f"❌ Error saving AI insights CSV: {e}")
            return ""
    
    def print_to_console(self, report: Dict[str, Any]):
        """Print executive-friendly report to console"""
        
        metadata = report['metadata']
        executive = report['executive_summary']
        metrics = report['campaign_metrics']
        optimization = report['optimization_insights']
        
        print("\n" + "="*80)
        print("🎯 EXECUTIVE CAMPAIGN ANALYSIS REPORT")
        print("="*80)
        
        # Header Information
        print(f"\n📊 CLIENT: {metadata['client_name'].upper()}")
        print(f"📅 Period: {metadata.get('analysis_period', {}).get('start_date', 'N/A')} to {metadata.get('analysis_period', {}).get('end_date', 'N/A')}")
        print(f"📺 Spots Analyzed: {metadata['spots_analyzed']:,}")
        print(f"🎯 Data Quality: {metadata['data_quality_score']:.0f}% | AI Confidence: {metadata['ai_confidence']:.0%}")
        
        # Executive Summary
        print(f"\n" + "="*60)
        print("📋 EXECUTIVE SUMMARY")
        print("="*60)
        
        print(f"\n{executive['ai_summary']}")
        
        # Key Findings
        if executive['key_findings']:
            print(f"\n🔍 KEY FINDINGS:")
            for i, finding in enumerate(executive['key_findings'], 1):
                print(f"   {i}. {finding}")
        
        # Campaign Metrics
        print(f"\n" + "="*60)
        print("📈 CAMPAIGN PERFORMANCE METRICS")
        print("="*60)
        
        totals = metrics['totals']
        efficiency = metrics['efficiency_metrics']
        
        # Core Metrics
        print(f"\n💰 CAMPAIGN TOTALS:")
        print(f"   Total Spend: ${totals.get('total_cost', 0):,.2f}")
        print(f"   Website Visits: {totals.get('total_visits', 0):,}")
        print(f"   Orders: {totals.get('total_orders', 0):,}")
        print(f"   Revenue: ${totals.get('total_revenue', 0):,.2f}")
        print(f"   Impressions: {totals.get('total_impressions', 0):,}")
        
        # Efficiency Metrics
        print(f"\n📊 EFFICIENCY METRICS:")
        if efficiency.get('roas'):
            print(f"   ROAS: {efficiency['roas']:.2f}x")
        if efficiency.get('cpm'):
            print(f"   CPM: ${efficiency['cpm']:.2f}")
        if efficiency.get('cpo'):
            print(f"   Cost per Order: ${efficiency['cpo']:.2f}")
        if totals.get('total_visits', 0) > 0 and totals.get('total_cost', 0) > 0:
            cpv = totals['total_cost'] / totals['total_visits']
            print(f"   Cost per Visit: ${cpv:.2f}")
        
        visit_rate = totals.get('total_visits', 0) / max(totals.get('total_spots', 1), 1)
        print(f"   Visits per Spot: {visit_rate:.2f}")
        
        # Performance vs Targets
        performance = metrics.get('performance_vs_targets', {})
        if performance:
            print(f"\n🎯 PERFORMANCE vs TARGETS:")
            for metric, data in performance.items():
                if isinstance(data, dict):
                    status = "✅" if data.get('status') in ['exceeds', 'efficient'] else "⚠️"
                    print(f"   {metric.upper()}: {data.get('grade', 'N/A')} {status}")
        
        # Top Performing Analysis
        print(f"\n" + "="*60)
        print("🏆 TOP PERFORMING SEGMENTS")
        print("="*60)
        
        # Top Stations
        stations = optimization.get('station_performance', [])
        if stations:
            print(f"\n📺 TOP STATIONS (by total visits):")
            for i, station in enumerate(stations[:10], 1):
                visits = station.get('total_visits', 0)
                spots = station.get('spots', 0)
                avg_visits = station.get('avg_visits_per_spot', 0)
                print(f"   {i:2d}. {station.get('station', 'Unknown')}: {visits:,} visits ({spots} spots, {avg_visits:.1f} avg/spot)")
        
        # Top Dayparts
        dayparts = optimization.get('daypart_performance', [])
        if dayparts:
            print(f"\n⏰ TOP DAYPARTS (by efficiency):")
            for i, daypart in enumerate(dayparts, 1):
                dp_name = daypart.get('daypart', 'Unknown')
                efficiency_val = daypart.get('avg_visits_per_spot', 0)
                spots = daypart.get('spots', 0)
                visits = daypart.get('total_visits', 0)
                print(f"   {i}. {dp_name}: {efficiency_val:.2f} visits/spot ({visits:,} visits from {spots} spots)")
        
        # Best Combinations
        combos = optimization.get('station_daypart_combinations', [])
        if combos:
            print(f"\n🎯 BEST STATION + DAYPART COMBINATIONS:")
            for i, combo in enumerate(combos[:10], 1):
                station = combo.get('station', 'Unknown')
                daypart = combo.get('daypart', 'Unknown')
                efficiency_val = combo.get('avg_visits_per_spot', 0)
                spots = combo.get('spots', 0)
                visits = combo.get('total_visits', 0)
                print(f"   {i:2d}. {station} + {daypart}: {efficiency_val:.2f} visits/spot ({visits:,} visits from {spots} spots)")
        
        # AI Analysis
        print(f"\n" + "="*60)
        print("🤖 AI ANALYSIS & INSIGHTS")
        print("="*60)
        
        # Descriptive Analysis
        ai_analysis = report['ai_analysis']
        descriptive = ai_analysis.get('descriptive_analysis', '')
        if descriptive and descriptive != 'Analysis not available':
            print(f"\n📊 PERFORMANCE ANALYSIS:")
            analysis_lines = descriptive.split('. ')
            for line in analysis_lines:
                if line.strip():
                    print(f"   • {line.strip()}.")
        
        # AI Recommendations - Handle both string and structured formats
        ai_recommendations = optimization.get('ai_recommendations', '')
        if isinstance(ai_recommendations, dict):
            # Structured format
            if 'optimization_recommendations' in ai_recommendations:
                print(f"\n🎯 AI-POWERED OPTIMIZATION RECOMMENDATIONS:")
                for rec in ai_recommendations['optimization_recommendations']:
                    impact_emoji = "🔥" if rec.get('impact_level') == 'High' else "📈"
                    print(f"   • {rec.get('area', 'Unknown')}: {rec.get('recommendation', 'Unknown')} {impact_emoji}")
        elif isinstance(ai_recommendations, str) and ai_recommendations != 'Recommendations not available':
            # String format (fallback)
            print(f"\n🎯 AI-POWERED OPTIMIZATION RECOMMENDATIONS:")
            recommendations = ai_recommendations.split('\n')
            for rec in recommendations:
                if rec.strip():
                    print(f"   {rec}")
        
        # Optimization Priorities
        priorities = optimization.get('optimization_priorities', [])
        if priorities:
            print(f"\n⚡ IMMEDIATE ACTION ITEMS:")
            for priority in priorities:
                impact_emoji = "🔥" if priority.get('impact') == 'High' else "📈" if priority.get('impact') == 'Medium' else "📊"
                effort = priority.get('effort', 'Unknown')
                area = priority.get('area', 'Unknown')
                rec = priority.get('recommendation', 'Unknown')
                print(f"   • {area}: {rec} {impact_emoji} (Impact: {priority.get('impact', 'Unknown')}, Effort: {effort})")
        
        # Technical Details
        print(f"\n" + "="*60)
        print("📋 TECHNICAL DETAILS")
        print("="*60)
        print(f"AI Model: {ai_analysis.get('model_used', 'Unknown')}")
        print(f"Analysis Confidence: {metadata['ai_confidence']:.0%}")
        print(f"Data Quality Score: {metadata['data_quality_score']:.1f}%")
        print(f"Generated: {metadata['generated_at']}")
        
        print("\n" + "="*80)
        print("END OF REPORT")
        print("="*80)
    
    def save_detailed_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save detailed report as formatted text file (mirrors console output)"""
        
        if filename is None:
            client_name = report['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_detailed_analysis_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.txt")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                metadata = report['metadata']
                executive = report['executive_summary']
                metrics = report['campaign_metrics']
                optimization = report['optimization_insights']
                
                # Write detailed report that mirrors console output
                file.write("="*80 + "\n")
                file.write("🎯 EXECUTIVE CAMPAIGN ANALYSIS REPORT\n")
                file.write("="*80 + "\n")
                
                # Header Information
                file.write(f"\n📊 CLIENT: {metadata['client_name'].upper()}\n")
                file.write(f"📅 Period: {metadata.get('analysis_period', {}).get('start_date', 'N/A')} to {metadata.get('analysis_period', {}).get('end_date', 'N/A')}\n")
                file.write(f"📺 Spots Analyzed: {metadata['spots_analyzed']:,}\n")
                file.write(f"🎯 Data Quality: {metadata['data_quality_score']:.0f}% | AI Confidence: {metadata['ai_confidence']:.0%}\n")
                
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
                
                # Campaign Metrics
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
                
                # Performance vs Targets
                performance = metrics.get('performance_vs_targets', {})
                if performance:
                    file.write(f"\n🎯 PERFORMANCE vs TARGETS:\n")
                    for metric, data in performance.items():
                        if isinstance(data, dict):
                            status = "✅" if data.get('status') in ['exceeds', 'efficient'] else "⚠️"
                            file.write(f"   {metric.upper()}: {data.get('grade', 'N/A')} {status}\n")
                
                # Top Performing Analysis
                file.write(f"\n" + "="*60 + "\n")
                file.write("🏆 TOP PERFORMING SEGMENTS\n")
                file.write("="*60 + "\n")
                
                # Top Stations
                stations = optimization.get('station_performance', [])
                if stations:
                    file.write(f"\n📺 TOP STATIONS (by total visits):\n")
                    for i, station in enumerate(stations[:10], 1):
                        visits = station.get('total_visits', 0)
                        spots = station.get('spots', 0)
                        avg_visits = station.get('avg_visits_per_spot', 0)
                        file.write(f"   {i:2d}. {station.get('station', 'Unknown')}: {visits:,} visits ({spots} spots, {avg_visits:.1f} avg/spot)\n")
                
                # Top Dayparts
                dayparts = optimization.get('daypart_performance', [])
                if dayparts:
                    file.write(f"\n⏰ TOP DAYPARTS (by efficiency):\n")
                    for i, daypart in enumerate(dayparts, 1):
                        dp_name = daypart.get('daypart', 'Unknown')
                        efficiency_val = daypart.get('avg_visits_per_spot', 0)
                        spots = daypart.get('spots', 0)
                        visits = daypart.get('total_visits', 0)
                        file.write(f"   {i}. {dp_name}: {efficiency_val:.2f} visits/spot ({visits:,} visits from {spots} spots)\n")
                
                # Best Combinations
                combos = optimization.get('station_daypart_combinations', [])
                if combos:
                    file.write(f"\n🎯 BEST STATION + DAYPART COMBINATIONS:\n")
                    for i, combo in enumerate(combos[:10], 1):
                        station = combo.get('station', 'Unknown')
                        daypart = combo.get('daypart', 'Unknown')
                        efficiency_val = combo.get('avg_visits_per_spot', 0)
                        spots = combo.get('spots', 0)
                        visits = combo.get('total_visits', 0)
                        file.write(f"   {i:2d}. {station} + {daypart}: {efficiency_val:.2f} visits/spot ({visits:,} visits from {spots} spots)\n")
                
                # AI Analysis
                file.write(f"\n" + "="*60 + "\n")
                file.write("🤖 AI ANALYSIS & INSIGHTS\n")
                file.write("="*60 + "\n")
                
                # Descriptive Analysis
                ai_analysis = report['ai_analysis']
                descriptive = ai_analysis.get('descriptive_analysis', '')
                if descriptive and descriptive != 'Analysis not available':
                    file.write(f"\n📊 PERFORMANCE ANALYSIS:\n")
                    analysis_lines = descriptive.split('. ')
                    for line in analysis_lines:
                        if line.strip():
                            file.write(f"   • {line.strip()}.\n")
                
                # AI Recommendations
                ai_recommendations = optimization.get('ai_recommendations', '')
                if isinstance(ai_recommendations, dict):
                    # Structured format
                    if 'optimization_recommendations' in ai_recommendations:
                        file.write(f"\n🎯 AI-POWERED OPTIMIZATION RECOMMENDATIONS:\n")
                        for rec in ai_recommendations['optimization_recommendations']:
                            impact_emoji = "🔥" if rec.get('impact_level') == 'High' else "📈"
                            file.write(f"   • {rec.get('area', 'Unknown')}: {rec.get('recommendation', 'Unknown')} {impact_emoji}\n")
                elif isinstance(ai_recommendations, str) and ai_recommendations != 'Recommendations not available':
                    file.write(f"\n🎯 AI-POWERED OPTIMIZATION RECOMMENDATIONS:\n")
                    recommendations = ai_recommendations.split('\n')
                    for rec in recommendations:
                        if rec.strip():
                            file.write(f"   {rec}\n")
                
                # Optimization Priorities
                priorities = optimization.get('optimization_priorities', [])
                if priorities:
                    file.write(f"\n⚡ IMMEDIATE ACTION ITEMS:\n")
                    for priority in priorities:
                        impact_emoji = "🔥" if priority.get('impact') == 'High' else "📈" if priority.get('impact') == 'Medium' else "📊"
                        effort = priority.get('effort', 'Unknown')
                        area = priority.get('area', 'Unknown')
                        rec = priority.get('recommendation', 'Unknown')
                        file.write(f"   • {area}: {rec} {impact_emoji} (Impact: {priority.get('impact', 'Unknown')}, Effort: {effort})\n")
                
                # Technical Details
                file.write(f"\n" + "="*60 + "\n")
                file.write("📋 TECHNICAL DETAILS\n")
                file.write("="*60 + "\n")
                file.write(f"AI Model: {ai_analysis.get('model_used', 'Unknown')}\n")
                file.write(f"Analysis Confidence: {metadata['ai_confidence']:.0%}\n")
                file.write(f"Data Quality Score: {metadata['data_quality_score']:.1f}%\n")
                file.write(f"Generated: {metadata['generated_at']}\n")
                
                file.write("\n" + "="*80 + "\n")
                file.write("END OF REPORT\n")
                file.write("="*80 + "\n")
            
            print(f"📊 Detailed analysis report saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving detailed report: {e}")
            return ""
    
    def save_to_file(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save comprehensive report to JSON file"""
        
        if filename is None:
            client_name = report['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_data_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.json")
        
        try:
            with open(filepath, 'w') as file:
                json.dump(report, file, indent=2, default=str)
            
            print(f"💾 Raw data report saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving JSON report: {e}")
            return ""
    
    def save_executive_summary(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save executive summary as readable text file"""
        
        if filename is None:
            client_name = report['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_executive_summary_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.txt")
        
        try:
            with open(filepath, 'w') as file:
                metadata = report['metadata']
                executive = report['executive_summary']
                
                file.write(f"EXECUTIVE SUMMARY - {metadata['client_name'].upper()}\n")
                file.write("="*60 + "\n\n")
                
                file.write(f"Analysis Period: {metadata.get('analysis_period', {}).get('start_date', 'N/A')} to {metadata.get('analysis_period', {}).get('end_date', 'N/A')}\n")
                file.write(f"Spots Analyzed: {metadata['spots_analyzed']:,}\n")
                file.write(f"Data Quality: {metadata['data_quality_score']:.0f}%\n\n")
                
                file.write("SUMMARY:\n")
                file.write(f"{executive['ai_summary']}\n\n")
                
                if executive['key_findings']:
                    file.write("KEY FINDINGS:\n")
                    for i, finding in enumerate(executive['key_findings'], 1):
                        file.write(f"{i}. {finding}\n")
                    file.write("\n")
                
                # Add optimization priorities
                priorities = report['optimization_insights'].get('optimization_priorities', [])
                if priorities:
                    file.write("IMMEDIATE ACTION ITEMS:\n")
                    for priority in priorities:
                        file.write(f"• {priority.get('recommendation', 'Unknown')} (Impact: {priority.get('impact', 'Unknown')})\n")
                
                file.write(f"\nGenerated: {metadata['generated_at']}\n")
            
            print(f"📋 Executive summary saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving executive summary: {e}")
            return ""
    
    def save_all_reports(self, report: Dict[str, Any], base_filename: str = None) -> Dict[str, str]:
        """Save all report formats and return file paths"""
        
        if base_filename is None:
            client_name = report['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_filename = f"{client_name}_{timestamp}"
        
        file_paths = {}
        
        # Save detailed report (mirrors console output)
        detailed_path = self.save_detailed_report(report, f"{base_filename}_detailed")
        if detailed_path:
            file_paths['detailed_analysis'] = detailed_path
        
        # Save executive summary
        exec_path = self.save_executive_summary(report, f"{base_filename}_executive")
        if exec_path:
            file_paths['executive_summary'] = exec_path
        
        # Save raw data JSON
        json_path = self.save_to_file(report, f"{base_filename}_data")
        if json_path:
            file_paths['json_data'] = json_path
        
        # Save AI insights CSV
        csv_path = self.save_ai_insights_csv(report, f"{base_filename}_ai_insights")
        if csv_path:
            file_paths['ai_insights_csv'] = csv_path
        
        return file_paths
    
    def _assess_overall_performance(self, totals: Dict, efficiency: Dict) -> str:
        """Generate overall performance assessment"""
        
        visit_rate = totals.get('total_visits', 0) / max(totals.get('total_spots', 1), 1)
        
        if visit_rate >= 2.0:
            return "Excellent - High engagement with strong visit generation"
        elif visit_rate >= 1.5:
            return "Strong - Above-average visit generation performance"
        elif visit_rate >= 1.0:
            return "Good - Solid visit generation meeting expectations"
        elif visit_rate >= 0.5:
            return "Fair - Moderate visit generation with room for improvement"
        else:
            return "Needs Improvement - Low visit generation requiring optimization"


# Test the Enhanced Report Generator
if __name__ == "__main__":
    print("🧪 Testing Enhanced Report Generator...")
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
                print(f"📊 Testing enhanced report generation for client: {client}")
                
                # Get data and generate analysis
                df = db.get_campaign_data(client=client, days=30)
                if not df.is_empty():
                    calculator = KPICalculator()
                    kpis = calculator.calculate_campaign_kpis(df)
                    
                    insight_generator = InsightGenerator()
                    insights = insight_generator.generate_comprehensive_insights(kpis, client)
                    
                    # Generate and display report
                    reporter = ReportGenerator()
                    report = reporter.generate_report(df, kpis, insights)
                    
                    # Print to console
                    reporter.print_to_console(report)
                    
                    # Save all report formats
                    file_paths = reporter.save_all_reports(report)
                    
                    print(f"\n✅ Enhanced report generation test completed!")
                    print(f"📁 Files saved:")
                    for report_type, path in file_paths.items():
                        if path:
                            print(f"   • {report_type}: {path}")
                else:
                    print("❌ No campaign data available")
            else:
                print("❌ No clients available")
                
    except ImportError as e:
        print(f"❌ Cannot import required modules: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")