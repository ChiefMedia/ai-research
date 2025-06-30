"""
Campaign Prompt Builder - Clean JSON-Focused Prompts
Builds structured prompts for Gemini with JSON schema requirements
"""

from typing import Dict, Any

class CampaignPromptBuilder:
    """Builds JSON-structured prompts for TV campaign analysis"""
    
    def build_analysis_prompt(self, kpis: Dict[str, Any], client_name: str = None) -> str:
        """Build comprehensive campaign analysis prompt with JSON schema"""
        
        campaign_overview = self._format_campaign_overview(kpis, client_name)
        recency_performance = self._format_recency_weighted_performance(kpis)
        station_daypart_breakdown = self._format_station_daypart_breakdown(kpis)
        json_schema = self._get_enhanced_json_schema()
        
        return f"""{campaign_overview}

{recency_performance}

{station_daypart_breakdown}

ANALYSIS TASK - COMPREHENSIVE MEDIA BUYER OPTIMIZATION:
You are an expert TV media buying analyst. Analyze the campaign data above and provide comprehensive actionable insights. Generate 20-30 total recommendations across multiple categories and scenarios.

CRITICAL INSTRUCTIONS:
1. RECENCY WEIGHTING: Prioritize the most recent 7 days heavily when making decisions. Use weeks 2-3+ for confirmation of trends only.
2. SAMPLE SIZE REQUIREMENTS: Only recommend actions for entities with 30+ spots (high confidence) or 10+ spots (medium confidence). Ignore entities with <10 spots.
3. WEEKLY SPOT REALLOCATION: All recommendations must specify exact weekly spot movements (e.g., "move 12 spots per week from STATION_X LATE to STATION_Y PRIME").
4. BUDGET NEUTRAL: All reallocations must sum to zero net change in total weekly spots. Specify exact sources and destinations.
5. DAYPART SPECIFICITY: Break down recommendations by station + daypart combinations unless performance trends are consistent across all dayparts for a station.
6. CONFIRMATION PERIOD: Only flag entities as "confirmed underperformers" if they show poor performance for 3+ weeks with adequate sample size (30+ spots).
7. IMPACT-BASED URGENCY: Assign urgency based on both absolute impact (total visits lost) and relative impact (% of campaign affected).
8. COMPREHENSIVE ANALYSIS: Provide insights across multiple optimization scenarios (conservative, aggressive, testing) and analysis categories.

OPTIMIZATION SCENARIOS TO INCLUDE:
- CONSERVATIVE (10-15% moves): Low-risk proven opportunities
- AGGRESSIVE (25-50% moves): High-confidence major reallocations
- TESTING (5-10% moves): Experimental opportunities for emerging patterns

ANALYSIS CATEGORIES TO COVER:
- Scaling opportunities (5-8 recommendations)
- Underperformers requiring action (3-5 recommendations)
- Budget reallocations (5-8 scenarios across conservative/aggressive)
- Daypart shifting within stations (3-5 recommendations)
- Performance tier analysis (2-4 insights)
- Temporal pattern insights (2-3 insights)
- Risk assessment insights (2-3 insights)
- Emerging opportunities (2-4 recommendations)
- Market dynamics hypotheses (1-2 speculative insights, clearly labeled)

BUDGET FLEXIBILITY NOTE: While maintaining budget neutrality, highlight opportunities where increasing total budget would yield significant positive impact.

Respond with ONLY valid JSON in this exact format:

{json_schema}

Rules:
- Use exact station/daypart names from the data above
- Provide specific weekly spot counts for all recommendations
- Ensure reallocation math adds up to zero net change within each scenario
- Generate 20-30 total insights across all categories
- Label speculative insights clearly in market_dynamics section
- Provide multiple optimization scenarios (conservative, aggressive, testing)
- Focus on actionable decisions for media buyers with comprehensive coverage"""
    
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
    
    def _format_recency_weighted_performance(self, kpis: Dict[str, Any]) -> str:
        """Format performance data with recency weighting"""
        
        time_patterns = kpis.get('time_patterns', {})
        daily_trends = time_patterns.get('daily_trends', [])
        
        if not daily_trends or len(daily_trends) < 7:
            return "RECENCY-WEIGHTED PERFORMANCE: Insufficient data for weekly analysis"
        
        total_days = len(daily_trends)
        
        # Week 1: Most recent 7 days
        week1_data = daily_trends[-7:] if total_days >= 7 else daily_trends
        week1_spots = sum(d.get('spots', 0) for d in week1_data)
        week1_visits = sum(d.get('visits', 0) for d in week1_data)
        week1_efficiency = week1_visits / max(week1_spots, 1)
        
        # Week 2: Days 8-14
        week2_data = daily_trends[-14:-7] if total_days >= 14 else []
        week2_spots = sum(d.get('spots', 0) for d in week2_data) if week2_data else 0
        week2_visits = sum(d.get('visits', 0) for d in week2_data) if week2_data else 0
        week2_efficiency = week2_visits / max(week2_spots, 1) if week2_spots > 0 else 0
        
        # Weeks 3+: Remaining period
        week3plus_data = daily_trends[:-14] if total_days > 14 else []
        week3plus_spots = sum(d.get('spots', 0) for d in week3plus_data) if week3plus_data else 0
        week3plus_visits = sum(d.get('visits', 0) for d in week3plus_data) if week3plus_data else 0
        week3plus_efficiency = week3plus_visits / max(week3plus_spots, 1) if week3plus_spots > 0 else 0
        
        # Calculate changes
        week_over_week_change = ((week1_efficiency - week2_efficiency) / max(week2_efficiency, 1)) * 100 if week2_efficiency > 0 else 0
        
        performance = f"""RECENCY-WEIGHTED PERFORMANCE (Prioritize Week 1 for decisions):

WEEK 1 (Most Recent 7 days) - PRIMARY DECISION DATA:
- Spots: {week1_spots:,} | Visits: {week1_visits:,} | Efficiency: {week1_efficiency:.2f} visits/spot
- Weekly Volume: {week1_spots} spots per week"""
        
        if week2_data:
            performance += f"""

WEEK 2 (Days 8-14) - COMPARISON DATA:
- Spots: {week2_spots:,} | Visits: {week2_visits:,} | Efficiency: {week2_efficiency:.2f} visits/spot
- Week-over-Week Change: {week_over_week_change:+.1f}%"""
        
        if week3plus_data:
            performance += f"""

WEEKS 3+ (Context Period) - CONFIRMATION DATA:
- Spots: {week3plus_spots:,} | Visits: {week3plus_visits:,} | Efficiency: {week3plus_efficiency:.2f} visits/spot
- Period Length: {len(week3plus_data)} days"""
        
        # Add momentum assessment
        if week2_efficiency > 0:
            if week_over_week_change > 10:
                momentum = "STRONG POSITIVE momentum - capitalize immediately"
            elif week_over_week_change > 5:
                momentum = "Positive momentum - consider scaling"
            elif week_over_week_change < -10:
                momentum = "DECLINING performance - urgent optimization needed"
            elif week_over_week_change < -5:
                momentum = "Negative momentum - investigate and adjust"
            else:
                momentum = "Stable performance - maintain current approach"
            
            performance += f"\n\nMOMENTUM ASSESSMENT: {momentum}"
        
        return performance
    
    def _format_station_daypart_breakdown(self, kpis: Dict[str, Any]) -> str:
        """Format detailed station + daypart performance breakdown"""
        
        dimensional = kpis.get('dimensional_analysis', {})
        station_data = dimensional.get('station_performance', [])
        daypart_data = dimensional.get('daypart_performance', [])
        combination_data = dimensional.get('station_daypart_combinations', [])
        
        breakdown = """STATION + DAYPART PERFORMANCE BREAKDOWN:

TOP STATION PERFORMERS (for scaling opportunities):"""
        
        # Station performance with sample size filtering
        if station_data:
            breakdown += "\nStation          | Spots | Visits | Efficiency | Sample Size | Confidence"
            breakdown += "\n-----------------|-------|--------|------------|-------------|------------"
            
            for station in station_data[:8]:
                name = (station.get('station') or 'Unknown')[:14].ljust(14)
                spots = station.get('spots', 0)
                visits = station.get('total_visits', 0)
                efficiency = station.get('avg_visits_per_spot', 0) or 0
                
                # Determine confidence based on sample size
                confidence = "HIGH" if spots >= 30 else "MEDIUM" if spots >= 10 else "LOW"
                
                breakdown += f"\n{name} | {spots:5} | {visits:6,} | {efficiency:10.1f} | {spots:11} | {confidence}"
        
        # Daypart performance
        if daypart_data:
            breakdown += "\n\nDAYPART EFFICIENCY (for time-based optimization):"
            breakdown += "\nDaypart   | Spots | Visits | Efficiency | Weekly Spots | Priority"
            breakdown += "\n----------|-------|--------|------------|--------------|----------"
            
            total_days = len(kpis.get('time_patterns', {}).get('daily_trends', []))
            weeks = max(1, total_days // 7)
            
            for daypart in daypart_data:
                name = (daypart.get('daypart') or 'Unknown')[:8].ljust(8)
                spots = daypart.get('spots', 0)
                visits = daypart.get('total_visits', 0)
                efficiency = daypart.get('avg_visits_per_spot', 0) or 0
                weekly_spots = spots // weeks
                
                priority = "SCALE" if efficiency >= 3.0 else "MAINTAIN" if efficiency >= 2.0 else "OPTIMIZE" if efficiency >= 1.0 else "REDUCE"
                
                breakdown += f"\n{name} | {spots:5} | {visits:6,} | {efficiency:10.1f} | {weekly_spots:12} | {priority}"
        
        # Station + Daypart combinations (for specific reallocation recommendations)
        if combination_data:
            breakdown += "\n\nSTATION + DAYPART COMBINATIONS (for specific reallocation):"
            breakdown += "\nStation + Daypart          | Spots | Efficiency | Weekly | Action Needed"
            breakdown += "\n---------------------------|-------|------------|--------|---------------"
            
            total_days = len(kpis.get('time_patterns', {}).get('daily_trends', []))
            weeks = max(1, total_days // 7)
            
            for combo in combination_data[:10]:
                station = combo.get('station', 'Unknown')[:8]
                daypart = combo.get('daypart', 'Unknown')[:6]
                name = f"{station}_{daypart}"[:25].ljust(25)
                spots = combo.get('spots', 0)
                efficiency = combo.get('avg_visits_per_spot', 0) or 0
                weekly_spots = spots // weeks
                
                if spots >= 30:
                    action = "SCALE UP" if efficiency >= 3.0 else "REDUCE" if efficiency < 1.5 else "MAINTAIN"
                elif spots >= 10:
                    action = "MONITOR"
                else:
                    action = "IGNORE"
                
                breakdown += f"\n{name} | {spots:5} | {efficiency:10.1f} | {weekly_spots:6} | {action}"
        
        return breakdown
    
    def _get_enhanced_json_schema(self) -> str:
        """Get the comprehensive JSON schema for extensive media buyer insights"""
        return """{
  "executive_summary": {
    "summary": "3-4 sentence comprehensive assessment focusing on recent performance and key optimization opportunities",
    "confidence": "High|Medium|Low",
    "urgency": "High|Medium|Low",
    "recent_momentum": "positive|negative|stable",
    "total_insights_generated": 25
  },
  "scaling_opportunities": [
    {
      "priority": 1,
      "entity": "STATION_NAME_DAYPART (e.g., TOP_STATION_PRIME)",
      "entity_type": "station_daypart",
      "current_weekly_spots": 25,
      "recommended_weekly_increase": 8,
      "optimization_scenario": "conservative|aggressive|testing",
      "action_type": "scale_up|test|investigate",
      "recommendation": "Specific weekly spot increase recommendation",
      "projected_weekly_impact": "Expected additional visits per week",
      "confidence": "High|Medium|Low",
      "sample_size": 45,
      "risk_level": "Low|Medium|High",
      "business_rationale": "Why this station+daypart combination warrants scaling"
    }
  ],
  "underperformers": [
    {
      "entity": "STATION_NAME_DAYPART",
      "entity_type": "station_daypart",
      "current_weekly_spots": 15,
      "weeks_of_poor_performance": 4,
      "issue": "Specific performance problem with recent data emphasis",
      "severity": "High|Medium|Low",
      "recommended_weekly_reduction": 10,
      "recommended_action": "reduce|optimize|eliminate|investigate",
      "sample_size": 60,
      "potential_cause": "creative_fatigue|competitive_pressure|audience_mismatch|unknown",
      "business_rationale": "Why this station+daypart requires immediate action"
    }
  ],
  "budget_reallocations": [
    {
      "scenario_type": "conservative|aggressive|testing",
      "from_entity": "WEAK_STATION_DAYPART",
      "to_entity": "STRONG_STATION_DAYPART",
      "weekly_spots_to_move": 12,
      "current_from_weekly_spots": 20,
      "current_to_weekly_spots": 18,
      "projected_weekly_impact": "Expected net visit improvement per week",
      "confidence": "High|Medium|Low",
      "implementation_priority": "High|Medium|Low",
      "percentage_change_from": "40% reduction",
      "percentage_change_to": "67% increase",
      "risk_assessment": "Analysis of potential risks"
    }
  ],
  "daypart_shifting": [
    {
      "station": "STATION_NAME",
      "from_daypart": "CURRENT_DAYPART",
      "to_daypart": "TARGET_DAYPART", 
      "weekly_spots_to_shift": 8,
      "projected_efficiency_gain": "Expected improvement",
      "confidence": "High|Medium|Low",
      "business_rationale": "Why this daypart shift makes sense"
    }
  ],
  "performance_tier_analysis": [
    {
      "tier": "Top Tier|Mid Tier|Bottom Tier",
      "entities": ["STATION_DAYPART_1", "STATION_DAYPART_2"],
      "characteristics": "Common performance characteristics",
      "recommended_strategy": "How to optimize this tier",
      "scaling_potential": "High|Medium|Low"
    }
  ],
  "temporal_insights": [
    {
      "pattern_type": "weekly_trend|daily_pattern|momentum_shift",
      "description": "Specific temporal pattern observed",
      "entities_affected": ["STATION_DAYPART_1", "STATION_DAYPART_2"],
      "recommended_timing_adjustment": "Specific timing recommendation",
      "projected_impact": "Expected improvement from timing change"
    }
  ],
  "emerging_opportunities": [
    {
      "entity": "STATION_NAME_DAYPART",
      "opportunity_type": "new_performer|recovering_asset|untested_potential",
      "current_weekly_spots": 5,
      "recommended_test_increase": 3,
      "testing_duration": "2-4 weeks",
      "success_metrics": "What to measure for success",
      "confidence": "Medium|Low",
      "business_rationale": "Why this deserves testing"
    }
  ],
  "risk_assessments": [
    {
      "risk_type": "high_volume_underperformer|market_saturation|competitive_pressure",
      "description": "Specific risk identified",
      "affected_entities": ["STATION_DAYPART_1"],
      "potential_impact": "Quantified risk impact",
      "mitigation_strategy": "How to address this risk",
      "urgency": "High|Medium|Low"
    }
  ],
  "market_dynamics": [
    {
      "hypothesis": "potential_creative_fatigue|competitive_interference|market_saturation",
      "evidence": "Data patterns supporting this hypothesis",
      "affected_entities": ["STATION_DAYPART_1", "STATION_DAYPART_2"],
      "confidence": "Speculative|Low|Medium",
      "recommended_investigation": "How to validate this hypothesis",
      "note": "This is speculative analysis based on performance patterns"
    }
  ],
  "budget_scaling_opportunities": [
    {
      "opportunity_description": "Where increasing total budget would yield significant ROI",
      "recommended_additional_weekly_spots": 25,
      "target_entities": ["TOP_STATION_PRIME", "STRONG_STATION_MORNING"],
      "projected_weekly_roi": "Expected return on incremental investment",
      "confidence": "High|Medium|Low",
      "scaling_scenario": "conservative|aggressive"
    }
  ],
  "trend_insights": [
    {
      "trend_description": "Recent performance trend with weekly context",
      "trend_direction": "positive|negative|stable",
      "entity": "STATION_DAYPART or Campaign",
      "weeks_observed": 3,
      "urgency": "High|Medium|Low",
      "weekly_impact": "Visits gained/lost per week due to trend",
      "recommended_response": "capitalize|monitor|correct|investigate"
    }
  ]
}"""


# Test the clean prompt builder
if __name__ == "__main__":
    print("🧪 Testing Clean Prompt Builder...")
    
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
        print("✅ Clean prompt builder test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()