"""
Report Generator - Format comprehensive campaign insights for Power BI consumption
Creates console, file, and structured outputs with granular station/daypart insights
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
    
    def generate_report(self, campaign_data: Any, kpis: Dict[str, Any], comprehensive_insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive report structure from comprehensive campaign analysis
        Input: Campaign data (DataFrame), KPIs, and comprehensive AI insights
        Output: Structured report ready for Power BI consumption
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
                'client_name': comprehensive_insights.get('metadata', {}).get('client_name', 'Unknown'),
                'analysis_period': metadata.get('date_range', {}),
                'spots_analyzed': metadata.get('spots_analyzed', 0),
                'data_quality_score': metadata.get('data_quality_score', 0),
                'ai_confidence': comprehensive_insights.get('metadata', {}).get('analysis_confidence', 0),
                'total_insights_generated': comprehensive_insights.get('metadata', {}).get('total_insights_generated', 0)
            },
            
            'executive_summary': {
                'ai_summary': comprehensive_insights.get('executive_summary', 'Summary not available'),
                'key_findings': comprehensive_insights.get('key_findings', []),
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
                'station_insights': comprehensive_insights.get('station_insights', []),
                'daypart_insights': comprehensive_insights.get('daypart_insights', []),
                'combination_insights': comprehensive_insights.get('station_daypart_insights', []),
                'performance_quadrants': comprehensive_insights.get('performance_quadrants', {}),
                'opportunity_matrix': comprehensive_insights.get('opportunity_matrix', []),
                'budget_reallocation_analysis': comprehensive_insights.get('budget_reallocation_analysis', {}),
                'optimization_priorities': comprehensive_insights.get('optimization_priorities', [])
            },
            
            'ai_analysis': {
                'comprehensive_insights': comprehensive_insights,
                'predictive_recommendations': comprehensive_insights.get('predictive_recommendations', []),
                'model_used': comprehensive_insights.get('metadata', {}).get('ai_model', 'Unknown')
            }
        }
        
        return report
    
    def print_insights_summary(self, comprehensive_insights: Dict[str, Any]):
        """Print Power BI focused insights summary"""
        
        metadata = comprehensive_insights.get('metadata', {})
        
        print(f"\n📊 CLIENT: {metadata.get('client_name', 'Unknown').upper()}")
        print(f"🤖 AI Model: {metadata.get('ai_model', 'Unknown')}")
        print(f"📈 Total Insights Generated: {metadata.get('total_insights_generated', 0):,}")
        print(f"🎯 Analysis Confidence: {metadata.get('analysis_confidence', 0):.0%}")
        
        # Station insights summary
        station_insights = comprehensive_insights.get('station_insights', [])
        if station_insights:
            print(f"\n📺 STATION INSIGHTS ({len(station_insights)} stations analyzed):")
            tier_counts = {}
            for insight in station_insights:
                tier = insight.get('performance_tier', 'Unknown')
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            for tier, count in tier_counts.items():
                print(f"   • {tier}: {count} stations")
        
        # Daypart insights summary
        daypart_insights = comprehensive_insights.get('daypart_insights', [])
        if daypart_insights:
            print(f"\n⏰ DAYPART INSIGHTS ({len(daypart_insights)} dayparts analyzed):")
            for insight in daypart_insights[:3]:
                efficiency = insight.get('efficiency_rating', 'Unknown')
                daypart = insight.get('daypart', 'Unknown')
                print(f"   • {daypart}: {efficiency} efficiency")
        
        # Performance quadrants summary
        quadrants = comprehensive_insights.get('performance_quadrants', {})
        if quadrants:
            print(f"\n🎯 PERFORMANCE QUADRANTS:")
            quadrant_labels = {
                'high_volume_high_efficiency': 'Champions (Scale These)',
                'low_volume_high_efficiency': 'Hidden Gems (Test These)',
                'high_volume_low_efficiency': 'Inefficient Giants (Optimize These)',
                'low_volume_low_efficiency': 'Underperformers (Consider Eliminating)'
            }
            
            for quadrant_key, stations in quadrants.items():
                label = quadrant_labels.get(quadrant_key, quadrant_key)
                print(f"   • {label}: {len(stations)} stations")
        
        # Opportunity matrix summary
        opportunities = comprehensive_insights.get('opportunity_matrix', [])
        if opportunities:
            print(f"\n💡 BUDGET REALLOCATION OPPORTUNITIES:")
            high_impact_opportunities = [o for o in opportunities if o.get('confidence') == 'High']
            print(f"   • High Confidence Opportunities: {len(high_impact_opportunities)}")
            if high_impact_opportunities:
                top_opportunity = high_impact_opportunities[0]
                print(f"   • Top Opportunity: {top_opportunity.get('from_station')} → {top_opportunity.get('to_station')}")
                print(f"     Expected Gain: {top_opportunity.get('projected_visit_gain', 0)} visits")
        
        print(f"\n📋 Ready for Power BI import with comprehensive dashboard insights!")
    
    def save_detailed_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save detailed report with comprehensive insights"""
        
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
                insights = report['optimization_insights']
                
                # Write report header
                file.write("="*80 + "\n")
                file.write("🎯 COMPREHENSIVE CAMPAIGN ANALYSIS REPORT\n")
                file.write("="*80 + "\n")
                
                # Header Information with metadata
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
                
                # Performance Metrics (existing section)
                self._write_performance_metrics_section(file, metrics)
                
                # Station Analysis
                file.write(f"\n" + "="*60 + "\n")
                file.write("📺 STATION ANALYSIS\n")
                file.write("="*60 + "\n")
                
                station_insights = insights.get('station_insights', [])
                if station_insights:
                    file.write(f"\n🎯 STATION-SPECIFIC AI INSIGHTS:\n")
                    for insight in station_insights[:10]:
                        station = insight.get('station', 'Unknown')
                        tier = insight.get('performance_tier', 'Unknown')
                        opportunity = insight.get('opportunity_type', 'Monitor')
                        recommendation = insight.get('recommendation', 'No recommendation')
                        impact = insight.get('expected_impact', 'Unknown impact')
                        
                        file.write(f"\n   • {station} ({tier}):\n")
                        file.write(f"     Type: {opportunity}\n")
                        file.write(f"     Recommendation: {recommendation}\n")
                        file.write(f"     Expected Impact: {impact}\n")
                
                # Daypart Analysis
                file.write(f"\n" + "="*60 + "\n")
                file.write("⏰ DAYPART ANALYSIS\n")
                file.write("="*60 + "\n")
                
                daypart_insights = insights.get('daypart_insights', [])
                if daypart_insights:
                    file.write(f"\n🎯 DAYPART-SPECIFIC AI INSIGHTS:\n")
                    for insight in daypart_insights:
                        daypart = insight.get('daypart', 'Unknown')
                        rating = insight.get('efficiency_rating', 'Unknown')
                        priority = insight.get('recommendation_priority', 'Low')
                        recommendation = insight.get('recommendation', 'No recommendation')
                        
                        file.write(f"\n   • {daypart} ({rating} efficiency):\n")
                        file.write(f"     Priority: {priority}\n")
                        file.write(f"     Recommendation: {recommendation}\n")
                
                # Performance Quadrants Analysis
                quadrants = insights.get('performance_quadrants', {})
                if quadrants:
                    file.write(f"\n" + "="*60 + "\n")
                    file.write("🎯 PERFORMANCE QUADRANTS ANALYSIS\n")
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
                            for station in stations[:5]:  # Top 5 per quadrant
                                name = station.get('station', 'Unknown')
                                volume = station.get('volume', 0)
                                efficiency = station.get('efficiency', 0)
                                action = station.get('action', 'Monitor')
                                file.write(f"   • {name}: {volume:,} visits, {efficiency:.1f} avg/spot → {action}\n")
                
                # Budget Reallocation Opportunities
                opportunities = insights.get('opportunity_matrix', [])
                if opportunities:
                    file.write(f"\n" + "="*60 + "\n")
                    file.write("💡 BUDGET REALLOCATION OPPORTUNITIES\n")
                    file.write("="*60 + "\n")
                    
                    for i, opportunity in enumerate(opportunities[:5], 1):
                        from_station = opportunity.get('from_station', 'Unknown')
                        to_station = opportunity.get('to_station', 'Unknown')
                        efficiency_gain = opportunity.get('efficiency_gain', 0)
                        projected_gain = opportunity.get('projected_visit_gain', 0)
                        confidence = opportunity.get('confidence', 'Medium')
                        
                        file.write(f"\n   {i}. {from_station} → {to_station}\n")
                        file.write(f"      Efficiency Gain: +{efficiency_gain:.1f} visits/spot\n")
                        file.write(f"      Projected Impact: +{projected_gain} visits\n")
                        file.write(f"      Confidence: {confidence}\n")
                
                # Technical Details
                file.write(f"\n" + "="*60 + "\n")
                file.write("📋 TECHNICAL DETAILS\n")
                file.write("="*60 + "\n")
                ai_analysis = report['ai_analysis']
                file.write(f"AI Model: {ai_analysis.get('model_used', 'Unknown')}\n")
                file.write(f"Analysis Confidence: {metadata['ai_confidence']:.0%}\n")
                file.write(f"Data Quality Score: {metadata['data_quality_score']:.1f}%\n")
                file.write(f"Total Insights Generated: {metadata['total_insights_generated']:,}\n")
                file.write(f"Generated: {metadata['generated_at']}\n")
                
                file.write("\n" + "="*80 + "\n")
                file.write("END OF REPORT\n")
                file.write("="*80 + "\n")
            
            print(f"📊 Detailed analysis report saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving detailed report: {e}")
            return ""
    
    def save_station_performance_csv(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save station performance data as CSV for Power BI"""
        
        if filename is None:
            client_name = report['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_station_performance_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        
        try:
            insights = report.get('optimization_insights', {})
            station_performance = insights.get('station_performance', [])
            station_insights = insights.get('station_insights', [])
            
            # Merge performance data with insights
            station_data = []
            
            # Create a lookup for insights by station
            insights_lookup = {insight.get('station'): insight for insight in station_insights}
            
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
                    'visits_per_thousand_impressions': station.get('visits_per_thousand_impressions', 0),
                    'performance_tier': insight.get('performance_tier', 'Unknown'),
                    'opportunity_type': insight.get('opportunity_type', 'Monitor'),
                    'ai_recommendation': insight.get('recommendation', ''),
                    'expected_impact': insight.get('expected_impact', ''),
                    'confidence': insight.get('confidence', 'Medium'),
                    'action_type': insight.get('action_type', 'monitor'),
                    'priority': insight.get('priority', 999),
                    'generated_date': report['metadata']['generated_at'][:10]
                })
            
            if station_data:
                fieldnames = ['client', 'station', 'total_visits', 'total_spots', 'avg_visits_per_spot', 
                             'total_cost', 'cpm', 'visits_per_thousand_impressions', 'performance_tier', 
                             'opportunity_type', 'ai_recommendation', 'expected_impact', 'confidence', 
                             'action_type', 'priority', 'generated_date']
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(station_data)
                
                print(f"📺 Station performance CSV saved to: {filepath}")
                return filepath
            else:
                print("⚠️  No station performance data available for CSV export")
                return ""
                
        except Exception as e:
            print(f"❌ Error saving station performance CSV: {e}")
            return ""
    
    def save_daypart_performance_csv(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save daypart performance data as CSV for Power BI"""
        
        if filename is None:
            client_name = report['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_daypart_performance_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        
        try:
            insights = report.get('optimization_insights', {})
            daypart_performance = insights.get('daypart_performance', [])
            daypart_insights = insights.get('daypart_insights', [])
            
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
                    'visit_efficiency': daypart.get('visit_efficiency', 0),
                    'visits_per_thousand_impressions': daypart.get('visits_per_thousand_impressions', 0),
                    'efficiency_rating': insight.get('efficiency_rating', 'Unknown'),
                    'recommendation_priority': insight.get('recommendation_priority', 'Low'),
                    'ai_recommendation': insight.get('recommendation', ''),
                    'expected_impact': insight.get('expected_impact', ''),
                    'confidence': insight.get('confidence', 'Medium'),
                    'action_type': insight.get('action_type', 'monitor'),
                    'priority': insight.get('priority', 999),
                    'generated_date': report['metadata']['generated_at'][:10]
                })
            
            if daypart_data:
                fieldnames = ['client', 'daypart', 'total_visits', 'total_spots', 'avg_visits_per_spot', 
                             'total_cost', 'cpm', 'visit_efficiency', 'visits_per_thousand_impressions', 
                             'efficiency_rating', 'recommendation_priority', 'ai_recommendation', 
                             'expected_impact', 'confidence', 'action_type', 'priority', 'generated_date']
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(daypart_data)
                
                print(f"⏰ Daypart performance CSV saved to: {filepath}")
                return filepath
            else:
                print("⚠️  No daypart performance data available for CSV export")
                return ""
                
        except Exception as e:
            print(f"❌ Error saving daypart performance CSV: {e}")
            return ""
    
    def save_combination_performance_csv(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save station+daypart combination performance data as CSV for Power BI"""
        
        if filename is None:
            client_name = report['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_combination_performance_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        
        try:
            insights = report.get('optimization_insights', {})
            combination_performance = insights.get('station_daypart_combinations', [])
            combination_insights = insights.get('combination_insights', [])
            
            # Create a lookup for insights by station+daypart
            insights_lookup = {}
            for insight in combination_insights:
                key = f"{insight.get('station')}_{insight.get('daypart')}"
                insights_lookup[key] = insight
            
            combination_data = []
            for combo in combination_performance:
                station = combo.get('station', 'Unknown')
                daypart = combo.get('daypart', 'Unknown')
                key = f"{station}_{daypart}"
                insight = insights_lookup.get(key, {})
                
                combination_data.append({
                    'client': report['metadata']['client_name'],
                    'station': station,
                    'daypart': daypart,
                    'combination': f"{station} + {daypart}",
                    'total_visits': combo.get('total_visits', 0),
                    'total_spots': combo.get('spots', 0),
                    'avg_visits_per_spot': combo.get('avg_visits_per_spot', 0),
                    'total_cost': combo.get('total_cost', 0),
                    'combo_tier': insight.get('combo_tier', 'Standard'),
                    'scaling_priority': insight.get('scaling_priority', 'Low'),
                    'confidence_level': insight.get('confidence_level', 'Low'),
                    'ai_recommendation': insight.get('recommendation', ''),
                    'expected_impact': insight.get('expected_impact', ''),
                    'action_type': insight.get('action_type', 'monitor'),
                    'priority': insight.get('priority', 999),
                    'generated_date': report['metadata']['generated_at'][:10]
                })
            
            if combination_data:
                fieldnames = ['client', 'station', 'daypart', 'combination', 'total_visits', 'total_spots', 
                             'avg_visits_per_spot', 'total_cost', 'combo_tier', 'scaling_priority', 
                             'confidence_level', 'ai_recommendation', 'expected_impact', 'action_type', 
                             'priority', 'generated_date']
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(combination_data)
                
                print(f"🎯 Station+Daypart combination CSV saved to: {filepath}")
                return filepath
            else:
                print("⚠️  No combination performance data available for CSV export")
                return ""
                
        except Exception as e:
            print(f"❌ Error saving combination performance CSV: {e}")
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
        
        # Performance vs Targets
        performance = metrics.get('performance_vs_targets', {})
        if performance:
            file.write(f"\n🎯 PERFORMANCE vs TARGETS:\n")
            for metric, data in performance.items():
                if isinstance(data, dict):
                    status = "✅" if data.get('status') in ['exceeds', 'efficient'] else "⚠️"
                    file.write(f"   {metric.upper()}: {data.get('grade', 'N/A')} {status}\n")
    
    def print_to_console(self, report: Dict[str, Any]):
        """Print comprehensive report to console"""
        
        metadata = report['metadata']
        executive = report['executive_summary']
        metrics = report['campaign_metrics']
        insights = report.get('optimization_insights', {})
        
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE CAMPAIGN ANALYSIS REPORT")
        print("="*80)
        
        # Header Information
        print(f"\n📊 CLIENT: {metadata['client_name'].upper()}")
        print(f"📅 Period: {metadata.get('analysis_period', {}).get('start_date', 'N/A')} to {metadata.get('analysis_period', {}).get('end_date', 'N/A')}")
        print(f"📺 Spots Analyzed: {metadata['spots_analyzed']:,}")
        print(f"🎯 Data Quality: {metadata['data_quality_score']:.0f}% | AI Confidence: {metadata['ai_confidence']:.0%}")
        print(f"🤖 AI Insights: {metadata.get('total_insights_generated', 0):,} total insights")
        
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
        
        # Performance Metrics (using existing logic)
        self._print_performance_metrics(metrics)
        
        # Station Insights Preview
        station_insights = insights.get('station_insights', [])
        if station_insights:
            print(f"\n" + "="*60)
            print("📺 TOP STATION INSIGHTS")
            print("="*60)
            
            for insight in station_insights[:5]:
                station = insight.get('station', 'Unknown')
                tier = insight.get('performance_tier', 'Unknown')
                opportunity = insight.get('opportunity_type', 'Monitor')
                print(f"\n   • {station} ({tier})")
                print(f"     Opportunity: {opportunity}")
                print(f"     AI Recommendation: {insight.get('recommendation', 'No recommendation')[:80]}...")
        
        # Performance Quadrants Summary
        quadrants = insights.get('performance_quadrants', {})
        if quadrants:
            print(f"\n" + "="*60)
            print("🎯 PERFORMANCE QUADRANTS SUMMARY")
            print("="*60)
            
            champions = quadrants.get('high_volume_high_efficiency', [])
            hidden_gems = quadrants.get('low_volume_high_efficiency', [])
            inefficient = quadrants.get('high_volume_low_efficiency', [])
            underperformers = quadrants.get('low_volume_low_efficiency', [])
            
            print(f"\n🏆 Champions (Scale These): {len(champions)} stations")
            if champions:
                for station in champions[:3]:
                    print(f"   • {station.get('station', 'Unknown')}: {station.get('volume', 0):,} visits")
            
            print(f"\n💎 Hidden Gems (Test These): {len(hidden_gems)} stations")
            if hidden_gems:
                for station in hidden_gems[:3]:
                    print(f"   • {station.get('station', 'Unknown')}: {station.get('efficiency', 0):.1f} visits/spot")
            
            print(f"\n⚠️  Inefficient Giants (Optimize These): {len(inefficient)} stations")
            print(f"🔻 Underperformers (Consider Eliminating): {len(underperformers)} stations")
        
        print("\n" + "="*80)
        print("END OF REPORT")
        print("="*80)
    
    def _print_performance_metrics(self, metrics: Dict[str, Any]):
        """Print performance metrics section"""
        
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
    
    def save_executive_summary(self, report: Dict[str, Any], filename: str = None) -> str:
        """Save executive summary with comprehensive insights"""
        
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
                
                # Add top optimization opportunities
                insights = report.get('optimization_insights', {})
                opportunities = insights.get('opportunity_matrix', [])
                if opportunities:
                    file.write("TOP OPTIMIZATION OPPORTUNITIES:\n")
                    for i, opp in enumerate(opportunities[:3], 1):
                        file.write(f"{i}. {opp.get('from_station', 'Unknown')} → {opp.get('to_station', 'Unknown')}: ")
                        file.write(f"+{opp.get('projected_visit_gain', 0)} visits ({opp.get('confidence', 'Medium')} confidence)\n")
                
                file.write(f"\nGenerated: {metadata['generated_at']}\n")
            
            print(f"📋 Executive summary saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving executive summary: {e}")
            return ""
    
    def _assess_overall_performance(self, totals: Dict, efficiency: Dict) -> str:
        """Generate overall performance assessment"""
        
        visit_rate = totals.get('total_visits', 0) / max(totals.get('total_spots', 1), 1)
        
        if visit_rate >= 2.0:
            return "Excellent - High engagement with strong visit generation and optimization opportunities"
        elif visit_rate >= 1.5:
            return "Strong - Above-average visit generation with clear optimization paths"
        elif visit_rate >= 1.0:
            return "Good - Solid visit generation with identified improvement opportunities"
        elif visit_rate >= 0.5:
            return "Fair - Moderate performance with significant optimization potential"
        else:
            return "Needs Improvement - Low performance requiring comprehensive optimization strategy"


# Test the Report Generator
if __name__ == "__main__":
    print("🧪 Testing Report Generator...")
    print("=" * 60)
    
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
                    comprehensive_insights = insight_generator.generate_comprehensive_insights(kpis, client)
                    
                    # Generate reports
                    reporter = ReportGenerator()
                    report = reporter.generate_report(df, kpis, comprehensive_insights)
                    
                    # Print to console
                    reporter.print_to_console(report)
                    
                    # Save Power BI optimized files
                    base_filename = f"{client.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    detailed_file = reporter.save_detailed_report(report, f"{base_filename}_test_detailed")
                    station_csv = reporter.save_station_performance_csv(report, f"{base_filename}_test_stations")
                    daypart_csv = reporter.save_daypart_performance_csv(report, f"{base_filename}_test_dayparts")
                    combination_csv = reporter.save_combination_performance_csv(report, f"{base_filename}_test_combinations")
                    insights_csv = insight_generator.save_insights_csv(comprehensive_insights, f"{base_filename}_test_insights")
                    
                    print(f"\n✅ Report generation test completed!")
                    print(f"📁 Files saved for Power BI integration:")
                    if detailed_file:
                        print(f"   • Detailed Report: {detailed_file}")
                    if station_csv:
                        print(f"   • Station Performance: {station_csv}")
                    if daypart_csv:
                        print(f"   • Daypart Performance: {daypart_csv}")
                    if combination_csv:
                        print(f"   • Combination Performance: {combination_csv}")
                    if insights_csv:
                        print(f"   • AI Insights: {insights_csv}")
                        
                else:
                    print("❌ No campaign data available")
            else:
                print("❌ No clients available")
                
    except ImportError as e:
        print(f"❌ Cannot import required modules: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")