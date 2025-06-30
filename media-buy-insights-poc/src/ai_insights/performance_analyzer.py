"""
AI Insights - Performance Analyzer Module
Simple, practical performance analysis for media buyers and account managers
"""

from typing import Dict, Any, List, Tuple
from .config import AnalysisConstants, UtilityFunctions

class PerformanceAnalyzer:
    """Analyzes performance patterns and generates practical recommendations for media buyers"""
    
    def __init__(self):
        """Initialize performance analyzer"""
        self.utils = UtilityFunctions()
    
    def analyze_performance_quadrants(self, context: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Simple quadrant analysis: Volume vs Efficiency
        
        Returns 4 clear buckets:
        - Scale These: High volume + High efficiency 
        - Test These: Low volume + High efficiency
        - Optimize These: High volume + Low efficiency  
        - Reduce These: Low volume + Low efficiency
        """
        
        station_data = context.get('station_performance', [])
        if not station_data:
            return {}
        
        # Calculate simple medians for quadrant split
        volumes = [s.get('total_visits', 0) for s in station_data]
        efficiencies = [s.get('avg_visits_per_spot', 0) for s in station_data]
        
        median_volume = sorted(volumes)[len(volumes) // 2] if volumes else 0
        median_efficiency = sorted(efficiencies)[len(efficiencies) // 2] if efficiencies else 0
        
        # Simple quadrant buckets
        quadrants = {
            'scale_these': [],      # High volume + High efficiency
            'test_these': [],       # Low volume + High efficiency  
            'optimize_these': [],   # High volume + Low efficiency
            'reduce_these': []      # Low volume + Low efficiency
        }
        
        for station in station_data:
            volume = station.get('total_visits', 0)
            efficiency = station.get('avg_visits_per_spot', 0)
            spots = station.get('spots', 0)
            trend = station.get('trend_direction', 'stable')
            
            # Simple classification
            high_volume = volume >= median_volume
            high_efficiency = efficiency >= median_efficiency
            
            # Basic station info for media buyer
            station_info = {
                'station': station.get('station', 'Unknown'),
                'volume': volume,
                'efficiency': efficiency,
                'spots': spots,
                'trend': trend,
                'confidence': 'High' if spots >= 50 else 'Medium' if spots >= 20 else 'Low'
            }
            
            # Simple action based on quadrant + trend
            if high_volume and high_efficiency:
                station_info['action'] = 'Scale up' if trend != 'declining' else 'Investigate decline'
                station_info['priority'] = 'High'
                quadrants['scale_these'].append(station_info)
                
            elif not high_volume and high_efficiency:
                station_info['action'] = 'Test more budget' if trend != 'declining' else 'Monitor closely'
                station_info['priority'] = 'Medium'
                quadrants['test_these'].append(station_info)
                
            elif high_volume and not high_efficiency:
                station_info['action'] = 'Optimize creative/targeting' if trend == 'improving' else 'Reduce budget'
                station_info['priority'] = 'Medium'
                quadrants['optimize_these'].append(station_info)
                
            else:
                station_info['action'] = 'Remove from plan' if trend != 'improving' else 'Monitor improvement'
                station_info['priority'] = 'Low'
                quadrants['reduce_these'].append(station_info)
        
        # Sort each quadrant by efficiency (best first)
        for quadrant in quadrants.values():
            quadrant.sort(key=lambda x: x['efficiency'], reverse=True)
        
        return quadrants
    
    def generate_opportunity_matrix(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate simple budget reallocation opportunities"""
        
        station_data = context.get('station_performance', [])
        if len(station_data) < 3:
            return []
        
        # Sort by efficiency 
        sorted_stations = sorted(station_data, key=lambda x: x.get('avg_visits_per_spot', 0), reverse=True)
        
        opportunities = []
        
        # Find top 3 and bottom 3 performers
        top_performers = sorted_stations[:3]
        bottom_performers = sorted_stations[-3:]
        
        # Simple reallocation suggestions
        for i, (top, bottom) in enumerate(zip(top_performers, reversed(bottom_performers))):
            top_efficiency = top.get('avg_visits_per_spot', 0)
            bottom_efficiency = bottom.get('avg_visits_per_spot', 0)
            bottom_spots = bottom.get('spots', 0)
            
            # Only suggest if meaningful difference and enough spots to move
            if top_efficiency > bottom_efficiency * 1.5 and bottom_spots >= 20:
                spots_to_move = min(bottom_spots // 2, 25)  # Move max half or 25 spots
                visit_gain = spots_to_move * (top_efficiency - bottom_efficiency)
                
                opportunities.append({
                    'from_station': bottom.get('station', 'Unknown'),
                    'to_station': top.get('station', 'Unknown'),
                    'spots_to_move': spots_to_move,
                    'efficiency_gain': round(top_efficiency - bottom_efficiency, 1),
                    'projected_visit_gain': int(visit_gain),
                    'confidence': 'High' if bottom_spots >= 40 else 'Medium',
                    'action': f"Move {spots_to_move} spots from {bottom.get('station')} to {top.get('station')}"
                })
        
        return opportunities[:5]  # Top 5 opportunities only
    
    def assess_portfolio_balance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simple portfolio health check"""
        
        quadrants = self.analyze_performance_quadrants(context)
        station_data = context.get('station_performance', [])
        daypart_data = context.get('daypart_performance', [])
        
        total_stations = len(station_data)
        if total_stations == 0:
            return {'health': 'No data'}
        
        # Simple counts
        scale_count = len(quadrants.get('scale_these', []))
        test_count = len(quadrants.get('test_these', []))
        reduce_count = len(quadrants.get('reduce_these', []))
        
        # Simple health assessment
        good_stations = scale_count + test_count
        good_ratio = good_stations / total_stations
        
        if good_ratio >= 0.6:
            health = 'Good'
            message = f"{good_stations}/{total_stations} stations performing well"
        elif good_ratio >= 0.4:
            health = 'Fair' 
            message = f"Only {good_stations}/{total_stations} stations performing well - optimization needed"
        else:
            health = 'Poor'
            message = f"Only {good_stations}/{total_stations} stations performing well - major changes needed"
        
        # Simple daypart concentration check
        daypart_concentration = 'Balanced'
        if daypart_data:
            total_daypart_spots = sum(d.get('spots', 0) for d in daypart_data)
            if total_daypart_spots > 0:
                max_daypart_pct = max(d.get('spots', 0) / total_daypart_spots for d in daypart_data)
                if max_daypart_pct > 0.6:
                    daypart_concentration = 'Too concentrated'
                elif max_daypart_pct < 0.2:
                    daypart_concentration = 'Too spread out'
        
        return {
            'health': health,
            'message': message,
            'good_stations': good_stations,
            'total_stations': total_stations,
            'daypart_balance': daypart_concentration,
            'recommendations': self._get_simple_recommendations(health, daypart_concentration, reduce_count)
        }
    
    def identify_scaling_candidates(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify top candidates for more budget"""
        
        station_data = context.get('station_performance', [])
        candidates = []
        
        for station in station_data:
            efficiency = station.get('avg_visits_per_spot', 0)
            volume = station.get('total_visits', 0)
            trend = station.get('trend_direction', 'stable')
            spots = station.get('spots', 0)
            
            # Simple scoring: efficiency + trend bonus + volume bonus
            score = efficiency
            if trend == 'improving':
                score += 1.0  # Trend bonus
            if volume > 500:
                score += 0.5  # Volume bonus
            
            # Only recommend stations with decent sample size and positive trends
            if efficiency >= 2.0 and spots >= 15 and trend != 'declining':
                candidates.append({
                    'station': station.get('station', 'Unknown'),
                    'efficiency': efficiency,
                    'trend': trend,
                    'score': round(score, 1),
                    'confidence': 'High' if spots >= 50 else 'Medium',
                    'reason': self._get_scaling_reason(efficiency, trend, volume)
                })
        
        # Sort by score and return top 5
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:5]
    
    def _get_simple_recommendations(self, health: str, daypart_balance: str, reduce_count: int) -> List[str]:
        """Generate simple recommendations for media buyers"""
        
        recommendations = []
        
        if health == 'Poor':
            recommendations.append("Major station lineup changes needed")
        elif health == 'Fair':
            recommendations.append("Optimize underperforming stations")
        
        if daypart_balance == 'Too concentrated':
            recommendations.append("Diversify daypart allocation")
        elif daypart_balance == 'Too spread out':
            recommendations.append("Focus on best performing dayparts")
        
        if reduce_count >= 3:
            recommendations.append(f"Consider removing {reduce_count} underperforming stations")
        
        if not recommendations:
            recommendations.append("Portfolio looks healthy - maintain current strategy")
        
        return recommendations
    
    def _get_scaling_reason(self, efficiency: float, trend: str, volume: int) -> str:
        """Simple reason for scaling recommendation"""
        
        reasons = []
        
        if efficiency >= 3.0:
            reasons.append("high efficiency")
        elif efficiency >= 2.0:
            reasons.append("good efficiency")
        
        if trend == 'improving':
            reasons.append("improving trend")
        
        if volume > 1000:
            reasons.append("proven scale")
        elif volume > 500:
            reasons.append("good volume")
        
        return " + ".join(reasons) if reasons else "solid performance"


# Test the simplified performance analyzer
if __name__ == "__main__":
    print("🧪 Testing Simplified Performance Analyzer...")
    
    # Create simple test data
    sample_context = {
        'station_performance': [
            # Scale these: high volume + high efficiency
            {'station': 'WINNER_1', 'total_visits': 1200, 'avg_visits_per_spot': 4.0, 'spots': 60, 'trend_direction': 'improving'},
            {'station': 'WINNER_2', 'total_visits': 1000, 'avg_visits_per_spot': 3.5, 'spots': 50, 'trend_direction': 'stable'},
            
            # Test these: low volume + high efficiency  
            {'station': 'HIDDEN_GEM', 'total_visits': 400, 'avg_visits_per_spot': 3.8, 'spots': 25, 'trend_direction': 'improving'},
            
            # Optimize these: high volume + low efficiency
            {'station': 'BIG_INEFFICIENT', 'total_visits': 900, 'avg_visits_per_spot': 1.8, 'spots': 80, 'trend_direction': 'declining'},
            
            # Reduce these: low volume + low efficiency
            {'station': 'LOSER_1', 'total_visits': 200, 'avg_visits_per_spot': 1.2, 'spots': 30, 'trend_direction': 'stable'},
            {'station': 'LOSER_2', 'total_visits': 150, 'avg_visits_per_spot': 1.0, 'spots': 25, 'trend_direction': 'declining'}
        ],
        'daypart_performance': [
            {'daypart': 'PRIME', 'spots': 120, 'avg_visits_per_spot': 3.5},
            {'daypart': 'DAYTIME', 'spots': 100, 'avg_visits_per_spot': 2.8},
            {'daypart': 'LATE', 'spots': 50, 'avg_visits_per_spot': 1.5}
        ]
    }
    
    analyzer = PerformanceAnalyzer()
    
    # Test quadrant analysis
    quadrants = analyzer.analyze_performance_quadrants(sample_context)
    print(f"✅ Quadrants: Scale={len(quadrants.get('scale_these', []))}, Test={len(quadrants.get('test_these', []))}, Optimize={len(quadrants.get('optimize_these', []))}, Reduce={len(quadrants.get('reduce_these', []))}")
    
    # Test opportunity matrix
    opportunities = analyzer.generate_opportunity_matrix(sample_context)
    print(f"✅ Opportunities: {len(opportunities)} reallocation suggestions")
    
    # Test portfolio balance
    balance = analyzer.assess_portfolio_balance(sample_context)
    print(f"✅ Portfolio health: {balance['health']} - {balance['message']}")
    
    # Test scaling candidates
    candidates = analyzer.identify_scaling_candidates(sample_context)
    print(f"✅ Scaling candidates: {len(candidates)} stations recommended for more budget")
    
    # Show sample results
    if quadrants.get('scale_these'):
        top_winner = quadrants['scale_these'][0]
        print(f"🎯 Top winner: {top_winner['station']} - {top_winner['action']}")
    
    if opportunities:
        top_opportunity = opportunities[0] 
        print(f"💡 Top opportunity: {top_opportunity['action']}")
    
    print("✅ Simplified Performance Analyzer test completed!")
    print("🎯 Focus: Clear action items for media buyers, not complex algorithms")