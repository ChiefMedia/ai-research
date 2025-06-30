"""
AI Insights - Main Module
Complete InsightGenerator class that orchestrates all other modules
"""

import os
from datetime import datetime
from typing import Dict, Any, List

# Import all sub-modules
from .config import ConfigManager, UtilityFunctions, AnalysisConstants
from .trend_analyzer import TrendAnalyzer
from .context_processor import ContextProcessor
from .insight_generators import InsightGenerators
from .performance_analyzer import PerformanceAnalyzer
from .csv_exporter import CSVExporter

class InsightGenerator:
    """
    Main class for generating comprehensive TV campaign insights
    Orchestrates all analysis modules to provide time-based insights for Power BI
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the comprehensive insights generator"""
        self.config_manager = ConfigManager(config_path)
        self.utils = UtilityFunctions()
        
        # Initialize sub-components
        self.trend_analyzer = None
        self.context_processor = None
        self.insight_generators = InsightGenerators()
        self.performance_analyzer = PerformanceAnalyzer()
        self.csv_exporter = CSVExporter()
    
    def generate_comprehensive_insights(self, kpis: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive insights for Power BI dashboard with time-based analysis
        
        Args:
            kpis: KPI data from KPICalculator
            client_name: Name of the client being analyzed
            
        Returns:
            Dict containing all insights organized by category
            
        Raises:
            Exception: If any part of the analysis fails - no fallback provided
        """
        print(f"🤖 Generating comprehensive AI insights for {client_name or 'campaign'}...")
        
        # Initialize trend analyzer with time patterns
        time_patterns = kpis.get('time_patterns', {})
        self.trend_analyzer = TrendAnalyzer(time_patterns)
        
        # Initialize context processor with trend analyzer
        self.context_processor = ContextProcessor(self.trend_analyzer)
        
        # Prepare comprehensive context data
        context = self.context_processor.prepare_comprehensive_context(kpis, client_name)
        
        # Generate all insight categories
        insights = {
            'metadata': {
                'generation_date': datetime.now().isoformat(),
                'ai_model': self.config_manager.get_ai_settings().get('model', 'modular-analysis-engine'),
                'client_name': client_name,
                'analysis_confidence': context.get('analysis_confidence', 0.7),
                'total_insights_generated': 0
            },
            
            # Executive level insights
            'executive_summary': self._generate_executive_summary(context),
            'key_findings': self.insight_generators.generate_executive_findings(context),
            'optimization_priorities': self.insight_generators.generate_optimization_priorities(context),
            
            # Granular insights for Power BI
            'station_insights': self.insight_generators.generate_station_insights(context),
            'daypart_insights': self.insight_generators.generate_daypart_insights(context),
            'station_daypart_insights': self.insight_generators.generate_combination_insights(context),
            
            # Performance analysis
            'performance_quadrants': self.performance_analyzer.analyze_performance_quadrants(context),
            'opportunity_matrix': self.performance_analyzer.generate_opportunity_matrix(context),
            'portfolio_balance': self.performance_analyzer.assess_portfolio_balance(context),
            'scaling_candidates': self.performance_analyzer.identify_scaling_candidates(context),
            
            # Time-based analysis from TrendAnalyzer
            'recent_vs_historical': self.trend_analyzer.compare_recent_vs_historical() if self.trend_analyzer.has_sufficient_data() else None,
            'weekly_trends': self.trend_analyzer.analyze_weekly_trends() if self.trend_analyzer.has_sufficient_data() else None,
            'latest_week_insights': self.trend_analyzer.get_latest_week_insights() if self.trend_analyzer.has_sufficient_data() else None,
            'trend_patterns': self.trend_analyzer.identify_trend_patterns() if self.trend_analyzer.has_sufficient_data() else None,
            
            # Context data for reference
            'context_data': context,
            
            # Structured data for Power BI consumption
            'prescriptive_recommendations': self._generate_structured_recommendations(context)
        }
        
        # Count total insights generated
        total_insights = self.utils.count_total_insights(insights)
        insights['metadata']['total_insights_generated'] = total_insights
        
        print(f"✅ Comprehensive AI insights generated: {total_insights} total insights across all categories")
        return insights
    
    def _generate_executive_summary(self, context: Dict[str, Any]) -> str:
        """Generate executive-level summary with comprehensive business context"""
        
        campaign_overview = context.get('campaign_overview', {})
        efficiency_metrics = context.get('efficiency_metrics', {})
        trend_analysis = context.get('trend_analysis', {})
        
        total_spots = campaign_overview.get('total_spots', 0)
        total_visits = campaign_overview.get('total_visits', 0)
        total_revenue = campaign_overview.get('total_revenue', 0)
        total_orders = campaign_overview.get('total_orders', 0)
        visits_per_spot = efficiency_metrics.get('visits_per_spot', 0)
        
        # Get trend context
        trend_assessment = trend_analysis.get('trend_assessment', 'stable')
        performance_change = trend_analysis.get('performance_change_pct', 0)
        
        # Create comprehensive summary with business impact
        if total_revenue > 0:
            revenue_per_spot = total_revenue / max(total_spots, 1)
            conversion_context = f" with {total_orders:,} orders" if total_orders > 0 else ""
            
            base_summary = (
                f"TV campaign generated ${total_revenue:,.0f} in revenue from {total_visits:,} website visits "
                f"across {total_spots} TV spots{conversion_context}, achieving ${revenue_per_spot:.0f} revenue per spot."
            )
            
            if trend_assessment in ['significantly_improved', 'improved']:
                trend_context = (
                    f" Recent performance acceleration shows {performance_change:.1f}% improvement, "
                    f"indicating strong campaign momentum and optimization opportunities."
                )
            elif trend_assessment in ['significantly_declined', 'declined']:
                trend_context = (
                    f" Performance decline of {abs(performance_change):.1f}% detected recently, "
                    f"requiring immediate investigation and optimization to restore effectiveness."
                )
            else:
                trend_context = f" Campaign maintains consistent performance with stable {visits_per_spot:.1f} visits per spot efficiency."
                
            return base_summary + trend_context
            
        elif total_visits > 0:
            performance_desc = (
                "exceptional" if visits_per_spot > 4 else
                "strong" if visits_per_spot > 2 else
                "solid" if visits_per_spot > 1 else
                "moderate"
            )
            
            base_summary = (
                f"TV campaign achieved {performance_desc} audience engagement with {total_visits:,} website visits "
                f"from {total_spots} spots, delivering {visits_per_spot:.1f} visits per TV spot."
            )
            
            if trend_assessment in ['significantly_improved', 'improved']:
                trend_context = (
                    f" Campaign shows {performance_change:.1f}% efficiency improvement, "
                    f"creating scaling opportunities and increased ROI potential."
                )
            elif trend_assessment in ['significantly_declined', 'declined']:
                trend_context = (
                    f" Efficiency declined {abs(performance_change):.1f}% recently, "
                    f"indicating need for creative refresh, targeting optimization, or media reallocation."
                )
            else:
                trend_context = f" Performance remains stable with consistent audience response patterns."
                
            return base_summary + trend_context
        else:
            data_quality = campaign_overview.get('data_quality_score', 0)
            attribution_coverage = campaign_overview.get('attribution_coverage', 0)
            
            return (
                f"Campaign analysis covers {total_spots} TV spots with {data_quality:.0f}% data quality "
                f"and {attribution_coverage:.0f}% attribution coverage. Enhanced tracking recommended "
                f"for comprehensive performance optimization."
            )
    
    def _generate_structured_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured recommendations optimized for Power BI consumption"""
        
        recommendations = []
        findings = []
        
        # Station-level recommendations with business context
        station_data = context.get('station_performance', [])
        for i, station in enumerate(station_data[:8], 1):  # Top 8 stations
            station_name = station.get('station', 'Unknown')
            opportunity_type = station.get('opportunity_type', 'Monitor')
            efficiency_score = station.get('efficiency_score', 1.0)
            trend_direction = station.get('trend_direction', 'stable')
            
            if opportunity_type in ['Scale Winner', 'Hidden Gem', 'Rising Star']:
                impact_multiplier = 1.5 if trend_direction == 'improving' else 1.0
                expected_impact_pct = int((efficiency_score - 1.0) * 100 * impact_multiplier)
                
                recommendations.append({
                    'priority': i,
                    'impact_level': 'High' if efficiency_score > 1.5 else 'Medium',
                    'area': 'Station Optimization',
                    'station': station_name,
                    'daypart': None,
                    'recommendation': f"{'Scale' if opportunity_type == 'Scale Winner' else 'Test scaling'} {station_name} - {opportunity_type.lower()}",
                    'expected_impact': f"Potential {expected_impact_pct}%+ efficiency gain through reallocation",
                    'confidence': station.get('confidence', 'Medium'),
                    'action_type': 'reallocate_budget',
                    'business_rationale': f"Leverage {efficiency_score:.1f}x efficiency advantage with {trend_direction} trend"
                })
        
        # Daypart-level recommendations
        daypart_data = context.get('daypart_performance', [])
        for i, daypart in enumerate(daypart_data[:3], len(recommendations) + 1):  # Top 3 dayparts
            daypart_name = daypart.get('daypart', 'Unknown')
            efficiency_index = daypart.get('efficiency_index', 1.0)
            volume_adequacy = daypart.get('volume_adequacy', 'Medium')
            
            if efficiency_index > 1.2:  # 20%+ above average
                recommendations.append({
                    'priority': i,
                    'impact_level': 'High' if efficiency_index > 1.4 else 'Medium',
                    'area': 'Daypart Optimization',
                    'station': None,
                    'daypart': daypart_name,
                    'recommendation': f"Increase {daypart_name} inventory allocation",
                    'expected_impact': f"{(efficiency_index - 1.0) * 100:.0f}% above average efficiency",
                    'confidence': 'High' if volume_adequacy == 'High' else 'Medium',
                    'action_type': 'schedule_optimization',
                    'business_rationale': f"Capitalize on {efficiency_index:.1f}x daypart efficiency advantage"
                })
        
        # Portfolio-level findings
        portfolio_balance = context.get('portfolio_balance', {})
        if isinstance(portfolio_balance, dict):
            health_score = portfolio_balance.get('portfolio_health_score', 0)
            recommendations_list = portfolio_balance.get('recommendations', [])
            
            for rec in recommendations_list[:2]:  # Top 2 portfolio recommendations
                findings.append(f"Portfolio insight: {rec}")
        
        return {
            'optimization_recommendations': recommendations,
            'portfolio_findings': findings,
            'total_recommendations': len(recommendations)
        }
    
    def save_insights_csv(self, insights: Dict[str, Any], filename: str = None) -> str:
        """Save comprehensive insights as CSV for Power BI consumption"""
        return self.csv_exporter.export_comprehensive_insights(insights, filename)
    
    def save_all_csv_files(self, context: Dict[str, Any], insights: Dict[str, Any], base_filename: str = None) -> List[str]:
        """Save all CSV files for comprehensive Power BI analysis"""
        return self.csv_exporter.export_all_csv_files(context, insights, base_filename)
    
    def create_powerbi_guide(self, exported_files: List[str]) -> str:
        """Create Power BI import guide for exported CSV files"""
        return self.csv_exporter.create_powerbi_import_guide(exported_files)


# Test the complete integrated module
if __name__ == "__main__":
    print("🧪 Testing Complete Integrated AI Insights Module...")
    
    # Create comprehensive sample KPI data
    sample_kpis = {
        'metadata': {
            'data_quality_score': 92.0,
            'date_range': {'start_date': '2025-06-01', 'end_date': '2025-06-27'},
            'primary_product': 'TEST_PRODUCT',
            'spots_analyzed': 834
        },
        'totals': {
            'total_spots': 834,
            'total_cost': 325000,
            'total_visits': 21500,
            'total_orders': 1750,
            'total_revenue': 87500,
            'total_impressions': 13400
        },
        'efficiency': {
            'roas': 0.27,
            'cpm': 24.25,
            'cpo': 185.71,
            'cpv': 15.12,
            'visit_to_order_rate': 0.081
        },
        'dimensional_analysis': {
            'station_performance': [
                {
                    'station': 'CHAMPION_STATION', 'avg_visits_per_spot': 4.2, 'total_visits': 1260,
                    'spots': 300, 'total_cost': 15000, 'cpm': 11.9
                },
                {
                    'station': 'RISING_STATION', 'avg_visits_per_spot': 2.8, 'total_visits': 560,
                    'spots': 200, 'total_cost': 12000, 'cpm': 21.4
                },
                {
                    'station': 'WEAK_STATION', 'avg_visits_per_spot': 1.2, 'total_visits': 240,
                    'spots': 200, 'total_cost': 10000, 'cpm': 41.7
                }
            ],
            'daypart_performance': [
                {
                    'daypart': 'PRIME', 'avg_visits_per_spot': 3.8, 'total_visits': 760,
                    'spots': 200, 'total_cost': 10000
                },
                {
                    'daypart': 'DAYTIME', 'avg_visits_per_spot': 2.5, 'total_visits': 500,
                    'spots': 200, 'total_cost': 8000
                }
            ],
            'station_daypart_combinations': [
                {
                    'station': 'CHAMPION_STATION', 'daypart': 'PRIME', 'avg_visits_per_spot': 5.2,
                    'total_visits': 520, 'spots': 100, 'total_cost': 5000
                }
            ]
        },
        'time_patterns': {
            'daily_trends': [
                {'date': '2025-06-15', 'spots': 30, 'visits': 72, 'revenue': 3600},
                {'date': '2025-06-16', 'spots': 28, 'visits': 70, 'revenue': 3500},
                {'date': '2025-06-17', 'spots': 32, 'visits': 80, 'revenue': 4000},
                {'date': '2025-06-18', 'spots': 29, 'visits': 75, 'revenue': 3750},
                {'date': '2025-06-19', 'spots': 35, 'visits': 88, 'revenue': 4400},
                {'date': '2025-06-20', 'spots': 33, 'visits': 85, 'revenue': 4250},
                {'date': '2025-06-21', 'spots': 36, 'visits': 95, 'revenue': 4750},
                {'date': '2025-06-22', 'spots': 38, 'visits': 100, 'revenue': 5000},
                {'date': '2025-06-23', 'spots': 35, 'visits': 92, 'revenue': 4600},
                {'date': '2025-06-24', 'spots': 40, 'visits': 108, 'revenue': 5400},
                {'date': '2025-06-25', 'spots': 37, 'visits': 98, 'revenue': 4900},
                {'date': '2025-06-26', 'spots': 42, 'visits': 115, 'revenue': 5750},
                {'date': '2025-06-27', 'spots': 39, 'visits': 105, 'revenue': 5250}
            ]
        }
    }
    
    # Test complete insight generator - let any exceptions bubble up
    generator = InsightGenerator()
    print(f"✅ Complete InsightGenerator initialized")
    
    # Generate comprehensive insights - no exception handling, let failures fail
    insights = generator.generate_comprehensive_insights(sample_kpis, "TEST_CLIENT_COMPLETE")
    print(f"✅ Comprehensive insights generated: {insights['metadata']['total_insights_generated']} total insights")
    
    # Test all insight categories
    print(f"✅ Executive summary: {len(insights['executive_summary'])} characters")
    print(f"✅ Key findings: {len(insights['key_findings'])} findings")
    print(f"✅ Station insights: {len(insights['station_insights'])} insights")
    print(f"✅ Daypart insights: {len(insights['daypart_insights'])} insights")
    print(f"✅ Combination insights: {len(insights['station_daypart_insights'])} insights")
    
    # Test performance analysis
    quadrants = insights['performance_quadrants']
    print(f"✅ Performance quadrants: {sum(len(stations) for stations in quadrants.values())} stations classified")
    print(f"✅ Opportunity matrix: {len(insights['opportunity_matrix'])} opportunities")
    print(f"✅ Portfolio balance: {insights['portfolio_balance'].get('portfolio_health_score', 'N/A')} health score")
    print(f"✅ Scaling candidates: {len(insights['scaling_candidates'])} candidates")
    
    # Test trend analysis
    print(f"✅ Recent vs historical: {insights['recent_vs_historical'].get('trend_assessment', 'N/A')}")
    print(f"✅ Weekly trends: {insights['weekly_trends'].get('trend_analysis', 'N/A')}")
    
    # Test CSV exports
    context = insights['context_data']
    csv_files = generator.save_all_csv_files(context, insights)
    print(f"✅ CSV files exported: {len(csv_files)} files")
    
    # Test Power BI guide
    guide_file = generator.create_powerbi_guide(csv_files)
    print(f"✅ Power BI guide created: {bool(guide_file)}")
    
    # Show sample insights
    if insights['key_findings']:
        print(f"\n🔍 Sample key finding: {insights['key_findings'][0]}")
    if insights['station_insights']:
        top_station_insight = insights['station_insights'][0]
        print(f"🔍 Sample station insight: {top_station_insight['station']} - {top_station_insight['recommendation'][:50]}...")
    
    print("\n✅ Complete Integrated AI Insights Module test completed successfully!")
    print("🎯 All modules working together: config, trend_analyzer, context_processor, insight_generators, performance_analyzer, csv_exporter")
    print("🚨 No fallback mechanisms - system will fail fast on any errors")