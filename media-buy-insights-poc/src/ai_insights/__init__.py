"""
AI Insights - Main Module
Main InsightGenerator class that orchestrates all other modules
"""

import os
from datetime import datetime
from typing import Dict, Any

# Import all sub-modules
from .config import ConfigManager, UtilityFunctions, AnalysisConstants
from .trend_analyzer import TrendAnalyzer

# Note: These imports would be added as we create the remaining modules
# from .context_processor import ContextProcessor
# from .insight_generators import InsightGenerators
# from .performance_analyzer import PerformanceAnalyzer
# from .csv_exporter import CSVExporter

class InsightGenerator:
    """
    Main class for generating comprehensive TV campaign insights
    Orchestrates all analysis modules to provide time-based insights for Power BI
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the comprehensive insights generator"""
        self.config_manager = ConfigManager(config_path)
        self.utils = UtilityFunctions()
        
        # Initialize sub-components (will be populated as modules are created)
        self.trend_analyzer = None
        self.context_processor = None
        self.insight_generators = None
        self.performance_analyzer = None
        self.csv_exporter = None
    
    def generate_comprehensive_insights(self, kpis: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive insights for Power BI dashboard with time-based analysis
        
        Args:
            kpis: KPI data from KPICalculator
            client_name: Name of the client being analyzed
            
        Returns:
            Dict containing all insights organized by category
        """
        print(f"🤖 Generating AI insights for {client_name or 'campaign'}...")
        
        try:
            # Initialize trend analyzer with time patterns
            time_patterns = kpis.get('time_patterns', {})
            self.trend_analyzer = TrendAnalyzer(time_patterns)
            
            # Prepare context data (simplified version for demo)
            context = self._prepare_basic_context(kpis, client_name)
            
            # Generate insights structure
            insights = {
                'metadata': {
                    'generation_date': datetime.now().isoformat(),
                    'ai_model': self.config_manager.get_ai_settings().get('model', 'gemini-2.0-flash'),
                    'client_name': client_name,
                    'analysis_confidence': self.utils.assess_analysis_confidence(kpis),
                    'total_insights_generated': 0
                },
                
                # Executive level insights
                'executive_summary': self._generate_basic_executive_summary(context),
                'key_findings': self._extract_basic_key_findings(context),
                'optimization_priorities': self._identify_basic_optimization_priorities(context),
                
                # Time-based analysis from TrendAnalyzer
                'recent_vs_historical': self.trend_analyzer.compare_recent_vs_historical(),
                'weekly_trends': self.trend_analyzer.analyze_weekly_trends(),
                'latest_week_insights': self.trend_analyzer.get_latest_week_insights(),
                'trend_patterns': self.trend_analyzer.identify_trend_patterns(),
                
                # Placeholder for full insights (would come from other modules)
                'station_insights': [],
                'daypart_insights': [],
                'station_daypart_insights': [],
                'performance_quadrants': {},
                'opportunity_matrix': [],
                
                # Structured data for Power BI consumption
                'prescriptive_recommendations': {
                    'optimization_recommendations': [],
                    'key_findings': []
                }
            }
            
            # Count total insights generated
            total_insights = self.utils.count_total_insights(insights)
            insights['metadata']['total_insights_generated'] = total_insights
            
            print(f"✅ AI insights generated: {total_insights} total insights")
            return insights
            
        except Exception as e:
            print(f"❌ Error generating insights: {e}")
            return self._fallback_insights(kpis, client_name)
    
    def _prepare_basic_context(self, kpis: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """Prepare basic context data (simplified version)"""
        
        totals = kpis.get('totals', {})
        efficiency = kpis.get('efficiency', {})
        metadata = kpis.get('metadata', {})
        
        context = {
            'client_name': client_name or 'Unknown Client',
            'campaign_overview': {
                'total_spots': totals.get('total_spots', 0),
                'total_cost': totals.get('total_cost', 0),
                'total_visits': totals.get('total_visits', 0),
                'total_orders': totals.get('total_orders', 0),
                'total_revenue': totals.get('total_revenue', 0),
                'total_impressions': totals.get('total_impressions', 0),
                'data_quality': metadata.get('data_quality_score', 0),
                'analysis_period': metadata.get('date_range', {})
            },
            'efficiency_metrics': {
                'overall_roas': efficiency.get('roas', 0),
                'overall_cpm': efficiency.get('cpm', 0),
                'overall_cpv': efficiency.get('cpv', 0),
                'overall_cpo': efficiency.get('cpo', 0),
                'overall_conversion_rate': efficiency.get('visit_to_order_rate', 0),
                'visits_per_spot': totals.get('total_visits', 0) / max(totals.get('total_spots', 1), 1)
            },
            # Add trend analysis
            'trend_analysis': self.trend_analyzer.compare_recent_vs_historical() if self.trend_analyzer else {},
            'weekly_trends': self.trend_analyzer.analyze_weekly_trends() if self.trend_analyzer else {}
        }
        
        return context
    
    def _generate_basic_executive_summary(self, context: Dict[str, Any]) -> str:
        """Generate executive-level summary with time-based context"""
        campaign_overview = context.get('campaign_overview', {})
        trend_analysis = context.get('trend_analysis', {})
        
        total_spots = campaign_overview.get('total_spots', 0)
        total_visits = campaign_overview.get('total_visits', 0)
        total_revenue = campaign_overview.get('total_revenue', 0)
        total_orders = campaign_overview.get('total_orders', 0)
        
        # Get trend context
        trend_assessment = trend_analysis.get('trend_assessment', 'stable')
        performance_change = trend_analysis.get('performance_change_pct', 0)
        
        # Create time-aware summary
        if total_revenue > 0:
            base_summary = f"TV campaign generated ${total_revenue:,.0f} in revenue through {total_orders:,} orders from {total_visits:,} website visits across {total_spots} TV spots."
            
            if trend_assessment in ['significantly_improved', 'improved']:
                trend_context = f" Recent performance shows {performance_change:.1f}% improvement."
            elif trend_assessment in ['significantly_declined', 'declined']:
                trend_context = f" Performance has declined {abs(performance_change):.1f}% recently - optimization needed."
            else:
                trend_context = f" Performance remains stable."
                
            return base_summary + trend_context
            
        elif total_visits > 0:
            visits_per_spot = total_visits / total_spots if total_spots > 0 else 0
            performance_desc = "strong" if visits_per_spot > 2 else "solid" if visits_per_spot > 1 else "moderate"
            base_summary = f"TV campaign generated {total_visits:,} website visits from {total_spots} spots, achieving {performance_desc} audience engagement."
            
            if trend_assessment in ['significantly_improved', 'improved']:
                trend_context = f" Campaign shows {performance_change:.1f}% improvement in efficiency."
            elif trend_assessment in ['significantly_declined', 'declined']:
                trend_context = f" Campaign efficiency declined {abs(performance_change):.1f}% recently."
            else:
                trend_context = f" Campaign maintains consistent performance."
                
            return base_summary + trend_context
        else:
            return f"Campaign analysis covers {total_spots} TV spots with limited attribution data available."
    
    def _extract_basic_key_findings(self, context: Dict[str, Any]) -> List[str]:
        """Extract key findings with time-based insights"""
        findings = []
        
        campaign_overview = context.get('campaign_overview', {})
        trend_analysis = context.get('trend_analysis', {})
        weekly_trends = context.get('weekly_trends', {})
        
        # Overall performance finding with trend
        total_spots = campaign_overview.get('total_spots', 0)
        total_visits = campaign_overview.get('total_visits', 0)
        trend_assessment = trend_analysis.get('trend_assessment', 'stable')
        performance_change = trend_analysis.get('performance_change_pct', 0)
        
        if total_visits > 0 and total_spots > 0:
            visit_rate = total_visits / total_spots
            performance_level = "Strong" if visit_rate > 2 else "Solid" if visit_rate > 1 else "Moderate"
            
            if trend_assessment in ['significantly_improved', 'improved']:
                findings.append(f"{performance_level} engagement trending up: {visit_rate:.1f} visits per spot with {performance_change:.1f}% recent improvement")
            elif trend_assessment in ['significantly_declined', 'declined']:
                findings.append(f"{performance_level} engagement declining: {visit_rate:.1f} visits per spot down {abs(performance_change):.1f}% recently")
            else:
                findings.append(f"{performance_level} engagement stable: {visit_rate:.1f} visits per TV spot")
        
        # Weekly trend insights
        if self.trend_analyzer and self.trend_analyzer.has_sufficient_data():
            latest_insights = self.trend_analyzer.get_latest_week_insights()
            week_insights = latest_insights.get('insights', [])
            findings.extend(week_insights[:2])  # Add top 2 weekly insights
        
        return findings[:4]  # Top 4 findings with time context
    
    def _identify_basic_optimization_priorities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify basic optimization priorities"""
        priorities = []
        
        trend_analysis = context.get('trend_analysis', {})
        trend_assessment = trend_analysis.get('trend_assessment', 'stable')
        performance_change = trend_analysis.get('performance_change_pct', 0)
        
        # Add trend-based priorities
        if trend_assessment == 'significantly_declined':
            priorities.append({
                'priority': 1,
                'area': 'Performance Recovery',
                'recommendation': 'Immediate investigation needed - significant performance decline detected',
                'impact': 'High',
                'effort': 'Medium',
                'trend_context': f"Performance declined {abs(performance_change):.1f}% recently"
            })
        elif trend_assessment == 'significantly_improved':
            priorities.append({
                'priority': 1,
                'area': 'Momentum Capitalization',
                'recommendation': 'Scale successful strategies - strong improvement momentum detected',
                'impact': 'High',
                'effort': 'Low',
                'trend_context': f"Performance improved {performance_change:.1f}% recently"
            })
        
        return priorities[:2]  # Top 2 priorities
    
    def save_insights_csv(self, insights: Dict[str, Any], filename: str = None) -> str:
        """Save insights as CSV for Power BI consumption (basic implementation)"""
        
        if filename is None:
            client_name = insights['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_insights_{timestamp}"
        
        output_dir = "output/reports"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{filename}.csv")
        
        try:
            import csv
            
            insights_data = []
            
            # Key Findings with time context
            key_findings = insights.get('key_findings', [])
            trend_analysis = insights.get('recent_vs_historical', {})
            trend_assessment = trend_analysis.get('trend_assessment', 'stable')
            
            for i, finding in enumerate(key_findings, 1):
                is_trend_finding = self.utils.is_trend_finding(finding)
                
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'insight_category': AnalysisConstants.INSIGHT_CATEGORIES['KEY_FINDING'],
                    'insight_type': 'executive_summary',
                    'priority': i,
                    'impact_level': 'High',
                    'station': None,
                    'daypart': None,
                    'metric_type': 'trend_analysis' if is_trend_finding else 'overall_performance',
                    'finding_description': finding,
                    'recommendation': f"Key insight: {finding}",
                    'action_required': 'leverage_trend' if is_trend_finding else 'monitor_and_leverage',
                    'confidence': 'High',
                    'trend_context': trend_assessment,
                    'time_based': 'yes' if is_trend_finding else 'no',
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Weekly trend insights
            latest_week = insights.get('latest_week_insights', {})
            for i, insight in enumerate(latest_week.get('insights', []), len(key_findings) + 1):
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'insight_category': 'weekly_trend',
                    'insight_type': 'trend_analysis',
                    'priority': i,
                    'impact_level': 'Medium',
                    'station': None,
                    'daypart': None,
                    'metric_type': 'weekly_performance',
                    'finding_description': insight,
                    'recommendation': f"Weekly trend: {insight}",
                    'action_required': 'monitor_trend',
                    'confidence': 'High',
                    'trend_context': 'weekly_change',
                    'time_based': 'yes',
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Write CSV
            if insights_data:
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=AnalysisConstants.CSV_FIELDNAMES)
                    writer.writeheader()
                    writer.writerows(insights_data)
                
                print(f"📊 Insights CSV saved: {filepath}")
                return filepath
            else:
                print("⚠️  No insights available for CSV export")
                return ""
                
        except Exception as e:
            print(f"❌ Error saving insights CSV: {e}")
            return ""
    
    def _fallback_insights(self, kpis: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """Fallback insights when AI generation fails"""
        return {
            'metadata': {
                'generation_date': datetime.now().isoformat(),
                'ai_model': 'fallback',
                'client_name': client_name,
                'analysis_confidence': 0.7,
                'total_insights_generated': 1
            },
            'executive_summary': f'TV campaign analysis for {client_name or "client"} completed.',
            'key_findings': ['AI analysis temporarily unavailable'],
            'optimization_priorities': [],
            'station_insights': [],
            'daypart_insights': [],
            'station_daypart_insights': [],
            'performance_quadrants': {},
            'opportunity_matrix': [],
            'recent_vs_historical': {},
            'weekly_trends': {},
            'latest_week_insights': {},
            'trend_patterns': {},
            'prescriptive_recommendations': {
                'optimization_recommendations': [],
                'key_findings': []
            }
        }


# Test the main module
if __name__ == "__main__":
    print("🧪 Testing Main InsightGenerator Module...")
    
    try:
        # Create sample KPI data
        sample_kpis = {
            'metadata': {
                'data_quality_score': 95.0,
                'date_range': {'start_date': '2025-06-01', 'end_date': '2025-06-27'}
            },
            'totals': {
                'total_spots': 834,
                'total_cost': 325000,
                'total_visits': 21500,
                'total_orders': 1750,
                'total_revenue': 81500,
                'total_impressions': 13400
            },
            'efficiency': {
                'roas': 0.25,
                'cpm': 24.25,
                'cpo': 185.71,
                'cpv': 15.12,
                'visit_to_order_rate': 0.081
            },
            'time_patterns': {
                'daily_trends': [
                    {'date': '2025-06-01', 'spots': 50, 'visits': 120, 'revenue': 5000},
                    {'date': '2025-06-02', 'spots': 45, 'visits': 115, 'revenue': 4800},
                    {'date': '2025-06-03', 'spots': 52, 'visits': 125, 'revenue': 5200},
                    {'date': '2025-06-04', 'spots': 48, 'visits': 118, 'revenue': 4900},
                    {'date': '2025-06-05', 'spots': 55, 'visits': 135, 'revenue': 5500},
                    {'date': '2025-06-06', 'spots': 50, 'visits': 122, 'revenue': 5100},
                    {'date': '2025-06-07', 'spots': 53, 'visits': 128, 'revenue': 5300},
                    {'date': '2025-06-08', 'spots': 60, 'visits': 145, 'revenue': 6000},
                    {'date': '2025-06-09', 'spots': 58, 'visits': 142, 'revenue': 5800},
                    {'date': '2025-06-10', 'spots': 62, 'visits': 148, 'revenue': 6200},
                    {'date': '2025-06-11', 'spots': 59, 'visits': 144, 'revenue': 5900},
                    {'date': '2025-06-12', 'spots': 65, 'visits': 155, 'revenue': 6500},
                    {'date': '2025-06-13', 'spots': 61, 'visits': 150, 'revenue': 6100},
                    {'date': '2025-06-14', 'spots': 63, 'visits': 152, 'revenue': 6300},
                ]
            }
        }
        
        # Test insight generator
        generator = InsightGenerator()
        print(f"✅ InsightGenerator initialized")
        
        # Generate insights
        insights = generator.generate_comprehensive_insights(sample_kpis, "TEST_CLIENT")
        print(f"✅ Insights generated: {insights['metadata']['total_insights_generated']} total")
        
        # Test CSV export
        csv_path = generator.save_insights_csv(insights)
        if csv_path:
            print(f"✅ CSV exported: {csv_path}")
        
        # Show some results
        print(f"✅ Executive Summary: {insights['executive_summary'][:100]}...")
        print(f"✅ Key Findings: {len(insights['key_findings'])} findings")
        print(f"✅ Trend Assessment: {insights['recent_vs_historical'].get('trend_assessment', 'N/A')}")
        
        print("✅ Main InsightGenerator module test completed successfully!")
        
    except Exception as e:
        print(f"❌ Main module test failed: {e}")
        import traceback
        traceback.print_exc()