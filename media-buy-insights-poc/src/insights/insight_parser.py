"""
Insight Parser - Clean JSON Response Processing  
Parses Gemini's JSON response into structured insights for Power BI
Hybrid approach: structured parsing for known categories + dynamic fallback
"""

import json
import re
import os
from typing import Dict, Any, List
from datetime import datetime

class InsightParser:
    """Clean JSON parser with hybrid processing for comprehensive insight capture"""
    
    def __init__(self, output_dir: str = "output/reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def parse_gemini_response(self, raw_response: str, client_name: str = None) -> Dict[str, Any]:
        """Parse Gemini's JSON response with hybrid approach"""
        
        # Save raw response for debugging
        self._save_raw_response(raw_response, client_name)
        
        # Extract and parse JSON
        gemini_json = self._extract_and_parse_json(raw_response)
        
        # Process known categories with structured parsing
        structured_insights = {
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
            'additional_insights': []
        }
        
        # Known categories that have structured parsing
        known_categories = {
            'executive_summary', 'scaling_opportunities', 'underperformers', 
            'budget_reallocations', 'trend_insights'
        }
        
        # Process any additional categories dynamically
        for category_name, category_data in gemini_json.items():
            if category_name not in known_categories and isinstance(category_data, list):
                # Use dynamic processing for unknown categories
                structured_insights[category_name] = self._parse_dynamic_category(category_data, category_name)
                print(f"🔄 Dynamically processed category: {category_name} ({len(category_data)} insights)")
        
        # Update insight count to include dynamic categories
        structured_insights['metadata']['insight_count'] = self._count_all_insights(structured_insights)
        
        return structured_insights
    
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
        json_str = re.sub(r'(?<!\\)"(?=[^"]*"[^"]*:)', '\\"', json_str)
        
        return json_str
    
    # Structured parsing methods for known categories
    def _parse_executive_summary(self, summary_json: Dict[str, Any]) -> Dict[str, Any]:
        """Parse executive summary section"""
        return {
            'summary': summary_json.get('summary', 'No executive summary provided'),
            'confidence': summary_json.get('confidence', 'Medium'),
            'urgency_level': summary_json.get('urgency', 'Medium'),
            'recent_momentum': summary_json.get('recent_momentum', 'stable')
        }
    
    def _parse_scaling_opportunities(self, opportunities_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse scaling opportunities"""
        opportunities = []
        
        for opp in opportunities_json:
            opportunities.append({
                'priority': opp.get('priority', 999),
                'entity': opp.get('entity', 'Unknown'),
                'optimization_scenario': opp.get('optimization_scenario', 'standard'),
                'current_weekly_spots': opp.get('current_weekly_spots', 0),
                'recommended_weekly_increase': opp.get('recommended_weekly_increase', 0),
                'action_type': opp.get('action_type', 'scale_up'),
                'recommendation': opp.get('recommendation', ''),
                'projected_weekly_impact': opp.get('projected_weekly_impact', ''),
                'confidence': opp.get('confidence', 'Medium'),
                'risk_level': opp.get('risk_level', 'Medium'),
                'business_rationale': opp.get('business_rationale', '')
            })
        
        return sorted(opportunities, key=lambda x: x['priority'])
    
    def _parse_underperformers(self, underperformers_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse underperformers"""
        underperformers = []
        
        for under in underperformers_json:
            underperformers.append({
                'entity': under.get('entity', 'Unknown'),
                'current_weekly_spots': under.get('current_weekly_spots', 0),
                'weeks_of_poor_performance': under.get('weeks_of_poor_performance', 0),
                'issue': under.get('issue', ''),
                'severity': under.get('severity', 'Medium'),
                'recommended_weekly_reduction': under.get('recommended_weekly_reduction', 0),
                'recommended_action': under.get('recommended_action', 'investigate'),
                'potential_cause': under.get('potential_cause', ''),
                'business_rationale': under.get('business_rationale', '')
            })
        
        return underperformers
    
    def _parse_budget_reallocations(self, reallocations_json: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse budget reallocations"""
        reallocations = []
        
        for realloc in reallocations_json:
            reallocations.append({
                'scenario_type': realloc.get('scenario_type', 'standard'),
                'from_entity': realloc.get('from_entity', ''),
                'to_entity': realloc.get('to_entity', ''),
                'weekly_spots_to_move': realloc.get('weekly_spots_to_move', 0),
                'current_from_weekly_spots': realloc.get('current_from_weekly_spots', 0),
                'current_to_weekly_spots': realloc.get('current_to_weekly_spots', 0),
                'projected_weekly_impact': realloc.get('projected_weekly_impact', ''),
                'confidence': realloc.get('confidence', 'Medium'),
                'implementation_priority': realloc.get('implementation_priority', 'Medium'),
                'percentage_change_from': realloc.get('percentage_change_from', ''),
                'percentage_change_to': realloc.get('percentage_change_to', ''),
                'risk_assessment': realloc.get('risk_assessment', '')
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
                'weeks_observed': trend.get('weeks_observed', 0),
                'urgency': trend.get('urgency', 'Medium'),
                'weekly_impact': trend.get('weekly_impact', ''),
                'recommended_response': trend.get('recommended_response', 'monitor')
            })
        
        return trends
    
    # Dynamic processing methods
    def _parse_dynamic_category(self, category_data: List[Dict[str, Any]], category_name: str) -> List[Dict[str, Any]]:
        """Dynamically parse any category not handled by structured methods"""
        
        parsed_insights = []
        
        for insight in category_data:
            if not isinstance(insight, dict):
                continue
            
            # Extract entity intelligently from various possible fields
            entity_info = self._extract_entity_from_insight(insight)
            
            # Build recommendation text from available fields
            recommendation_text = self._build_recommendation_text(insight)
            
            # Extract standard fields with intelligent defaults
            parsed_insight = {
                'entity': entity_info.get('entity', 'Unknown'),
                'station': entity_info.get('station'),
                'daypart': entity_info.get('daypart'),
                'recommendation': recommendation_text,
                'priority': insight.get('priority', 999),
                'confidence': insight.get('confidence', 'Medium'),
                'urgency': insight.get('urgency', 'Medium'),
                'category_type': category_name,
                'raw_data': insight  # Preserve original for reference
            }
            
            # Add category-specific fields if available
            self._add_category_specific_fields(parsed_insight, insight, category_name)
            
            parsed_insights.append(parsed_insight)
        
        return parsed_insights
    
    def _extract_entity_from_insight(self, insight: Dict[str, Any]) -> Dict[str, str]:
        """Extract entity information from any insight object"""
        
        # Try common entity field names
        entity_fields = ['entity', 'station', 'from_entity', 'to_entity', 'target_entities', 'affected_entities']
        
        station = None
        daypart = None
        entity = None
        
        for field in entity_fields:
            if field in insight and insight[field]:
                entity_value = insight[field]
                
                # Handle list of entities (take first one)
                if isinstance(entity_value, list) and entity_value:
                    entity_value = entity_value[0]
                
                if isinstance(entity_value, str):
                    entity = entity_value
                    break
        
        # Parse entity into station and daypart
        if entity:
            if '_' in entity:
                parts = entity.split('_', 1)
                station = parts[0]
                daypart = parts[1] if len(parts) > 1 else None
            elif ' ' in entity:
                parts = entity.split(' ', 1)
                station = parts[0]
                daypart = parts[1] if len(parts) > 1 else None
            else:
                station = entity
        
        # Try to extract station/daypart from separate fields
        if not station:
            station = insight.get('station')
        if not daypart:
            daypart = insight.get('daypart')
        
        return {
            'entity': entity or f"{station or 'Unknown'}_{daypart or ''}".strip('_'),
            'station': station,
            'daypart': daypart
        }
    
    def _build_recommendation_text(self, insight: Dict[str, Any]) -> str:
        """Build comprehensive recommendation text from available fields"""
        
        # Try common text fields in order of preference
        text_fields = [
            'recommendation', 'description', 'opportunity_description', 
            'trend_description', 'issue', 'hypothesis', 'pattern_type'
        ]
        
        main_text = ""
        for field in text_fields:
            if field in insight and insight[field]:
                main_text = str(insight[field])
                break
        
        # Add additional context from other fields
        additional_info = []
        
        # Add numeric recommendations
        numeric_fields = [
            'recommended_weekly_increase', 'recommended_weekly_reduction',
            'weekly_spots_to_move', 'weekly_spots_to_shift', 'current_weekly_spots'
        ]
        
        for field in numeric_fields:
            if field in insight and insight[field]:
                additional_info.append(f"{field.replace('_', ' ')}: {insight[field]}")
        
        # Add impact/projection info
        impact_fields = [
            'projected_impact', 'projected_weekly_impact', 'projected_efficiency_gain',
            'potential_impact', 'weekly_impact'
        ]
        
        for field in impact_fields:
            if field in insight and insight[field]:
                additional_info.append(f"Impact: {insight[field]}")
                break
        
        # Add rationale if available
        rationale_fields = ['business_rationale', 'rationale', 'evidence', 'characteristics']
        for field in rationale_fields:
            if field in insight and insight[field]:
                additional_info.append(f"Rationale: {insight[field]}")
                break
        
        # Combine main text with additional info
        if additional_info:
            recommendation = f"{main_text}. {'. '.join(additional_info)}"
        else:
            recommendation = main_text or "Insight identified from campaign analysis"
        
        return recommendation
    
    def _add_category_specific_fields(self, parsed_insight: Dict[str, Any], raw_insight: Dict[str, Any], category_name: str):
        """Add category-specific fields based on category type"""
        
        # Add fields based on category patterns
        if 'scaling' in category_name.lower():
            parsed_insight['action_type'] = raw_insight.get('action_type', 'scale_up')
            parsed_insight['projected_impact'] = raw_insight.get('projected_weekly_impact', raw_insight.get('projected_impact'))
            
        elif 'underperform' in category_name.lower():
            parsed_insight['severity'] = raw_insight.get('severity', 'Medium')
            parsed_insight['recommended_action'] = raw_insight.get('recommended_action', 'investigate')
            parsed_insight['weeks_of_poor_performance'] = raw_insight.get('weeks_of_poor_performance', 0)
            
        elif 'reallocation' in category_name.lower() or 'budget' in category_name.lower():
            parsed_insight['from_entity'] = raw_insight.get('from_entity')
            parsed_insight['to_entity'] = raw_insight.get('to_entity')
            parsed_insight['spots_to_move'] = raw_insight.get('weekly_spots_to_move', raw_insight.get('spots_to_move'))
            
        elif 'daypart' in category_name.lower():
            parsed_insight['from_daypart'] = raw_insight.get('from_daypart')
            parsed_insight['to_daypart'] = raw_insight.get('to_daypart')
            
        elif 'risk' in category_name.lower():
            parsed_insight['risk_type'] = raw_insight.get('risk_type')
            parsed_insight['mitigation_strategy'] = raw_insight.get('mitigation_strategy')
            
        elif 'trend' in category_name.lower():
            parsed_insight['trend_direction'] = raw_insight.get('trend_direction', 'stable')
            parsed_insight['weeks_observed'] = raw_insight.get('weeks_observed', 0)
    
    # Utility methods
    def _count_insights(self, gemini_json: Dict[str, Any]) -> int:
        """Count total insights in raw Gemini JSON response"""
        count = 0
        for key, value in gemini_json.items():
            if isinstance(value, list):
                count += len(value)
            elif key == 'executive_summary' and isinstance(value, dict) and value.get('summary'):
                count += 1
        return count
    
    def _count_all_insights(self, structured_insights: Dict[str, Any]) -> int:
        """Count total insights across all categories"""
        count = 0
        
        for key, value in structured_insights.items():
            if key == 'metadata':
                continue
            elif key == 'executive_summary' and value.get('summary'):
                count += 1
            elif isinstance(value, list):
                count += len(value)
        
        return count


# Test the clean parser
if __name__ == "__main__":
    print("🧪 Testing Hybrid JSON Insight Parser...")
    
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
          "entity": "TOP_STATION_PRIME",
          "optimization_scenario": "aggressive",
          "recommended_weekly_increase": 8,
          "confidence": "High"
        }
      ],
      "daypart_shifting": [
        {
          "station": "MID_STATION",
          "from_daypart": "LATE",
          "to_daypart": "PRIME",
          "weekly_spots_to_shift": 5
        }
      ]
    }
    '''
    
    try:
        parser = InsightParser()
        insights = parser.parse_gemini_response(sample_response, "TEST_CLIENT")
        
        print(f"✅ Parsing successful")
        print(f"📊 Total insights: {insights['metadata']['insight_count']}")
        print(f"📋 Categories found: {list(insights.keys())}")
        
        print("\n✅ Hybrid JSON parser test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    def parse_gemini_response(self, raw_response: str, client_name: str = None) -> Dict[str, Any]:
        """
        Parse Gemini's JSON response into structured insights with dynamic fallback
        
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
        
        # Process known categories with structured parsing
        structured_insights = {
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
            'additional_insights': []
        }
        
        # Known categories that have structured parsing
        known_categories = {
            'executive_summary', 'scaling_opportunities', 'underperformers', 
            'budget_reallocations', 'trend_insights'
        }
        
        # Process any additional categories dynamically
        for category_name, category_data in gemini_json.items():
            if category_name not in known_categories and isinstance(category_data, list):
                # Use dynamic processing for unknown categories
                structured_insights[category_name] = self._parse_dynamic_category(category_data, category_name)
                print(f"🔄 Dynamically processed category: {category_name} ({len(category_data)} insights)")
        
        # Update insight count to include dynamic categories
        structured_insights['metadata']['insight_count'] = self._count_all_insights(structured_insights)
        
        return structured_insights
    
    def _count_insights(self, gemini_json: Dict[str, Any]) -> int:
        """Count total insights in raw Gemini JSON response"""
        count = 0
        for key, value in gemini_json.items():
            if isinstance(value, list):
                count += len(value)
            elif key == 'executive_summary' and isinstance(value, dict) and value.get('summary'):
                count += 1
        return count
    
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
    
    def _parse_dynamic_category(self, category_data: List[Dict[str, Any]], category_name: str) -> List[Dict[str, Any]]:
        """
        Dynamically parse any category not handled by structured methods
        
        Args:
            category_data: List of insight objects from Gemini
            category_name: Name of the category
            
        Returns:
            Standardized list of insights
        """
        
        parsed_insights = []
        
        for insight in category_data:
            if not isinstance(insight, dict):
                continue
            
            # Extract entity intelligently from various possible fields
            entity_info = self._extract_entity_from_insight(insight)
            
            # Build recommendation text from available fields
            recommendation_text = self._build_recommendation_text(insight)
            
            # Extract standard fields with intelligent defaults
            parsed_insight = {
                'entity': entity_info.get('entity', 'Unknown'),
                'station': entity_info.get('station'),
                'daypart': entity_info.get('daypart'),
                'recommendation': recommendation_text,
                'priority': insight.get('priority', 999),
                'confidence': insight.get('confidence', 'Medium'),
                'urgency': insight.get('urgency', 'Medium'),
                'category_type': category_name,
                'raw_data': insight  # Preserve original for reference
            }
            
            # Add category-specific fields if available
            self._add_category_specific_fields(parsed_insight, insight, category_name)
            
            parsed_insights.append(parsed_insight)
        
        return parsed_insights
    
    def _extract_entity_from_insight(self, insight: Dict[str, Any]) -> Dict[str, str]:
        """Extract entity information from any insight object"""
        
        # Try common entity field names
        entity_fields = ['entity', 'station', 'from_entity', 'to_entity', 'target_entities', 'affected_entities']
        
        station = None
        daypart = None
        entity = None
        
        for field in entity_fields:
            if field in insight and insight[field]:
                entity_value = insight[field]
                
                # Handle list of entities (take first one)
                if isinstance(entity_value, list) and entity_value:
                    entity_value = entity_value[0]
                
                if isinstance(entity_value, str):
                    entity = entity_value
                    break
        
        # Parse entity into station and daypart
        if entity:
            if '_' in entity:
                parts = entity.split('_', 1)
                station = parts[0]
                daypart = parts[1] if len(parts) > 1 else None
            elif ' ' in entity:
                parts = entity.split(' ', 1)
                station = parts[0]
                daypart = parts[1] if len(parts) > 1 else None
            else:
                station = entity
        
        # Try to extract station/daypart from separate fields
        if not station:
            station = insight.get('station')
        if not daypart:
            daypart = insight.get('daypart')
        
        return {
            'entity': entity or f"{station or 'Unknown'}_{daypart or ''}".strip('_'),
            'station': station,
            'daypart': daypart
        }
    
    def _build_recommendation_text(self, insight: Dict[str, Any]) -> str:
        """Build comprehensive recommendation text from available fields"""
        
        # Try common text fields in order of preference
        text_fields = [
            'recommendation', 'description', 'opportunity_description', 
            'trend_description', 'issue', 'hypothesis', 'pattern_type'
        ]
        
        main_text = ""
        for field in text_fields:
            if field in insight and insight[field]:
                main_text = str(insight[field])
                break
        
        # Add additional context from other fields
        additional_info = []
        
        # Add numeric recommendations
        numeric_fields = [
            'recommended_weekly_increase', 'recommended_weekly_reduction',
            'weekly_spots_to_move', 'weekly_spots_to_shift', 'current_weekly_spots'
        ]
        
        for field in numeric_fields:
            if field in insight and insight[field]:
                additional_info.append(f"{field.replace('_', ' ')}: {insight[field]}")
        
        # Add impact/projection info
        impact_fields = [
            'projected_impact', 'projected_weekly_impact', 'projected_efficiency_gain',
            'potential_impact', 'weekly_impact'
        ]
        
        for field in impact_fields:
            if field in insight and insight[field]:
                additional_info.append(f"Impact: {insight[field]}")
                break
        
        # Add rationale if available
        rationale_fields = ['business_rationale', 'rationale', 'evidence', 'characteristics']
        for field in rationale_fields:
            if field in insight and insight[field]:
                additional_info.append(f"Rationale: {insight[field]}")
                break
        
        # Combine main text with additional info
        if additional_info:
            recommendation = f"{main_text}. {'. '.join(additional_info)}"
        else:
            recommendation = main_text or "Insight identified from campaign analysis"
        
        return recommendation
    
    def _add_category_specific_fields(self, parsed_insight: Dict[str, Any], raw_insight: Dict[str, Any], category_name: str):
        """Add category-specific fields based on category type"""
        
        # Add fields based on category patterns
        if 'scaling' in category_name.lower():
            parsed_insight['action_type'] = raw_insight.get('action_type', 'scale_up')
            parsed_insight['projected_impact'] = raw_insight.get('projected_weekly_impact', raw_insight.get('projected_impact'))
            
        elif 'underperform' in category_name.lower():
            parsed_insight['severity'] = raw_insight.get('severity', 'Medium')
            parsed_insight['recommended_action'] = raw_insight.get('recommended_action', 'investigate')
            parsed_insight['weeks_of_poor_performance'] = raw_insight.get('weeks_of_poor_performance', 0)
            
        elif 'reallocation' in category_name.lower() or 'budget' in category_name.lower():
            parsed_insight['from_entity'] = raw_insight.get('from_entity')
            parsed_insight['to_entity'] = raw_insight.get('to_entity')
            parsed_insight['spots_to_move'] = raw_insight.get('weekly_spots_to_move', raw_insight.get('spots_to_move'))
            
        elif 'daypart' in category_name.lower():
            parsed_insight['from_daypart'] = raw_insight.get('from_daypart')
            parsed_insight['to_daypart'] = raw_insight.get('to_daypart')
            
        elif 'risk' in category_name.lower():
            parsed_insight['risk_type'] = raw_insight.get('risk_type')
            parsed_insight['mitigation_strategy'] = raw_insight.get('mitigation_strategy')
            
        elif 'trend' in category_name.lower():
            parsed_insight['trend_direction'] = raw_insight.get('trend_direction', 'stable')
            parsed_insight['weeks_observed'] = raw_insight.get('weeks_observed', 0)
    
    def _count_all_insights(self, structured_insights: Dict[str, Any]) -> int:
        """Count total insights across all categories"""
        count = 0
        
        for key, value in structured_insights.items():
            if key == 'metadata':
                continue
            elif key == 'executive_summary' and value.get('summary'):
                count += 1
            elif isinstance(value, list):
                count += len(value)
        
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