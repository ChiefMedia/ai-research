"""
AI Insights Engine - Generate comprehensive granular insights for Power BI Dashboard
Produces station-level, daypart-level, and combination-level insights for advanced analytics
"""

import os
import google.generativeai as genai
import yaml
import json
import csv
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class InsightGenerator:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize AI Insights Engine with comprehensive analysis capabilities"""
        self.config_path = config_path
        self._load_config()
        self._setup_gemini()
        self._load_insight_templates()
    
    def _load_config(self):
        """Load configuration settings"""
        try:
            with open(self.config_path, 'r') as file:
                self.config = yaml.safe_load(file)
                self.ai_settings = self.config.get('ai_settings', {})
        except FileNotFoundError:
            print(f"⚠️  Config file {self.config_path} not found, using defaults")
            self.ai_settings = {
                'model': 'gemini-2.0-flash',
                'temperature': 0.3,
                'max_tokens': 4000
            }
    
    def _setup_gemini(self):
        """Configure Google Gemini API"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            genai.configure(api_key=api_key)
            model_name = self.ai_settings.get('model', 'gemini-2.0-flash')
            self.model = genai.GenerativeModel(model_name)
            print(f"✅ Gemini AI initialized with {model_name}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Gemini AI: {e}")
            print("💡 Check your .env file has GEMINI_API_KEY set")
            raise
    
    def _load_insight_templates(self):
        """Load prompt templates for granular insights"""
        self.insight_templates = {
            'station_insights': self._get_station_insight_template(),
            'daypart_insights': self._get_daypart_insight_template(),
            'combination_insights': self._get_combination_insight_template(),
            'performance_assessment': self._get_performance_assessment_template(),
            'opportunity_analysis': self._get_opportunity_analysis_template()
        }
    
    def generate_comprehensive_insights(self, kpis: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive insights for Power BI dashboard
        Returns structured insights with granular station, daypart, and combination analysis
        """
        print(f"🤖 Generating comprehensive AI insights for {client_name or 'campaign'}...")
        
        try:
            # Prepare enhanced context data
            context = self._prepare_enhanced_context(kpis, client_name)
            
            # Generate all insight categories
            insights = {
                'metadata': {
                    'generation_date': datetime.now().isoformat(),
                    'ai_model': self.ai_settings.get('model', 'gemini-2.0-flash'),
                    'client_name': client_name,
                    'analysis_confidence': self._assess_analysis_confidence(kpis),
                    'total_insights_generated': 0  # Will be updated at the end
                },
                
                # Executive level insights (existing)
                'executive_summary': self._generate_executive_summary(context),
                'key_findings': self._extract_key_findings(context),
                'optimization_priorities': self._identify_optimization_priorities(context),
                
                # New granular insights for Power BI
                'station_insights': self._generate_station_insights(context),
                'daypart_insights': self._generate_daypart_insights(context),
                'station_daypart_insights': self._generate_combination_insights(context),
                'performance_quadrants': self._analyze_performance_quadrants(context),
                'opportunity_matrix': self._generate_opportunity_matrix(context),
                'predictive_recommendations': self._generate_predictive_recommendations(context),
                'budget_reallocation_analysis': self._analyze_budget_reallocation(context),
                
                # Structured data for Power BI consumption
                'prescriptive_recommendations': self._generate_structured_recommendations(context)
            }
            
            # Count total insights generated
            total_insights = self._count_total_insights(insights)
            insights['metadata']['total_insights_generated'] = total_insights
            
            print(f"✅ Enhanced AI insights generated: {total_insights} total insights")
            return insights
            
        except Exception as e:
            print(f"❌ Error generating enhanced insights: {e}")
            return self._fallback_enhanced_insights(kpis, client_name)
    
    def _prepare_context(self, kpis: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """Prepare comprehensive context data for AI analysis"""
        
        totals = kpis.get('totals', {})
        efficiency = kpis.get('efficiency', {})
        performance = kpis.get('performance_vs_targets', {})
        metadata = kpis.get('metadata', {})
        dimensional = kpis.get('dimensional_analysis', {})
        
        # Extract product information from metadata if available
        default_product = metadata.get('primary_product', 'DEFAULT')
        
        # Context with detailed breakdowns
        context = {
            'client_name': client_name or 'Unknown Client',
            'primary_product': default_product,
            'campaign_overview': {
                'total_spots': totals.get('total_spots', 0),
                'total_cost': totals.get('total_cost', 0),
                'total_visits': totals.get('total_visits', 0),
                'total_orders': totals.get('total_orders', 0),
                'total_revenue': totals.get('total_revenue', 0),
                'total_impressions': totals.get('total_impressions', 0),
                'data_quality': metadata.get('data_quality_score', 0),
                'analysis_period': metadata.get('date_range', {})
            },
            
            'efficiency_metrics': {
                'overall_roas': efficiency.get('roas', 0),
                'overall_cpm': efficiency.get('cpm', 0),
                'overall_cpv': efficiency.get('cpv', 0),
                'overall_cpo': efficiency.get('cpo', 0),
                'overall_conversion_rate': efficiency.get('visit_to_order_rate', 0),
                'visits_per_spot': totals.get('total_visits', 0) / max(totals.get('total_spots', 1), 1)
            },
            
            'station_performance': self._process_station_data(dimensional.get('station_performance', []), default_product),
            'daypart_performance': self._process_daypart_data(dimensional.get('daypart_performance', []), default_product),
            'combination_performance': self._process_combination_data(dimensional.get('station_daypart_combinations', []), default_product),
            
            'performance_benchmarks': {
                'top_quartile_threshold': self._calculate_performance_quartile(dimensional.get('station_performance', []), 0.75),
                'median_performance': self._calculate_performance_quartile(dimensional.get('station_performance', []), 0.5),
                'bottom_quartile_threshold': self._calculate_performance_quartile(dimensional.get('station_performance', []), 0.25)
            },
            
            'targets': kpis.get('targets', {}),
            'time_patterns': kpis.get('time_patterns', {})
        }
        
        return context
    
    def _process_station_data(self, station_data: List[Dict], default_product: str = 'DEFAULT') -> List[Dict]:
        """Enhance station data with performance classifications"""
        if not station_data:
            return []
        
        enhanced_stations = []
        
        # Calculate benchmarks
        visit_rates = [s.get('avg_visits_per_spot', 0) for s in station_data if s.get('avg_visits_per_spot', 0) > 0]
        if not visit_rates:
            return station_data
        
        visit_rates.sort()
        top_quartile = visit_rates[int(len(visit_rates) * 0.75)] if len(visit_rates) > 3 else visit_rates[-1]
        median = visit_rates[int(len(visit_rates) * 0.5)]
        bottom_quartile = visit_rates[int(len(visit_rates) * 0.25)] if len(visit_rates) > 3 else visit_rates[0]
        
        for station in station_data:
            station_with_product = station.copy()
            station_with_product['product'] = default_product  # Add product information
            visit_rate = station.get('avg_visits_per_spot', 0)
            
            # Performance classification
            if visit_rate >= top_quartile:
                station_with_product['performance_tier'] = 'Tier 1 - High Performer'
                station_with_product['performance_score'] = 'Excellent'
            elif visit_rate >= median:
                station_with_product['performance_tier'] = 'Tier 2 - Above Average'
                station_with_product['performance_score'] = 'Good'
            elif visit_rate >= bottom_quartile:
                station_with_product['performance_tier'] = 'Tier 3 - Below Average'
                station_with_product['performance_score'] = 'Fair'
            else:
                station_with_product['performance_tier'] = 'Tier 4 - Underperformer'
                station_with_product['performance_score'] = 'Poor'
            
            # Efficiency vs volume analysis
            total_visits = station.get('total_visits', 0)
            spots = station.get('spots', 0)
            
            if total_visits > 1000 and visit_rate > median:
                station_with_product['opportunity_type'] = 'Scale Winner'
            elif total_visits < 500 and visit_rate > top_quartile:
                station_with_product['opportunity_type'] = 'Hidden Gem'
            elif total_visits > 1000 and visit_rate < bottom_quartile:
                station_with_product['opportunity_type'] = 'Optimize or Reduce'
            else:
                station_with_product['opportunity_type'] = 'Monitor'
            
            enhanced_stations.append(station_with_product)
        
        return enhanced_stations
    
    def _process_daypart_data(self, daypart_data: List[Dict], default_product: str = 'DEFAULT') -> List[Dict]:
        """Enhance daypart data with performance insights"""
        if not daypart_data:
            return []
        
        dayparts_with_product = []
        
        # Calculate daypart benchmarks
        daypart_rates = [d.get('avg_visits_per_spot', 0) for d in daypart_data if d.get('avg_visits_per_spot', 0) > 0]
        if not daypart_rates:
            return daypart_data
        
        daypart_rates.sort()
        best_performance = daypart_rates[-1]
        worst_performance = daypart_rates[0]
        avg_performance = sum(daypart_rates) / len(daypart_rates)
        
        for daypart in daypart_data:
            daypart_with_product = daypart.copy()
            daypart_with_product['product'] = default_product  # Add product information
            visit_rate = daypart.get('avg_visits_per_spot', 0)
            
            # Performance relative to other dayparts
            if visit_rate >= best_performance * 0.9:
                daypart_with_product['daypart_rank'] = 'Prime Time'
                daypart_with_product['efficiency_rating'] = 'Excellent'
            elif visit_rate >= avg_performance:
                daypart_with_product['daypart_rank'] = 'Strong Performer'
                daypart_with_product['efficiency_rating'] = 'Good'
            elif visit_rate >= worst_performance * 1.5:
                daypart_with_product['daypart_rank'] = 'Average'
                daypart_with_product['efficiency_rating'] = 'Fair'
            else:
                daypart_with_product['daypart_rank'] = 'Off-Peak'
                daypart_with_product['efficiency_rating'] = 'Poor'
            
            # Cost efficiency analysis
            total_spots = daypart.get('spots', 0)
            if total_spots > 50:  # Significant volume
                if visit_rate > avg_performance:
                    daypart_with_product['recommendation_priority'] = 'High - Scale Up'
                else:
                    daypart_with_product['recommendation_priority'] = 'Medium - Optimize'
            else:
                if visit_rate > avg_performance:
                    daypart_with_product['recommendation_priority'] = 'Medium - Test Scale'
                else:
                    daypart_with_product['recommendation_priority'] = 'Low - Monitor'
            
            dayparts_with_product.append(daypart_with_product)
        
        return dayparts_with_product
    
    def _process_combination_data(self, combination_data: List[Dict], default_product: str = 'DEFAULT') -> List[Dict]:
        """Enhance station+daypart combination data"""
        if not combination_data:
            return []
        
        combinations_with_product = []
        
        # Calculate combination benchmarks
        combo_rates = [c.get('avg_visits_per_spot', 0) for c in combination_data if c.get('avg_visits_per_spot', 0) > 0]
        if not combo_rates:
            return combination_data
        
        combo_rates.sort()
        top_combo_rate = combo_rates[-1] if combo_rates else 0
        median_combo_rate = combo_rates[len(combo_rates) // 2] if combo_rates else 0
        
        for combo in combination_data:
            combo_with_product = combo.copy()
            combo_with_product['product'] = default_product  # Add product information
            visit_rate = combo.get('avg_visits_per_spot', 0)
            spots = combo.get('spots', 0)
            
            # Combination performance scoring
            if visit_rate >= top_combo_rate * 0.8:
                combo_with_product['combo_tier'] = 'Golden Combination'
                combo_with_product['scaling_priority'] = 'Immediate'
            elif visit_rate >= median_combo_rate:
                combo_with_product['combo_tier'] = 'Strong Combination'
                combo_with_product['scaling_priority'] = 'High'
            else:
                combo_with_product['combo_tier'] = 'Standard Combination'
                combo_with_product['scaling_priority'] = 'Low'
            
            # Sample size confidence
            if spots >= 20:
                combo_with_product['confidence_level'] = 'High'
            elif spots >= 10:
                combo_with_product['confidence_level'] = 'Medium'
            else:
                combo_with_product['confidence_level'] = 'Low'
            
            combinations_with_product.append(combo_with_product)
        
        return combinations_with_product
    
    def _generate_station_insights(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific insights for each station"""
        
        station_data = context.get('station_performance', [])
        if not station_data:
            return []
        
        insights = []
        
        for station in station_data[:15]:  # Top 15 stations
            station_name = station.get('station', 'Unknown')
            product = station.get('product', context.get('primary_product', 'DEFAULT'))
            visit_rate = station.get('avg_visits_per_spot', 0)
            total_visits = station.get('total_visits', 0)
            spots = station.get('spots', 0)
            performance_tier = station.get('performance_tier', 'Unknown')
            opportunity_type = station.get('opportunity_type', 'Monitor')
            
            # Generate AI insight for this specific station
            insight = {
                'station': station_name,
                'product': product,
                'insight_type': 'station_analysis',
                'performance_tier': performance_tier,
                'opportunity_type': opportunity_type,
                'visit_rate': visit_rate,
                'total_visits': total_visits,
                'spots': spots,
                'confidence': 'High' if spots >= 20 else 'Medium' if spots >= 10 else 'Low'
            }
            
            # Generate specific recommendation based on performance
            if opportunity_type == 'Scale Winner':
                insight['recommendation'] = f"Scale {station_name} immediately - proven high-volume, high-efficiency performer"
                insight['expected_impact'] = f"Potential to increase visits by {int(visit_rate * 50)}-{int(visit_rate * 100)} per 50 additional spots"
                insight['action_type'] = 'scale_budget'
                insight['priority'] = 1
            elif opportunity_type == 'Hidden Gem':
                insight['recommendation'] = f"Test scaling {station_name} - high efficiency with growth potential"
                insight['expected_impact'] = f"Low-risk opportunity to discover {int(visit_rate * 20)}-{int(visit_rate * 40)} additional visits"
                insight['action_type'] = 'test_scale'
                insight['priority'] = 2
            elif opportunity_type == 'Optimize or Reduce':
                insight['recommendation'] = f"Optimize or reduce spend on {station_name} - high volume but poor efficiency"
                insight['expected_impact'] = f"Redirect ${spots * 50:,.0f} in spend to higher-performing stations"
                insight['action_type'] = 'reduce_spend'
                insight['priority'] = 1
            else:
                insight['recommendation'] = f"Monitor {station_name} performance and test optimization strategies"
                insight['expected_impact'] = "Track performance trends for future decision making"
                insight['action_type'] = 'monitor'
                insight['priority'] = 3
            
            insights.append(insight)
        
        return insights
    
    def _generate_daypart_insights(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific insights for each daypart"""
        
        daypart_data = context.get('daypart_performance', [])
        if not daypart_data:
            return []
        
        insights = []
        
        for daypart in daypart_data:
            daypart_name = daypart.get('daypart', 'Unknown')
            product = daypart.get('product', context.get('primary_product', 'DEFAULT'))
            visit_rate = daypart.get('avg_visits_per_spot', 0)
            total_visits = daypart.get('total_visits', 0)
            spots = daypart.get('spots', 0)
            efficiency_rating = daypart.get('efficiency_rating', 'Unknown')
            recommendation_priority = daypart.get('recommendation_priority', 'Low')
            
            insight = {
                'daypart': daypart_name,
                'product': product,
                'insight_type': 'daypart_analysis',
                'efficiency_rating': efficiency_rating,
                'recommendation_priority': recommendation_priority,
                'visit_rate': visit_rate,
                'total_visits': total_visits,
                'spots': spots,
                'confidence': 'High' if spots >= 30 else 'Medium' if spots >= 15 else 'Low'
            }
            
            # Generate daypart-specific recommendations
            if 'Scale Up' in recommendation_priority:
                insight['recommendation'] = f"Immediately increase {daypart_name} budget - highest efficiency daypart"
                insight['expected_impact'] = f"Scale to capture {int(visit_rate * 100)}-{int(visit_rate * 200)} additional visits"
                insight['action_type'] = 'increase_daypart_budget'
                insight['priority'] = 1
            elif 'Test Scale' in recommendation_priority:
                insight['recommendation'] = f"Test increasing {daypart_name} investment - shows efficiency potential"
                insight['expected_impact'] = f"Controlled test could yield {int(visit_rate * 25)}-{int(visit_rate * 50)} more visits"
                insight['action_type'] = 'test_daypart_increase'
                insight['priority'] = 2
            elif 'Optimize' in recommendation_priority:
                insight['recommendation'] = f"Optimize {daypart_name} targeting and creative rotation"
                insight['expected_impact'] = f"Improve efficiency to match top dayparts"
                insight['action_type'] = 'optimize_daypart'
                insight['priority'] = 2
            else:
                insight['recommendation'] = f"Monitor {daypart_name} trends and consider budget reallocation"
                insight['expected_impact'] = "Maintain current performance while exploring alternatives"
                insight['action_type'] = 'monitor_daypart'
                insight['priority'] = 3
            
            insights.append(insight)
        
        return insights
    
    def _generate_combination_insights(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights for station+daypart combinations"""
        
        combination_data = context.get('combination_performance', [])
        if not combination_data:
            return []
        
        insights = []
        
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
            
            insight = {
                'station': station,
                'daypart': daypart,
                'product': product,
                'combination': f"{station} + {daypart}",
                'insight_type': 'combination_analysis',
                'combo_tier': combo_tier,
                'scaling_priority': scaling_priority,
                'visit_rate': visit_rate,
                'total_visits': total_visits,
                'spots': spots,
                'confidence': confidence_level
            }
            
            # Generate combination-specific recommendations
            if combo_tier == 'Golden Combination':
                insight['recommendation'] = f"Scale {station} + {daypart} immediately - golden combination identified"
                insight['expected_impact'] = f"High-confidence opportunity for {int(visit_rate * 50)}-{int(visit_rate * 100)} additional visits"
                insight['action_type'] = 'scale_combination'
                insight['priority'] = 1
            elif combo_tier == 'Strong Combination':
                insight['recommendation'] = f"Increase investment in {station} + {daypart} - proven strong performance"
                insight['expected_impact'] = f"Medium-risk opportunity for {int(visit_rate * 25)}-{int(visit_rate * 50)} additional visits"
                insight['action_type'] = 'increase_combination'
                insight['priority'] = 2
            else:
                insight['recommendation'] = f"Monitor {station} + {daypart} and test optimization"
                insight['expected_impact'] = f"Baseline combination for comparison and testing"
                insight['action_type'] = 'monitor_combination'
                insight['priority'] = 3
            
            insights.append(insight)
        
        return insights
    
    def _analyze_performance_quadrants(self, context: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Analyze stations by volume vs efficiency quadrants"""
        
        station_data = context.get('station_performance', [])
        if not station_data:
            return {}
        
        # Calculate medians for quadrant analysis
        visit_volumes = [s.get('total_visits', 0) for s in station_data]
        efficiency_rates = [s.get('avg_visits_per_spot', 0) for s in station_data]
        
        median_volume = sorted(visit_volumes)[len(visit_volumes) // 2] if visit_volumes else 0
        median_efficiency = sorted(efficiency_rates)[len(efficiency_rates) // 2] if efficiency_rates else 0
        
        quadrants = {
            'high_volume_high_efficiency': [],  # Scale these
            'low_volume_high_efficiency': [],   # Test scaling these
            'high_volume_low_efficiency': [],   # Optimize or reduce these
            'low_volume_low_efficiency': []     # Consider eliminating these
        }
        
        for station in station_data:
            volume = station.get('total_visits', 0)
            efficiency = station.get('avg_visits_per_spot', 0)
            
            station_analysis = {
                'station': station.get('station', 'Unknown'),
                'volume': volume,
                'efficiency': efficiency,
                'spots': station.get('spots', 0),
                'cost_estimate': station.get('spots', 0) * 50  # Rough cost estimate
            }
            
            if volume >= median_volume and efficiency >= median_efficiency:
                station_analysis['quadrant'] = 'Champions'
                station_analysis['action'] = 'Scale immediately'
                quadrants['high_volume_high_efficiency'].append(station_analysis)
            elif volume < median_volume and efficiency >= median_efficiency:
                station_analysis['quadrant'] = 'Hidden Gems'
                station_analysis['action'] = 'Test scaling'
                quadrants['low_volume_high_efficiency'].append(station_analysis)
            elif volume >= median_volume and efficiency < median_efficiency:
                station_analysis['quadrant'] = 'Inefficient Giants'
                station_analysis['action'] = 'Optimize or reduce'
                quadrants['high_volume_low_efficiency'].append(station_analysis)
            else:
                station_analysis['quadrant'] = 'Underperformers'
                station_analysis['action'] = 'Consider eliminating'
                quadrants['low_volume_low_efficiency'].append(station_analysis)
        
        return quadrants
    
    def _generate_opportunity_matrix(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate opportunity matrix for budget reallocation"""
        
        station_data = context.get('station_performance', [])
        if not station_data:
            return []
        
        opportunities = []
        
        # Sort by efficiency
        sorted_stations = sorted(station_data, key=lambda x: x.get('avg_visits_per_spot', 0), reverse=True)
        
        if len(sorted_stations) >= 2:
            top_performers = sorted_stations[:3]
            bottom_performers = sorted_stations[-3:]
            
            for i, top_station in enumerate(top_performers):
                for j, bottom_station in enumerate(bottom_performers):
                    if top_station['station'] != bottom_station['station']:
                        opportunity = {
                            'opportunity_type': 'budget_reallocation',
                            'from_station': bottom_station.get('station', 'Unknown'),
                            'to_station': top_station.get('station', 'Unknown'),
                            'from_efficiency': bottom_station.get('avg_visits_per_spot', 0),
                            'to_efficiency': top_station.get('avg_visits_per_spot', 0),
                            'efficiency_gain': top_station.get('avg_visits_per_spot', 0) - bottom_station.get('avg_visits_per_spot', 0),
                            'potential_spots_to_move': min(bottom_station.get('spots', 0) // 2, 25),
                            'priority': i + 1
                        }
                        
                        # Calculate projected impact
                        spots_to_move = opportunity['potential_spots_to_move']
                        projected_gain = spots_to_move * opportunity['efficiency_gain']
                        opportunity['projected_visit_gain'] = int(projected_gain)
                        opportunity['confidence'] = 'High' if spots_to_move >= 10 else 'Medium'
                        
                        opportunities.append(opportunity)
        
        return opportunities[:10]  # Top 10 opportunities
    
    def _generate_predictive_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate predictive recommendations based on performance patterns"""
        
        recommendations = []
        
        # Seasonal pattern predictions
        time_patterns = context.get('time_patterns', {})
        if time_patterns.get('daily_trends'):
            recommendations.append({
                'recommendation_type': 'seasonal_optimization',
                'insight': 'Optimize daypart allocation based on daily performance patterns',
                'expected_impact': 'Improve overall efficiency by 15-25%',
                'implementation_timeline': '2-3 weeks',
                'confidence': '85%'
            })
        
        # Station performance predictions
        station_data = context.get('station_performance', [])
        if len(station_data) >= 5:
            top_station = station_data[0]
            recommendations.append({
                'recommendation_type': 'performance_scaling',
                'insight': f"Scale {top_station.get('station', 'top performer')} based on consistent high performance",
                'expected_impact': f"Potential for {int(top_station.get('avg_visits_per_spot', 0) * 100)} additional visits per 100 spots",
                'implementation_timeline': '1-2 weeks',
                'confidence': '90%'
            })
        
        # Budget efficiency predictions
        campaign_overview = context.get('campaign_overview', {})
        efficiency_metrics = context.get('efficiency_metrics', {})
        
        if efficiency_metrics.get('overall_cpv', 0) > 0:
            recommendations.append({
                'recommendation_type': 'cost_optimization',
                'insight': 'Implement CPV-based budget allocation to improve cost efficiency',
                'expected_impact': f"Reduce cost per visit by ${efficiency_metrics.get('overall_cpv', 0) * 0.2:.2f}",
                'implementation_timeline': '1 week',
                'confidence': '75%'
            })
        
        return recommendations
    
    def _analyze_budget_reallocation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze optimal budget reallocation scenarios"""
        
        station_data = context.get('station_performance', [])
        campaign_overview = context.get('campaign_overview', {})
        
        if not station_data or len(station_data) < 3:
            return {}
        
        current_total_cost = campaign_overview.get('total_cost', 0)
        current_total_visits = campaign_overview.get('total_visits', 0)
        
        # Calculate current cost per visit
        current_cpv = current_total_cost / current_total_visits if current_total_visits > 0 else 0
        
        # Simulate reallocation scenarios
        scenarios = {
            'current_performance': {
                'total_cost': current_total_cost,
                'total_visits': current_total_visits,
                'cpv': current_cpv
            }
        }
        
        # Scenario 1: Move budget from bottom 25% to top 25%
        if len(station_data) >= 4:
            top_quartile = station_data[:len(station_data)//4]
            bottom_quartile = station_data[-len(station_data)//4:]
            
            avg_top_efficiency = sum(s.get('avg_visits_per_spot', 0) for s in top_quartile) / len(top_quartile)
            avg_bottom_efficiency = sum(s.get('avg_visits_per_spot', 0) for s in bottom_quartile) / len(bottom_quartile)
            
            # Calculate reallocation impact
            bottom_spots = sum(s.get('spots', 0) for s in bottom_quartile)
            spots_to_reallocate = bottom_spots // 2  # Move half the spots
            
            projected_visit_loss = spots_to_reallocate * avg_bottom_efficiency
            projected_visit_gain = spots_to_reallocate * avg_top_efficiency
            net_visit_gain = projected_visit_gain - projected_visit_loss
            
            scenarios['top_quartile_reallocation'] = {
                'description': 'Reallocate 50% of bottom quartile budget to top quartile',
                'spots_moved': spots_to_reallocate,
                'projected_visit_gain': int(net_visit_gain),
                'efficiency_improvement': f"{((avg_top_efficiency / avg_bottom_efficiency - 1) * 100):.1f}%",
                'confidence': 'High' if spots_to_reallocate >= 20 else 'Medium'
            }
        
        return scenarios
    
    def _generate_structured_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured recommendations for CSV export to Power BI"""
        
        recommendations = []
        findings = []
        
        # Station-level recommendations
        station_data = context.get('station_performance', [])
        for i, station in enumerate(station_data[:10], 1):
            station_name = station.get('station', 'Unknown')
            visit_rate = station.get('avg_visits_per_spot', 0)
            opportunity_type = station.get('opportunity_type', 'Monitor')
            
            if opportunity_type == 'Scale Winner':
                recommendations.append({
                    'priority': i,
                    'impact_level': 'High',
                    'area': 'Station Optimization',
                    'station': station_name,
                    'daypart': None,
                    'recommendation': f"Reallocate budget to {station_name} due to its high visit per spot ratio.",
                    'expected_impact': f"Increase overall visits by {int(visit_rate * 10)}%",
                    'confidence': '95%',
                    'action_type': 'reallocate_budget'
                })
                
                findings.append({
                    'priority': i,
                    'finding_type': 'efficiency',
                    'station': station_name,
                    'daypart': None,
                    'description': f"{station_name} is the most efficient station with {visit_rate:.1f} visits per spot.",
                    'impact_level': 'High'
                })
            
            elif opportunity_type == 'Optimize or Reduce':
                recommendations.append({
                    'priority': i + 10,
                    'impact_level': 'Medium',
                    'area': 'Station Optimization',
                    'station': station_name,
                    'daypart': None,
                    'recommendation': f"Reduce spend on {station_name} due to its low visit per spot ratio.",
                    'expected_impact': f"Reduce wasted spend by {int((1 - visit_rate/max(s.get('avg_visits_per_spot', 1) for s in station_data)) * 100)}%",
                    'confidence': '75%',
                    'action_type': 'reduce_spend'
                })
                
                findings.append({
                    'priority': i + 10,
                    'finding_type': 'inefficiency',
                    'station': station_name,
                    'daypart': None,
                    'description': f"{station_name} is underperforming with only {visit_rate:.1f} visits per spot.",
                    'impact_level': 'Medium'
                })
        
        # Daypart-level recommendations
        daypart_data = context.get('daypart_performance', [])
        for i, daypart in enumerate(daypart_data, 1):
            daypart_name = daypart.get('daypart', 'Unknown')
            visit_rate = daypart.get('avg_visits_per_spot', 0)
            recommendation_priority = daypart.get('recommendation_priority', 'Low')
            
            if 'Scale Up' in recommendation_priority:
                recommendations.append({
                    'priority': i + 5,
                    'impact_level': 'Medium',
                    'area': 'Daypart Optimization',
                    'station': None,
                    'daypart': daypart_name,
                    'recommendation': f"Increase spend on {daypart_name} daypart to capitalize on its strong performance.",
                    'expected_impact': f"Improve visit rate by {int(visit_rate * 2)}%",
                    'confidence': '80%',
                    'action_type': 'daypart_shift'
                })
                
                findings.append({
                    'priority': i + 5,
                    'finding_type': 'efficiency',
                    'station': None,
                    'daypart': daypart_name,
                    'description': f"{daypart_name} is the most efficient daypart with {visit_rate:.1f} visits per spot.",
                    'impact_level': 'High'
                })
        
        # Combination-level recommendations
        combination_data = context.get('combination_performance', [])
        for i, combo in enumerate(combination_data[:5], 1):
            station = combo.get('station', 'Unknown')
            daypart = combo.get('daypart', 'Unknown')
            visit_rate = combo.get('avg_visits_per_spot', 0)
            combo_tier = combo.get('combo_tier', 'Standard')
            
            if combo_tier == 'Golden Combination':
                recommendations.append({
                    'priority': i + 15,
                    'impact_level': 'Medium',
                    'area': 'Combination Scaling',
                    'station': station,
                    'daypart': daypart,
                    'recommendation': f"Explore scaling {station} + {daypart} combination given its strong performance.",
                    'expected_impact': f"Increase visits by {int(visit_rate * 20)}+",
                    'confidence': '70%',
                    'action_type': 'scale_combination'
                })
        
        return {
            'optimization_recommendations': recommendations,
            'key_findings': findings
        }
    
    def _count_total_insights(self, insights: Dict[str, Any]) -> int:
        """Count total insights generated across all categories"""
        count = 0
        
        # Count each insight category
        count += len(insights.get('key_findings', []))
        count += len(insights.get('optimization_priorities', []))
        count += len(insights.get('station_insights', []))
        count += len(insights.get('daypart_insights', []))
        count += len(insights.get('station_daypart_insights', []))
        count += len(insights.get('predictive_recommendations', []))
        count += len(insights.get('opportunity_matrix', []))
        
        # Count quadrant analysis
        quadrants = insights.get('performance_quadrants', {})
        for quadrant_data in quadrants.values():
            count += len(quadrant_data)
        
        # Count structured recommendations
        structured = insights.get('prescriptive_recommendations', {})
        count += len(structured.get('optimization_recommendations', []))
        count += len(structured.get('key_findings', []))
        
        return count
    
    def _calculate_performance_quartile(self, data: List[Dict], percentile: float) -> float:
        """Calculate performance quartile for benchmarking"""
        if not data:
            return 0.0
        
        values = [item.get('avg_visits_per_spot', 0) for item in data if item.get('avg_visits_per_spot', 0) > 0]
        if not values:
            return 0.0
        
        values.sort()
        index = int(len(values) * percentile)
        return values[min(index, len(values) - 1)]
    
    def _assess_analysis_confidence(self, kpis: Dict[str, Any]) -> float:
        """Assess confidence level in the analysis"""
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
        elif spots >= 500:
            confidence_factors.append(0.9)
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
        
        # Station diversity factor
        dimensional = kpis.get('dimensional_analysis', {})
        station_count = len(dimensional.get('station_performance', []))
        if station_count >= 10:
            confidence_factors.append(0.9)
        elif station_count >= 5:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    
    def _generate_executive_summary(self, context: Dict[str, Any]) -> str:
        """Generate executive-level summary"""
        campaign_overview = context.get('campaign_overview', {})
        efficiency_metrics = context.get('efficiency_metrics', {})
        
        total_spots = campaign_overview.get('total_spots', 0)
        total_visits = campaign_overview.get('total_visits', 0)
        total_revenue = campaign_overview.get('total_revenue', 0)
        total_orders = campaign_overview.get('total_orders', 0)
        
        # Create context-aware summary
        if total_revenue > 0:
            return f"""Our TV campaign successfully drove ${total_revenue:,.0f} in revenue through {total_orders:,} orders generated from {total_visits:,} website visits originating from {total_spots} TV spots. While a solid foundation, we need to compare these initial results against projected ROI to determine if the campaign is on track to meet or exceed revenue targets."""
        elif total_visits > 0:
            visits_per_spot = total_visits / total_spots if total_spots > 0 else 0
            performance_desc = "excellent" if visits_per_spot > 2 else "strong" if visits_per_spot > 1 else "moderate"
            return f"""Our TV campaign generated {total_visits:,} website visits from {total_spots} spots, achieving {performance_desc} audience engagement with {visits_per_spot:.1f} visits per spot. The campaign demonstrates effective media placement with opportunities for optimization through strategic station and daypart reallocation."""
        else:
            return f"""Campaign analysis covers {total_spots} TV spots with limited attribution data available. Recommend implementing comprehensive visit tracking to measure campaign effectiveness and optimize media spend allocation."""
    
    def _extract_key_findings(self, context: Dict[str, Any]) -> List[str]:
        """Extract key findings focused on actionable insights"""
        findings = []
        
        campaign_overview = context.get('campaign_overview', {})
        efficiency_metrics = context.get('efficiency_metrics', {})
        station_data = context.get('station_performance', [])
        daypart_data = context.get('daypart_performance', [])
        combination_data = context.get('combination_performance', [])
        
        # Overall performance finding
        total_spots = campaign_overview.get('total_spots', 0)
        total_visits = campaign_overview.get('total_visits', 0)
        if total_visits > 0 and total_spots > 0:
            visit_rate = total_visits / total_spots
            performance_level = "Excellent" if visit_rate > 2 else "Strong" if visit_rate > 1 else "Moderate"
            findings.append(f"{performance_level} engagement: {visit_rate:.1f} visits per TV spot")
        
        # Top station finding
        if station_data:
            top_station = station_data[0]
            findings.append(f"Top station {top_station.get('station', 'Unknown')} generated {top_station.get('total_visits', 0):,} visits from {top_station.get('spots', 0)} spots")
        
        # Best daypart finding
        if daypart_data:
            best_daypart = daypart_data[0]
            findings.append(f"{best_daypart.get('daypart', 'Unknown')} daypart shows highest efficiency at {best_daypart.get('avg_visits_per_spot', 0):.1f} visits per spot")
        
        # Best combination finding
        if combination_data:
            best_combo = combination_data[0]
            findings.append(f"Best combination: {best_combo.get('station', 'Unknown')} + {best_combo.get('daypart', 'Unknown')} averaging {best_combo.get('avg_visits_per_spot', 0):.1f} visits per spot")
        
        return findings[:5]
    
    def _identify_optimization_priorities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify top optimization priorities"""
        priorities = []
        
        station_data = context.get('station_performance', [])
        daypart_data = context.get('daypart_performance', [])
        
        # Station reallocation priority
        if len(station_data) >= 3:
            top_station = station_data[0]
            bottom_station = station_data[-1]
            
            if top_station.get('avg_visits_per_spot', 0) > bottom_station.get('avg_visits_per_spot', 0) * 1.5:
                priorities.append({
                    'priority': 1,
                    'area': 'Station Optimization',
                    'recommendation': f"Reallocate budget from low-performing stations to {top_station.get('station', 'top performer')}",
                    'impact': 'High',
                    'effort': 'Low',
                    'expected_benefit': f"Increase efficiency by {((top_station.get('avg_visits_per_spot', 0) / bottom_station.get('avg_visits_per_spot', 1)) - 1) * 100:.0f}%"
                })
        
        # Daypart optimization priority
        if len(daypart_data) >= 2:
            best_daypart = daypart_data[0]
            worst_daypart = daypart_data[-1]
            
            if best_daypart.get('avg_visits_per_spot', 0) > worst_daypart.get('avg_visits_per_spot', 0) * 1.3:
                priorities.append({
                    'priority': 2,
                    'area': 'Daypart Optimization',
                    'recommendation': f"Shift budget from {worst_daypart.get('daypart', 'low-performing')} to {best_daypart.get('daypart', 'high-performing')} dayparts",
                    'impact': 'High',
                    'effort': 'Medium',
                    'expected_benefit': f"Improve visit rate by {((best_daypart.get('avg_visits_per_spot', 0) / worst_daypart.get('avg_visits_per_spot', 1)) - 1) * 100:.0f}%"
                })
        
        return priorities[:3]
    
    def save_insights_csv(self, insights: Dict[str, Any], filename: str = None) -> str:
        """Save comprehensive insights as CSV for Power BI consumption"""
        
        if filename is None:
            client_name = insights['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_insights_{timestamp}"
        
        output_dir = "output/reports"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{filename}.csv")
        
        try:
            insights_data = []
            
            # Station insights
            for insight in insights.get('station_insights', []):
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'product': insight.get('product', 'DEFAULT'),  # Add product from insight or default
                    'insight_category': 'station',
                    'insight_type': insight.get('insight_type', 'station_analysis'),
                    'priority': insight.get('priority', 999),
                    'impact_level': 'High' if insight.get('priority', 999) <= 2 else 'Medium',
                    'station': insight.get('station'),
                    'daypart': None,
                    'performance_tier': insight.get('performance_tier'),
                    'opportunity_type': insight.get('opportunity_type'),
                    'recommendation': insight.get('recommendation', ''),
                    'expected_impact': insight.get('expected_impact', ''),
                    'confidence': insight.get('confidence', 'Medium'),
                    'action_type': insight.get('action_type', 'optimize'),
                    'visit_rate': insight.get('visit_rate', 0),
                    'total_visits': insight.get('total_visits', 0),
                    'spots': insight.get('spots', 0),
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Daypart insights
            for insight in insights.get('daypart_insights', []):
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'product': insight.get('product', 'DEFAULT'),  # Add product from insight or default
                    'insight_category': 'daypart',
                    'insight_type': insight.get('insight_type', 'daypart_analysis'),
                    'priority': insight.get('priority', 999),
                    'impact_level': 'High' if insight.get('priority', 999) <= 2 else 'Medium',
                    'station': None,
                    'daypart': insight.get('daypart'),
                    'performance_tier': None,
                    'opportunity_type': insight.get('efficiency_rating'),
                    'recommendation': insight.get('recommendation', ''),
                    'expected_impact': insight.get('expected_impact', ''),
                    'confidence': insight.get('confidence', 'Medium'),
                    'action_type': insight.get('action_type', 'optimize'),
                    'visit_rate': insight.get('visit_rate', 0),
                    'total_visits': insight.get('total_visits', 0),
                    'spots': insight.get('spots', 0),
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Station+Daypart combination insights
            for insight in insights.get('station_daypart_insights', []):
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'product': insight.get('product', 'DEFAULT'),  # Add product from insight or default
                    'insight_category': 'combination',
                    'insight_type': insight.get('insight_type', 'combination_analysis'),
                    'priority': insight.get('priority', 999),
                    'impact_level': 'High' if insight.get('priority', 999) <= 2 else 'Medium',
                    'station': insight.get('station'),
                    'daypart': insight.get('daypart'),
                    'performance_tier': insight.get('combo_tier'),
                    'opportunity_type': insight.get('scaling_priority'),
                    'recommendation': insight.get('recommendation', ''),
                    'expected_impact': insight.get('expected_impact', ''),
                    'confidence': insight.get('confidence', 'Medium'),
                    'action_type': insight.get('action_type', 'optimize'),
                    'visit_rate': insight.get('visit_rate', 0),
                    'total_visits': insight.get('total_visits', 0),
                    'spots': insight.get('spots', 0),
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Performance quadrant insights
            quadrants = insights.get('performance_quadrants', {})
            for quadrant_name, quadrant_data in quadrants.items():
                for item in quadrant_data:
                    insights_data.append({
                        'client': insights['metadata']['client_name'],
                        'product': item.get('product', 'DEFAULT'),  # Add product from item or default
                        'insight_category': 'quadrant',
                        'insight_type': 'quadrant_analysis',
                        'priority': 1 if quadrant_name == 'high_volume_high_efficiency' else 2,
                        'impact_level': 'High' if quadrant_name in ['high_volume_high_efficiency', 'low_volume_high_efficiency'] else 'Medium',
                        'station': item.get('station'),
                        'daypart': None,
                        'performance_tier': item.get('quadrant'),
                        'opportunity_type': quadrant_name.replace('_', ' ').title(),
                        'recommendation': item.get('action', ''),
                        'expected_impact': f"Volume: {item.get('volume', 0)}, Efficiency: {item.get('efficiency', 0):.1f}",
                        'confidence': 'High',
                        'action_type': item.get('action', '').lower().replace(' ', '_'),
                        'visit_rate': item.get('efficiency', 0),
                        'total_visits': item.get('volume', 0),
                        'spots': item.get('spots', 0),
                        'generated_date': insights['metadata']['generation_date'][:10]
                    })
            
            # Opportunity matrix insights
            for opportunity in insights.get('opportunity_matrix', []):
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'product': opportunity.get('product', 'DEFAULT'),  # Add product from opportunity or default
                    'insight_category': 'opportunity',
                    'insight_type': 'reallocation_opportunity',
                    'priority': opportunity.get('priority', 999),
                    'impact_level': 'High' if opportunity.get('priority', 999) <= 3 else 'Medium',
                    'station': f"{opportunity.get('from_station')} → {opportunity.get('to_station')}",
                    'daypart': None,
                    'performance_tier': None,
                    'opportunity_type': 'Budget Reallocation',
                    'recommendation': f"Move {opportunity.get('potential_spots_to_move', 0)} spots from {opportunity.get('from_station')} to {opportunity.get('to_station')}",
                    'expected_impact': f"Gain {opportunity.get('projected_visit_gain', 0)} visits",
                    'confidence': opportunity.get('confidence', 'Medium'),
                    'action_type': 'budget_reallocation',
                    'visit_rate': opportunity.get('efficiency_gain', 0),
                    'total_visits': opportunity.get('projected_visit_gain', 0),
                    'spots': opportunity.get('potential_spots_to_move', 0),
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Write CSV
            if insights_data:
                fieldnames = ['client', 'product', 'insight_category', 'insight_type', 'priority', 'impact_level', 
                             'station', 'daypart', 'performance_tier', 'opportunity_type', 'recommendation', 
                             'expected_impact', 'confidence', 'action_type', 'visit_rate', 'total_visits', 
                             'spots', 'generated_date']
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(insights_data)
                
                print(f"📊 Enhanced insights CSV saved to: {filepath}")
                print(f"📝 Exported {len(insights_data)} comprehensive insights to CSV")
                return filepath
            else:
                print("⚠️  No insights available for CSV export")
                return ""
                
        except Exception as e:
            print(f"❌ Error saving enhanced insights CSV: {e}")
            return ""
    
    def _fallback_enhanced_insights(self, kpis: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """Fallback insights when AI generation fails"""
        return {
            'metadata': {
                'generation_date': datetime.now().isoformat(),
                'ai_model': 'fallback',
                'client_name': client_name,
                'analysis_confidence': 0.7,
                'total_insights_generated': 1
            },
            'executive_summary': f'Enhanced TV campaign analysis for {client_name or "client"} completed with limited AI insights.',
            'key_findings': ['Enhanced AI analysis temporarily unavailable'],
            'optimization_priorities': [],
            'station_insights': [],
            'daypart_insights': [],
            'station_daypart_insights': [],
            'performance_quadrants': {},
            'opportunity_matrix': [],
            'predictive_recommendations': [],
            'budget_reallocation_analysis': {},
            'prescriptive_recommendations': {
                'optimization_recommendations': [],
                'key_findings': []
            }
        }
    
    # Template methods for AI prompts
    def _get_station_insight_template(self) -> str:
        return """Analyze each station's performance individually and provide specific insights."""
    
    def _get_daypart_insight_template(self) -> str:
        return """Analyze each daypart's efficiency and provide optimization recommendations."""
    
    def _get_combination_insight_template(self) -> str:
        return """Analyze station+daypart combinations for scaling opportunities."""
    
    def _get_performance_assessment_template(self) -> str:
        return """Assess overall campaign performance against industry benchmarks."""
    
    def _get_opportunity_analysis_template(self) -> str:
        return """Identify specific opportunities for budget reallocation and optimization."""


# Test the AI Insights Engine
if __name__ == "__main__":
    print("🧪 Testing AI Insights Engine...")
    print("=" * 60)
    
    try:
        import sys
        sys.path.append('.')
        from src.database import DatabaseManager
        from src.kpi_calculator import KPICalculator
        
        with DatabaseManager() as db:
            clients = db.get_available_clients(30)
            if clients:
                client = clients[0]
                print(f"📊 Testing insights for client: {client}")
                
                df = db.get_campaign_data(client=client, days=30)
                if not df.is_empty():
                    calculator = KPICalculator()
                    kpis = calculator.calculate_campaign_kpis(df)
                    
                    insight_generator = InsightGenerator()
                    insights = insight_generator.generate_comprehensive_insights(kpis, client)
                    
                    print(f"\n✅ AI insights test completed!")
                    print(f"📊 Insight categories generated: {list(insights.keys())}")
                    print(f"📈 Total insights: {insights['metadata']['total_insights_generated']}")
                    
                    # Test CSV export
                    csv_path = insight_generator.save_insights_csv(insights)
                    if csv_path:
                        print(f"📁 CSV saved for Power BI: {csv_path}")
                    
                else:
                    print("❌ No campaign data available for testing")
            else:
                print("❌ No clients available for testing")
                
    except ImportError as e:
        print(f"❌ Cannot import required modules: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    print("🧪 Testing Enhanced AI Insights Engine...")
    print("=" * 60)
    
    try:
        import sys
        sys.path.append('.')
        from src.database import DatabaseManager
        from src.kpi_calculator import KPICalculator
        
        with DatabaseManager() as db:
            clients = db.get_available_clients(30)
            if clients:
                client = clients[0]
                print(f"📊 Testing enhanced insights for client: {client}")
                
                df = db.get_campaign_data(client=client, days=30)
                if not df.is_empty():
                    calculator = KPICalculator()
                    kpis = calculator.calculate_campaign_kpis(df)
                    
                    insight_generator = InsightGenerator()
                    insights = insight_generator.generate_comprehensive_insights(kpis, client)
                    
                    print(f"\n✅ Enhanced insights test completed!")
                    print(f"📊 Insight categories generated: {list(insights.keys())}")
                    print(f"📈 Total insights: {insights['metadata']['total_insights_generated']}")
                    
                    # Test CSV export
                    csv_path = insight_generator.save_insights_csv(insights)
                    if csv_path:
                        print(f"📁 CSV saved for Power BI: {csv_path}")
                    
                else:
                    print("❌ No campaign data available for testing")
            else:
                print("❌ No clients available for testing")
                
    except ImportError as e:
        print(f"❌ Cannot import required modules: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")