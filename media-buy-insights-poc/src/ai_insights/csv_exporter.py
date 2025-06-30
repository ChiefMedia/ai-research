"""
AI Insights - CSV Exporter Module
Handles comprehensive CSV export functionality for Power BI consumption
"""

import os
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional
from .config import AnalysisConstants, UtilityFunctions

class CSVExporter:
    """Exports insights and performance data to CSV files for Power BI dashboards"""
    
    def __init__(self, output_dir: str = "output/reports"):
        """Initialize CSV exporter with output directory"""
        self.output_dir = output_dir
        self.utils = UtilityFunctions()
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export_comprehensive_insights(self, insights: Dict[str, Any], filename: str = None) -> str:
        """Export comprehensive insights as CSV for Power BI consumption"""
        
        if filename is None:
            client_name = insights['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_insights_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        
        try:
            insights_data = []
            generation_date = insights['metadata']['generation_date'][:10]
            client_name = insights['metadata']['client_name']
            
            # Executive findings with enhanced metadata
            insights_data.extend(self._process_executive_findings(insights, generation_date))
            
            # Station insights with performance context
            insights_data.extend(self._process_station_insights(insights, generation_date))
            
            # Daypart insights with scheduling context
            insights_data.extend(self._process_daypart_insights(insights, generation_date))
            
            # Combination insights with synergy analysis
            insights_data.extend(self._process_combination_insights(insights, generation_date))
            
            # Performance quadrant insights
            insights_data.extend(self._process_quadrant_insights(insights, generation_date))
            
            # Opportunity matrix insights
            insights_data.extend(self._process_opportunity_matrix(insights, generation_date))
            
            # Optimization priorities
            insights_data.extend(self._process_optimization_priorities(insights, generation_date))
            
            # Weekly trend insights
            insights_data.extend(self._process_weekly_trends(insights, generation_date))
            
            # Write comprehensive CSV
            if not insights_data:
                raise ValueError("No insights data available for CSV export")
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=AnalysisConstants.CSV_FIELDNAMES)
                writer.writeheader()
                writer.writerows(insights_data)
            
            print(f"📊 Comprehensive insights CSV saved: {filepath}")
            return filepath
                
        except Exception as e:
            print(f"❌ Error saving comprehensive insights CSV: {e}")
            return ""
    
    def export_station_performance(self, context: Dict[str, Any], insights: Dict[str, Any], filename: str = None) -> str:
        """Export detailed station performance data for Power BI station analysis"""
        
        if filename is None:
            client_name = insights['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_stations_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        
        try:
            station_data = context.get('station_performance', [])
            station_insights = insights.get('station_insights', [])
            
            # Create lookup for insights by station
            insights_lookup = {insight.get('station'): insight for insight in station_insights}
            
            station_export_data = []
            generation_date = insights['metadata']['generation_date'][:10]
            client_name = insights['metadata']['client_name']
            
            for station in station_data:
                station_name = station.get('station', 'Unknown')
                insight = insights_lookup.get(station_name, {})
                
                station_record = {
                    'client': client_name,
                    'station': station_name,
                    'product': station.get('product', context.get('primary_product', 'DEFAULT')),
                    'total_visits': station.get('total_visits', 0),
                    'total_spots': station.get('spots', 0),
                    'avg_visits_per_spot': station.get('avg_visits_per_spot', 0),
                    'total_cost': station.get('total_cost', 0),
                    'cpm': station.get('cpm', 0),
                    'efficiency_score': station.get('efficiency_score', 1.0),
                    'volume_score': station.get('volume_score', 1.0),
                    'strategic_value': station.get('strategic_value', 0),
                    'performance_tier': insight.get('performance_tier', station.get('performance_tier', 'Unknown')),
                    'opportunity_type': insight.get('opportunity_type', station.get('opportunity_type', 'Monitor')),
                    'trend_direction': station.get('trend_direction', 'stable'),
                    'recent_efficiency': station.get('recent_efficiency', station.get('avg_visits_per_spot', 0)),
                    'weeks_analyzed': station.get('weeks_analyzed', 0),
                    'ai_recommendation': insight.get('recommendation', ''),
                    'expected_impact': insight.get('expected_impact', ''),
                    'confidence': insight.get('confidence', station.get('confidence', 'Medium')),
                    'action_type': insight.get('action_type', 'monitor'),
                    'priority': insight.get('priority', 999),
                    'risk_level': station.get('risk_level', 'Medium'),
                    'generated_date': generation_date
                }
                
                station_export_data.append(station_record)
            
            # Define station-specific fieldnames
            station_fieldnames = [
                'client', 'station', 'product', 'total_visits', 'total_spots', 'avg_visits_per_spot', 
                'total_cost', 'cpm', 'efficiency_score', 'volume_score', 'strategic_value',
                'performance_tier', 'opportunity_type', 'trend_direction', 'recent_efficiency', 
                'weeks_analyzed', 'ai_recommendation', 'expected_impact', 'confidence', 
                'action_type', 'priority', 'risk_level', 'generated_date'
            ]
            
            if not station_export_data:
                raise ValueError("No station performance data available for CSV export")
            
            # Define station-specific fieldnames
            station_fieldnames = [
                'client', 'station', 'product', 'total_visits', 'total_spots', 'avg_visits_per_spot', 
                'total_cost', 'cpm', 'efficiency_score', 'volume_score', 'strategic_value',
                'performance_tier', 'opportunity_type', 'trend_direction', 'recent_efficiency', 
                'weeks_analyzed', 'ai_recommendation', 'expected_impact', 'confidence', 
                'action_type', 'priority', 'risk_level', 'generated_date'
            ]
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=station_fieldnames)
                writer.writeheader()
                writer.writerows(station_export_data)
            
            print(f"📺 Station performance CSV saved: {filepath}")
            return filepath
                
        except Exception as e:
            print(f"❌ Error saving station performance CSV: {e}")
            return ""
    
    def export_daypart_performance(self, context: Dict[str, Any], insights: Dict[str, Any], filename: str = None) -> str:
        """Export detailed daypart performance data for Power BI scheduling analysis"""
        
        if filename is None:
            client_name = insights['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_dayparts_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        
        try:
            daypart_data = context.get('daypart_performance', [])
            daypart_insights = insights.get('daypart_insights', [])
            
            # Create lookup for insights by daypart
            insights_lookup = {insight.get('daypart'): insight for insight in daypart_insights}
            
            daypart_export_data = []
            generation_date = insights['metadata']['generation_date'][:10]
            client_name = insights['metadata']['client_name']
            
            for daypart in daypart_data:
                daypart_name = daypart.get('daypart', 'Unknown')
                insight = insights_lookup.get(daypart_name, {})
                
                daypart_record = {
                    'client': client_name,
                    'daypart': daypart_name,
                    'product': daypart.get('product', context.get('primary_product', 'DEFAULT')),
                    'total_visits': daypart.get('total_visits', 0),
                    'total_spots': daypart.get('spots', 0),
                    'avg_visits_per_spot': daypart.get('avg_visits_per_spot', 0),
                    'total_cost': daypart.get('total_cost', 0),
                    'cpm': daypart.get('cpm', 0),
                    'efficiency_index': daypart.get('efficiency_index', 1.0),
                    'volume_adequacy': daypart.get('volume_adequacy', 'Medium'),
                    'efficiency_rating': insight.get('efficiency_rating', daypart.get('efficiency_rating', 'Unknown')),
                    'recommendation_priority': insight.get('recommendation_priority', daypart.get('recommendation_priority', 'Low')),
                    'trend_direction': daypart.get('trend_direction', 'stable'),
                    'recent_efficiency': daypart.get('recent_efficiency', daypart.get('avg_visits_per_spot', 0)),
                    'weeks_analyzed': daypart.get('weeks_analyzed', 0),
                    'ai_recommendation': insight.get('recommendation', ''),
                    'expected_impact': insight.get('expected_impact', ''),
                    'scheduling_advantage': insight.get('scheduling_advantage', 0),
                    'confidence': insight.get('confidence', daypart.get('confidence', 'Medium')),
                    'action_type': insight.get('action_type', 'monitor'),
                    'priority': insight.get('priority', 999),
                    'generated_date': generation_date
                }
                
                daypart_export_data.append(daypart_record)
            
            # Define daypart-specific fieldnames
            daypart_fieldnames = [
                'client', 'daypart', 'product', 'total_visits', 'total_spots', 'avg_visits_per_spot', 
                'total_cost', 'cpm', 'efficiency_index', 'volume_adequacy', 'efficiency_rating', 
                'recommendation_priority', 'trend_direction', 'recent_efficiency', 'weeks_analyzed',
                'ai_recommendation', 'expected_impact', 'scheduling_advantage', 'confidence', 
                'action_type', 'priority', 'generated_date'
            ]
            
            if not daypart_export_data:
                raise ValueError("No daypart performance data available for CSV export")
            
            # Define daypart-specific fieldnames
            daypart_fieldnames = [
                'client', 'daypart', 'product', 'total_visits', 'total_spots', 'avg_visits_per_spot', 
                'total_cost', 'cpm', 'efficiency_index', 'volume_adequacy', 'efficiency_rating', 
                'recommendation_priority', 'trend_direction', 'recent_efficiency', 'weeks_analyzed',
                'ai_recommendation', 'expected_impact', 'scheduling_advantage', 'confidence', 
                'action_type', 'priority', 'generated_date'
            ]
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=daypart_fieldnames)
                writer.writeheader()
                writer.writerows(daypart_export_data)
            
            print(f"⏰ Daypart performance CSV saved: {filepath}")
            return filepath
                
        except Exception as e:
            print(f"❌ Error saving daypart performance CSV: {e}")
            return ""
    
    def export_opportunity_matrix(self, insights: Dict[str, Any], filename: str = None) -> str:
        """Export opportunity matrix for Power BI opportunity analysis"""
        
        if filename is None:
            client_name = insights['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_opportunities_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        
        try:
            opportunities = insights.get('opportunity_matrix', [])
            
            if not opportunities:
                raise ValueError("No opportunity matrix data available for CSV export")
            
            opportunity_export_data = []
            generation_date = insights['metadata']['generation_date'][:10]
            client_name = insights['metadata']['client_name']
            
            for opportunity in opportunities:
                opportunity_record = {
                    'client': client_name,
                    'opportunity_id': opportunity.get('opportunity_id', 0),
                    'opportunity_type': opportunity.get('opportunity_type', 'unknown'),
                    'from_station': opportunity.get('from_station', ''),
                    'to_station': opportunity.get('to_station', ''),
                    'from_daypart': opportunity.get('from_daypart', ''),
                    'to_daypart': opportunity.get('to_daypart', ''),
                    'efficiency_gain': opportunity.get('efficiency_gain', 0),
                    'efficiency_gap': opportunity.get('efficiency_gap', 0),
                    'potential_spots_to_move': opportunity.get('potential_spots_to_move', 0),
                    'projected_visit_gain': opportunity.get('projected_visit_gain', 0),
                    'current_visits_from_spots': opportunity.get('current_visits_from_spots', 0),
                    'projected_visits_from_spots': opportunity.get('projected_visits_from_spots', 0),
                    'confidence': opportunity.get('confidence', 'Medium'),
                    'priority': opportunity.get('priority', 999),
                    'implementation_complexity': opportunity.get('implementation_complexity', 'Medium'),
                    'timeline': opportunity.get('timeline', 'TBD'),
                    'business_rationale': opportunity.get('business_rationale', ''),
                    'recommended_action': opportunity.get('recommended_action', ''),
                    'momentum_advantage': opportunity.get('momentum_advantage', 0),
                    'projected_improvement': opportunity.get('projected_improvement', ''),
                    'generated_date': generation_date
                }
                
                opportunity_export_data.append(opportunity_record)
            
            # Define opportunity-specific fieldnames
            opportunity_fieldnames = [
                'client', 'opportunity_id', 'opportunity_type', 'from_station', 'to_station', 
                'from_daypart', 'to_daypart', 'efficiency_gain', 'efficiency_gap', 
                'potential_spots_to_move', 'projected_visit_gain', 'current_visits_from_spots',
                'projected_visits_from_spots', 'confidence', 'priority', 'implementation_complexity',
                'timeline', 'business_rationale', 'recommended_action', 'momentum_advantage',
                'projected_improvement', 'generated_date'
            ]
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=opportunity_fieldnames)
                writer.writeheader()
                writer.writerows(opportunity_export_data)
            
            print(f"💡 Opportunity matrix CSV saved: {filepath}")
            return filepath
                
        except Exception as e:
            print(f"❌ Error saving opportunity matrix CSV: {e}")
            return ""
    
    def export_performance_quadrants(self, insights: Dict[str, Any], filename: str = None) -> str:
        """Export performance quadrants for Power BI portfolio analysis"""
        
        if filename is None:
            client_name = insights['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_quadrants_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.csv")
        
        try:
            quadrants = insights.get('performance_quadrants', {})
            
            if not quadrants:
                raise ValueError("No performance quadrants data available for CSV export")
            
            quadrant_export_data = []
            generation_date = insights['metadata']['generation_date'][:10]
            client_name = insights['metadata']['client_name']
            
            # Process each quadrant
            quadrant_labels = {
                'high_volume_high_efficiency': 'Champions',
                'low_volume_high_efficiency': 'Hidden Gems',
                'high_volume_low_efficiency': 'Inefficient Giants',
                'low_volume_low_efficiency': 'Underperformers'
            }
            
            for quadrant_key, stations in quadrants.items():
                quadrant_label = quadrant_labels.get(quadrant_key, quadrant_key)
                
                for station in stations:
                    quadrant_record = {
                        'client': client_name,
                        'station': station.get('station', 'Unknown'),
                        'quadrant_key': quadrant_key,
                        'quadrant_label': quadrant_label,
                        'volume': station.get('volume', 0),
                        'efficiency': station.get('efficiency', 0),
                        'spots': station.get('spots', 0),
                        'trend_direction': station.get('trend_direction', 'stable'),
                        'efficiency_score': station.get('efficiency_score', 1.0),
                        'volume_score': station.get('volume_score', 1.0),
                        'strategic_value': station.get('strategic_value', 0),
                        'action': station.get('action', 'Monitor'),
                        'investment_priority': station.get('investment_priority', 'Medium'),
                        'risk_level': station.get('risk_level', 'Medium'),
                        'confidence': station.get('confidence', 'Medium'),
                        'generated_date': generation_date
                    }
                    
                    quadrant_export_data.append(quadrant_record)
            
            # Define quadrant-specific fieldnames
            quadrant_fieldnames = [
                'client', 'station', 'quadrant_key', 'quadrant_label', 'volume', 'efficiency', 
                'spots', 'trend_direction', 'efficiency_score', 'volume_score', 'strategic_value',
                'action', 'investment_priority', 'risk_level', 'confidence', 'generated_date'
            ]
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=quadrant_fieldnames)
                writer.writeheader()
                writer.writerows(quadrant_export_data)
            
            print(f"📊 Performance quadrants CSV saved: {filepath}")
            return filepath
                
        except Exception as e:
            print(f"❌ Error saving performance quadrants CSV: {e}")
            return ""
    
    def _process_executive_findings(self, insights: Dict[str, Any], generation_date: str) -> List[Dict]:
        """Process executive findings for CSV export"""
        
        findings_data = []
        key_findings = insights.get('key_findings', [])
        trend_analysis = insights.get('recent_vs_historical', {})
        trend_assessment = trend_analysis.get('trend_assessment', 'stable')
        client_name = insights['metadata']['client_name']
        
        for i, finding in enumerate(key_findings, 1):
            is_trend_finding = self.utils.is_trend_finding(finding)
            
            finding_record = {
                'client': client_name,
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
                'generated_date': generation_date
            }
            
            findings_data.append(finding_record)
        
        return findings_data
    
    def _process_station_insights(self, insights: Dict[str, Any], generation_date: str) -> List[Dict]:
        """Process station insights for CSV export"""
        
        station_data = []
        station_insights = insights.get('station_insights', [])
        client_name = insights['metadata']['client_name']
        
        for insight in station_insights:
            opportunity_type = insight.get('opportunity_type', 'Monitor')
            trend_direction = insight.get('trend_direction', 'stable')
            
            # Standardize action and metric types
            action_required, metric_type = self.utils.standardize_opportunity_type(opportunity_type)
            
            station_record = {
                'client': client_name,
                'insight_category': AnalysisConstants.INSIGHT_CATEGORIES['STATION_ANALYSIS'],
                'insight_type': 'station_optimization',
                'priority': insight.get('priority', 999),
                'impact_level': 'High' if insight.get('priority', 999) <= 2 else 'Medium',
                'station': insight.get('station'),
                'daypart': None,
                'metric_type': metric_type,
                'finding_description': self._create_station_finding_description(insight),
                'recommendation': insight.get('recommendation', ''),
                'action_required': action_required,
                'confidence': insight.get('confidence', 'Medium'),
                'trend_context': trend_direction,
                'time_based': 'yes' if trend_direction != 'stable' else 'no',
                'generated_date': generation_date
            }
            
            station_data.append(station_record)
        
        return station_data
    
    def _process_daypart_insights(self, insights: Dict[str, Any], generation_date: str) -> List[Dict]:
        """Process daypart insights for CSV export"""
        
        daypart_data = []
        daypart_insights = insights.get('daypart_insights', [])
        client_name = insights['metadata']['client_name']
        
        for insight in daypart_insights:
            recommendation_priority = insight.get('recommendation_priority', 'Low')
            trend_direction = insight.get('trend_direction', 'stable')
            
            # Determine action type based on priority
            if 'Scale Up' in recommendation_priority:
                action_required = AnalysisConstants.ACTION_TYPES['SCALE_IMMEDIATELY']
                metric_type = AnalysisConstants.METRIC_TYPES['PRIME_TIME_EFFICIENCY']
            elif 'Test Scale' in recommendation_priority:
                action_required = AnalysisConstants.ACTION_TYPES['TEST_SCALING']
                metric_type = AnalysisConstants.METRIC_TYPES['STRONG_EFFICIENCY']
            else:
                action_required = AnalysisConstants.ACTION_TYPES['MONITOR']
                metric_type = AnalysisConstants.METRIC_TYPES['AVERAGE_EFFICIENCY']
            
            daypart_record = {
                'client': client_name,
                'insight_category': AnalysisConstants.INSIGHT_CATEGORIES['DAYPART_ANALYSIS'],
                'insight_type': 'daypart_optimization',
                'priority': insight.get('priority', 999),
                'impact_level': 'High' if 'Scale Up' in recommendation_priority else 'Medium',
                'station': None,
                'daypart': insight.get('daypart'),
                'metric_type': metric_type,
                'finding_description': self._create_daypart_finding_description(insight),
                'recommendation': insight.get('recommendation', ''),
                'action_required': action_required,
                'confidence': insight.get('confidence', 'Medium'),
                'trend_context': trend_direction,
                'time_based': 'yes' if trend_direction != 'stable' else 'no',
                'generated_date': generation_date
            }
            
            daypart_data.append(daypart_record)
        
        return daypart_data
    
    def _process_combination_insights(self, insights: Dict[str, Any], generation_date: str) -> List[Dict]:
        """Process combination insights for CSV export"""
        
        combination_data = []
        combination_insights = insights.get('station_daypart_insights', [])
        client_name = insights['metadata']['client_name']
        
        for insight in combination_insights:
            combo_tier = insight.get('combo_tier', 'Standard')
            
            # Determine action and metric type based on tier
            if combo_tier == 'Golden Combination':
                action_required = AnalysisConstants.ACTION_TYPES['SCALE_IMMEDIATELY']
                metric_type = AnalysisConstants.METRIC_TYPES['GOLDEN_COMBINATION']
            elif combo_tier == 'Strong Combination':
                action_required = AnalysisConstants.ACTION_TYPES['TEST_SCALING']
                metric_type = AnalysisConstants.METRIC_TYPES['STRONG_COMBINATION']
            else:
                action_required = AnalysisConstants.ACTION_TYPES['MONITOR']
                metric_type = 'standard_combination'
            
            combination_record = {
                'client': client_name,
                'insight_category': AnalysisConstants.INSIGHT_CATEGORIES['COMBINATION_ANALYSIS'],
                'insight_type': 'combination_optimization',
                'priority': insight.get('priority', 999),
                'impact_level': 'High' if combo_tier in ['Golden Combination', 'Strong Combination'] else 'Medium',
                'station': insight.get('station'),
                'daypart': insight.get('daypart'),
                'metric_type': metric_type,
                'finding_description': self._create_combination_finding_description(insight),
                'recommendation': insight.get('recommendation', ''),
                'action_required': action_required,
                'confidence': insight.get('confidence', 'Medium'),
                'trend_context': 'combination_synergy',
                'time_based': 'no',
                'generated_date': generation_date
            }
            
            combination_data.append(combination_record)
        
        return combination_data
    
    def _process_quadrant_insights(self, insights: Dict[str, Any], generation_date: str) -> List[Dict]:
        """Process performance quadrant insights for CSV export"""
        
        quadrant_data = []
        quadrants = insights.get('performance_quadrants', {})
        client_name = insights['metadata']['client_name']
        
        quadrant_actions = {
            'high_volume_high_efficiency': AnalysisConstants.ACTION_TYPES['SCALE_IMMEDIATELY'],
            'low_volume_high_efficiency': AnalysisConstants.ACTION_TYPES['TEST_SCALING'],
            'high_volume_low_efficiency': AnalysisConstants.ACTION_TYPES['OPTIMIZE_OR_REDUCE'],
            'low_volume_low_efficiency': AnalysisConstants.ACTION_TYPES['OPTIMIZE_OR_REDUCE']
        }
        
        for quadrant_key, stations in quadrants.items():
            action_required = quadrant_actions.get(quadrant_key, AnalysisConstants.ACTION_TYPES['MONITOR'])
            
            for station in stations[:3]:  # Top 3 per quadrant for CSV
                quadrant_record = {
                    'client': client_name,
                    'insight_category': 'quadrant_analysis',
                    'insight_type': 'portfolio_optimization',
                    'priority': 1 if quadrant_key == 'high_volume_high_efficiency' else 2 if quadrant_key == 'low_volume_high_efficiency' else 3,
                    'impact_level': 'High' if quadrant_key in ['high_volume_high_efficiency', 'low_volume_high_efficiency'] else 'Medium',
                    'station': station.get('station'),
                    'daypart': None,
                    'metric_type': quadrant_key,
                    'finding_description': f"{station.get('station')} in {station.get('quadrant', 'Unknown')} quadrant: {station.get('action', 'Monitor')}",
                    'recommendation': station.get('action', 'Monitor'),
                    'action_required': action_required,
                    'confidence': station.get('confidence', 'Medium'),
                    'trend_context': station.get('trend_direction', 'stable'),
                    'time_based': 'yes' if station.get('trend_direction') != 'stable' else 'no',
                    'generated_date': generation_date
                }
                
                quadrant_data.append(quadrant_record)
        
        return quadrant_data
    
    def _process_opportunity_matrix(self, insights: Dict[str, Any], generation_date: str) -> List[Dict]:
        """Process opportunity matrix for CSV export"""
        
        opportunity_data = []
        opportunities = insights.get('opportunity_matrix', [])
        client_name = insights['metadata']['client_name']
        
        for opportunity in opportunities[:5]:  # Top 5 opportunities
            opportunity_record = {
                'client': client_name,
                'insight_category': AnalysisConstants.INSIGHT_CATEGORIES['BUDGET_OPPORTUNITY'],
                'insight_type': 'budget_reallocation',
                'priority': opportunity.get('priority', 999),
                'impact_level': 'High' if opportunity.get('priority', 999) <= 2 else 'Medium',
                'station': opportunity.get('to_station', ''),
                'daypart': opportunity.get('to_daypart', ''),
                'metric_type': AnalysisConstants.METRIC_TYPES['BUDGET_REALLOCATION'],
                'finding_description': self._create_opportunity_finding_description(opportunity),
                'recommendation': opportunity.get('business_rationale', ''),
                'action_required': AnalysisConstants.ACTION_TYPES['REALLOCATE_BUDGET'],
                'confidence': opportunity.get('confidence', 'Medium'),
                'trend_context': opportunity.get('opportunity_type', 'reallocation'),
                'time_based': 'yes' if 'trend' in opportunity.get('opportunity_type', '') else 'no',
                'generated_date': generation_date
            }
            
            opportunity_data.append(opportunity_record)
        
        return opportunity_data
    
    def _process_optimization_priorities(self, insights: Dict[str, Any], generation_date: str) -> List[Dict]:
        """Process optimization priorities for CSV export"""
        
        priority_data = []
        priorities = insights.get('optimization_priorities', [])
        client_name = insights['metadata']['client_name']
        
        for priority in priorities:
            priority_record = {
                'client': client_name,
                'insight_category': AnalysisConstants.INSIGHT_CATEGORIES['KEY_OPTIMIZATION'],
                'insight_type': 'optimization_priority',
                'priority': priority.get('priority', 999),
                'impact_level': priority.get('impact', 'Medium'),
                'station': None,
                'daypart': None,
                'metric_type': 'optimization_opportunity',
                'finding_description': f"{priority.get('area', 'Unknown')}: {priority.get('recommendation', '')}",
                'recommendation': priority.get('recommendation', ''),
                'action_required': 'implement_optimization',
                'confidence': 'High',
                'trend_context': priority.get('area', 'optimization'),
                'time_based': 'yes' if 'trend' in priority.get('area', '').lower() else 'no',
                'generated_date': generation_date
            }
            
            priority_data.append(priority_record)
        
        return priority_data
    
    def _process_weekly_trends(self, insights: Dict[str, Any], generation_date: str) -> List[Dict]:
        """Process weekly trend insights for CSV export"""
        
        trend_data = []
        latest_week = insights.get('latest_week_insights', {})
        weekly_insights = latest_week.get('insights', [])
        client_name = insights['metadata']['client_name']
        
        for i, insight in enumerate(weekly_insights, 1):
            trend_record = {
                'client': client_name,
                'insight_category': 'weekly_trend',
                'insight_type': 'trend_analysis',
                'priority': len(insights.get('key_findings', [])) + i,
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
                'generated_date': generation_date
            }
            
            trend_data.append(trend_record)
        
        return trend_data
    
    def _create_station_finding_description(self, insight: Dict[str, Any]) -> str:
        """Create descriptive finding text for station insights"""
        
        station = insight.get('station', 'Unknown')
        trend_direction = insight.get('trend_direction', 'stable')
        recent_efficiency = insight.get('recent_efficiency', 0)
        overall_efficiency = insight.get('visit_rate', 0)
        
        if trend_direction == 'improving':
            return f"{station} shows {trend_direction} trend: {recent_efficiency:.1f} recent vs {overall_efficiency:.1f} overall efficiency"
        elif trend_direction == 'declining':
            return f"{station} performance declining: {recent_efficiency:.1f} recent vs {overall_efficiency:.1f} baseline"
        else:
            return f"{station} maintains {overall_efficiency:.1f} visits per spot consistently"
    
    def _create_daypart_finding_description(self, insight: Dict[str, Any]) -> str:
        """Create descriptive finding text for daypart insights"""
        
        daypart = insight.get('daypart', 'Unknown')
        efficiency_rating = insight.get('efficiency_rating', 'Unknown')
        visit_rate = insight.get('visit_rate', 0)
        trend_direction = insight.get('trend_direction', 'stable')
        
        if 'Trending' in efficiency_rating:
            return f"{daypart} daypart {efficiency_rating.lower()}: {visit_rate:.1f} visits per spot"
        else:
            return f"{daypart} daypart {trend_direction} performance: {visit_rate:.1f} visits per spot"
    
    def _create_combination_finding_description(self, insight: Dict[str, Any]) -> str:
        """Create descriptive finding text for combination insights"""
        
        combination = insight.get('combination', 'Unknown')
        combo_tier = insight.get('combo_tier', 'Standard')
        synergy_score = insight.get('synergy_score', 1.0)
        visit_rate = insight.get('visit_rate', 0)
        
        return f"{combination} achieves {combo_tier} status: {visit_rate:.1f} visits per spot with {synergy_score:.1f}x synergy"
    
    def _create_opportunity_finding_description(self, opportunity: Dict[str, Any]) -> str:
        """Create descriptive finding text for opportunity insights"""
        
        opportunity_type = opportunity.get('opportunity_type', 'unknown')
        
        if opportunity_type == AnalysisConstants.METRIC_TYPES['BUDGET_REALLOCATION']:
            from_station = opportunity.get('from_station', 'Unknown')
            to_station = opportunity.get('to_station', 'Unknown')
            projected_gain = opportunity.get('projected_visit_gain', 0)
            efficiency_gain = opportunity.get('efficiency_gain', 0)
            
            return f"Reallocation opportunity: {from_station} → {to_station} (+{projected_gain} visits, +{efficiency_gain:.1f} efficiency)"
        
        elif opportunity_type == 'trend_momentum':
            station = opportunity.get('station', 'Unknown')
            momentum_advantage = opportunity.get('momentum_advantage', 0)
            
            return f"Momentum opportunity: {station} improving +{momentum_advantage:.1f} efficiency trend"
        
        elif opportunity_type == 'daypart_reallocation':
            from_daypart = opportunity.get('from_daypart', 'Unknown')
            to_daypart = opportunity.get('to_daypart', 'Unknown')
            efficiency_gap = opportunity.get('efficiency_gap', 0)
            
            return f"Daypart shift opportunity: {from_daypart} → {to_daypart} (+{efficiency_gap:.1f} efficiency)"
        
        else:
            return f"Optimization opportunity: {opportunity_type}"
    
    def export_all_csv_files(self, context: Dict[str, Any], insights: Dict[str, Any], 
                           base_filename: str = None) -> List[str]:
        """Export all CSV files for comprehensive Power BI analysis"""
        
        if base_filename is None:
            client_name = insights['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_filename = f"{client_name}_{timestamp}"
        
        exported_files = []
        
        try:
            # Export comprehensive insights
            insights_file = self.export_comprehensive_insights(insights, f"{base_filename}_insights")
            if insights_file:
                exported_files.append(insights_file)
            
            # Export station performance
            station_file = self.export_station_performance(context, insights, f"{base_filename}_stations")
            if station_file:
                exported_files.append(station_file)
            
            # Export daypart performance
            daypart_file = self.export_daypart_performance(context, insights, f"{base_filename}_dayparts")
            if daypart_file:
                exported_files.append(daypart_file)
            
            # Export opportunity matrix
            opportunity_file = self.export_opportunity_matrix(insights, f"{base_filename}_opportunities")
            if opportunity_file:
                exported_files.append(opportunity_file)
            
            # Export performance quadrants
            quadrants_file = self.export_performance_quadrants(insights, f"{base_filename}_quadrants")
            if quadrants_file:
                exported_files.append(quadrants_file)
            
            if exported_files:
                print(f"\n📊 Complete Power BI CSV export completed:")
                for file_path in exported_files:
                    file_name = os.path.basename(file_path)
                    print(f"   📁 {file_name}")
                print(f"\n💡 Import these {len(exported_files)} CSV files into Power BI for comprehensive dashboard visualization")
            
            return exported_files
            
        except Exception as e:
            print(f"❌ Error during comprehensive CSV export: {e}")
            return exported_files  # Return any files that were successfully created
    
    def create_powerbi_import_guide(self, exported_files: List[str]) -> str:
        """Create a guide for importing CSV files into Power BI"""
        
        if not exported_files:
            return ""
        
        guide_filename = "PowerBI_Import_Guide.md"
        guide_filepath = os.path.join(self.output_dir, guide_filename)
        
        try:
            with open(guide_filepath, 'w', encoding='utf-8') as file:
                file.write("# Power BI Import Guide - TV Campaign Insights\n\n")
                file.write("## Overview\n")
                file.write("This guide helps you import the exported CSV files into Power BI for comprehensive TV campaign analysis.\n\n")
                
                file.write("## CSV Files Description\n\n")
                
                for file_path in exported_files:
                    file_name = os.path.basename(file_path)
                    
                    if 'insights' in file_name:
                        file.write(f"### {file_name}\n")
                        file.write("**Purpose**: Comprehensive AI insights and recommendations\n")
                        file.write("**Use for**: Executive dashboard, key findings, optimization priorities\n")
                        file.write("**Key fields**: insight_category, finding_description, recommendation, priority\n\n")
                    
                    elif 'stations' in file_name:
                        file.write(f"### {file_name}\n")
                        file.write("**Purpose**: Station-level performance analysis\n")
                        file.write("**Use for**: Station comparison, efficiency analysis, budget allocation\n")
                        file.write("**Key fields**: station, efficiency_score, opportunity_type, ai_recommendation\n\n")
                    
                    elif 'dayparts' in file_name:
                        file.write(f"### {file_name}\n")
                        file.write("**Purpose**: Daypart scheduling optimization\n")
                        file.write("**Use for**: Time-based analysis, scheduling decisions, daypart efficiency\n")
                        file.write("**Key fields**: daypart, efficiency_index, recommendation_priority\n\n")
                    
                    elif 'opportunities' in file_name:
                        file.write(f"### {file_name}\n")
                        file.write("**Purpose**: Budget reallocation opportunities\n")
                        file.write("**Use for**: Investment decisions, ROI optimization, strategic planning\n")
                        file.write("**Key fields**: opportunity_type, projected_visit_gain, confidence\n\n")
                    
                    elif 'quadrants' in file_name:
                        file.write(f"### {file_name}\n")
                        file.write("**Purpose**: Portfolio performance quadrants\n")
                        file.write("**Use for**: Strategic station classification, investment prioritization\n")
                        file.write("**Key fields**: quadrant_label, strategic_value, investment_priority\n\n")
                
                file.write("## Power BI Import Steps\n\n")
                file.write("1. **Open Power BI Desktop**\n")
                file.write("2. **Get Data > Text/CSV**\n")
                file.write("3. **Select each CSV file** and import with these settings:\n")
                file.write("   - File Origin: Unicode (UTF-8)\n")
                file.write("   - Delimiter: Comma\n")
                file.write("   - Data Type Detection: Based on first 200 rows\n")
                file.write("4. **Create Relationships** between tables using common fields:\n")
                file.write("   - client (common across all tables)\n")
                file.write("   - station (where applicable)\n")
                file.write("   - daypart (where applicable)\n")
                file.write("5. **Build Visualizations** using the imported data\n\n")
                
                file.write("## Recommended Visualizations\n\n")
                file.write("### Executive Dashboard\n")
                file.write("- **KPI Cards**: Total visits, revenue, efficiency scores\n")
                file.write("- **Insights Table**: Key findings with priorities\n")
                file.write("- **Trend Chart**: Performance change over time\n\n")
                
                file.write("### Station Analysis\n")
                file.write("- **Scatter Plot**: Volume vs Efficiency (quadrant view)\n")
                file.write("- **Bar Chart**: Top performing stations\n")
                file.write("- **Heat Map**: Station performance matrix\n\n")
                
                file.write("### Optimization Dashboard\n")
                file.write("- **Opportunity Matrix**: Reallocation recommendations\n")
                file.write("- **Action Items**: Prioritized recommendations\n")
                file.write("- **Investment Pipeline**: Scaling candidates\n\n")
                
                file.write("## Best Practices\n\n")
                file.write("- **Filter by client** for multi-client analyses\n")
                file.write("- **Use confidence levels** to focus on reliable insights\n")
                file.write("- **Prioritize by impact_level** and priority fields\n")
                file.write("- **Track trends** using time_based and trend_context fields\n")
                file.write("- **Refresh data regularly** for up-to-date insights\n\n")
                
                file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            print(f"📖 Power BI import guide created: {guide_filepath}")
            return guide_filepath
            
        except Exception as e:
            print(f"❌ Error creating Power BI import guide: {e}")
            return ""


# Test the CSV exporter module
if __name__ == "__main__":
    print("🧪 Testing CSV Exporter Module...")
    
    try:
        # Create sample insights data
        sample_insights = {
            'metadata': {
                'generation_date': '2025-06-30T13:34:03',
                'client_name': 'TEST_CLIENT',
                'total_insights_generated': 15
            },
            'key_findings': [
                'Strong engagement trending up: 2.5 visits per spot with 15.2% recent improvement',
                'Top station EXAMPLE accelerating: 1,200 visits from 300 spots with improving trends',
                'Prime daypart strengthening: 3.8 visits per spot and improving'
            ],
            'station_insights': [
                {
                    'station': 'TOP_STATION', 'opportunity_type': 'Scale Winner', 'trend_direction': 'improving',
                    'visit_rate': 4.2, 'recent_efficiency': 4.5, 'confidence': 'High', 'priority': 1,
                    'recommendation': 'Scale TOP_STATION immediately - proven performer'
                }
            ],
            'daypart_insights': [
                {
                    'daypart': 'PRIME', 'recommendation_priority': 'High - Scale Up', 'trend_direction': 'stable',
                    'visit_rate': 3.8, 'recent_efficiency': 3.8, 'confidence': 'High', 'priority': 1,
                    'recommendation': 'Increase PRIME inventory immediately - top efficiency window'
                }
            ],
            'station_daypart_insights': [
                {
                    'station': 'TOP_STATION', 'daypart': 'PRIME', 'combination': 'TOP_STATION + PRIME',
                    'combo_tier': 'Golden Combination', 'synergy_score': 1.6, 'confidence': 'High',
                    'recommendation': 'Scale TOP_STATION + PRIME aggressively - golden combination'
                }
            ],
            'performance_quadrants': {
                'high_volume_high_efficiency': [
                    {
                        'station': 'CHAMPION_1', 'volume': 1200, 'efficiency': 4.0, 'spots': 300,
                        'trend_direction': 'improving', 'efficiency_score': 1.8, 'volume_score': 0.8,
                        'strategic_value': 2.1, 'action': 'Scale immediately', 'confidence': 'High'
                    }
                ]
            },
            'opportunity_matrix': [
                {
                    'opportunity_id': 1, 'opportunity_type': 'budget_reallocation',
                    'from_station': 'WEAK_STATION', 'to_station': 'STRONG_STATION',
                    'efficiency_gain': 2.1, 'projected_visit_gain': 105, 'confidence': 'High',
                    'priority': 1, 'business_rationale': 'Leverage 2.1 visits/spot efficiency advantage'
                }
            ],
            'optimization_priorities': [
                {
                    'priority': 1, 'area': 'Station Budget Reallocation',
                    'recommendation': 'Shift budget from underperformers to top performers',
                    'impact': 'High'
                }
            ],
            'latest_week_insights': {
                'insights': ['Strong improvement: 15.2% efficiency change in latest week']
            }
        }
        
        sample_context = {
            'primary_product': 'TEST_PRODUCT',
            'station_performance': [
                {
                    'station': 'TOP_STATION', 'total_visits': 1260, 'spots': 300, 'avg_visits_per_spot': 4.2,
                    'total_cost': 15000, 'cpm': 11.9, 'efficiency_score': 1.8, 'volume_score': 0.8,
                    'performance_tier': 'High Performer', 'opportunity_type': 'Scale Winner',
                    'trend_direction': 'improving', 'confidence': 'High'
                }
            ],
            'daypart_performance': [
                {
                    'daypart': 'PRIME', 'total_visits': 760, 'spots': 200, 'avg_visits_per_spot': 3.8,
                    'total_cost': 10000, 'efficiency_index': 1.4, 'volume_adequacy': 'High',
                    'efficiency_rating': 'Excellent', 'recommendation_priority': 'High - Scale Up',
                    'trend_direction': 'stable', 'confidence': 'High'
                }
            ]
        }
        
        # Test CSV exporter
        exporter = CSVExporter()
        
        # Test comprehensive insights export
        insights_file = exporter.export_comprehensive_insights(sample_insights)
        print(f"✅ Comprehensive insights exported: {bool(insights_file)}")
        
        # Test station performance export
        station_file = exporter.export_station_performance(sample_context, sample_insights)
        print(f"✅ Station performance exported: {bool(station_file)}")
        
        # Test daypart performance export
        daypart_file = exporter.export_daypart_performance(sample_context, sample_insights)
        print(f"✅ Daypart performance exported: {bool(daypart_file)}")
        
        # Test opportunity matrix export
        opportunity_file = exporter.export_opportunity_matrix(sample_insights)
        print(f"✅ Opportunity matrix exported: {bool(opportunity_file)}")
        
        # Test performance quadrants export
        quadrants_file = exporter.export_performance_quadrants(sample_insights)
        print(f"✅ Performance quadrants exported: {bool(quadrants_file)}")
        
        # Test comprehensive export
        all_files = exporter.export_all_csv_files(sample_context, sample_insights)
        print(f"✅ All CSV files exported: {len(all_files)} files")
        
        # Test Power BI guide creation
        guide_file = exporter.create_powerbi_import_guide(all_files)
        print(f"✅ Power BI guide created: {bool(guide_file)}")
        
        print("✅ CSV Exporter module test completed successfully!")
        
    except Exception as e:
        print(f"❌ CSV Exporter module test failed: {e}")
        import traceback
        traceback.print_exc()