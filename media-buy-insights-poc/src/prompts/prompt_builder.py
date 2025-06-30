"""
Campaign Prompt Builder - Clean JSON-Focused Prompts
Builds structured prompts for Gemini with JSON schema requirements
"""

from typing import Dict, Any

class CampaignPromptBuilder:
    """Builds JSON-structured prompts for TV campaign analysis"""
    
    def build_analysis_prompt(self, kpis: Dict[str, Any], client_name: str = None) -> str:
        """
        Build comprehensive campaign analysis prompt with JSON schema
        
        Args:
            kpis: KPI data from KPICalculator
            client_name: Name of client being analyzed
            
        Returns:
            Formatted prompt with JSON schema for Gemini
        """
        
        campaign_overview = self._format_campaign_overview(kpis, client_name)
        station_table = self._format_station_table(kpis)
        daypart_table = self._format_daypart_table(kpis)
        weekly_trends = self._format_weekly_trends(kpis)
        json_schema = self._get_json_schema()
        
        return f"""{campaign_overview}

{station_table}

{daypart_table}

{weekly_trends}

ANALYSIS TASK:
You are an expert TV media buying analyst. Analyze the campaign data above and provide actionable insights for media buyers.

CRITICAL: Respond with ONLY valid JSON in this exact format. No markdown, explanations, or additional text.

{json_schema}

Rules:
1. Use exact station/daypart names from the tables above
2. Provide specific, quantified recommendations
3. Focus on actionable budget allocation decisions
4. Ensure all JSON fields are properly formatted"""
    
    def _format_campaign_overview(self, kpis: Dict[str, Any], client_name: str) -> str:
        """Format campaign overview section"""
        
        metadata = kpis.get('metadata', {})
        totals = kpis.get('totals', {})
        efficiency = kpis.get('efficiency', {})
        
        # Safe value extraction
        total_spots = totals.get('total_spots', 0) or 0
        total_visits = totals.get('total_visits', 0) or 0
        total_cost = totals.get('total_cost', 0) or 0
        total_revenue = totals.get('total_revenue', 0) or 0
        
        visits_per_spot = total_visits / max(total_spots, 1)
        
        # Date range
        date_range = metadata.get('date_range', {})
        start_date = date_range.get('start_date', 'Unknown')
        end_date = date_range.get('end_date', 'Unknown')
        
        overview = f"""CAMPAIGN OVERVIEW - {client_name or 'Unknown'}
Period: {start_date} to {end_date}
Total Spots: {total_spots:,} | Visits: {total_visits:,} | Efficiency: {visits_per_spot:.2f} visits/spot
Investment: ${total_cost:,.0f}"""

        if total_revenue and total_revenue > 0:
            roas = efficiency.get('roas', 0) or 0
            overview += f" | Revenue: ${total_revenue:,.0f} | ROAS: {roas:.2f}x"
        
        return overview
    
    def _format_station_table(self, kpis: Dict[str, Any]) -> str:
        """Format station performance table"""
        
        dimensional = kpis.get('dimensional_analysis', {})
        station_data = dimensional.get('station_performance', [])
        
        if not station_data:
            return "STATION PERFORMANCE: No data available"
        
        table = """STATION PERFORMANCE:
Station      | Visits | Spots | Efficiency | Cost      | Ranking
-------------|--------|-------|------------|-----------|--------"""
        
        for i, station in enumerate(station_data[:10], 1):
            name = (station.get('station') or 'Unknown')[:11].ljust(11)
            visits = station.get('total_visits', 0) or 0
            spots = station.get('spots', 0) or 0
            efficiency = station.get('avg_visits_per_spot', 0) or 0
            cost = station.get('total_cost', 0) or 0
            
            ranking = "Top" if i <= 3 else "Good" if i <= 6 else "Weak"
            
            table += f"\n{name} | {visits:6,} | {spots:5} | {efficiency:10.1f} | ${cost:8,.0f} | {ranking}"
        
        return table
    
    def _format_daypart_table(self, kpis: Dict[str, Any]) -> str:
        """Format daypart performance table"""
        
        dimensional = kpis.get('dimensional_analysis', {})
        daypart_data = dimensional.get('daypart_performance', [])
        
        if not daypart_data:
            return "DAYPART PERFORMANCE: No data available"
        
        table = """DAYPART PERFORMANCE:
Daypart  | Visits | Spots | Efficiency | Cost      | Priority
---------|--------|-------|------------|-----------|----------"""
        
        for daypart in daypart_data:
            name = (daypart.get('daypart') or 'Unknown')[:8].ljust(8)
            visits = daypart.get('total_visits', 0) or 0
            spots = daypart.get('spots', 0) or 0
            efficiency = daypart.get('avg_visits_per_spot', 0) or 0
            cost = daypart.get('total_cost', 0) or 0
            
            priority = "High" if efficiency >= 30 else "Medium" if efficiency >= 15 else "Low"
            
            table += f"\n{name} | {visits:6,} | {spots:5} | {efficiency:10.1f} | ${cost:8,.0f} | {priority}"
        
        return table
    
    def _format_weekly_trends(self, kpis: Dict[str, Any]) -> str:
        """Format weekly trend analysis"""
        
        time_patterns = kpis.get('time_patterns', {})
        daily_trends = time_patterns.get('daily_trends', [])
        
        if not daily_trends or len(daily_trends) < 14:
            return "WEEKLY TRENDS: Insufficient data for trend analysis"
        
        # Simple week-over-week calculation
        recent_week = daily_trends[-7:]
        previous_week = daily_trends[-14:-7]
        
        recent_efficiency = sum(d.get('visits', 0) for d in recent_week) / max(sum(d.get('spots', 1) for d in recent_week), 1)
        prev_efficiency = sum(d.get('visits', 0) for d in previous_week) / max(sum(d.get('spots', 1) for d in previous_week), 1)
        
        efficiency_change = ((recent_efficiency - prev_efficiency) / max(prev_efficiency, 1)) * 100
        
        trend_direction = "Improving" if efficiency_change > 5 else "Declining" if efficiency_change < -5 else "Stable"
        
        return f"""WEEKLY TRENDS:
Recent Week Efficiency: {recent_efficiency:.1f} visits/spot
Previous Week Efficiency: {prev_efficiency:.1f} visits/spot
Week-over-Week Change: {efficiency_change:+.1f}%
Trend Direction: {trend_direction}"""
    
    def _get_json_schema(self) -> str:
        """Get the required JSON schema"""
        return """{
  "executive_summary": {
    "summary": "2-3 sentence campaign assessment focusing on key opportunities and issues",
    "confidence": "High|Medium|Low",
    "urgency": "High|Medium|Low"
  },
  "scaling_opportunities": [
    {
      "priority": 1,
      "entity": "EXACT_STATION_OR_DAYPART_NAME",
      "entity_type": "station|daypart",
      "action_type": "scale_up|test|investigate",
      "recommendation": "Specific actionable recommendation",
      "projected_impact": "Quantified benefit (e.g., '15% efficiency gain', '50 more visits')",
      "confidence": "High|Medium|Low",
      "business_rationale": "Why this opportunity exists"
    }
  ],
  "underperformers": [
    {
      "entity": "EXACT_STATION_OR_DAYPART_NAME",
      "entity_type": "station|daypart",
      "issue": "Specific performance problem",
      "severity": "High|Medium|Low", 
      "recommended_action": "reduce|optimize|eliminate|investigate",
      "business_rationale": "Why action is needed"
    }
  ],
  "budget_reallocations": [
    {
      "from_entity": "SOURCE_STATION",
      "to_entity": "TARGET_STATION",
      "spots_to_move": 15,
      "projected_impact": "Expected improvement",
      "confidence": "High|Medium|Low",
      "implementation_priority": "High|Medium|Low"
    }
  ],
  "trend_insights": [
    {
      "trend_description": "Observed trend with specifics",
      "trend_direction": "positive|negative|stable",
      "entity": "Station/daypart/campaign affected",
      "urgency": "High|Medium|Low",
      "recommended_response": "capitalize|monitor|correct|investigate"
    }
  ]
}"""


