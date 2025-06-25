"""
AI Insights Engine - Generate executive insights from campaign KPIs using Google Gemini
Transforms structured KPI data into actionable business intelligence
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
                'temperature': 0.7,
                'max_tokens': 1500
            }
    
    def _setup_gemini(self):
        """Configure Google Gemini API"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            genai.configure(api_key=api_key)
            # Updated model name for current Gemini API
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
        Output: Structured insights ready for executive reporting
        """
        print(f"🤖 Generating AI insights for {client_name or 'campaign'}...")
        
        try:
            # Prepare context data for AI
            context = self._prepare_context_data(kpis, client_name)
            
            # Generate different types of insights
            insights = {
                'metadata': {
                    'generation_date': datetime.now().isoformat(),
                    'ai_model': self.ai_settings.get('model', 'gemini-pro'),
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
        """Prepare structured context data for AI prompts with tracking context"""
        
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
        """Assess what metrics are actually tracked vs missing - with better revenue context"""
        
        tracking_status = {}
        
        # Revenue tracking assessment - more nuanced
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
        
        # Visits tracking (should always be tracked if we have data)
        if total_visits > 0:
            tracking_status['visits'] = 'tracked'
            tracking_status['visits_note'] = f'{total_visits:,} website visits tracked'
        else:
            tracking_status['visits'] = 'limited'
            tracking_status['visits_note'] = 'Limited visit attribution'
        
        # Impressions tracking
        total_impressions = totals.get('total_impressions', 0)
        if total_impressions > 0:
            tracking_status['impressions'] = 'tracked'
            tracking_status['impressions_note'] = f'{total_impressions:,} impressions tracked'
        else:
            tracking_status['impressions'] = 'not_tracked'
            tracking_status['impressions_note'] = 'No impression tracking'
        
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
        
        # Convert complex data structures to formatted strings
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
    
    def _generate_prescriptive_insights(self, context: Dict[str, Any]) -> str:
        """Generate prescriptive recommendations for optimization"""
        
        # Convert complex data structures to formatted strings
        formatted_context = self._format_context_for_prompts(context)
        prompt = self.prompt_templates['prescriptive'].format(**formatted_context)
        
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
            print(f"⚠️  Error generating prescriptive insights: {e}")
            return self._fallback_prescriptive_analysis(context)
    
    def _generate_executive_summary(self, context: Dict[str, Any]) -> str:
        """Generate executive-level summary"""
        
        # Convert complex data structures to formatted strings
        formatted_context = self._format_context_for_prompts(context)
        prompt = self.prompt_templates['executive_summary'].format(**formatted_context)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,  # Lower temperature for executive summaries
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
            for i, station in enumerate(station_data[:10], 1):  # Top 10
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
            for i, daypart in enumerate(daypart_data[:8], 1):  # Top 8
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
            for i, combo in enumerate(combo_data[:5], 1):  # Top 5
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
        
        # Tracking quality finding
        tracking = context.get('tracking_context', {})
        if tracking.get('overall_coverage', 0) >= 0.75:
            findings.append(f"Strong attribution tracking with {tracking.get('overall_coverage', 0):.0%} metric coverage")
        
        return findings[:5]
    
    def _identify_optimization_priorities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify optimization priorities focused on stations and dayparts"""
        priorities = []
        
        station_data = context.get('station_insights', [])
        daypart_data = context.get('daypart_insights', [])
        
        # Priority 1: Station reallocation (if performance variance exists)
        if len(station_data) >= 3:
            top_station_visits = station_data[0].get('avg_visits_per_spot', 0)
            bottom_station_visits = station_data[-1].get('avg_visits_per_spot', 0)
            
            if top_station_visits > bottom_station_visits * 1.5:  # 50% performance gap
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
            
            if best_efficiency > worst_efficiency * 1.3:  # 30% efficiency gap
                priorities.append({
                    'priority': 2,
                    'area': 'Daypart Optimization',
                    'recommendation': f"Shift budget from {worst_daypart.get('daypart', 'low-performing')} to {best_daypart.get('daypart', 'high-performing')} dayparts",
                    'impact': 'High',
                    'effort': 'Medium'
                })
        
        # Priority 3: Scale best combinations
        combo_data = context.get('station_daypart_combinations', [])
        if combo_data:
            best_combo = combo_data[0]
            if best_combo.get('avg_visits_per_spot', 0) > 1.5:
                priorities.append({
                    'priority': 3,
                    'area': 'Combination Scaling',
                    'recommendation': f"Scale {best_combo.get('station', 'top')} + {best_combo.get('daypart', 'performing')} combination",
                    'impact': 'Medium',
                    'effort': 'Low'
                })
        
        # Priority 4: Attribution enhancement (if tracking gaps exist)
        tracking = context.get('tracking_context', {})
        if tracking.get('revenue', '') == 'not_tracked':
            priorities.append({
                'priority': 4,
                'area': 'Attribution Enhancement',
                'recommendation': 'Implement revenue tracking to measure full campaign ROI',
                'impact': 'Medium',
                'effort': 'High'
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
        
        # Return average confidence
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    
    def _get_descriptive_template(self) -> str:
        """Template for descriptive analysis prompts - focused on stations and dayparts"""
        return """
You are a TV media buying expert analyzing campaign performance. Focus on ACTIONABLE insights about stations and dayparts.

Campaign Overview:
- Client: {client_name}
- TV Spots: {total_spots} spots
- Website Visits Generated: {total_visits:,}
- Data Quality: {data_quality:.0f}%

IMPORTANT - Campaign Context:
{performance_context}
Success Metric: {success_metric}
Revenue Tracking: {revenue_note}

TOP PERFORMING STATIONS:
{station_insights}

DAYPART PERFORMANCE ANALYSIS:
{daypart_insights}

BEST STATION/DAYPART COMBINATIONS:
{station_daypart_combinations}

Provide a focused analysis in 3-4 sentences covering:
1. Overall campaign effectiveness (visits per spot rate)
2. Top performing stations and their visit generation rates  
3. Most effective dayparts for driving traffic
4. Key insights from station/daypart combination analysis

Focus on MEDIA BUYING insights. This campaign tracks website visits as the primary success metric.
"""
    
    def _get_prescriptive_template(self) -> str:
        """Template for prescriptive recommendations - station and daypart focused"""
        return """
You are a TV media buying strategist. Provide SPECIFIC station and daypart optimization recommendations.

Campaign Performance:
- Client: {client_name}
- Total Spend: ${total_cost:,.2f} 
- {total_spots} TV spots generated {total_visits:,} website visits
- Cost per visit: ${cost_per_visit:.2f}

Campaign Context: {performance_context}

TOP PERFORMING STATIONS (prioritize these):
{station_insights}

DAYPART EFFICIENCY ANALYSIS:
{daypart_insights}

BEST STATION/DAYPART COMBINATIONS:
{station_daypart_combinations}

Provide 4-5 SPECIFIC media buying recommendations:

1. STATION BUDGET REALLOCATION: Which specific stations to increase/decrease spending on based on visit efficiency
2. DAYPART OPTIMIZATION: Which specific dayparts are most/least cost-efficient for driving visits  
3. HIGH-PERFORMANCE SCALING: Which station/daypart combinations to scale up immediately
4. COST EFFICIENCY IMPROVEMENTS: How to reduce cost per visit while maintaining volume
5. TESTING OPPORTUNITIES: New station/daypart combinations to test based on performance patterns

Each recommendation should be:
- Specific (mention actual stations/dayparts from the data)
- Quantified (include visit rates, costs, or efficiency metrics)
- Actionable (clear next steps for media buying team)

Focus on optimizing for website visits and cost efficiency.
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
    
    def _fallback_prescriptive_analysis(self, context: Dict[str, Any]) -> str:
        """Fallback prescriptive analysis when AI fails"""
        return """Optimization Recommendations:
1. Analyze top-performing time slots and markets to identify scaling opportunities (High Impact, Medium Effort)
2. Review attribution tracking to ensure comprehensive measurement of campaign impact (High Impact, Low Effort)  
3. Test creative variations in highest-volume markets to improve engagement rates (Medium Impact, Medium Effort)
4. Optimize media mix based on cost-per-visit performance across different dayparts (Medium Impact, Low Effort)"""
    
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
            'prescriptive_recommendations': 'Optimization recommendations unavailable. Please retry analysis.',
            'executive_summary': f'TV campaign analysis for {client_name or "client"} completed with limited AI insights.',
            'key_findings': ['AI analysis temporarily unavailable'],
            'optimization_priorities': []
        }
    
    def print_insights_summary(self, insights: Dict[str, Any]):
        """Print executive-friendly insights summary to console"""
        print("\n" + "="*60)
        print("🤖 AI CAMPAIGN INSIGHTS")
        print("="*60)
        
        # Metadata
        metadata = insights['metadata']
        print(f"\n🤖 AI Analysis: {metadata.get('ai_model', 'Unknown')} (Confidence: {metadata.get('analysis_confidence', 0):.0%})")
        print(f"📅 Generated: {metadata.get('generation_date', 'Unknown')}")
        
        # Executive Summary
        print(f"\n📋 EXECUTIVE SUMMARY")
        print(f"   {insights.get('executive_summary', 'Not available')}")
        
        # Key Findings
        findings = insights.get('key_findings', [])
        if findings:
            print(f"\n🔍 KEY FINDINGS")
            for i, finding in enumerate(findings, 1):
                print(f"   {i}. {finding}")
        
        # Descriptive Analysis
        print(f"\n📊 PERFORMANCE ANALYSIS")
        analysis = insights.get('descriptive_analysis', 'Not available')
        # Split long text into readable chunks
        if len(analysis) > 200:
            words = analysis.split()
            chunks = [' '.join(words[i:i+30]) for i in range(0, len(words), 30)]
            for chunk in chunks:
                print(f"   {chunk}")
        else:
            print(f"   {analysis}")
        
        # Optimization Priorities
        priorities = insights.get('optimization_priorities', [])
        if priorities:
            print(f"\n🎯 OPTIMIZATION PRIORITIES")
            for priority in priorities:
                impact_emoji = "🔥" if priority['impact'] == 'High' else "📈" if priority['impact'] == 'Medium' else "📊"
                print(f"   {priority['priority']}. {priority['area']}: {priority['recommendation']} {impact_emoji}")
        
        print("="*60)


# Test the AI Insights Engine
if __name__ == "__main__":
    print("🧪 Testing AI Insights Engine...")
    print("=" * 50)
    
    # Test with sample KPI data
    try:
        import sys
        sys.path.append('.')
        from src.database import DatabaseManager
        from src.kpi_calculator import KPICalculator
        
        with DatabaseManager() as db:
            # Get sample data
            clients = db.get_available_clients(30)
            if clients:
                print(f"📋 Available clients: {', '.join(clients)}")
                
                # Check for command line client argument
                if len(sys.argv) > 1:
                    client = sys.argv[1].upper()
                    if client not in clients:
                        print(f"❌ Client '{client}' not found. Available: {', '.join(clients)}")
                        sys.exit(1)
                else:
                    # Interactive selection
                    print(f"\n🎯 Select a client for analysis:")
                    for i, client_name in enumerate(clients[:10], 1):
                        print(f"   {i}. {client_name}")
                    
                    try:
                        choice = input(f"\nEnter client number (1-{min(len(clients), 10)}) or press Enter for {clients[0]}: ").strip()
                        if choice == "":
                            client = clients[0]
                        else:
                            client_index = int(choice) - 1
                            if 0 <= client_index < len(clients):
                                client = clients[client_index]
                            else:
                                print(f"Invalid choice. Using {clients[0]}")
                                client = clients[0]
                    except (ValueError, KeyboardInterrupt):
                        print(f"Using default client: {clients[0]}")
                        client = clients[0]
                
                print(f"📊 Testing AI insights for client: {client}")
                
                # Get campaign data and calculate KPIs
                df = db.get_campaign_data(client=client, days=30)
                if not df.is_empty():
                    calculator = KPICalculator()
                    kpis = calculator.calculate_campaign_kpis(df)
                    
                    # Generate AI insights
                    insight_generator = InsightGenerator()
                    insights = insight_generator.generate_comprehensive_insights(kpis, client)
                    
                    # Print results
                    insight_generator.print_insights_summary(insights)
                    
                    print(f"\n✅ AI insights test completed successfully!")
                else:
                    print("❌ No campaign data available for testing")
            else:
                print("❌ No clients available for testing")
                
    except ImportError as e:
        print(f"❌ Cannot import required modules: {e}")
        print("💡 Ensure database.py and kpi_calculator.py are available")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("💡 Check your GEMINI_API_KEY in .env file")