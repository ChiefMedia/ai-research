"""
AI Insights - Context Processor Module
Handles data processing, preparation, and context enrichment for AI analysis
"""

from typing import Dict, Any, List, Optional
from .config import AnalysisConstants, UtilityFunctions
from .trend_analyzer import TrendAnalyzer

class ContextProcessor:
    """Processes and enriches KPI data for comprehensive AI analysis"""
    
    def __init__(self, trend_analyzer: TrendAnalyzer = None):
        """Initialize context processor with optional trend analyzer"""
        self.trend_analyzer = trend_analyzer
        self.utils = UtilityFunctions()
    
    def prepare_comprehensive_context(self, kpis: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """
        Prepare comprehensive context data for AI analysis with time-based insights
        
        Args:
            kpis: KPI data from KPICalculator
            client_name: Name of the client being analyzed
            
        Returns:
            Dict containing enriched context data ready for insight generation
        """
        
        totals = kpis.get('totals', {})
        efficiency = kpis.get('efficiency', {})
        dimensional = kpis.get('dimensional_analysis', {})
        time_patterns = kpis.get('time_patterns', {})
        metadata = kpis.get('metadata', {})
        
        # Extract product information from metadata if available
        default_product = metadata.get('primary_product', 'DEFAULT')
        
        # Build comprehensive context with time-based analysis
        context = {
            'client_name': client_name or 'Unknown Client',
            'primary_product': default_product,
            
            # Campaign overview metrics
            'campaign_overview': self._build_campaign_overview(totals, metadata),
            
            # Efficiency metrics with benchmarking
            'efficiency_metrics': self._build_efficiency_metrics(totals, efficiency),
            
            # Enhanced performance data with trend context
            'station_performance': self._process_station_data_with_trends(
                dimensional.get('station_performance', []), 
                time_patterns, 
                default_product
            ),
            'daypart_performance': self._process_daypart_data_with_trends(
                dimensional.get('daypart_performance', []), 
                time_patterns, 
                default_product
            ),
            'combination_performance': self._process_combination_data(
                dimensional.get('station_daypart_combinations', []), 
                default_product
            ),
            
            # Market performance if available
            'market_performance': self._process_market_data(
                dimensional.get('market_performance', [])
            ),
            
            # Time-based analysis
            'trend_analysis': self._get_trend_analysis(),
            'weekly_trends': self._get_weekly_trends(),
            'recent_vs_historical': self._get_recent_vs_historical(),
            
            # Metadata and quality metrics
            'targets': kpis.get('targets', {}),
            'data_quality': self._assess_data_quality(metadata, totals),
            'analysis_confidence': self.utils.assess_analysis_confidence(kpis)
        }
        
        return context
    
    def _build_campaign_overview(self, totals: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Build campaign overview section"""
        return {
            'total_spots': totals.get('total_spots', 0),
            'total_cost': totals.get('total_cost', 0),
            'total_visits': totals.get('total_visits', 0),
            'total_orders': totals.get('total_orders', 0),
            'total_leads': totals.get('total_leads', 0),
            'total_revenue': totals.get('total_revenue', 0),
            'total_impressions': totals.get('total_impressions', 0),
            'data_quality_score': metadata.get('data_quality_score', 0),
            'analysis_period': metadata.get('date_range', {}),
            'attribution_coverage': self._calculate_attribution_coverage(totals)
        }
    
    def _build_efficiency_metrics(self, totals: Dict[str, Any], efficiency: Dict[str, Any]) -> Dict[str, Any]:
        """Build efficiency metrics with derived calculations"""
        total_spots = max(totals.get('total_spots', 1), 1)
        total_visits = totals.get('total_visits', 0)
        total_cost = totals.get('total_cost', 0)
        
        return {
            'overall_roas': efficiency.get('roas', 0),
            'overall_cpm': efficiency.get('cpm', 0),
            'overall_cpv': efficiency.get('cpv', 0),
            'overall_cpo': efficiency.get('cpo', 0),
            'overall_cpl': efficiency.get('cpl', 0),
            'overall_conversion_rate': efficiency.get('visit_to_order_rate', 0),
            'lead_to_order_rate': efficiency.get('lead_to_order_rate', 0),
            'visits_per_spot': total_visits / total_spots,
            'cost_efficiency_score': self._calculate_cost_efficiency_score(totals, efficiency),
            'volume_efficiency_score': self._calculate_volume_efficiency_score(totals)
        }
    
    def _process_station_data_with_trends(self, station_data: List[Dict], 
                                        time_patterns: Dict, default_product: str = 'DEFAULT') -> List[Dict]:
        """Process station data with comprehensive trend analysis and performance classification"""
        if not station_data:
            return []
        
        processed_stations = []
        
        # Calculate performance benchmarks
        visit_rates = [s.get('avg_visits_per_spot', 0) for s in station_data 
                      if s.get('avg_visits_per_spot', 0) > 0]
        if not visit_rates:
            return station_data
        
        # Performance quartiles for classification
        top_quartile = self.utils.calculate_performance_quartile(station_data, 0.75)
        median = self.utils.calculate_performance_quartile(station_data, 0.50)
        bottom_quartile = self.utils.calculate_performance_quartile(station_data, 0.25)
        
        for station in station_data:
            station_processed = station.copy()
            station_processed['product'] = default_product
            
            visit_rate = station.get('avg_visits_per_spot', 0)
            total_visits = station.get('total_visits', 0)
            total_spots = station.get('spots', 0)
            station_name = station.get('station', 'Unknown')
            
            # Get trend context from trend analyzer if available
            trend_context = self._get_entity_trend_context('station', station_name)
            station_processed.update(trend_context)
            
            # Performance tier classification with trend awareness
            base_tier = self._classify_performance_tier(visit_rate, top_quartile, median, bottom_quartile)
            trend_direction = trend_context.get('trend_direction', 'stable')
            
            if trend_direction == 'improving':
                station_processed['performance_tier'] = f'{base_tier} (Improving)'
            elif trend_direction == 'declining':
                station_processed['performance_tier'] = f'{base_tier} (Declining)'
            else:
                station_processed['performance_tier'] = base_tier
            
            # Opportunity classification based on volume, efficiency, and trends
            station_processed['opportunity_type'] = self._classify_station_opportunity(
                total_visits, visit_rate, trend_direction, median, top_quartile
            )
            
            # Confidence assessment
            station_processed['confidence'] = self.utils.determine_confidence_level(
                total_spots, trend_context.get('weeks_analyzed', 0)
            )
            
            # Add performance scores
            station_processed['efficiency_score'] = visit_rate / max(median, 1) if median > 0 else 1
            station_processed['volume_score'] = self._calculate_volume_score(total_visits, station_data)
            
            processed_stations.append(station_processed)
        
        # Sort by overall opportunity score (efficiency * volume with trend boost)
        for station in processed_stations:
            trend_boost = 1.2 if station.get('trend_direction') == 'improving' else 0.8 if station.get('trend_direction') == 'declining' else 1.0
            station['opportunity_score'] = station.get('efficiency_score', 1) * station.get('volume_score', 1) * trend_boost
        
        processed_stations.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
        
        return processed_stations
    
    def _process_daypart_data_with_trends(self, daypart_data: List[Dict], 
                                        time_patterns: Dict, default_product: str = 'DEFAULT') -> List[Dict]:
        """Process daypart data with trend analysis and efficiency classification"""
        if not daypart_data:
            return []
        
        dayparts_processed = []
        
        # Calculate daypart benchmarks
        daypart_rates = [d.get('avg_visits_per_spot', 0) for d in daypart_data 
                        if d.get('avg_visits_per_spot', 0) > 0]
        if not daypart_rates:
            return daypart_data
        
        avg_performance = sum(daypart_rates) / len(daypart_rates)
        top_daypart_rate = max(daypart_rates)
        
        for daypart in daypart_data:
            daypart_processed = daypart.copy()
            daypart_processed['product'] = default_product
            
            visit_rate = daypart.get('avg_visits_per_spot', 0)
            total_spots = daypart.get('spots', 0)
            daypart_name = daypart.get('daypart', 'Unknown')
            
            # Get trend context
            trend_context = self._get_entity_trend_context('daypart', daypart_name)
            daypart_processed.update(trend_context)
            
            # Performance rating with trend context
            base_rating = self._classify_daypart_efficiency(visit_rate, avg_performance, top_daypart_rate)
            trend_direction = trend_context.get('trend_direction', 'stable')
            
            if trend_direction == 'improving':
                daypart_processed['efficiency_rating'] = f'{base_rating} - Trending Up'
            elif trend_direction == 'declining':
                daypart_processed['efficiency_rating'] = f'{base_rating} - Trending Down'
            else:
                daypart_processed['efficiency_rating'] = base_rating
            
            # Recommendation priority with trend and volume considerations
            daypart_processed['recommendation_priority'] = self._classify_daypart_priority(
                total_spots, visit_rate, avg_performance, trend_direction
            )
            
            # Confidence assessment
            daypart_processed['confidence'] = self.utils.determine_confidence_level(
                total_spots, trend_context.get('weeks_analyzed', 0)
            )
            
            # Add performance metrics
            daypart_processed['efficiency_index'] = visit_rate / max(avg_performance, 1) if avg_performance > 0 else 1
            daypart_processed['volume_adequacy'] = 'High' if total_spots >= 50 else 'Medium' if total_spots >= 20 else 'Low'
            
            dayparts_processed.append(daypart_processed)
        
        # Sort by efficiency with trend consideration
        dayparts_processed.sort(key=lambda x: x.get('efficiency_index', 0) * 
                               (1.2 if x.get('trend_direction') == 'improving' else 0.8 if x.get('trend_direction') == 'declining' else 1.0), 
                               reverse=True)
        
        return dayparts_processed
    
    def _process_combination_data(self, combination_data: List[Dict], default_product: str = 'DEFAULT') -> List[Dict]:
        """Process station+daypart combination data with performance scoring"""
        if not combination_data:
            return []
        
        combinations_processed = []
        
        # Calculate combination benchmarks
        combo_rates = [c.get('avg_visits_per_spot', 0) for c in combination_data 
                      if c.get('avg_visits_per_spot', 0) > 0]
        if not combo_rates:
            return combination_data
        
        combo_rates.sort()
        top_combo_rate = combo_rates[-1] if combo_rates else 0
        median_combo_rate = combo_rates[len(combo_rates) // 2] if combo_rates else 0
        
        for combo in combination_data:
            combo_processed = combo.copy()
            combo_processed['product'] = default_product
            
            visit_rate = combo.get('avg_visits_per_spot', 0)
            spots = combo.get('spots', 0)
            station = combo.get('station', 'Unknown')
            daypart = combo.get('daypart', 'Unknown')
            
            # Combination performance scoring
            if visit_rate >= top_combo_rate * 0.8:
                combo_processed['combo_tier'] = 'Golden Combination'
                combo_processed['scaling_priority'] = 'Immediate'
            elif visit_rate >= median_combo_rate * 1.2:
                combo_processed['combo_tier'] = 'Strong Combination'
                combo_processed['scaling_priority'] = 'High'
            elif visit_rate >= median_combo_rate:
                combo_processed['combo_tier'] = 'Good Combination'
                combo_processed['scaling_priority'] = 'Medium'
            else:
                combo_processed['combo_tier'] = 'Standard Combination'
                combo_processed['scaling_priority'] = 'Low'
            
            # Sample size confidence
            combo_processed['confidence_level'] = self.utils.determine_confidence_level(spots)
            
            # Synergy score (how much better than individual components)
            combo_processed['synergy_score'] = self._calculate_synergy_score(visit_rate, median_combo_rate)
            
            # Investment recommendation
            combo_processed['investment_recommendation'] = self._get_combination_investment_recommendation(
                combo_processed['combo_tier'], combo_processed['confidence_level'], spots
            )
            
            combinations_processed.append(combo_processed)
        
        # Sort by synergy score and visit rate
        combinations_processed.sort(key=lambda x: (x.get('synergy_score', 0), x.get('avg_visits_per_spot', 0)), reverse=True)
        
        return combinations_processed
    
    def _process_market_data(self, market_data: List[Dict]) -> List[Dict]:
        """Process market-level performance data if available"""
        if not market_data:
            return []
        
        # Add basic processing for market data
        for market in market_data:
            total_visits = market.get('total_visits', 0)
            total_spots = market.get('spots', 0)
            
            if total_spots > 0:
                market['market_efficiency'] = total_visits / total_spots
                market['market_scale'] = 'Large' if total_spots >= 100 else 'Medium' if total_spots >= 50 else 'Small'
            else:
                market['market_efficiency'] = 0
                market['market_scale'] = 'Unknown'
        
        return sorted(market_data, key=lambda x: x.get('total_visits', 0), reverse=True)
    
    def _get_trend_analysis(self) -> Dict[str, Any]:
        """Get trend analysis from trend analyzer if available"""
        if self.trend_analyzer:
            return self.trend_analyzer.compare_recent_vs_historical()
        return {'comparison': 'no_trend_analyzer'}
    
    def _get_weekly_trends(self) -> Dict[str, Any]:
        """Get weekly trends from trend analyzer if available"""
        if self.trend_analyzer:
            return self.trend_analyzer.analyze_weekly_trends()
        return {'trend_analysis': 'no_trend_analyzer'}
    
    def _get_recent_vs_historical(self) -> Dict[str, Any]:
        """Get recent vs historical comparison"""
        if self.trend_analyzer:
            return self.trend_analyzer.compare_recent_vs_historical()
        return {'comparison': 'no_trend_analyzer'}
    
    def _get_entity_trend_context(self, entity_type: str, entity_name: str) -> Dict[str, Any]:
        """Get trend context for a specific entity"""
        if self.trend_analyzer:
            return self.trend_analyzer.get_trend_context_for_entity(entity_type, entity_name)
        
        # Fallback context
        return {
            'trend_direction': 'stable',
            'recent_efficiency': 0,
            'volume_stability': 'unknown',
            'weeks_analyzed': 0,
            'confidence_level': 'Medium'
        }
    
    def _calculate_attribution_coverage(self, totals: Dict[str, Any]) -> float:
        """Calculate what percentage of spots have attribution data"""
        total_spots = totals.get('total_spots', 0)
        total_visits = totals.get('total_visits', 0)
        
        if total_spots == 0:
            return 0.0
        
        # Estimate coverage based on non-zero visits
        return min((total_visits / max(total_spots, 1)) * 100, 100.0) if total_visits > 0 else 0.0
    
    def _calculate_cost_efficiency_score(self, totals: Dict[str, Any], efficiency: Dict[str, Any]) -> float:
        """Calculate a normalized cost efficiency score (0-100)"""
        cpm = efficiency.get('cpm', 0)
        cpv = efficiency.get('cpv', 0)
        
        if cpm == 0 and cpv == 0:
            return 50.0  # Neutral score when no cost data
        
        # Normalize against industry benchmarks (lower is better for costs)
        cpm_score = max(0, min(100, (20 - cpm) * 5)) if cpm > 0 else 50
        cpv_score = max(0, min(100, (15 - cpv) * 10)) if cpv > 0 else 50
        
        return (cpm_score + cpv_score) / 2
    
    def _calculate_volume_efficiency_score(self, totals: Dict[str, Any]) -> float:
        """Calculate volume efficiency score based on visits per spot"""
        total_visits = totals.get('total_visits', 0)
        total_spots = totals.get('total_spots', 1)
        
        visits_per_spot = total_visits / max(total_spots, 1)
        
        # Score based on visits per spot (2+ is excellent, 1+ is good)
        if visits_per_spot >= 2.0:
            return 100.0
        elif visits_per_spot >= 1.5:
            return 80.0
        elif visits_per_spot >= 1.0:
            return 60.0
        elif visits_per_spot >= 0.5:
            return 40.0
        else:
            return 20.0
    
    def _classify_performance_tier(self, visit_rate: float, top_quartile: float, 
                                 median: float, bottom_quartile: float) -> str:
        """Classify performance tier based on quartiles"""
        if visit_rate >= top_quartile:
            return 'High Performer'
        elif visit_rate >= median:
            return 'Above Average'
        elif visit_rate >= bottom_quartile:
            return 'Average'
        else:
            return 'Below Average'
    
    def _classify_station_opportunity(self, total_visits: int, visit_rate: float, 
                                    trend_direction: str, median: float, top_quartile: float) -> str:
        """Classify station opportunity type based on volume, efficiency, and trends"""
        if total_visits > 1000 and visit_rate >= top_quartile and trend_direction != 'declining':
            return 'Scale Winner'
        elif total_visits < 500 and visit_rate >= top_quartile and trend_direction == 'improving':
            return 'Hidden Gem'
        elif trend_direction == 'improving':
            return 'Rising Star'
        elif total_visits > 1000 and visit_rate < median:
            return 'Optimize or Reduce'
        else:
            return 'Monitor'
    
    def _classify_daypart_efficiency(self, visit_rate: float, avg_performance: float, top_rate: float) -> str:
        """Classify daypart efficiency rating"""
        if visit_rate >= avg_performance * 1.3:
            return 'Excellent'
        elif visit_rate >= avg_performance * 1.1:
            return 'Good'
        elif visit_rate >= avg_performance * 0.9:
            return 'Fair'
        else:
            return 'Poor'
    
    def _classify_daypart_priority(self, total_spots: int, visit_rate: float, 
                                 avg_performance: float, trend_direction: str) -> str:
        """Classify daypart recommendation priority"""
        if total_spots >= 50 and visit_rate > avg_performance and trend_direction != 'declining':
            return 'High - Scale Up'
        elif trend_direction == 'declining':
            return 'Medium - Investigate Decline'
        elif visit_rate > avg_performance:
            return 'Medium - Test Scale'
        else:
            return 'Low - Monitor'
    
    def _calculate_volume_score(self, total_visits: int, all_station_data: List[Dict]) -> float:
        """Calculate volume score relative to other stations"""
        all_visits = [s.get('total_visits', 0) for s in all_station_data]
        if not all_visits:
            return 1.0
        
        max_visits = max(all_visits)
        if max_visits == 0:
            return 1.0
        
        return total_visits / max_visits
    
    def _calculate_synergy_score(self, combo_rate: float, median_rate: float) -> float:
        """Calculate synergy score for station+daypart combinations"""
        if median_rate == 0:
            return 1.0
        
        return combo_rate / median_rate
    
    def _get_combination_investment_recommendation(self, combo_tier: str, confidence: str, spots: int) -> str:
        """Get investment recommendation for combinations"""
        if combo_tier == 'Golden Combination' and confidence == 'High':
            return 'Scale Aggressively'
        elif combo_tier in ['Golden Combination', 'Strong Combination'] and spots >= 10:
            return 'Increase Investment'
        elif combo_tier == 'Strong Combination':
            return 'Test Scale'
        else:
            return 'Monitor Performance'
    
    def _assess_data_quality(self, metadata: Dict[str, Any], totals: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall data quality for analysis"""
        data_quality_score = metadata.get('data_quality_score', 0)
        attribution_coverage = self._calculate_attribution_coverage(totals)
        
        return {
            'overall_score': data_quality_score,
            'attribution_coverage': attribution_coverage,
            'sample_size_adequacy': 'High' if totals.get('total_spots', 0) >= 500 else 'Medium' if totals.get('total_spots', 0) >= 100 else 'Low',
            'recommendation': self._get_data_quality_recommendation(data_quality_score, attribution_coverage)
        }
    
    def _get_data_quality_recommendation(self, quality_score: float, attribution_coverage: float) -> str:
        """Get recommendation based on data quality"""
        if quality_score >= 90 and attribution_coverage >= 80:
            return 'Excellent data quality - high confidence insights'
        elif quality_score >= 70 and attribution_coverage >= 60:
            return 'Good data quality - reliable insights'
        elif quality_score >= 50 or attribution_coverage >= 40:
            return 'Fair data quality - insights available with caveats'
        else:
            return 'Poor data quality - limited insight reliability'


# Test the context processor module
if __name__ == "__main__":
    print("🧪 Testing Context Processor Module...")
    
    try:
        from .trend_analyzer import TrendAnalyzer
        
        # Create sample KPI data
        sample_kpis = {
            'metadata': {
                'data_quality_score': 85.0,
                'date_range': {'start_date': '2025-06-01', 'end_date': '2025-06-27'},
                'primary_product': 'TEST_PRODUCT'
            },
            'totals': {
                'total_spots': 500,
                'total_cost': 125000,
                'total_visits': 1250,
                'total_orders': 85,
                'total_revenue': 42500,
                'total_impressions': 8500
            },
            'efficiency': {
                'roas': 0.34,
                'cpm': 14.71,
                'cpo': 147.06,
                'cpv': 100.00,
                'visit_to_order_rate': 0.068
            },
            'dimensional_analysis': {
                'station_performance': [
                    {'station': 'TEST_STATION_1', 'avg_visits_per_spot': 3.5, 'total_visits': 350, 'spots': 100},
                    {'station': 'TEST_STATION_2', 'avg_visits_per_spot': 2.2, 'total_visits': 220, 'spots': 100},
                    {'station': 'TEST_STATION_3', 'avg_visits_per_spot': 1.8, 'total_visits': 180, 'spots': 100}
                ],
                'daypart_performance': [
                    {'daypart': 'PRIME', 'avg_visits_per_spot': 4.0, 'total_visits': 400, 'spots': 100},
                    {'daypart': 'DAYTIME', 'avg_visits_per_spot': 2.5, 'total_visits': 250, 'spots': 100}
                ]
            },
            'time_patterns': {
                'daily_trends': [
                    {'date': '2025-06-01', 'spots': 25, 'visits': 62, 'revenue': 2500},
                    {'date': '2025-06-02', 'spots': 23, 'visits': 58, 'revenue': 2300},
                    {'date': '2025-06-03', 'spots': 26, 'visits': 65, 'revenue': 2600}
                ]
            }
        }
        
        # Test with trend analyzer
        trend_analyzer = TrendAnalyzer(sample_kpis['time_patterns'])
        processor = ContextProcessor(trend_analyzer)
        
        # Process context
        context = processor.prepare_comprehensive_context(sample_kpis, 'TEST_CLIENT')
        
        print(f"✅ Context prepared for client: {context['client_name']}")
        print(f"✅ Campaign overview: {len(context['campaign_overview'])} metrics")
        print(f"✅ Station performance: {len(context['station_performance'])} stations processed")
        print(f"✅ Daypart performance: {len(context['daypart_performance'])} dayparts processed")
        print(f"✅ Data quality score: {context['data_quality']['overall_score']}")
        print(f"✅ Analysis confidence: {context['analysis_confidence']:.1%}")
        
        # Test station processing
        if context['station_performance']:
            top_station = context['station_performance'][0]
            print(f"✅ Top station: {top_station['station']} ({top_station['opportunity_type']})")
        
        # Test trend integration
        trend_analysis = context['trend_analysis']
        print(f"✅ Trend analysis: {trend_analysis.get('trend_assessment', 'N/A')}")
        
        print("✅ Context Processor module test completed successfully!")
        
    except Exception as e:
        print(f"❌ Context Processor module test failed: {e}")
        import traceback
        traceback.print_exc()