# Test the clean prompt builder
if __name__ == "__main__":
    print("🧪 Testing Clean Prompt Builder...")
    
    # Sample KPI data
    sample_kpis = {
        'metadata': {
            'date_range': {'start_date': '2025-06-01', 'end_date': '2025-06-27'}
        },
        'totals': {
            'total_spots': 500,
            'total_visits': 1250,
            'total_cost': 125000,
            'total_revenue': 62500
        },
        'efficiency': {
            'roas': 0.5
        },
        'dimensional_analysis': {
            'station_performance': [
                {'station': 'TOP_STATION', 'total_visits': 400, 'spots': 100, 'avg_visits_per_spot': 4.0, 'total_cost': 25000},
                {'station': 'WEAK_STATION', 'total_visits': 150, 'spots': 100, 'avg_visits_per_spot': 1.5, 'total_cost': 20000}
            ],
            'daypart_performance': [
                {'daypart': 'PRIME', 'total_visits': 600, 'spots': 150, 'avg_visits_per_spot': 4.0, 'total_cost': 30000}
            ]
        },
        'time_patterns': {
            'daily_trends': [
                {'spots': 20, 'visits': 50}, {'spots': 22, 'visits': 55},
                {'spots': 18, 'visits': 45}, {'spots': 25, 'visits': 62},
                {'spots': 23, 'visits': 58}, {'spots': 21, 'visits': 52},
                {'spots': 24, 'visits': 60}, {'spots': 26, 'visits': 65},
                {'spots': 24, 'visits': 60}, {'spots': 27, 'visits': 68},
                {'spots': 25, 'visits': 62}, {'spots': 28, 'visits': 70},
                {'spots': 26, 'visits': 65}, {'spots': 29, 'visits': 72}
            ]
        }
    }
    
    try:
        builder = CampaignPromptBuilder()
        prompt = builder.build_analysis_prompt(sample_kpis, "TEST_CLIENT")
        
        print(f"✅ Prompt generated ({len(prompt):,} characters)")
        
        # Check for required sections
        required = ["CAMPAIGN OVERVIEW", "STATION PERFORMANCE", "DAYPART PERFORMANCE", "JSON"]
        missing = [section for section in required if section not in prompt]
        
        if missing:
            print(f"⚠️  Missing sections: {missing}")
        else:
            print("✅ All required sections present")
        
        print("✅ Clean prompt builder test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()