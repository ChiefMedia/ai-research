"""
AI Insights - Trend Analyzer Module
Handles time-based analysis, weekly trends, and recent vs historical comparisons
"""

from typing import Dict, Any, List
from .config import AnalysisConstants

class TrendAnalyzer:
    """Analyzes time-based patterns and trends in campaign data"""
    
    def __init__(self, time_patterns: Dict[str, Any]):
        """Initialize trend analyzer with time pattern data"""
        self.time_patterns = time_patterns
        self.daily_trends = time_patterns.get('daily_trends', [])
        self.weekly_data = []
        
        # Aggregate daily data to weekly if available
        if self.daily_trends:
            self.weekly_data = self.aggregate_to_weekly(self.daily_trends)
    
    def aggregate_to_weekly(self, daily_trends: List[Dict]) -> List[Dict]:
        """Aggregate daily data to weekly for trend analysis"""
        if not daily_trends:
            return []
        
        weekly_data = []
        current_week = []
        
        for i, day in enumerate(daily_trends):
            current_week.append(day)
            
            # Every 7 days or at the end, create a week summary
            if len(current_week) >= 7 or i == len(daily_trends) - 1:
                if current_week:
                    week_summary = {
                        'week_start': current_week[0].get('date', 'Unknown'),
                        'week_end': current_week[-1].get('date', 'Unknown'),
                        'total_spots': sum(d.get('spots', 0) for d in current_week),
                        'total_revenue': sum(d.get('revenue', 0) for d in current_week),
                        'total_visits': sum(d.get('visits', 0) for d in current_week),
                        'avg_daily_spots': sum(d.get('spots', 0) for d in current_week) / len(current_week),
                        'avg_daily_efficiency': (sum(d.get('visits', 0) for d in current_week) / 
                                               max(sum(d.get('spots', 1) for d in current_week), 1))
                    }
                    weekly_data.append(week_summary)
                current_week = []
        
        return weekly_data
    
    def calculate_weekly_trend(self, entity_name: str = None) -> Dict[str, Any]:
        """Calculate weekly trend for a specific entity (station/daypart) or overall"""
        if len(self.weekly_data) < 2:
            return {
                'trend_direction': 'insufficient_data',
                'recent_avg_efficiency': 0,
                'volume_stability': 'unknown',
                'weeks_analyzed': len(self.weekly_data)
            }
        
        # Use overall weekly trends (in full implementation, filter by entity_name)
        recent_weeks = self.weekly_data[-2:] if len(self.weekly_data) >= 2 else self.weekly_data
        earlier_weeks = self.weekly_data[:-2] if len(self.weekly_data) > 2 else []
        
        recent_avg = sum(w.get('avg_daily_efficiency', 0) for w in recent_weeks) / len(recent_weeks)
        
        if earlier_weeks:
            earlier_avg = sum(w.get('avg_daily_efficiency', 0) for w in earlier_weeks) / len(earlier_weeks)
            if recent_avg > earlier_avg * AnalysisConstants.IMPROVING_THRESHOLD:
                trend_direction = 'improving'
            elif recent_avg < earlier_avg * AnalysisConstants.DECLINING_THRESHOLD:
                trend_direction = 'declining'
            else:
                trend_direction = 'stable'
        else:
            trend_direction = 'stable'
        
        # Volume stability analysis
        recent_volumes = [w.get('total_spots', 0) for w in recent_weeks]
        if len(recent_volumes) > 1:
            volume_cv = ((max(recent_volumes) - min(recent_volumes)) / 
                        max(sum(recent_volumes) / len(recent_volumes), 1))
            volume_stability = 'stable' if volume_cv < 0.3 else 'volatile'
        else:
            volume_stability = 'stable'
        
        return {
            'trend_direction': trend_direction,
            'recent_avg_efficiency': recent_avg,
            'volume_stability': volume_stability,
            'weeks_analyzed': len(self.weekly_data)
        }
    
    def analyze_weekly_trends(self) -> Dict[str, Any]:
        """Analyze overall weekly trends and week-over-week changes"""
        if not self.daily_trends:
            return {'trend_analysis': 'insufficient_data'}
        
        if len(self.weekly_data) < 2:
            return {'trend_analysis': 'insufficient_weeks'}
        
        # Calculate week-over-week changes
        week_over_week_changes = []
        for i in range(1, len(self.weekly_data)):
            prev_week = self.weekly_data[i-1]
            curr_week = self.weekly_data[i]
            
            # Calculate efficiency change
            efficiency_change = ((curr_week.get('avg_daily_efficiency', 0) - 
                                prev_week.get('avg_daily_efficiency', 0)) / 
                               max(prev_week.get('avg_daily_efficiency', 1), 1)) * 100
            
            # Calculate volume change
            volume_change = ((curr_week.get('total_spots', 0) - prev_week.get('total_spots', 0)) / 
                           max(prev_week.get('total_spots', 1), 1)) * 100
            
            week_over_week_changes.append({
                'week': i + 1,
                'efficiency_change_pct': efficiency_change,
                'volume_change_pct': volume_change
            })
        
        return {
            'weekly_data': self.weekly_data,
            'week_over_week_changes': week_over_week_changes,
            'trend_analysis': 'completed',
            'total_weeks_analyzed': len(self.weekly_data)
        }
    
    def compare_recent_vs_historical(self, recent_days: int = 7) -> Dict[str, Any]:
        """Compare recent performance vs historical average"""
        if not self.daily_trends or len(self.daily_trends) < (recent_days * 2):
            return {'comparison': 'insufficient_data'}
        
        # Split into recent and historical periods
        recent_period = self.daily_trends[-recent_days:]
        historical_period = self.daily_trends[:-recent_days]
        
        # Calculate efficiency for each period
        recent_avg_efficiency = (sum(d.get('visits', 0) for d in recent_period) / 
                               max(sum(d.get('spots', 1) for d in recent_period), 1))
        historical_avg_efficiency = (sum(d.get('visits', 0) for d in historical_period) / 
                                    max(sum(d.get('spots', 1) for d in historical_period), 1))
        
        # Calculate performance change percentage
        performance_change = ((recent_avg_efficiency - historical_avg_efficiency) / 
                            max(historical_avg_efficiency, 1)) * 100
        
        # Assess trend
        if performance_change > 10:
            trend_assessment = 'significantly_improved'
        elif performance_change > 5:
            trend_assessment = 'improved'
        elif performance_change < -10:
            trend_assessment = 'significantly_declined'
        elif performance_change < -5:
            trend_assessment = 'declined'
        else:
            trend_assessment = 'stable'
        
        return {
            'recent_avg_efficiency': recent_avg_efficiency,
            'historical_avg_efficiency': historical_avg_efficiency,
            'performance_change_pct': performance_change,
            'trend_assessment': trend_assessment,
            'days_recent': len(recent_period),
            'days_historical': len(historical_period)
        }
    
    def get_latest_week_insights(self) -> Dict[str, Any]:
        """Get insights about the most recent week"""
        if len(self.weekly_data) < 2:
            return {'insight': 'insufficient_data_for_latest_week'}
        
        latest_week = self.weekly_data[-1]
        previous_week = self.weekly_data[-2]
        
        # Calculate week-over-week changes
        efficiency_change = ((latest_week.get('avg_daily_efficiency', 0) - 
                            previous_week.get('avg_daily_efficiency', 0)) / 
                           max(previous_week.get('avg_daily_efficiency', 1), 1)) * 100
        
        volume_change = ((latest_week.get('total_spots', 0) - previous_week.get('total_spots', 0)) / 
                        max(previous_week.get('total_spots', 1), 1)) * 100
        
        revenue_change = ((latest_week.get('total_revenue', 0) - previous_week.get('total_revenue', 0)) / 
                         max(previous_week.get('total_revenue', 1), 1)) * 100
        
        # Generate insights
        insights = []
        
        if abs(efficiency_change) > 10:
            direction = 'improvement' if efficiency_change > 0 else 'decline'
            insights.append(f"Strong {direction}: {abs(efficiency_change):.1f}% efficiency change in latest week")
        
        if abs(volume_change) > 15:
            direction = 'surge' if volume_change > 0 else 'drop'
            insights.append(f"Volume {direction}: {abs(volume_change):.1f}% change in spots last week")
        
        if abs(revenue_change) > 15:
            direction = 'increase' if revenue_change > 0 else 'decrease'
            insights.append(f"Revenue {direction}: {abs(revenue_change):.1f}% change last week")
        
        return {
            'latest_week_data': latest_week,
            'efficiency_change_pct': efficiency_change,
            'volume_change_pct': volume_change,
            'revenue_change_pct': revenue_change,
            'insights': insights
        }
    
    def identify_trend_patterns(self) -> Dict[str, Any]:
        """Identify patterns in the trend data"""
        if len(self.weekly_data) < 3:
            return {'patterns': 'insufficient_data'}
        
        patterns = {
            'consistent_growth': False,
            'consistent_decline': False,
            'volatile_performance': False,
            'seasonal_pattern': False
        }
        
        # Check for consistent growth/decline
        efficiency_changes = []
        for i in range(1, len(self.weekly_data)):
            prev_week = self.weekly_data[i-1]
            curr_week = self.weekly_data[i]
            change = curr_week.get('avg_daily_efficiency', 0) - prev_week.get('avg_daily_efficiency', 0)
            efficiency_changes.append(change)
        
        # Analyze patterns
        positive_changes = sum(1 for change in efficiency_changes if change > 0)
        negative_changes = sum(1 for change in efficiency_changes if change < 0)
        
        if positive_changes >= len(efficiency_changes) * 0.8:
            patterns['consistent_growth'] = True
        elif negative_changes >= len(efficiency_changes) * 0.8:
            patterns['consistent_decline'] = True
        
        # Check volatility
        efficiency_values = [w.get('avg_daily_efficiency', 0) for w in self.weekly_data]
        if efficiency_values:
            avg_efficiency = sum(efficiency_values) / len(efficiency_values)
            variance = sum((x - avg_efficiency) ** 2 for x in efficiency_values) / len(efficiency_values)
            cv = (variance ** 0.5) / avg_efficiency if avg_efficiency > 0 else 0
            
            if cv > 0.3:
                patterns['volatile_performance'] = True
        
        return patterns
    
    def get_trend_context_for_entity(self, entity_type: str, entity_name: str) -> Dict[str, Any]:
        """Get trend context for a specific station or daypart"""
        # This is a simplified version - in full implementation, 
        # would filter weekly data by specific entity
        base_trend = self.calculate_weekly_trend(entity_name)
        
        # Add entity-specific context
        context = {
            'entity_type': entity_type,
            'entity_name': entity_name,
            'trend_direction': base_trend.get('trend_direction', 'stable'),
            'recent_efficiency': base_trend.get('recent_avg_efficiency', 0),
            'volume_stability': base_trend.get('volume_stability', 'unknown'),
            'weeks_analyzed': base_trend.get('weeks_analyzed', 0),
            'confidence_level': 'High' if base_trend.get('weeks_analyzed', 0) >= 3 else 'Medium'
        }
        
        # Add specific recommendations based on entity type and trend
        if entity_type == 'station':
            context['recommendation_focus'] = self._get_station_trend_recommendation(
                base_trend.get('trend_direction', 'stable')
            )
        elif entity_type == 'daypart':
            context['recommendation_focus'] = self._get_daypart_trend_recommendation(
                base_trend.get('trend_direction', 'stable')
            )
        
        return context
    
    def _get_station_trend_recommendation(self, trend_direction: str) -> str:
        """Get trend-based recommendation for stations"""
        if trend_direction == 'improving':
            return 'Consider scaling - positive momentum detected'
        elif trend_direction == 'declining':
            return 'Investigate decline - performance dropping'
        else:
            return 'Monitor performance - stable trend'
    
    def _get_daypart_trend_recommendation(self, trend_direction: str) -> str:
        """Get trend-based recommendation for dayparts"""
        if trend_direction == 'improving':
            return 'Increase daypart investment - efficiency improving'
        elif trend_direction == 'declining':
            return 'Optimize daypart strategy - efficiency declining'
        else:
            return 'Maintain current daypart allocation - stable performance'
    
    def get_weekly_data(self) -> List[Dict]:
        """Get the aggregated weekly data"""
        return self.weekly_data
    
    def has_sufficient_data(self) -> bool:
        """Check if there's sufficient data for trend analysis"""
        return len(self.weekly_data) >= 2 and len(self.daily_trends) >= 14


