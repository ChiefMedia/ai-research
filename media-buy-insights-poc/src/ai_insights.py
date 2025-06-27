"""
AI Insights Engine - Generate executive insights from campaign KPIs using Google Gemini
Transforms structured KPI data into actionable business intelligence with CSV export capability
"""

import os
import google.generativeai as genai
import yaml
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class InsightGenerator:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize AI Insights Engine with Gemini API"""
        self.config_path = config_path
        self._load_config()
        self._setup_gemini()
        self._load_prompt_templates()
    
    def _load_config(self):
        """Load configuration settings"""
        try:
            with open(self.config_path, 'r') as file:
                self.config = yaml.safe_load(file)
                self.ai_settings = self.config.get('ai_settings', {})
        except FileNotFoundError:
            print(f"⚠️  Config file {self.config_path} not found, using defaults")
            self.ai_settings = {
                'model': 'gemini-1.5-flash',
                'temperature': 0.3,
                'max_tokens': 2000
            }
    
    def _setup_gemini(self):
        """Configure Google Gemini API"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            genai.configure(api_key=api_key)
            model_name = self.ai_settings.get('model', 'gemini-1.5-flash')
            self.model = genai.GenerativeModel(model_name)
            print(f"✅ Gemini AI initialized successfully with {model_name}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Gemini AI: {e}")
            print("💡 Check your .env file has GEMINI_API_KEY set")
            raise
    
    def _load_prompt_templates(self):
        """Load and prepare prompt templates"""
        self.prompt_templates = {
            'descriptive': self._get_descriptive_template(),
            'prescriptive': self._get_prescriptive_template(),
            'executive_summary': self._get_executive_summary_template()
        }
    
    def generate_comprehensive_insights(self, kpis: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """
        Main method: Generate comprehensive AI insights from KPI data
        Input: KPI dictionary from kpi_calculator.py
        Output: Structured insights ready for executive reporting and CSV export
        """
        print(f"🤖 Generating AI insights for {client_name or 'campaign'}...")
        
        try:
            # Prepare context data for AI
            context = self._prepare_context_data(kpis, client_name)
            
            # Generate structured insights
            insights = {
                'metadata': {
                    'generation_date': datetime.now().isoformat(),
                    'ai_model': self.ai_settings.get('model', 'gemini-1.5-flash'),
                    'client_name': client_name,
                    'analysis_confidence': self._assess_analysis_confidence(kpis)
                },
                'descriptive_analysis': self._generate_descriptive_insights(context),
                'prescriptive_recommendations': self._generate_prescriptive_insights(context),
                'executive_summary': self._generate_executive_summary(context),
                'key_findings': self._extract_key_findings(context),
                'optimization_priorities': self._identify_optimization_priorities(context)
            }
            
            print(f"✅ AI insights generated successfully")
            return insights
            
        except Exception as e:
            print(f"❌ Error generating AI insights: {e}")
            return self._fallback_insights(kpis, client_name)
    
    def _prepare_context_data(self, kpis: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """Prepare structured context data for AI prompts"""
        
        # Extract key metrics for AI context
        totals = kpis.get('totals', {})
        efficiency = kpis.get('efficiency', {})
        performance = kpis.get('performance_vs_targets', {})
        metadata = kpis.get('metadata', {})
        dimensional = kpis.get('dimensional_analysis', {})
        
        # Determine what's actually tracked vs not tracked
        tracking_context = self._assess_tracking_capabilities(totals)
        
        context = {
            'client_name': client_name or 'Unknown Client',
            'campaign_scale': {
                'total_spots': totals.get('total_spots', 0),
                'date_range': metadata.get('date_range', {}),
                'data_quality': metadata.get('data_quality_score', 0)
            },
            'performance_metrics': {
                'total_revenue': totals.get('total_revenue', 0),
                'total_visits': totals.get('total_visits', 0),
                'total_orders': totals.get('total_orders', 0),
                'total_impressions': totals.get('total_impressions', 0),
                'total_cost': totals.get('total_cost', 0),
                'roas': efficiency.get('roas'),
                'cpm': efficiency.get('cpm'),
                'cpo': efficiency.get('cpo'),
                'conversion_rate': efficiency.get('visit_to_order_rate'),
                'revenue_per_visit': efficiency.get('revenue_per_visit')
            },
            'tracking_context': tracking_context,
            'station_insights': dimensional.get('station_performance', []),
            'daypart_insights': dimensional.get('daypart_performance', []),
            'station_daypart_combinations': dimensional.get('station_daypart_combinations', []),
            'target_performance': performance,
            'time_patterns': kpis.get('time_patterns', {}),
            'targets': kpis.get('targets', {}),
            'executive_summary': kpis.get('summary', {})
        }
        
        return context
    
    def _assess_tracking_capabilities(self, totals: Dict[str, float]) -> Dict[str, Any]:
        """Assess what metrics are actually tracked vs missing"""
        
        tracking_status = {}
        
        # Revenue tracking assessment
        total_revenue = totals.get('total_revenue', 0)
        total_visits = totals.get('total_visits', 0)
        
        if total_revenue > 0:
            tracking_status['revenue'] = 'tracked'
            tracking_status['revenue_note'] = f'${total_revenue:,.2f} in attributed revenue'
        elif total_visits > 0:
            tracking_status['revenue'] = 'not_tracked_but_visits_available'
            tracking_status['revenue_note'] = 'Revenue attribution not implemented - campaign optimized for website visits'
        else:
            tracking_status['revenue'] = 'not_tracked'
            tracking_status['revenue_note'] = 'No revenue or visit attribution available'
        
        # Orders tracking assessment  
        total_orders = totals.get('total_orders', 0)
        if total_orders > 0:
            tracking_status['orders'] = 'tracked'
            tracking_status['orders_note'] = f'{total_orders:,} orders tracked'
        elif total_visits > 0:
            tracking_status['orders'] = 'not_tracked_but_visits_available'
            tracking_status['orders_note'] = 'Order tracking not implemented - focus on visit generation'
        else:
            tracking_status['orders'] = 'not_tracked'
            tracking_status['orders_note'] = 'No order tracking available'
        
        # Visits tracking
        if total_visits > 0:
            tracking_status['visits'] = 'tracked'
            tracking_status['visits_note'] = f'{total_visits:,} website visits tracked'
        else:
            tracking_status['visits'] = 'limited'
            tracking_status['visits_note'] = 'Limited visit attribution'
        
        # Campaign assessment context
        if total_visits > 0 and total_revenue == 0:
            tracking_status['campaign_type'] = 'visit_optimization'
            tracking_status['success_metric'] = 'website_visits'
            tracking_status['performance_context'] = 'Campaign successfully driving website traffic - revenue attribution not implemented'
        elif total_revenue > 0:
            tracking_status['campaign_type'] = 'full_attribution'
            tracking_status['success_metric'] = 'revenue_and_visits'
            tracking_status['performance_context'] = 'Full attribution tracking available for comprehensive analysis'
        else:
            tracking_status['campaign_type'] = 'limited_tracking'
            tracking_status['success_metric'] = 'impressions_only'
            tracking_status['performance_context'] = 'Limited attribution - recommend implementing visit tracking'
        
        return tracking_status
    
    def _generate_descriptive_insights(self, context: Dict[str, Any]) -> str:
        """Generate descriptive analysis of campaign performance"""
        
        formatted_context = self._format_context_for_prompts(context)
        prompt = self.prompt_templates['descriptive'].format(**formatted_context)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.ai_settings.get('temperature', 0.7),
                    max_output_tokens=self.ai_settings.get('max_tokens', 1500)
                )
            )
            return response.text.strip()
            
        except Exception as e:
            print(f"⚠️  Error generating descriptive insights: {e}")
            return self._fallback_descriptive_analysis(context)
    
    def _generate_prescriptive_insights(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured prescriptive recommendations for CSV export"""
        
        formatted_context = self._format_context_for_prompts(context)
        prompt = self.prompt_templates['prescriptive'].format(**formatted_context)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more consistent JSON
                    max_output_tokens=2000
                )
            )
            
            # Validate and clean the response
            structured_response = self._validate_and_clean_gemini_response(response.text)
            return structured_response
            
        except Exception as e:
            print(f"⚠️  Error generating prescriptive insights: {e}")
            return self._fallback_structured_insights()
    
    def _validate_and_clean_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Validate and clean Gemini JSON response"""
        try:
            # Clean the response
            cleaned = response_text.strip()
            
            # Remove markdown code blocks if present
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            # Parse JSON
            data = json.loads(cleaned.strip())
            
            # Validate required structure
            if 'optimization_recommendations' not in data:
                raise ValueError("Missing optimization_recommendations")
            if 'key_findings' not in data:
                raise ValueError("Missing key_findings")
            
            # Validate each recommendation
            for i, rec in enumerate(data['optimization_recommendations']):
                required_fields = ['priority', 'impact_level', 'area', 'recommendation', 'expected_impact', 'confidence']
                for field in required_fields:
                    if field not in rec:
                        raise ValueError(f"Recommendation {i} missing required field: {field}")
                
                # Standardize impact levels
                if rec['impact_level'] not in ['High', 'Medium', 'Low']:
                    # Try to map common variations
                    impact_map = {
                        'high': 'High', 'medium': 'Medium', 'low': 'Low',
                        'critical': 'High', 'important': 'Medium', 'minor': 'Low'
                    }
                    rec['impact_level'] = impact_map.get(rec['impact_level'].lower(), 'Medium')
                
                # Ensure station/daypart are null if not specified
                if 'station' not in rec:
                    rec['station'] = None
                if 'daypart' not in rec:
                    rec['daypart'] = None
                if 'action_type' not in rec:
                    rec['action_type'] = 'optimize'
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON from Gemini: {e}")
            return self._fallback_structured_insights()
        except Exception as e:
            print(f"❌ Error validating Gemini response: {e}")
            return self._fallback_structured_insights()
    
    def _fallback_structured_insights(self) -> Dict[str, Any]:
        """Fallback structured insights when Gemini fails"""
        return {
            "optimization_recommendations": [
                {
                    "priority": 1,
                    "impact_level": "Medium",
                    "area": "Analysis Required",
                    "station": None,
                    "daypart": None,
                    "recommendation": "AI analysis temporarily unavailable - review campaign data manually",
                    "expected_impact": "Manual analysis required",
                    "confidence": "N/A",
                    "action_type": "manual_review"
                }
            ],
            "key_findings": [
                {
                    "priority": 1,
                    "finding_type": "system",
                    "station": None,
                    "daypart": None,
                    "description": "AI insights temporarily unavailable",
                    "impact_level": "Low"
                }
            ]
        }
    
    def _generate_executive_summary(self, context: Dict[str, Any]) -> str:
        """Generate executive-level summary"""
        
        formatted_context = self._format_context_for_prompts(context)
        prompt = self.prompt_templates['executive_summary'].format(**formatted_context)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=800
                )
            )
            return response.text.strip()
            
        except Exception as e:
            print(f"⚠️  Error generating executive summary: {e}")
            return self._fallback_executive_summary(context)
    
    def _format_context_for_prompts(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Convert complex data structures to formatted strings for AI prompts"""
        
        formatted = context.copy()
        
        # Ensure all required nested dictionary keys exist with safe defaults
        if 'performance_metrics' not in formatted:
            formatted['performance_metrics'] = {}
        
        performance_metrics = formatted['performance_metrics']
        required_metrics = [
            'total_visits', 'total_orders', 'total_revenue', 'total_cost', 
            'total_impressions', 'roas', 'cpm', 'cpo'
        ]
        
        for metric in required_metrics:
            if metric not in performance_metrics or performance_metrics[metric] is None:
                if metric.startswith('total_'):
                    performance_metrics[metric] = 0
                else:
                    performance_metrics[metric] = 0.0
        
        # Ensure campaign_scale exists with defaults
        if 'campaign_scale' not in formatted:
            formatted['campaign_scale'] = {}
        
        campaign_scale = formatted['campaign_scale']
        scale_defaults = {
            'total_spots': 0,
            'data_quality': 0.0
        }
        
        for key, default_value in scale_defaults.items():
            if key not in campaign_scale or campaign_scale[key] is None:
                campaign_scale[key] = default_value
        
        # Ensure tracking_context exists with defaults
        if 'tracking_context' not in formatted:
            formatted['tracking_context'] = {}
        
        tracking_context = formatted['tracking_context']
        tracking_defaults = {
            'performance_context': 'Campaign tracking context not available',
            'success_metric': 'website_visits',
            'revenue_note': 'Revenue tracking status unknown'
        }
        
        for key, default_value in tracking_defaults.items():
            if key not in tracking_context or tracking_context[key] is None:
                tracking_context[key] = default_value
        
        # Flatten nested dictionaries into simple variables for template formatting
        formatted['client_name'] = context.get('client_name', 'Unknown Client')
        formatted['total_spots'] = campaign_scale['total_spots']
        formatted['data_quality'] = campaign_scale['data_quality']
        formatted['total_visits'] = performance_metrics['total_visits']
        formatted['total_orders'] = performance_metrics['total_orders']
        formatted['total_revenue'] = performance_metrics['total_revenue']
        formatted['total_cost'] = performance_metrics['total_cost']
        formatted['performance_context'] = tracking_context['performance_context']
        formatted['success_metric'] = tracking_context['success_metric']
        formatted['revenue_note'] = tracking_context['revenue_note']
        
        # Calculate cost per visit safely
        if performance_metrics['total_visits'] > 0 and performance_metrics['total_cost'] > 0:
            formatted['cost_per_visit'] = performance_metrics['total_cost'] / performance_metrics['total_visits']
        else:
            formatted['cost_per_visit'] = 0.0
        
        # Format station insights
        station_data = context.get('station_insights', [])
        if station_data:
            station_text = []
            for i, station in enumerate(station_data[:10], 1):
                name = station.get('station', 'Unknown')
                visits = station.get('total_visits', 0)
                spots = station.get('spots', 0)
                avg_visits = station.get('avg_visits_per_spot', 0)
                station_text.append(f"{i}. {name}: {visits:,} visits from {spots} spots ({avg_visits:.1f} avg/spot)")
            formatted['station_insights'] = '\n'.join(station_text)
        else:
            formatted['station_insights'] = "No station performance data available"
        
        # Format daypart insights
        daypart_data = context.get('daypart_insights', [])
        if daypart_data:
            daypart_text = []
            for i, daypart in enumerate(daypart_data[:8], 1):
                name = daypart.get('daypart', 'Unknown')
                visits = daypart.get('total_visits', 0)
                spots = daypart.get('spots', 0)
                avg_visits = daypart.get('avg_visits_per_spot', 0)
                daypart_text.append(f"{i}. {name}: {visits:,} visits from {spots} spots ({avg_visits:.1f} avg/spot)")
            formatted['daypart_insights'] = '\n'.join(daypart_text)
        else:
            formatted['daypart_insights'] = "No daypart performance data available"
        
        # Format station/daypart combinations
        combo_data = context.get('station_daypart_combinations', [])
        if combo_data:
            combo_text = []
            for i, combo in enumerate(combo_data[:5], 1):
                station = combo.get('station', 'Unknown')
                daypart = combo.get('daypart', 'Unknown')
                spots = combo.get('spots', 0)
                avg_visits = combo.get('avg_visits_per_spot', 0)
                combo_text.append(f"{i}. {station} + {daypart}: {avg_visits:.1f} visits/spot ({spots} spots)")
            formatted['station_daypart_combinations'] = '\n'.join(combo_text)
        else:
            formatted['station_daypart_combinations'] = "No station/daypart combination data available"
        
        return formatted
    
    def _extract_key_findings(self, context: Dict[str, Any]) -> List[str]:
        """Extract 3-5 key findings focused on stations and dayparts"""
        findings = []
        
        # Visit efficiency finding
        metrics = context['performance_metrics']
        if metrics['total_visits'] > 0:
            visit_rate = metrics['total_visits'] / context['campaign_scale']['total_spots']
            if visit_rate > 1.5:
                findings.append(f"Excellent engagement: {visit_rate:.1f} visits per TV spot")
            elif visit_rate > 1.0:
                findings.append(f"Strong engagement: {visit_rate:.1f} visits per TV spot")
            else:
                findings.append(f"Moderate engagement: {visit_rate:.1f} visits per TV spot")
        
        # Top station finding
        station_data = context.get('station_insights', [])
        if station_data:
            top_station = station_data[0]
            findings.append(f"Top station {top_station.get('station', 'Unknown')} generated {top_station.get('total_visits', 0):,} visits from {top_station.get('spots', 0)} spots")
        
        # Best daypart finding
        daypart_data = context.get('daypart_insights', [])
        if daypart_data:
            best_daypart = daypart_data[0]
            avg_visits = best_daypart.get('avg_visits_per_spot', 0)
            findings.append(f"{best_daypart.get('daypart', 'Unknown')} daypart shows highest efficiency at {avg_visits:.1f} visits per spot")
        
        # Station/daypart combination insight
        combo_data = context.get('station_daypart_combinations', [])
        if combo_data:
            best_combo = combo_data[0]
            findings.append(f"Best combination: {best_combo.get('station', 'Unknown')} + {best_combo.get('daypart', 'Unknown')} averaging {best_combo.get('avg_visits_per_spot', 0):.1f} visits per spot")
        
        return findings[:5]
    
    def _identify_optimization_priorities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify optimization priorities focused on stations and dayparts"""
        priorities = []
        
        station_data = context.get('station_insights', [])
        daypart_data = context.get('daypart_insights', [])
        
        # Priority 1: Station reallocation
        if len(station_data) >= 3:
            top_station_visits = station_data[0].get('avg_visits_per_spot', 0)
            bottom_station_visits = station_data[-1].get('avg_visits_per_spot', 0)
            
            if top_station_visits > bottom_station_visits * 1.5:
                priorities.append({
                    'priority': 1,
                    'area': 'Station Optimization',
                    'recommendation': f"Reallocate budget from low-performing stations to {station_data[0].get('station', 'top performer')}",
                    'impact': 'High',
                    'effort': 'Low'
                })
        
        # Priority 2: Daypart optimization
        if len(daypart_data) >= 2:
            best_daypart = daypart_data[0]
            worst_daypart = daypart_data[-1]
            
            best_efficiency = best_daypart.get('avg_visits_per_spot', 0)
            worst_efficiency = worst_daypart.get('avg_visits_per_spot', 0)
            
            if best_efficiency > worst_efficiency * 1.3:
                priorities.append({
                    'priority': 2,
                    'area': 'Daypart Optimization',
                    'recommendation': f"Shift budget from {worst_daypart.get('daypart', 'low-performing')} to {best_daypart.get('daypart', 'high-performing')} dayparts",
                    'impact': 'High',
                    'effort': 'Medium'
                })
        
        return priorities[:3]
    
    def _assess_analysis_confidence(self, kpis: Dict[str, Any]) -> float:
        """Assess confidence level in the analysis based on data quality and volume"""
        
        metadata = kpis.get('metadata', {})
        totals = kpis.get('totals', {})
        
        confidence_factors = []
        
        # Data quality factor
        data_quality = metadata.get('data_quality_score', 0)
        confidence_factors.append(data_quality / 100)
        
        # Sample size factor  
        spots = totals.get('total_spots', 0)
        if spots >= 1000:
            confidence_factors.append(1.0)
        elif spots >= 100:
            confidence_factors.append(0.8)
        elif spots >= 50:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.4)
        
        # Attribution coverage factor
        visits = totals.get('total_visits', 0)
        if visits > 0:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.3)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    
    def _get_descriptive_template(self) -> str:
        """Template for descriptive analysis prompts"""
        return """
You are a TV media buying expert analyzing campaign performance. Focus on ACTIONABLE insights about stations and dayparts.

Campaign Overview:
- Client: {client_name}
- TV Spots: {total_spots} spots
- Website Visits Generated: {total_visits:,}
- Data Quality: {data_quality:.0f}%

Campaign Context: {performance_context}

TOP PERFORMING STATIONS:
{station_insights}

DAYPART PERFORMANCE:
{daypart_insights}

BEST COMBINATIONS:
{station_daypart_combinations}

Provide a focused analysis in 3-4 sentences covering:
1. Overall campaign effectiveness (visits per spot rate)
2. Top performing stations and their visit generation rates  
3. Most effective dayparts for driving traffic
4. Key insights from station/daypart combination analysis

Focus on MEDIA BUYING insights. This campaign tracks website visits as the primary success metric.
"""
    
    def _get_prescriptive_template(self) -> str:
        """Template that enforces strict JSON structure"""
        return """
You are a TV media buying strategist. You MUST respond with ONLY valid JSON in the exact format specified below.

Campaign Data:
- Client: {client_name}
- {total_spots} spots generated {total_visits:,} visits
- Cost per visit: ${cost_per_visit:.2f}

TOP STATIONS: {station_insights}
TOP DAYPARTS: {daypart_insights}
TOP COMBINATIONS: {station_daypart_combinations}

CRITICAL: Respond with ONLY this JSON structure. No additional text before or after.

{{
  "optimization_recommendations": [
    {{
      "priority": 1,
      "impact_level": "High",
      "area": "Station Optimization", 
      "station": "LMN",
      "daypart": null,
      "recommendation": "Reallocate budget from low-performing stations to LMN",
      "expected_impact": "Reduce CPO by $100-200",
      "confidence": "90%",
      "action_type": "reallocate_budget"
    }},
    {{
      "priority": 2,
      "impact_level": "High",
      "area": "Daypart Optimization",
      "station": null, 
      "daypart": "WK",
      "recommendation": "Shift budget from LF to WK dayparts",
      "expected_impact": "Improve ROAS by 25%",
      "confidence": "85%",
      "action_type": "daypart_shift"
    }},
    {{
      "priority": 3,
      "impact_level": "Medium",
      "area": "Combination Scaling",
      "station": "LMN",
      "daypart": "WK", 
      "recommendation": "Scale LMN + WK combination by 30%",
      "expected_impact": "Increase visits by 500+",
      "confidence": "90%",
      "action_type": "scale_combination"
    }}
  ],
  "key_findings": [
    {{
      "priority": 1,
      "finding_type": "efficiency",
      "station": "LMN",
      "daypart": null,
      "description": "LMN demonstrates highest efficiency at 42.5 visits per spot",
      "impact_level": "High"
    }}
  ]
}}

Rules:
- Always include exactly 3-5 optimization_recommendations
- Always include exactly 3-5 key_findings  
- impact_level must be: "High", "Medium", or "Low"
- station and daypart can be null if not applicable
- action_type must be one of: "reallocate_budget", "daypart_shift", "scale_combination", "reduce_spend", "test_new"
- confidence must end with %
- Use station names exactly as they appear in the data
"""
    
    def _get_executive_summary_template(self) -> str:
        """Template for executive summaries"""
        return """
You are presenting TV campaign results to C-level executives.

Key Campaign Metrics:
- {total_spots} TV spots generated {total_visits:,} website visits
- Campaign drove {total_orders:,} orders worth ${total_revenue:,.2f}
- Data quality score: {data_quality:.0f}%

Create a 2-3 sentence executive summary that:
1. Highlights the most important business outcome
2. Provides clear context on campaign performance
3. Indicates if results meet, exceed, or fall short of expectations

Use business language appropriate for executive leadership.
"""
    
    def _fallback_descriptive_analysis(self, context: Dict[str, Any]) -> str:
        """Fallback descriptive analysis when AI fails"""
        metrics = context['performance_metrics']
        scale = context['campaign_scale']
        
        return f"""Campaign Analysis: {context['client_name']} executed a TV advertising campaign with {scale['total_spots']:,} spots, 
generating {metrics['total_visits']:,} website visits and {metrics['total_orders']:,} orders. 
The campaign achieved ${metrics['total_revenue']:,.2f} in attributed revenue with {scale['data_quality']:.0f}% data quality. 
Performance metrics indicate {'strong' if metrics['total_visits'] > scale['total_spots'] else 'moderate'} audience engagement."""
    
    def _fallback_executive_summary(self, context: Dict[str, Any]) -> str:
        """Fallback executive summary when AI fails"""
        metrics = context['performance_metrics']
        scale = context['campaign_scale']
        
        visit_rate = metrics['total_visits'] / scale['total_spots'] if scale['total_spots'] > 0 else 0
        
        return f"""{context['client_name']}'s TV campaign generated {metrics['total_visits']:,} website visits from {scale['total_spots']:,} spots, 
achieving a {visit_rate:.1f} visits-per-spot rate. The campaign demonstrates {'strong' if visit_rate > 1.0 else 'solid'} audience engagement 
with comprehensive attribution tracking providing {scale['data_quality']:.0f}% data confidence."""
    
    def _fallback_insights(self, kpis: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """Fallback insights when AI generation fails completely"""
        return {
            'metadata': {
                'generation_date': datetime.now().isoformat(),
                'ai_model': 'fallback',
                'client_name': client_name,
                'analysis_confidence': 0.7
            },
            'descriptive_analysis': 'Campaign performance analysis unavailable due to AI service interruption.',
            'prescriptive_recommendations': self._fallback_structured_insights(),
            'executive_summary': f'TV campaign analysis for {client_name or "client"} completed with limited AI insights.',
            'key_findings': ['AI analysis temporarily unavailable'],
            'optimization_priorities': []
        }


# Test the AI Insights Engine
if __name__ == "__main__":
    print("🧪 Testing AI Insights Engine...")
    print("=" * 50)
    
    try:
        import sys
        sys.path.append('.')
        from src.database import DatabaseManager
        from src.kpi_calculator import KPICalculator
        
        with DatabaseManager() as db:
            clients = db.get_available_clients(30)
            if clients:
                client = clients[0]
                print(f"📊 Testing AI insights for client: {client}")
                
                df = db.get_campaign_data(client=client, days=30)
                if not df.is_empty():
                    calculator = KPICalculator()
                    kpis = calculator.calculate_campaign_kpis(df)
                    
                    insight_generator = InsightGenerator()
                    insights = insight_generator.generate_comprehensive_insights(kpis, client)
                    
                    print(f"\n✅ AI insights test completed successfully!")
                    print(f"Generated insights: {list(insights.keys())}")
                else:
                    print("❌ No campaign data available for testing")
            else:
                print("❌ No clients available for testing")
                
    except ImportError as e:
        print(f"❌ Cannot import required modules: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")