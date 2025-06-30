"""
AI Insights - Insight Generators Module
Generates specific insights for stations, dayparts, and combinations
"""

from typing import Dict, Any, List
from .config import AnalysisConstants, UtilityFunctions

class InsightGenerators:
    """Generates detailed insights for different campaign dimensions"""
    
    def __init__(self):
        """Initialize insight generators"""
        self.utils = UtilityFunctions()
    
    def generate_station_insights(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive insights for each station with actionable recommendations"""
        
        station_data = context.get('station_performance', [])
        if not station_data:
            return []
        
        insights = []
        client_name = context.get('client_name', 'Unknown')
        
        for station in station_data[:15]:  # Top 15 stations for detailed analysis
            station_name = station.get('station', 'Unknown')
            product = station.get('product', context.get('primary_product', 'DEFAULT'))
            visit_rate = station.get('avg_visits_per_spot', 0)
            total_visits = station.get('total_visits', 0)
            spots = station.get('spots', 0)
            performance_tier = station.get('performance_tier', 'Unknown')
            opportunity_type = station.get('opportunity_type', 'Monitor')
            
            # Get trend context
            trend_direction = station.get('trend_direction', 'stable')
            recent_efficiency = station.get('recent_efficiency', visit_rate)
            efficiency_score = station.get('efficiency_score', 1.0)
            volume_score = station.get('volume_score', 1.0)
            weeks_analyzed = station.get('weeks_analyzed', 0)
            
            insight = {
                'station': station_name,
                'client': client_name,
                'product': product,
                'insight_type': AnalysisConstants.INSIGHT_CATEGORIES['STATION_ANALYSIS'],
                'performance_tier': performance_tier,
                'opportunity_type': opportunity_type,
                'visit_rate': visit_rate,
                'recent_efficiency': recent_efficiency,
                'total_visits': total_visits,
                'spots': spots,
                'trend_direction': trend_direction,
                'efficiency_score': efficiency_score,
                'volume_score': volume_score,
                'confidence': self.utils.determine_confidence_level(spots, weeks_analyzed)
            }
            
            # Generate time-contextualized recommendations
            recommendation_data = self._generate_station_recommendation(
                station_name, opportunity_type, trend_direction, efficiency_score, 
                volume_score, recent_efficiency, visit_rate
            )
            insight.update(recommendation_data)
            
            insights.append(insight)
        
        return insights
    
    def generate_daypart_insights(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive insights for each daypart with scheduling recommendations"""
        
        daypart_data = context.get('daypart_performance', [])
        if not daypart_data:
            return []
        
        insights = []
        client_name = context.get('client_name', 'Unknown')
        
        for daypart in daypart_data:
            daypart_name = daypart.get('daypart', 'Unknown')
            product = daypart.get('product', context.get('primary_product', 'DEFAULT'))
            visit_rate = daypart.get('avg_visits_per_spot', 0)
            total_visits = daypart.get('total_visits', 0)
            spots = daypart.get('spots', 0)
            efficiency_rating = daypart.get('efficiency_rating', 'Unknown')
            recommendation_priority = daypart.get('recommendation_priority', 'Low')
            
            # Get trend context
            trend_direction = daypart.get('trend_direction', 'stable')
            recent_efficiency = daypart.get('recent_efficiency', visit_rate)
            efficiency_index = daypart.get('efficiency_index', 1.0)
            volume_adequacy = daypart.get('volume_adequacy', 'Medium')
            weeks_analyzed = daypart.get('weeks_analyzed', 0)
            
            insight = {
                'daypart': daypart_name,
                'client': client_name,
                'product': product,
                'insight_type': AnalysisConstants.INSIGHT_CATEGORIES['DAYPART_ANALYSIS'],
                'efficiency_rating': efficiency_rating,
                'recommendation_priority': recommendation_priority,
                'visit_rate': visit_rate,
                'recent_efficiency': recent_efficiency,
                'total_visits': total_visits,
                'spots': spots,
                'trend_direction': trend_direction,
                'efficiency_index': efficiency_index,
                'volume_adequacy': volume_adequacy,
                'confidence': self.utils.determine_confidence_level(spots, weeks_analyzed)
            }
            
            # Generate daypart-specific recommendations
            recommendation_data = self._generate_daypart_recommendation(
                daypart_name, recommendation_priority, trend_direction, 
                efficiency_index, volume_adequacy, recent_efficiency
            )
            insight.update(recommendation_data)
            
            insights.append(insight)
        
        return insights
    
    def generate_combination_insights(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights for station+daypart combinations"""
        
        combination_data = context.get('combination_performance', [])
        if not combination_data:
            return []
        
        insights = []
        client_name = context.get('client_name', 'Unknown')
        
        for combo in combination_data[:20]:  # Top 20 combinations
            station = combo.get('station', 'Unknown')
            daypart = combo.get('daypart', 'Unknown')
            product = combo.get('product', context.get('primary_product', 'DEFAULT'))
            visit_rate = combo.get('avg_visits_per_spot', 0)
            total_visits = combo.get('total_visits', 0)
            spots = combo.get('spots', 0)
            combo_tier = combo.get('combo_tier', 'Standard')
            scaling_priority = combo.get('scaling_priority', 'Low')
            confidence_level = combo.get('confidence_level', 'Low')
            synergy_score = combo.get('synergy_score', 1.0)
            investment_recommendation = combo.get('investment_recommendation', 'Monitor')
            
            insight = {
                'station': station,
                'daypart': daypart,
                'client': client_name,
                'product': product,
                'combination': f"{station} + {daypart}",
                'insight_type': AnalysisConstants.INSIGHT_CATEGORIES['COMBINATION_ANALYSIS'],
                'combo_tier': combo_tier,
                'scaling_priority': scaling_priority,
                'visit_rate': visit_rate,
                'total_visits': total_visits,
                'spots': spots,
                'synergy_score': synergy_score,
                'confidence': confidence_level
            }
            
            # Generate combination-specific recommendations
            recommendation_data = self._generate_combination_recommendation(
                station, daypart, combo_tier, scaling_priority, synergy_score, 
                confidence_level, investment_recommendation
            )
            insight.update(recommendation_data)
            
            insights.append(insight)
        
        return insights
    
    def generate_executive_findings(self, context: Dict[str, Any]) -> List[str]:
        """Generate executive-level key findings with business impact focus"""
        findings = []
        
        campaign_overview = context.get('campaign_overview', {})
        efficiency_metrics = context.get('efficiency_metrics', {})
        station_data = context.get('station_performance', [])
        daypart_data = context.get('daypart_performance', [])
        trend_analysis = context.get('trend_analysis', {})
        
        # Overall performance finding with business context
        total_spots = campaign_overview.get('total_spots', 0)
        total_visits = campaign_overview.get('total_visits', 0)
        total_revenue = campaign_overview.get('total_revenue', 0)
        visits_per_spot = efficiency_metrics.get('visits_per_spot', 0)
        
        # Trend context
        trend_assessment = trend_analysis.get('trend_assessment', 'stable')
        performance_change = trend_analysis.get('performance_change_pct', 0)
        
        # Primary performance finding with trend and business impact
        if total_revenue > 0:
            revenue_efficiency = total_revenue / max(total_spots, 1)
            if trend_assessment in ['significantly_improved', 'improved']:
                findings.append(
                    f"Revenue acceleration detected: ${revenue_efficiency:.0f} per spot with {performance_change:.1f}% recent improvement, "
                    f"generating ${total_revenue:,.0f} total"
                )
            elif trend_assessment in ['significantly_declined', 'declined']:
                findings.append(
                    f"Revenue efficiency declining: ${revenue_efficiency:.0f} per spot down {abs(performance_change):.1f}% recently, "
                    f"impacting ${total_revenue:,.0f} campaign performance"
                )
            else:
                findings.append(
                    f"Stable revenue generation: ${revenue_efficiency:.0f} per spot maintaining ${total_revenue:,.0f} total revenue"
                )
        elif total_visits > 0:
            performance_level = "Excellent" if visits_per_spot > 3 else "Strong" if visits_per_spot > 2 else "Solid" if visits_per_spot > 1 else "Moderate"
            if trend_assessment in ['significantly_improved', 'improved']:
                findings.append(
                    f"{performance_level} engagement surging: {visits_per_spot:.1f} visits per spot with {performance_change:.1f}% momentum"
                )
            elif trend_assessment in ['significantly_declined', 'declined']:
                findings.append(
                    f"{performance_level} engagement weakening: {visits_per_spot:.1f} visits per spot declining {abs(performance_change):.1f}%"
                )
            else:
                findings.append(
                    f"{performance_level} engagement sustained: {visits_per_spot:.1f} visits per TV spot consistently"
                )
        
        # Top station opportunity with business rationale
        if station_data:
            top_station = station_data[0]
            station_name = top_station.get('station', 'Unknown')
            station_visits = top_station.get('total_visits', 0)
            station_spots = top_station.get('spots', 0)
            opportunity_type = top_station.get('opportunity_type', 'Monitor')
            trend_direction = top_station.get('trend_direction', 'stable')
            
            if opportunity_type == 'Scale Winner':
                findings.append(
                    f"Scale opportunity: {station_name} delivering {station_visits:,} visits from {station_spots} spots - "
                    f"prime candidate for budget reallocation"
                )
            elif opportunity_type == 'Hidden Gem' and trend_direction == 'improving':
                findings.append(
                    f"Emerging winner: {station_name} shows untapped potential with improving efficiency - "
                    f"test increased investment"
                )
            elif opportunity_type == 'Rising Star':
                findings.append(
                    f"Momentum play: {station_name} building strength with {station_visits:,} visits - "
                    f"capitalize on positive trend"
                )
        
        # Best daypart opportunity with scheduling implications
        if daypart_data:
            best_daypart = daypart_data[0]
            daypart_name = best_daypart.get('daypart', 'Unknown')
            daypart_efficiency = best_daypart.get('visit_rate', 0)
            daypart_spots = best_daypart.get('spots', 0)
            trend_direction = best_daypart.get('trend_direction', 'stable')
            
            if daypart_efficiency > 0:
                if trend_direction == 'improving':
                    findings.append(
                        f"Scheduling advantage: {daypart_name} daypart strengthening at {daypart_efficiency:.1f} visits per spot - "
                        f"shift more inventory to this window"
                    )
                elif daypart_spots >= 50:  # High volume daypart
                    findings.append(
                        f"Prime inventory: {daypart_name} delivers {daypart_efficiency:.1f} visits per spot consistently - "
                        f"core scheduling foundation"
                    )
                else:
                    findings.append(
                        f"Efficiency leader: {daypart_name} achieves {daypart_efficiency:.1f} visits per spot - "
                        f"expand presence in this daypart"
                    )
        
        # Attribution and data quality insight
        attribution_coverage = campaign_overview.get('attribution_coverage', 0)
        data_quality_score = campaign_overview.get('data_quality_score', 0)
        
        if attribution_coverage >= 80 and data_quality_score >= 90:
            findings.append(
                f"High-quality attribution tracking enables precise optimization across {total_spots} spots"
            )
        elif attribution_coverage >= 60:
            findings.append(
                f"Good attribution coverage ({attribution_coverage:.0f}%) provides reliable optimization direction"
            )
        elif attribution_coverage < 40:
            findings.append(
                f"Limited attribution data ({attribution_coverage:.0f}% coverage) constrains optimization precision"
            )
        
        return findings[:4]  # Return top 4 most impactful findings
    
    def generate_optimization_priorities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate prioritized optimization opportunities with business impact"""
        priorities = []
        
        station_data = context.get('station_performance', [])
        daypart_data = context.get('daypart_performance', [])
        trend_analysis = context.get('trend_analysis', {})
        efficiency_metrics = context.get('efficiency_metrics', {})
        
        # Station reallocation opportunities
        if len(station_data) >= 3:
            top_performers = [s for s in station_data[:3] if s.get('opportunity_type') in ['Scale Winner', 'Hidden Gem']]
            underperformers = [s for s in station_data[-3:] if s.get('efficiency_score', 1) < 0.7]
            
            if top_performers and underperformers:
                top_station = top_performers[0]
                worst_station = underperformers[-1]
                
                efficiency_gap = top_station.get('visit_rate', 0) - worst_station.get('visit_rate', 0)
                potential_spots = min(worst_station.get('spots', 0) // 2, 50)
                projected_gain = potential_spots * efficiency_gap
                
                priorities.append({
                    'priority': 1,
                    'area': 'Station Budget Reallocation',
                    'recommendation': f"Shift {potential_spots} spots from {worst_station.get('station', 'underperformer')} to {top_station.get('station', 'top performer')}",
                    'impact': 'High',
                    'effort': 'Low',
                    'projected_visit_gain': int(projected_gain),
                    'business_rationale': f"Capitalize on {efficiency_gap:.1f} visits/spot efficiency difference"
                })
        
        # Daypart optimization opportunities
        if len(daypart_data) >= 2:
            best_daypart = daypart_data[0]
            worst_daypart = daypart_data[-1]
            
            efficiency_gap = best_daypart.get('visit_rate', 0) - worst_daypart.get('visit_rate', 0)
            if efficiency_gap > best_daypart.get('visit_rate', 0) * 0.2:  # 20%+ difference
                priorities.append({
                    'priority': 2,
                    'area': 'Daypart Scheduling Optimization',
                    'recommendation': f"Increase {best_daypart.get('daypart', 'top daypart')} inventory, reduce {worst_daypart.get('daypart', 'weak daypart')}",
                    'impact': 'High',
                    'effort': 'Medium',
                    'efficiency_advantage': f"{efficiency_gap:.1f} visits/spot",
                    'business_rationale': f"Leverage {best_daypart.get('daypart', 'strong')} daypart's superior audience engagement"
                })
        
        # Trend-based urgent priorities
        trend_assessment = trend_analysis.get('trend_assessment', 'stable')
        performance_change = trend_analysis.get('performance_change_pct', 0)
        
        if trend_assessment == 'significantly_declined':
            priorities.insert(0, {
                'priority': 1,
                'area': 'Performance Recovery',
                'recommendation': 'Immediate investigation and corrective action required',
                'impact': 'Critical',
                'effort': 'High',
                'urgency': 'Immediate',
                'performance_decline': f"{abs(performance_change):.1f}%",
                'business_rationale': 'Prevent further campaign deterioration and revenue loss'
            })
        elif trend_assessment == 'significantly_improved':
            priorities.insert(0, {
                'priority': 1,
                'area': 'Momentum Capitalization',
                'recommendation': 'Scale successful strategies while momentum is strong',
                'impact': 'High',
                'effort': 'Low',
                'opportunity_window': 'Active',
                'performance_improvement': f"{performance_change:.1f}%",
                'business_rationale': 'Maximize ROI during peak performance period'
            })
        
        # Cost efficiency opportunities
        cost_efficiency_score = efficiency_metrics.get('cost_efficiency_score', 50)
        if cost_efficiency_score < 40:
            priorities.append({
                'priority': 3,
                'area': 'Cost Efficiency Improvement',
                'recommendation': 'Review CPM and negotiate better rates with underperforming stations',
                'impact': 'Medium',
                'effort': 'Medium',
                'cost_efficiency_score': cost_efficiency_score,
                'business_rationale': 'Improve campaign ROI through cost optimization'
            })
        
        return priorities[:3]  # Top 3 priorities to maintain focus
    
    def _generate_station_recommendation(self, station_name: str, opportunity_type: str, 
                                       trend_direction: str, efficiency_score: float, 
                                       volume_score: float, recent_efficiency: float, 
                                       overall_efficiency: float) -> Dict[str, Any]:
        """Generate detailed station recommendation with specific actions"""
        
        # Determine action type and priority based on multiple factors
        action_type, metric_type = self.utils.standardize_opportunity_type(opportunity_type)
        
        # Generate specific recommendation text
        if opportunity_type == 'Scale Winner' and trend_direction != 'declining':
            recommendation = f"Immediately increase {station_name} budget allocation - proven high-volume performer"
            expected_impact = f"Scale reliable performance: {recent_efficiency:.1f} recent efficiency"
            priority = 1
        elif opportunity_type == 'Hidden Gem' and trend_direction == 'improving':
            recommendation = f"Test scaling {station_name} - strong efficiency with growth potential"
            expected_impact = f"Capitalize on improving trend: {recent_efficiency:.1f} vs {overall_efficiency:.1f} baseline"
            priority = 1
        elif opportunity_type == 'Rising Star':
            recommendation = f"Monitor {station_name} closely and prepare to scale - building momentum"
            expected_impact = f"Track {trend_direction} trend: {recent_efficiency:.1f} current efficiency"
            priority = 2
        elif opportunity_type == 'Optimize or Reduce':
            if trend_direction == 'improving':
                recommendation = f"Give {station_name} probationary period - recent improvement detected"
                expected_impact = f"Monitor turnaround: {recent_efficiency:.1f} recent vs {overall_efficiency:.1f} overall"
                priority = 3
            else:
                recommendation = f"Reduce {station_name} allocation - consistently underperforming"
                expected_impact = f"Redirect budget from poor performer: {overall_efficiency:.1f} efficiency"
                priority = 1
        else:
            recommendation = f"Continue monitoring {station_name} performance trends"
            expected_impact = f"Maintain current allocation: {recent_efficiency:.1f} efficiency"
            priority = 3
        
        return {
            'recommendation': recommendation,
            'expected_impact': expected_impact,
            'action_type': action_type,
            'metric_type': metric_type,
            'priority': priority,
            'efficiency_advantage': recent_efficiency - overall_efficiency if recent_efficiency > overall_efficiency else 0
        }
    
    def _generate_daypart_recommendation(self, daypart_name: str, recommendation_priority: str,
                                       trend_direction: str, efficiency_index: float,
                                       volume_adequacy: str, recent_efficiency: float) -> Dict[str, Any]:
        """Generate detailed daypart recommendation with scheduling actions"""
        
        # Determine specific action based on priority and trends
        if 'Scale Up' in recommendation_priority and trend_direction != 'declining':
            recommendation = f"Increase {daypart_name} inventory immediately - top efficiency window"
            action_type = AnalysisConstants.ACTION_TYPES['SCALE_IMMEDIATELY']
            priority = 1
        elif 'Scale Up' in recommendation_priority and trend_direction == 'declining':
            recommendation = f"Investigate {daypart_name} efficiency decline before scaling"
            action_type = 'investigate_daypart_decline'
            priority = 1
        elif 'Test Scale' in recommendation_priority and trend_direction == 'improving':
            recommendation = f"Test increased {daypart_name} investment - efficiency improving"
            action_type = AnalysisConstants.ACTION_TYPES['TEST_SCALING']
            priority = 2
        elif 'Investigate' in recommendation_priority:
            recommendation = f"Analyze {daypart_name} performance drop and optimize creative/targeting"
            action_type = 'investigate_and_optimize'
            priority = 1
        else:
            recommendation = f"Monitor {daypart_name} performance and maintain current allocation"
            action_type = AnalysisConstants.ACTION_TYPES['MONITOR']
            priority = 3
        
        # Determine metric type based on efficiency
        if efficiency_index >= 1.3:
            metric_type = AnalysisConstants.METRIC_TYPES['PRIME_TIME_EFFICIENCY']
        elif efficiency_index >= 1.1:
            metric_type = AnalysisConstants.METRIC_TYPES['STRONG_EFFICIENCY']
        else:
            metric_type = AnalysisConstants.METRIC_TYPES['AVERAGE_EFFICIENCY']
        
        return {
            'recommendation': recommendation,
            'expected_impact': f"Daypart efficiency: {recent_efficiency:.1f} visits/spot ({efficiency_index:.1f}x average)",
            'action_type': action_type,
            'metric_type': metric_type,
            'priority': priority,
            'scheduling_advantage': efficiency_index - 1.0,
            'volume_assessment': volume_adequacy
        }
    
    def _generate_combination_recommendation(self, station: str, daypart: str, combo_tier: str,
                                           scaling_priority: str, synergy_score: float,
                                           confidence_level: str, investment_recommendation: str) -> Dict[str, Any]:
        """Generate detailed combination recommendation with investment guidance"""
        
        combination_name = f"{station} + {daypart}"
        
        # Generate specific recommendation based on tier and confidence
        if combo_tier == 'Golden Combination' and confidence_level == 'High':
            recommendation = f"Scale {combination_name} aggressively - proven golden combination"
            action_type = AnalysisConstants.ACTION_TYPES['SCALE_IMMEDIATELY']
            metric_type = AnalysisConstants.METRIC_TYPES['GOLDEN_COMBINATION']
            priority = 1
        elif combo_tier == 'Strong Combination' and confidence_level in ['High', 'Medium']:
            recommendation = f"Increase investment in {combination_name} - strong synergy detected"
            action_type = AnalysisConstants.ACTION_TYPES['TEST_SCALING']
            metric_type = AnalysisConstants.METRIC_TYPES['STRONG_COMBINATION']
            priority = 2
        elif combo_tier == 'Golden Combination' and confidence_level == 'Low':
            recommendation = f"Test {combination_name} with larger sample - promising early results"
            action_type = AnalysisConstants.ACTION_TYPES['TEST_SCALING']
            metric_type = AnalysisConstants.METRIC_TYPES['GOLDEN_COMBINATION']
            priority = 2
        else:
            recommendation = f"Monitor {combination_name} performance and optimize as needed"
            action_type = AnalysisConstants.ACTION_TYPES['MONITOR']
            metric_type = 'standard_combination'
            priority = 3
        
        return {
            'recommendation': recommendation,
            'expected_impact': f"Combination synergy: {synergy_score:.1f}x baseline performance",
            'action_type': action_type,
            'metric_type': metric_type,
            'priority': priority,
            'investment_guidance': investment_recommendation,
            'synergy_advantage': synergy_score - 1.0 if synergy_score > 1.0 else 0
        }


# Test the insight generators module
if __name__ == "__main__":
    print("🧪 Testing Insight Generators Module...")
    
    try:
        # Create sample context data
        sample_context = {
            'client_name': 'TEST_CLIENT',
            'primary_product': 'TEST_PRODUCT',
            'campaign_overview': {
                'total_spots': 750,
                'total_visits': 1875,
                'total_revenue': 93750,
                'attribution_coverage': 85.0,
                'data_quality_score': 90.0
            },
            'efficiency_metrics': {
                'visits_per_spot': 2.5,
                'cost_efficiency_score': 75.0
            },
            'station_performance': [
                {
                    'station': 'TOP_STATION', 'avg_visits_per_spot': 4.2, 'total_visits': 840,
                    'spots': 200, 'opportunity_type': 'Scale Winner', 'trend_direction': 'improving',
                    'efficiency_score': 1.8, 'volume_score': 0.9, 'recent_efficiency': 4.5
                },
                {
                    'station': 'RISING_STATION', 'avg_visits_per_spot': 2.8, 'total_visits': 280,
                    'spots': 100, 'opportunity_type': 'Rising Star', 'trend_direction': 'improving',
                    'efficiency_score': 1.2, 'volume_score': 0.3, 'recent_efficiency': 3.2
                }
            ],
            'daypart_performance': [
                {
                    'daypart': 'PRIME', 'avg_visits_per_spot': 3.8, 'total_visits': 760,
                    'spots': 200, 'efficiency_rating': 'Excellent', 'recommendation_priority': 'High - Scale Up',
                    'trend_direction': 'stable', 'efficiency_index': 1.4, 'volume_adequacy': 'High'
                }
            ],
            'combination_performance': [
                {
                    'station': 'TOP_STATION', 'daypart': 'PRIME', 'avg_visits_per_spot': 5.2,
                    'total_visits': 520, 'spots': 100, 'combo_tier': 'Golden Combination',
                    'scaling_priority': 'Immediate', 'synergy_score': 1.6, 'confidence_level': 'High'
                }
            ],
            'trend_analysis': {
                'trend_assessment': 'improved',
                'performance_change_pct': 15.2
            }
        }
        
        # Test insight generators
        generators = InsightGenerators()
        
        # Test station insights
        station_insights = generators.generate_station_insights(sample_context)
        print(f"✅ Station insights generated: {len(station_insights)} insights")
        if station_insights:
            top_insight = station_insights[0]
            print(f"✅ Top station insight: {top_insight['station']} - {top_insight['recommendation']}")
        
        # Test daypart insights
        daypart_insights = generators.generate_daypart_insights(sample_context)
        print(f"✅ Daypart insights generated: {len(daypart_insights)} insights")
        if daypart_insights:
            print(f"✅ Daypart insight: {daypart_insights[0]['daypart']} - {daypart_insights[0]['recommendation']}")
        
        # Test combination insights
        combo_insights = generators.generate_combination_insights(sample_context)
        print(f"✅ Combination insights generated: {len(combo_insights)} insights")
        if combo_insights:
            print(f"✅ Combo insight: {combo_insights[0]['combination']} - {combo_insights[0]['recommendation']}")
        
        # Test executive findings
        executive_findings = generators.generate_executive_findings(sample_context)
        print(f"✅ Executive findings generated: {len(executive_findings)} findings")
        if executive_findings:
            print(f"✅ Top finding: {executive_findings[0][:100]}...")
        
        # Test optimization priorities
        optimization_priorities = generators.generate_optimization_priorities(sample_context)
        print(f"✅ Optimization priorities generated: {len(optimization_priorities)} priorities")
        if optimization_priorities:
            print(f"✅ Top priority: {optimization_priorities[0]['area']} - {optimization_priorities[0]['recommendation'][:50]}...")
        
        print("✅ Insight Generators module test completed successfully!")
        
    except Exception as e:
        print(f"❌ Insight Generators module test failed: {e}")
        import traceback
        traceback.print_exc()