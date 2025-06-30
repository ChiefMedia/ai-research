"""
Power BI Insight Formatter - Optimized CSV Generation
Converts structured insights into streamlined Power BI rows (10 columns)
"""

import os
import csv
from typing import Dict, Any, List
from datetime import datetime

class PowerBIInsightFormatter:
    """Optimized formatter for Power BI CSV output - 10 column structure"""
    
    def __init__(self, output_dir: str = "output/reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Optimized 10-column structure
        self.columns = [
            'client',
            'insight_id', 
            'category',
            'station',
            'daypart',
            'recommendation',
            'priority',
            'confidence',
            'urgency',
            'generated_date'
        ]
    
    def format_for_powerbi(self, parsed_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert parsed insights to optimized Power BI rows with dynamic processing"""
        
        rows = []
        client = parsed_insights['metadata']['client_name']
        date = parsed_insights['metadata']['generated_at'][:10]
        
        # Process known categories with structured formatting
        known_formatters = {
            'executive_summary': self._format_executive_summary,
            'scaling_opportunities': self._format_scaling_opportunities,
            'underperformers': self._format_underperformers,
            'budget_reallocations': self._format_budget_reallocations,
            'trend_insights': self._format_trend_insights
        }
        
        # Process known categories
        for category, formatter in known_formatters.items():
            if category in parsed_insights:
                rows.extend(formatter(parsed_insights[category], client, date))
        
        # Process any unknown categories dynamically
        for category_name, category_data in parsed_insights.items():
            if category_name not in known_formatters and category_name != 'metadata' and isinstance(category_data, list):
                rows.extend(self._format_dynamic_category(category_data, category_name, client, date))
                print(f"🔄 Dynamically formatted category: {category_name} ({len(category_data)} insights)")
        
        return rows
    
    def save_to_csv(self, powerbi_rows: List[Dict[str, Any]], filename: str = None) -> str:
        """Save formatted insights to CSV"""
        
        if not powerbi_rows:
            raise ValueError("No insights to save")
        
        if filename is None:
            client = powerbi_rows[0].get('client', 'unknown').lower().replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client}_gemini_insights_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.columns)
                writer.writeheader()
                writer.writerows(powerbi_rows)
            
            return filepath
            
        except Exception as e:
            raise RuntimeError(f"Failed to save CSV: {e}")
    
    def _format_executive_summary(self, summary: Dict[str, Any], client: str, date: str) -> List[Dict[str, Any]]:
        """Format executive summary"""
        
        if not summary.get('summary'):
            return []
        
        return [{
            'client': client,
            'insight_id': 'EXEC_001',
            'category': 'executive_summary',
            'station': None,
            'daypart': None,
            'recommendation': f"{summary['summary']} (Confidence: {summary.get('confidence', 'Medium')}, Momentum: {summary.get('recent_momentum', 'stable')})",
            'priority': 1,
            'confidence': summary.get('confidence', 'Medium'),
            'urgency': summary.get('urgency', 'Medium'),
            'generated_date': date
        }]
    
    def _format_scaling_opportunities(self, opportunities: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format scaling opportunities with scenario types"""
        
        formatted = []
        
        for i, opp in enumerate(opportunities):
            scenario = opp.get('optimization_scenario', 'standard')
            entity_parts = self._parse_single_entity(opp.get('entity', ''))
            
            # Build comprehensive recommendation text
            recommendation = f"Increase by {opp.get('recommended_weekly_increase', 'TBD')} spots/week from current {opp.get('current_weekly_spots', 'TBD')} spots. "
            recommendation += f"Projected impact: {opp.get('projected_weekly_impact', 'TBD')}. "
            recommendation += f"Risk: {opp.get('risk_level', 'Unknown')}. "
            recommendation += f"Rationale: {opp.get('business_rationale', 'Performance opportunity')}"
            
            formatted.append({
                'client': client,
                'insight_id': f'SCALE_{scenario.upper()}_{i+1:03d}',
                'category': f'scaling_{scenario}',
                'station': entity_parts['station'],
                'daypart': entity_parts['daypart'],
                'recommendation': recommendation,
                'priority': opp.get('priority', i + 1),
                'confidence': opp.get('confidence', 'Medium'),
                'urgency': 'High' if opp.get('priority', 99) <= 2 else 'Medium',
                'generated_date': date
            })
        
        return formatted
    
    def _format_underperformers(self, underperformers: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format underperformers"""
        
        formatted = []
        
        for i, under in enumerate(underperformers):
            entity_parts = self._parse_single_entity(under.get('entity', ''))
            weeks_poor = under.get('weeks_of_poor_performance', 0)
            
            # Determine category based on confirmation period
            category = 'underperformer_confirmed' if weeks_poor >= 3 else 'underperformer_potential'
            
            # Build comprehensive recommendation
            recommendation = f"Reduce by {under.get('recommended_weekly_reduction', 'TBD')} spots/week from current {under.get('current_weekly_spots', 'TBD')} spots. "
            recommendation += f"Issue: {under.get('issue', 'Performance decline')}. "
            recommendation += f"Poor performance for {weeks_poor} weeks. "
            if under.get('potential_cause'):
                recommendation += f"Potential cause: {under.get('potential_cause')}. "
            recommendation += f"Action: {under.get('recommended_action', 'investigate')}. "
            recommendation += f"Rationale: {under.get('business_rationale', 'Performance improvement needed')}"
            
            formatted.append({
                'client': client,
                'insight_id': f'UNDER_{category.split("_")[1].upper()}_{i+1:03d}',
                'category': category,
                'station': entity_parts['station'],
                'daypart': entity_parts['daypart'],
                'recommendation': recommendation,
                'priority': i + 1,
                'confidence': 'High',
                'urgency': under.get('severity', 'Medium'),
                'generated_date': date
            })
        
        return formatted
    
    def _format_budget_reallocations(self, reallocations: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format budget reallocations - separate rows for from/to"""
        
        formatted = []
        
        for i, realloc in enumerate(reallocations):
            scenario = realloc.get('scenario_type', 'standard')
            spots_to_move = realloc.get('weekly_spots_to_move', 'TBD')
            
            # FROM entity (reduction)
            from_parts = self._parse_single_entity(realloc.get('from_entity', ''))
            from_recommendation = f"REDUCE by {spots_to_move} spots/week ({realloc.get('percentage_change_from', 'TBD')}). "
            from_recommendation += f"Current: {realloc.get('current_from_weekly_spots', 'TBD')} spots/week. "
            from_recommendation += f"Risk assessment: {realloc.get('risk_assessment', 'Standard reallocation')}"
            
            formatted.append({
                'client': client,
                'insight_id': f'REALLOC_{scenario.upper()}_FROM_{i+1:03d}',
                'category': f'reallocation_{scenario}_from',
                'station': from_parts['station'],
                'daypart': from_parts['daypart'],
                'recommendation': from_recommendation,
                'priority': i + 1,
                'confidence': realloc.get('confidence', 'High'),
                'urgency': realloc.get('implementation_priority', 'High'),
                'generated_date': date
            })
            
            # TO entity (increase)
            to_parts = self._parse_single_entity(realloc.get('to_entity', ''))
            to_recommendation = f"INCREASE by {spots_to_move} spots/week ({realloc.get('percentage_change_to', 'TBD')}). "
            to_recommendation += f"Current: {realloc.get('current_to_weekly_spots', 'TBD')} spots/week. "
            to_recommendation += f"Projected impact: {realloc.get('projected_weekly_impact', 'Efficiency improvement')}"
            
            formatted.append({
                'client': client,
                'insight_id': f'REALLOC_{scenario.upper()}_TO_{i+1:03d}',
                'category': f'reallocation_{scenario}_to',
                'station': to_parts['station'],
                'daypart': to_parts['daypart'],
                'recommendation': to_recommendation,
                'priority': i + 1,
                'confidence': realloc.get('confidence', 'High'),
                'urgency': realloc.get('implementation_priority', 'High'),
                'generated_date': date
            })
        
        return formatted
    
    def _format_daypart_shifting(self, shifts: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format daypart shifting recommendations"""
        
        formatted = []
        
        for i, shift in enumerate(shifts):
            recommendation = f"Shift {shift.get('weekly_spots_to_shift', 'TBD')} spots/week from {shift.get('from_daypart', 'TBD')} to {shift.get('to_daypart', 'TBD')}. "
            recommendation += f"Projected efficiency gain: {shift.get('projected_efficiency_gain', 'TBD')}. "
            recommendation += f"Rationale: {shift.get('business_rationale', 'Daypart optimization opportunity')}"
            
            formatted.append({
                'client': client,
                'insight_id': f'DAYSHIFT_{i+1:03d}',
                'category': 'daypart_shift',
                'station': shift.get('station'),
                'daypart': f"{shift.get('from_daypart', 'TBD')} → {shift.get('to_daypart', 'TBD')}",
                'recommendation': recommendation,
                'priority': i + 1,
                'confidence': shift.get('confidence', 'Medium'),
                'urgency': 'Medium',
                'generated_date': date
            })
        
        return formatted
    
    def _format_performance_tiers(self, tiers: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format performance tier analysis - one row per entity in tier"""
        
        formatted = []
        
        for tier_data in tiers:
            tier_name = tier_data.get('tier', 'Unknown').lower().replace(' ', '_')
            entities = tier_data.get('entities', [])
            characteristics = tier_data.get('characteristics', '')
            strategy = tier_data.get('recommended_strategy', '')
            
            for i, entity in enumerate(entities):
                entity_parts = self._parse_single_entity(entity)
                
                recommendation = f"Tier: {tier_data.get('tier', 'Unknown')}. "
                recommendation += f"Characteristics: {characteristics}. "
                recommendation += f"Strategy: {strategy}. "
                recommendation += f"Scaling potential: {tier_data.get('scaling_potential', 'Unknown')}"
                
                formatted.append({
                    'client': client,
                    'insight_id': f'TIER_{tier_name.upper()}_{i+1:03d}',
                    'category': f'performance_tier_{tier_name}',
                    'station': entity_parts['station'],
                    'daypart': entity_parts['daypart'],
                    'recommendation': recommendation,
                    'priority': i + 1,
                    'confidence': 'Medium',
                    'urgency': 'Low',
                    'generated_date': date
                })
        
        return formatted
    
    def _format_temporal_insights(self, insights: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format temporal pattern insights"""
        
        formatted = []
        
        for i, insight in enumerate(insights):
            entities = insight.get('entities_affected', [])
            
            for j, entity in enumerate(entities):
                entity_parts = self._parse_single_entity(entity)
                
                recommendation = f"Pattern: {insight.get('pattern_type', 'Unknown')}. "
                recommendation += f"Description: {insight.get('description', 'Temporal pattern detected')}. "
                recommendation += f"Timing adjustment: {insight.get('recommended_timing_adjustment', 'Monitor pattern')}. "
                recommendation += f"Projected impact: {insight.get('projected_impact', 'TBD')}"
                
                formatted.append({
                    'client': client,
                    'insight_id': f'TEMPORAL_{i+1:03d}_{j+1:03d}',
                    'category': 'temporal_pattern',
                    'station': entity_parts['station'],
                    'daypart': entity_parts['daypart'],
                    'recommendation': recommendation,
                    'priority': i + 1,
                    'confidence': 'Medium',
                    'urgency': 'Medium',
                    'generated_date': date
                })
        
        return formatted
    
    def _format_emerging_opportunities(self, opportunities: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format emerging opportunities"""
        
        formatted = []
        
        for i, opp in enumerate(opportunities):
            entity_parts = self._parse_single_entity(opp.get('entity', ''))
            
            recommendation = f"Test increase by {opp.get('recommended_test_increase', 'TBD')} spots/week from current {opp.get('current_weekly_spots', 'TBD')} spots. "
            recommendation += f"Type: {opp.get('opportunity_type', 'Unknown')}. "
            recommendation += f"Test duration: {opp.get('testing_duration', '2-4 weeks')}. "
            recommendation += f"Success metrics: {opp.get('success_metrics', 'Performance improvement')}. "
            recommendation += f"Rationale: {opp.get('business_rationale', 'Emerging opportunity')}"
            
            formatted.append({
                'client': client,
                'insight_id': f'EMERGING_{i+1:03d}',
                'category': 'emerging_opportunity',
                'station': entity_parts['station'],
                'daypart': entity_parts['daypart'],
                'recommendation': recommendation,
                'priority': i + 1,
                'confidence': opp.get('confidence', 'Low'),
                'urgency': 'Low',
                'generated_date': date
            })
        
        return formatted
    
    def _format_risk_assessments(self, risks: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format risk assessment insights"""
        
        formatted = []
        
        for i, risk in enumerate(risks):
            entities = risk.get('affected_entities', [])
            
            for j, entity in enumerate(entities):
                entity_parts = self._parse_single_entity(entity)
                
                recommendation = f"Risk: {risk.get('risk_type', 'Unknown')}. "
                recommendation += f"Description: {risk.get('description', 'Risk identified')}. "
                recommendation += f"Potential impact: {risk.get('potential_impact', 'TBD')}. "
                recommendation += f"Mitigation: {risk.get('mitigation_strategy', 'Monitor closely')}"
                
                formatted.append({
                    'client': client,
                    'insight_id': f'RISK_{i+1:03d}_{j+1:03d}',
                    'category': 'risk_assessment',
                    'station': entity_parts['station'],
                    'daypart': entity_parts['daypart'],
                    'recommendation': recommendation,
                    'priority': i + 1,
                    'confidence': 'Medium',
                    'urgency': risk.get('urgency', 'Medium'),
                    'generated_date': date
                })
        
        return formatted
    
    def _format_market_dynamics(self, dynamics: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format market dynamics (speculative analysis)"""
        
        formatted = []
        
        for i, dynamic in enumerate(dynamics):
            entities = dynamic.get('affected_entities', [])
            
            for j, entity in enumerate(entities):
                entity_parts = self._parse_single_entity(entity)
                
                recommendation = f"SPECULATIVE: {dynamic.get('hypothesis', 'Unknown hypothesis')}. "
                recommendation += f"Evidence: {dynamic.get('evidence', 'Pattern analysis')}. "
                recommendation += f"Investigation: {dynamic.get('recommended_investigation', 'Monitor performance')}. "
                recommendation += f"Note: {dynamic.get('note', 'Speculative analysis based on performance patterns')}"
                
                formatted.append({
                    'client': client,
                    'insight_id': f'MARKET_{i+1:03d}_{j+1:03d}',
                    'category': 'market_dynamics',
                    'station': entity_parts['station'],
                    'daypart': entity_parts['daypart'],
                    'recommendation': recommendation,
                    'priority': i + 1,
                    'confidence': dynamic.get('confidence', 'Low'),
                    'urgency': 'Low',
                    'generated_date': date
                })
        
        return formatted
    
    def _format_budget_scaling(self, scaling: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format budget scaling opportunities"""
        
        formatted = []
        
        for i, scale in enumerate(scaling):
            entities = scale.get('target_entities', [])
            
            for j, entity in enumerate(entities):
                entity_parts = self._parse_single_entity(entity)
                
                recommendation = f"Budget increase opportunity: {scale.get('opportunity_description', 'Scale budget for ROI')}. "
                recommendation += f"Additional spots: {scale.get('recommended_additional_weekly_spots', 'TBD')} per week. "
                recommendation += f"Projected ROI: {scale.get('projected_weekly_roi', 'TBD')}. "
                recommendation += f"Scenario: {scale.get('scaling_scenario', 'standard')}"
                
                formatted.append({
                    'client': client,
                    'insight_id': f'BUDGET_SCALE_{i+1:03d}_{j+1:03d}',
                    'category': f'budget_scaling_{scale.get("scaling_scenario", "standard")}',
                    'station': entity_parts['station'],
                    'daypart': entity_parts['daypart'],
                    'recommendation': recommendation,
                    'priority': i + 1,
                    'confidence': scale.get('confidence', 'Medium'),
                    'urgency': 'Medium',
                    'generated_date': date
                })
        
        return formatted
    
    def _format_trend_insights(self, trends: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format trend insights"""
        
        formatted = []
        
        for i, trend in enumerate(trends):
            entity_parts = self._parse_single_entity(trend.get('entity', ''))
            
            recommendation = f"Trend: {trend.get('trend_direction', 'unknown')} ({trend.get('weeks_observed', 'TBD')} weeks). "
            recommendation += f"Description: {trend.get('trend_description', 'Performance trend detected')}. "
            recommendation += f"Weekly impact: {trend.get('weekly_impact', 'TBD')}. "
            recommendation += f"Response: {trend.get('recommended_response', 'monitor')}"
            
            formatted.append({
                'client': client,
                'insight_id': f'TREND_{i+1:03d}',
                'category': 'trend_insight',
                'station': entity_parts['station'],
                'daypart': entity_parts['daypart'],
                'recommendation': recommendation,
                'priority': i + 1,
                'confidence': 'Medium',
                'urgency': trend.get('urgency', 'Medium'),
                'generated_date': date
            })
        
        return formatted
    
    def _format_dynamic_category(self, insights: List[Dict[str, Any]], category_name: str, client: str, date: str) -> List[Dict[str, Any]]:
        """
        Dynamically format any category not handled by structured formatters
        
        Args:
            insights: List of insights from parser
            category_name: Name of the category
            client: Client name
            date: Generated date
            
        Returns:
            List of formatted Power BI rows
        """
        
        formatted = []
        
        for i, insight in enumerate(insights):
            # Handle entities that might be lists (performance tiers, etc.)
            entities = self._extract_entities_from_insight(insight)
            
            for j, entity_info in enumerate(entities):
                
                # Generate unique insight ID
                if len(entities) > 1:
                    insight_id = f'{category_name.upper()}_{i+1:03d}_{j+1:03d}'
                else:
                    insight_id = f'{category_name.upper()}_{i+1:03d}'
                
                # Build comprehensive recommendation text
                recommendation = self._build_comprehensive_recommendation(insight, entity_info)
                
                formatted.append({
                    'client': client,
                    'insight_id': insight_id,
                    'category': category_name,
                    'station': entity_info.get('station'),
                    'daypart': entity_info.get('daypart'),
                    'recommendation': recommendation,
                    'priority': insight.get('priority', i + 1),
                    'confidence': insight.get('confidence', 'Medium'),
                    'urgency': insight.get('urgency', 'Medium'),
                    'generated_date': date
                })
        
        return formatted
    
    def _extract_entities_from_insight(self, insight: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract all entities from an insight (handles single entities and lists)"""
        
        entities = []
        
        # Check for multiple entities in common fields
        multi_entity_fields = ['entities', 'target_entities', 'affected_entities']
        
        for field in multi_entity_fields:
            if field in insight and isinstance(insight[field], list):
                for entity in insight[field]:
                    entities.append(self._parse_single_entity(entity))
                return entities
        
        # Check for single entity fields
        single_entity_fields = ['entity', 'station', 'from_entity', 'to_entity']
        
        for field in single_entity_fields:
            if field in insight and insight[field]:
                entities.append(self._parse_single_entity(insight[field]))
                break
        
        # If no entities found, create default
        if not entities:
            entities.append({'station': None, 'daypart': None, 'entity': 'Unknown'})
        
        return entities
    
    def _parse_single_entity(self, entity: str) -> Dict[str, str]:
        """Parse a single entity string into station and daypart"""
        
        if not entity or entity == 'Unknown':
            return {'station': None, 'daypart': None, 'entity': entity}
        
        # Handle formats like "STATION_DAYPART" or "STATION DAYPART"
        if '_' in entity:
            parts = entity.split('_', 1)
            return {
                'station': parts[0],
                'daypart': parts[1] if len(parts) > 1 else None,
                'entity': entity
            }
        elif ' ' in entity:
            parts = entity.split(' ', 1)
            return {
                'station': parts[0],
                'daypart': parts[1] if len(parts) > 1 else None,
                'entity': entity
            }
        else:
            # Assume it's just a station name
            return {'station': entity, 'daypart': None, 'entity': entity}
    
    def _build_comprehensive_recommendation(self, insight: Dict[str, Any], entity_info: Dict[str, str]) -> str:
        """Build comprehensive recommendation text from insight data"""
        
        # Start with main recommendation text
        main_text = insight.get('recommendation', '')
        
        # Add category-specific information
        category_type = insight.get('category_type', '')
        
        if 'scaling' in category_type:
            if insight.get('projected_impact'):
                main_text += f" Projected impact: {insight['projected_impact']}."
            if insight.get('action_type'):
                main_text += f" Action: {insight['action_type']}."
                
        elif 'underperform' in category_type:
            if insight.get('severity'):
                main_text += f" Severity: {insight['severity']}."
            if insight.get('weeks_of_poor_performance'):
                main_text += f" Poor performance for {insight['weeks_of_poor_performance']} weeks."
                
        elif 'reallocation' in category_type or 'budget' in category_type:
            if insight.get('from_entity') and insight.get('to_entity'):
                main_text += f" Move from {insight['from_entity']} to {insight['to_entity']}."
            if insight.get('spots_to_move'):
                main_text += f" Spots to move: {insight['spots_to_move']}."
                
        elif 'daypart' in category_type:
            if insight.get('from_daypart') and insight.get('to_daypart'):
                main_text += f" Shift from {insight['from_daypart']} to {insight['to_daypart']}."
                
        elif 'risk' in category_type:
            if insight.get('risk_type'):
                main_text += f" Risk type: {insight['risk_type']}."
            if insight.get('mitigation_strategy'):
                main_text += f" Mitigation: {insight['mitigation_strategy']}."
                
        elif 'trend' in category_type:
            if insight.get('trend_direction'):
                main_text += f" Trend: {insight['trend_direction']}."
            if insight.get('weeks_observed'):
                main_text += f" Observed for {insight['weeks_observed']} weeks."
        
        # Add entity context if not already in text
        if entity_info.get('entity') and entity_info['entity'] not in main_text:
            main_text = f"Entity: {entity_info['entity']}. {main_text}"
        
        # Ensure we have some text
        if not main_text.strip():
            main_text = f"Insight identified for {entity_info.get('entity', 'campaign')} from {category_type} analysis."
        
        return main_text.strip()


# Test the optimized formatter
if __name__ == "__main__":
    print("🧪 Testing Optimized Power BI Formatter...")
    
    # Sample comprehensive insights
    sample_insights = {
        'metadata': {
            'client_name': 'TEST_CLIENT',
            'generated_at': '2025-06-30T15:30:00',
            'insight_count': 25
        },
        'executive_summary': {
            'summary': 'Campaign performing well with multiple optimization opportunities across conservative and aggressive scenarios',
            'confidence': 'High',
            'urgency': 'Medium',
            'recent_momentum': 'positive'
        },
        'scaling_opportunities': [
            {
                'priority': 1,
                'entity': 'TOP_STATION_PRIME',
                'optimization_scenario': 'aggressive',
                'current_weekly_spots': 25,
                'recommended_weekly_increase': 12,
                'projected_weekly_impact': '45 additional visits',
                'confidence': 'High',
                'risk_level': 'Low',
                'business_rationale': 'Proven high performer'
            }
        ],
        'daypart_shifting': [
            {
                'station': 'MID_STATION',
                'from_daypart': 'LATE',
                'to_daypart': 'PRIME',
                'weekly_spots_to_shift': 8,
                'projected_efficiency_gain': '25% improvement',
                'confidence': 'Medium',
                'business_rationale': 'Better audience match in prime'
            }
        ]
    }
    
    try:
        formatter = PowerBIInsightFormatter()
        rows = formatter.format_for_powerbi(sample_insights)
        
        print(f"✅ Formatted {len(rows)} Power BI rows")
        print(f"📊 Columns: {len(formatter.columns)} (optimized from 18)")
        
        # Show sample row
        if rows:
            print(f"🔍 Sample row: {rows[0]}")
        
        csv_path = formatter.save_to_csv(rows)
        print(f"✅ CSV saved: {os.path.basename(csv_path)}")
        
        print("✅ Optimized Power BI formatter test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
if __name__ == "__main__":
    print("🧪 Testing Optimized Power BI Formatter...")
    
    # Sample comprehensive insights
    sample_insights = {
        'metadata': {
            'client_name': 'TEST_CLIENT',
            'generated_at': '2025-06-30T15:30:00',
            'insight_count': 25
        },
        'executive_summary': {
            'summary': 'Campaign performing well with multiple optimization opportunities across conservative and aggressive scenarios',
            'confidence': 'High',
            'urgency': 'Medium',
            'recent_momentum': 'positive'
        },
        'scaling_opportunities': [
            {
                'priority': 1,
                'entity': 'TOP_STATION_PRIME',
                'optimization_scenario': 'aggressive',
                'current_weekly_spots': 25,
                'recommended_weekly_increase': 12,
                'projected_weekly_impact': '45 additional visits',
                'confidence': 'High',
                'risk_level': 'Low',
                'business_rationale': 'Proven high performer'
            }
        ],
        'daypart_shifting': [
            {
                'station': 'MID_STATION',
                'from_daypart': 'LATE',
                'to_daypart': 'PRIME',
                'weekly_spots_to_shift': 8,
                'projected_efficiency_gain': '25% improvement',
                'confidence': 'Medium',
                'business_rationale': 'Better audience match in prime'
            }
        ]
    }
    
    try:
        formatter = PowerBIInsightFormatter()
        rows = formatter.format_for_powerbi(sample_insights)
        
        print(f"✅ Formatted {len(rows)} Power BI rows")
        print(f"📊 Columns: {len(formatter.columns)} (optimized from 18)")
        
        # Show sample row
        if rows:
            print(f"🔍 Sample row: {rows[0]}")
        
        csv_path = formatter.save_to_csv(rows)
        print(f"✅ CSV saved: {os.path.basename(csv_path)}")
        
        print("✅ Optimized Power BI formatter test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()