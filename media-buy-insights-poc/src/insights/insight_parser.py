"""
Insight Parser - Clean JSON Response Processing
Parses Gemini's JSON response into structured insights for Power BI
"""

import json
import re
import os
from typing import Dict, Any, List
from datetime import datetime

class InsightParser:
    """Clean JSON parser for Gemini campaign insights"""
    
    def __init__(self, output_dir: str = "output/reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def parse_gemini_response(self, raw_response: str, client_name: str = None) -> Dict[str, Any]:
        """
        Parse Gemini's JSON response into structured insights
        
        Args:
            raw_response: Raw JSON response from Gemini
            client_name: Client name for metadata
            
        Returns:
            Structured insights dictionary
        """
        
        # Save raw response for debugging
        self._save_raw_response(raw_response, client_name)
        
        # Extract and parse JSON
        gemini_json = self._extract_and_parse_json(raw_response)
        
        # Convert to standardized format
        return {
            'metadata': {
                'client_name': client_name or 'Unknown',
                'generated_at': datetime.now().isoformat(),
                'source': 'gemini_json',
                'raw_response_length': len(raw_response),
                'parsing_success': True,
                'insight_count': self._count_insights(gemini_json)
            },
            'executive_summary': self._parse_executive_summary(gemini_json.get('executive_summary', {})),
            'scaling_opportunities': self._parse_scaling_opportunities(gemini_json.get('scaling_opportunities', [])),
            'underperformers': self._parse_underperformers(gemini_json.get('underperformers', [])),
            'budget_reallocations': self._parse_budget_reallocations(gemini_json.get('budget_reallocations', [])),
            'trend_insights': self._parse_trend_insights(gemini_json.get('trend_insights', [])),
            'additional_insights': []  # Not needed with structured JSON
        }
    
    def _save_raw_response(self, raw_response: str, client_name: str):
        """Save raw response for debugging"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            client = (client_name or 'unknown').lower().replace(' ', '_')
            filename = f"{client}_gemini_raw_{timestamp}.txt"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Gemini Raw Response - {client_name}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Length: {len(raw_response)} characters\n")
                f.write("="*60 + "\n\n")
                f.write(raw_response)
            
            print(f"💾 Raw response saved: {filename}")
            
        except Exception as e:
            print(f"⚠️  Could not save raw response: {e}")
    
    def _extract_and_parse_json(self, response: str) -> Dict[str, Any]:
        """Extract and parse JSON from response"""
        
        # Clean response - remove markdown, extra text
        cleaned = self._clean_response(response)
        
        # Attempt to parse JSON
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Try to repair common JSON issues
            repaired = self._repair_json(cleaned)
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                raise ValueError(f"Cannot parse Gemini JSON response. Error: {e}")
    
    def _clean_response(self, response: str) -> str:
        """Clean response to extract pure JSON"""
        
        # Remove markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        # Find JSON boundaries
        start = response.find('{')
        if start == -1:
            raise ValueError("No JSON object found in response")
        
        # Find matching closing brace
        brace_count = 0
        end = -1
        
        for i, char in enumerate(response[start:], start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        
        if end == -1:
            raise ValueError("Incomplete JSON object in response")
        
        return response[start:end].strip()
    
    def _repair_json(self, json_str: str) -> str:
        """Attempt to repair common JSON issues"""
        
        # Fix trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # Fix unescaped quotes (basic attempt)
        # This is a simple fix - more complex cases might still fail
        json_str = re.sub(r'(?<!\\)"(?=[^"]*"[^"]*:)', '\\"', json_str)
        
        return json_str
    
    def _parse_executive_summary(self, summary_json: Dict[str, Any]) -> Dict[str, Any]:
        """Parse executive summary section"""
        return {
            'summary': summary_json.get('summary', 'No executive summary provided'),
            'confidence': summary_json.get('confidence', 'Medium'),
            'urgency_level': summary_json.get('urgency', 'Medium'),
            'key_themes': []  # Could extract from summary text if needed
        }
    
    def _parse_scaling_opportunities(self, opportunities_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse scaling opportunities"""
        opportunities = []
        
        for opp in opportunities_json:
            opportunities.append({
                'priority': opp.get('priority', 999),
                'station': opp.get('entity') if opp.get('entity_type') == 'station' else None,
                'daypart': opp.get('entity') if opp.get('entity_type') == 'daypart' else None,
                'recommendation': opp.get('recommendation', ''),
                'action_type': opp.get('action_type', 'monitor'),
                'projected_impact': opp.get('projected_impact', ''),
                'confidence': opp.get('confidence', 'Medium'),
                'business_rationale': opp.get('business_rationale', '')
            })
        
        return sorted(opportunities, key=lambda x: x['priority'])
    
    def _parse_underperformers(self, underperformers_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse underperformers"""
        underperformers = []
        
        for under in underperformers_json:
            underperformers.append({
                'entity': under.get('entity', 'Unknown'),
                'issue': under.get('issue', ''),
                'entity_type': under.get('entity_type', 'unknown'),
                'severity': under.get('severity', 'Medium'),
                'recommended_action': under.get('recommended_action', 'investigate'),
                'business_rationale': under.get('business_rationale', '')
            })
        
        return underperformers
    
    def _parse_budget_reallocations(self, reallocations_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse budget reallocations"""
        reallocations = []
        
        for realloc in reallocations_json:
            reallocations.append({
                'from_station': realloc.get('from_entity', ''),
                'to_station': realloc.get('to_entity', ''),
                'spots_to_move': realloc.get('spots_to_move', 0),
                'projected_impact': realloc.get('projected_impact', ''),
                'confidence': realloc.get('confidence', 'Medium'),
                'implementation_priority': realloc.get('implementation_priority', 'Medium')
            })
        
        return reallocations
    
    def _parse_trend_insights(self, trends_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse trend insights"""
        trends = []
        
        for trend in trends_json:
            trends.append({
                'trend_description': trend.get('trend_description', ''),
                'trend_direction': trend.get('trend_direction', 'stable'),
                'entity': trend.get('entity', ''),
                'urgency': trend.get('urgency', 'Medium'),
                'recommended_response': trend.get('recommended_response', 'monitor')
            })
        
        return trends
    
    def _count_insights(self, gemini_json: Dict[str, Any]) -> int:
        """Count total insights in JSON response"""
        count = 0
        count += len(gemini_json.get('scaling_opportunities', []))
        count += len(gemini_json.get('underperformers', []))
        count += len(gemini_json.get('budget_reallocations', []))
        count += len(gemini_json.get('trend_insights', []))
        return count


# Test the clean parser
if __name__ == "__main__":
    print("🧪 Testing Clean JSON Insight Parser...")
    
    # Sample JSON response
    sample_response = '''
    {
      "executive_summary": {
        "summary": "Campaign performing well with TOP_STATION at 4.2 visits/spot efficiency",
        "confidence": "High",
        "urgency": "Medium"
      },
      "scaling_opportunities": [
        {
          "priority": 1,
          "entity": "TOP_STATION",
          "entity_type": "station",
          "action_type": "scale_up",
          "recommendation": "Increase TOP_STATION budget by 25%",
          "projected_impact": "15% efficiency gain",
          "confidence": "High",
          "business_rationale": "Proven high performance"
        }
      ],
      "underperformers": [
        {
          "entity": "WEAK_STATION",
          "entity_type": "station",
          "issue": "Performance 50% below average",
          "severity": "High",
          "recommended_action": "reduce",
          "business_rationale": "Consistent underperformance"
        }
      ],
      "budget_reallocations": [
        {
          "from_entity": "WEAK_STATION",
          "to_entity": "TOP_STATION",
          "spots_to_move": 15,
          "projected_impact": "45 additional visits",
          "confidence": "High",
          "implementation_priority": "High"
        }
      ],
      "trend_insights": [
        {
          "trend_description": "Efficiency increasing 12% week-over-week",
          "trend_direction": "positive",
          "entity": "Campaign",
          "urgency": "Medium",
          "recommended_response": "capitalize"
        }
      ]
    }
    '''
    
    try:
        parser = InsightParser()
        insights = parser.parse_gemini_response(sample_response, "TEST_CLIENT")
        
        print(f"✅ Parsing successful")
        print(f"📊 Total insights: {insights['metadata']['insight_count']}")
        print(f"📋 Executive summary: {bool(insights['executive_summary']['summary'])}")
        print(f"🚀 Scaling opportunities: {len(insights['scaling_opportunities'])}")
        print(f"⚠️  Underperformers: {len(insights['underperformers'])}")
        print(f"💰 Budget reallocations: {len(insights['budget_reallocations'])}")
        print(f"📈 Trend insights: {len(insights['trend_insights'])}")
        
        print("\n✅ Clean JSON parser test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()