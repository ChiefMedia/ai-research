"""
Power BI Insight Formatter - Clean CSV Generation
Converts structured insights into standardized Power BI rows
"""

import os
import csv
from typing import Dict, Any, List
from datetime import datetime

class PowerBIInsightFormatter:
    """Clean formatter for Power BI CSV output"""
    
    def __init__(self, output_dir: str = "output/reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.columns = [
            'client', 'insight_id', 'insight_category', 'insight_type', 'priority',
            'impact_level', 'station', 'daypart', 'recommendation', 'projected_impact',
            'confidence', 'action_type', 'urgency', 'entity_type', 'trend_direction',
            'implementation_timeline', 'business_rationale', 'generated_date'
        ]
    
    def format_for_powerbi(self, parsed_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert parsed insights to Power BI rows
        
        Args:
            parsed_insights: Structured insights from InsightParser
            
        Returns:
            List of standardized rows for Power BI
        """
        
        rows = []
        client = parsed_insights['metadata']['client_name']
        date = parsed_insights['metadata']['generated_at'][:10]
        
        # Executive summary
        rows.extend(self._format_executive_summary(parsed_insights.get('executive_summary', {}), client, date))
        
        # Scaling opportunities
        rows.extend(self._format_scaling_opportunities(parsed_insights.get('scaling_opportunities', []), client, date))
        
        # Underperformers
        rows.extend(self._format_underperformers(parsed_insights.get('underperformers', []), client, date))
        
        # Budget reallocations
        rows.extend(self._format_budget_reallocations(parsed_insights.get('budget_reallocations', []), client, date))
        
        # Trend insights
        rows.extend(self._format_trend_insights(parsed_insights.get('trend_insights', []), client, date))
        
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
            'insight_category': 'Executive Summary',
            'insight_type': 'strategic_overview',
            'priority': 1,
            'impact_level': 'High',
            'station': None,
            'daypart': None,
            'recommendation': summary['summary'],
            'projected_impact': None,
            'confidence': summary.get('confidence', 'Medium'),
            'action_type': 'strategic_review',
            'urgency': summary.get('urgency_level', 'Medium'),
            'entity_type': 'campaign',
            'trend_direction': None,
            'implementation_timeline': 'Immediate',
            'business_rationale': 'Executive strategic context',
            'generated_date': date
        }]
    
    def _format_scaling_opportunities(self, opportunities: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format scaling opportunities"""
        
        formatted = []
        
        for i, opp in enumerate(opportunities):
            formatted.append({
                'client': client,
                'insight_id': f'SCALE_{i+1:03d}',
                'insight_category': 'Scaling Opportunity',
                'insight_type': 'performance_optimization',
                'priority': opp.get('priority', i + 1),
                'impact_level': 'High',
                'station': opp.get('station'),
                'daypart': opp.get('daypart'),
                'recommendation': opp.get('recommendation', ''),
                'projected_impact': opp.get('projected_impact'),
                'confidence': opp.get('confidence', 'Medium'),
                'action_type': opp.get('action_type', 'scale_up'),
                'urgency': 'High' if opp.get('priority', 99) <= 2 else 'Medium',
                'entity_type': 'station' if opp.get('station') else 'daypart',
                'trend_direction': 'positive',
                'implementation_timeline': self._get_timeline(opp.get('action_type')),
                'business_rationale': opp.get('business_rationale', ''),
                'generated_date': date
            })
        
        return formatted
    
    def _format_underperformers(self, underperformers: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format underperformers"""
        
        formatted = []
        
        for i, under in enumerate(underperformers):
            formatted.append({
                'client': client,
                'insight_id': f'UNDER_{i+1:03d}',
                'insight_category': 'Underperformer',
                'insight_type': 'performance_issue',
                'priority': i + 1,
                'impact_level': under.get('severity', 'Medium'),
                'station': under.get('entity') if under.get('entity_type') == 'station' else None,
                'daypart': under.get('entity') if under.get('entity_type') == 'daypart' else None,
                'recommendation': under.get('issue', ''),
                'projected_impact': 'Performance improvement needed',
                'confidence': 'High',
                'action_type': under.get('recommended_action', 'investigate'),
                'urgency': under.get('severity', 'Medium'),
                'entity_type': under.get('entity_type', 'unknown'),
                'trend_direction': 'negative',
                'implementation_timeline': 'Immediate' if under.get('severity') == 'High' else 'Short-term',
                'business_rationale': under.get('business_rationale', ''),
                'generated_date': date
            })
        
        return formatted
    
    def _format_budget_reallocations(self, reallocations: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format budget reallocations"""
        
        formatted = []
        
        for i, realloc in enumerate(reallocations):
            spots = realloc.get('spots_to_move', 'budget')
            from_station = realloc.get('from_station', '')
            to_station = realloc.get('to_station', '')
            
            recommendation = f"Move {spots} spots from {from_station} to {to_station}" if from_station and to_station else "Budget reallocation recommended"
            
            formatted.append({
                'client': client,
                'insight_id': f'BUDGET_{i+1:03d}',
                'insight_category': 'Budget Reallocation',
                'insight_type': 'resource_optimization',
                'priority': i + 1,
                'impact_level': 'High',
                'station': to_station,
                'daypart': None,
                'recommendation': recommendation,
                'projected_impact': realloc.get('projected_impact', 'Efficiency improvement'),
                'confidence': realloc.get('confidence', 'High'),
                'action_type': 'reallocate_budget',
                'urgency': realloc.get('implementation_priority', 'High'),
                'entity_type': 'budget_allocation',
                'trend_direction': 'optimization',
                'implementation_timeline': 'Short-term',
                'business_rationale': f"Reallocate from {from_station} to {to_station}" if from_station and to_station else "Budget optimization",
                'generated_date': date
            })
        
        return formatted
    
    def _format_trend_insights(self, trends: List[Dict[str, Any]], client: str, date: str) -> List[Dict[str, Any]]:
        """Format trend insights"""
        
        formatted = []
        
        for i, trend in enumerate(trends):
            formatted.append({
                'client': client,
                'insight_id': f'TREND_{i+1:03d}',
                'insight_category': 'Trend Analysis',
                'insight_type': 'trend_insight',
                'priority': i + 1,
                'impact_level': 'Medium',
                'station': None,
                'daypart': None,
                'recommendation': trend.get('trend_description', ''),
                'projected_impact': f"Trend: {trend.get('trend_direction', 'unknown')}",
                'confidence': 'Medium',
                'action_type': trend.get('recommended_response', 'monitor'),
                'urgency': trend.get('urgency', 'Medium'),
                'entity_type': 'trend_analysis',
                'trend_direction': trend.get('trend_direction', 'unknown'),
                'implementation_timeline': 'Ongoing',
                'business_rationale': 'Monitor performance trajectory',
                'generated_date': date
            })
        
        return formatted
    
    def _get_timeline(self, action_type: str) -> str:
        """Get implementation timeline"""
        timeline_map = {
            'scale_up': 'Immediate',
            'scale_down': 'Short-term', 
            'test': 'Short-term',
            'optimize': 'Medium-term',
            'investigate': 'Immediate'
        }
        return timeline_map.get(action_type, 'Medium-term')


# Test the clean formatter
if __name__ == "__main__":
    print("🧪 Testing Clean Power BI Formatter...")
    
    # Sample insights
    sample_insights = {
        'metadata': {
            'client_name': 'TEST_CLIENT',
            'generated_at': '2025-06-30T15:30:00'
        },
        'executive_summary': {
            'summary': 'Campaign performing well with scaling opportunities',
            'confidence': 'High',
            'urgency_level': 'Medium'
        },
        'scaling_opportunities': [
            {
                'priority': 1,
                'station': 'TOP_STATION',
                'recommendation': 'Scale TOP_STATION budget by 25%',
                'action_type': 'scale_up',
                'projected_impact': '15% efficiency gain',
                'confidence': 'High',
                'business_rationale': 'Proven performance'
            }
        ],
        'underperformers': [
            {
                'entity': 'WEAK_STATION',
                'entity_type': 'station',
                'issue': 'Underperforming by 50%',
                'severity': 'High',
                'recommended_action': 'reduce',
                'business_rationale': 'Poor ROI'
            }
        ],
        'budget_reallocations': [],
        'trend_insights': []
    }
    
    try:
        formatter = PowerBIInsightFormatter()
        rows = formatter.format_for_powerbi(sample_insights)
        
        print(f"✅ Formatted {len(rows)} Power BI rows")
        
        csv_path = formatter.save_to_csv(rows)
        print(f"✅ CSV saved: {os.path.basename(csv_path)}")
        
        print("✅ Clean Power BI formatter test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()