# Test the trend analyzer module
if __name__ == "__main__":
    print("🧪 Testing Trend Analyzer Module...")
    
    try:
        # Create sample time patterns data
        sample_time_patterns = {
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
        
        # Test trend analyzer
        analyzer = TrendAnalyzer(sample_time_patterns)
        print(f"✅ Trend analyzer initialized with {len(analyzer.daily_trends)} daily trends")
        print(f"✅ Weekly data aggregated: {len(analyzer.weekly_data)} weeks")
        
        # Test weekly trend calculation
        weekly_trend = analyzer.calculate_weekly_trend()
        print(f"✅ Weekly trend calculated: {weekly_trend['trend_direction']}")
        
        # Test recent vs historical comparison
        recent_vs_historical = analyzer.compare_recent_vs_historical()
        print(f"✅ Recent vs historical: {recent_vs_historical['trend_assessment']}")
        
        # Test weekly trends analysis
        weekly_analysis = analyzer.analyze_weekly_trends()
        print(f"✅ Weekly analysis: {weekly_analysis['trend_analysis']}")
        
        # Test latest week insights
        latest_insights = analyzer.get_latest_week_insights()
        print(f"✅ Latest week insights: {len(latest_insights.get('insights', []))} insights")
        
        # Test trend patterns
        patterns = analyzer.identify_trend_patterns()
        print(f"✅ Trend patterns identified: {sum(patterns.values())} patterns detected")
        
        # Test entity context
        station_context = analyzer.get_trend_context_for_entity('station', 'TEST_STATION')
        print(f"✅ Entity context: {station_context['recommendation_focus']}")
        
        # Test data sufficiency
        has_data = analyzer.has_sufficient_data()
        print(f"✅ Data sufficiency check: {has_data}")
        
        print("✅ Trend Analyzer module test completed successfully!")
        
    except Exception as e:
        print(f"❌ Trend Analyzer module test failed: {e}")
        import traceback
        traceback.print_exc()