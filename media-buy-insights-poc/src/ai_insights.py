"""
AI Insights Engine - Generate comprehensive insights for Power BI Dashboard
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
    
    def generate_comprehensive_insights(self, kpis: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive insights for Power BI dashboard
        Returns structured insights with granular station, daypart, and combination analysis
        """
        print(f"🤖 Generating AI insights for {client_name or 'campaign'}...")
        
        try:
            # Prepare context data - FIXED: Use correct method name
            context = self._prepare_context(kpis, client_name)
            
            # Generate all insight categories
            insights = {
                'metadata': {
                    'generation_date': datetime.now().isoformat(),
                    'ai_model': self.ai_settings.get('model', 'gemini-2.0-flash'),
                    'client_name': client_name,
                    'analysis_confidence': self._assess_analysis_confidence(kpis),
                    'total_insights_generated': 0  # Will be updated at the end
                },
                
                # Executive level insights
                'executive_summary': self._generate_executive_summary(context),
                'key_findings': self._extract_key_findings(context),
                'optimization_priorities': self._identify_optimization_priorities(context),
                
                # Granular insights for Power BI
                'station_insights': self._generate_station_insights(context),
                'daypart_insights': self._generate_daypart_insights(context),
                'station_daypart_insights': self._generate_combination_insights(context),
                'performance_quadrants': self._analyze_performance_quadrants(context),
                'opportunity_matrix': self._generate_opportunity_matrix(context),
                
                # Structured data for Power BI consumption
                'prescriptive_recommendations': self._generate_structured_recommendations(context)
            }
            
            # Count total insights generated
            total_insights = self._count_total_insights(insights)
            insights['metadata']['total_insights_generated'] = total_insights
            
            print(f"✅ AI insights generated: {total_insights} total insights")
            return insights
            
        except Exception as e:
            print(f"❌ Error generating insights: {e}")
            return self._fallback_insights(kpis, client_name)
    
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
        """Process station data with performance classifications"""
        if not station_data:
            return []
        
        processed_stations = []
        
        # Calculate benchmarks
        visit_rates = [s.get('avg_visits_per_spot', 0) for s in station_data if s.get('avg_visits_per_spot', 0) > 0]
        if not visit_rates:
            return station_data
        
        visit_rates.sort()
        top_quartile = visit_rates[int(len(visit_rates) * 0.75)] if len(visit_rates) > 3 else visit_rates[-1]
        median = visit_rates[int(len(visit_rates) * 0.5)]
        bottom_quartile = visit_rates[int(len(visit_rates) * 0.25)] if len(visit_rates) > 3 else visit_rates[0]
        
        for station in station_data:
            station_processed = station.copy()
            station_processed['product'] = default_product
            visit_rate = station.get('avg_visits_per_spot', 0)
            
            # Performance classification
            if visit_rate >= top_quartile:
                station_processed['performance_tier'] = 'High Performer'
                station_processed['performance_score'] = 'Excellent'
            elif visit_rate >= median:
                station_processed['performance_tier'] = 'Above Average'
                station_processed['performance_score'] = 'Good'
            elif visit_rate >= bottom_quartile:
                station_processed['performance_tier'] = 'Below Average'
                station_processed['performance_score'] = 'Fair'
            else:
                station_processed['performance_tier'] = 'Underperformer'
                station_processed['performance_score'] = 'Poor'
            
            # Opportunity classification
            total_visits = station.get('total_visits', 0)
            if total_visits > 1000 and visit_rate > median:
                station_processed['opportunity_type'] = 'Scale Winner'
            elif total_visits < 500 and visit_rate > top_quartile:
                station_processed['opportunity_type'] = 'Hidden Gem'
            elif total_visits > 1000 and visit_rate < bottom_quartile:
                station_processed['opportunity_type'] = 'Optimize or Reduce'
            else:
                station_processed['opportunity_type'] = 'Monitor'
            
            processed_stations.append(station_processed)
        
        return processed_stations
    
    def _process_daypart_data(self, daypart_data: List[Dict], default_product: str = 'DEFAULT') -> List[Dict]:
        """Process daypart data with performance insights"""
        if not daypart_data:
            return []
        
        dayparts_processed = []
        
        # Calculate daypart benchmarks
        daypart_rates = [d.get('avg_visits_per_spot', 0) for d in daypart_data if d.get('avg_visits_per_spot', 0) > 0]
        if not daypart_rates:
            return daypart_data
        
        daypart_rates.sort()
        best_performance = daypart_rates[-1]
        avg_performance = sum(daypart_rates) / len(daypart_rates)
        
        for daypart in daypart_data:
            daypart_processed = daypart.copy()
            daypart_processed['product'] = default_product
            visit_rate = daypart.get('avg_visits_per_spot', 0)
            
            # Performance relative to other dayparts
            if visit_rate >= best_performance * 0.9:
                daypart_processed['daypart_rank'] = 'Prime Time'
                daypart_processed['efficiency_rating'] = 'Excellent'
            elif visit_rate >= avg_performance:
                daypart_processed['daypart_rank'] = 'Strong Performer'
                daypart_processed['efficiency_rating'] = 'Good'
            else:
                daypart_processed['daypart_rank'] = 'Off-Peak'
                daypart_processed['efficiency_rating'] = 'Fair'
            
            # Recommendation priority
            total_spots = daypart.get('spots', 0)
            if total_spots > 50:
                if visit_rate > avg_performance:
                    daypart_processed['recommendation_priority'] = 'High - Scale Up'
                else:
                    daypart_processed['recommendation_priority'] = 'Medium - Optimize'
            else:
                if visit_rate > avg_performance:
                    daypart_processed['recommendation_priority'] = 'Medium - Test Scale'
                else:
                    daypart_processed['recommendation_priority'] = 'Low - Monitor'
            
            dayparts_processed.append(daypart_processed)
        
        return dayparts_processed
    
    def _process_combination_data(self, combination_data: List[Dict], default_product: str = 'DEFAULT') -> List[Dict]:
        """Process station+daypart combination data"""
        if not combination_data:
            return []
        
        combinations_processed = []
        
        # Calculate combination benchmarks
        combo_rates = [c.get('avg_visits_per_spot', 0) for c in combination_data if c.get('avg_visits_per_spot', 0) > 0]
        if not combo_rates:
            return combination_data
        
        combo_rates.sort()
        top_combo_rate = combo_rates[-1] if combo_rates else 0
        median_combo_rate = combo_rates[len(combo_rates) // 2] if combo_rates else 0
        
        for combo in combination_data:
            combo_processed = combo.copy()
            combo_processed['product'] = default_product
            visit_rate = combo.get('avg_visits_per_spot', 0)
            spots = combo.get('spots', 0)
            
            # Combination performance scoring
            if visit_rate >= top_combo_rate * 0.8:
                combo_processed['combo_tier'] = 'Golden Combination'
                combo_processed['scaling_priority'] = 'Immediate'
            elif visit_rate >= median_combo_rate:
                combo_processed['combo_tier'] = 'Strong Combination'
                combo_processed['scaling_priority'] = 'High'
            else:
                combo_processed['combo_tier'] = 'Standard Combination'
                combo_processed['scaling_priority'] = 'Low'
            
            # Sample size confidence
            if spots >= 20:
                combo_processed['confidence_level'] = 'High'
            elif spots >= 10:
                combo_processed['confidence_level'] = 'Medium'
            else:
                combo_processed['confidence_level'] = 'Low'
            
            combinations_processed.append(combo_processed)
        
        return combinations_processed
    
    def _generate_station_insights(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific insights for each station"""
        
        station_data = context.get('station_performance', [])
        if not station_data:
            return []
        
        insights = []
        
        for station in station_data[:10]:  # Top 10 stations
            station_name = station.get('station', 'Unknown')
            product = station.get('product', context.get('primary_product', 'DEFAULT'))
            visit_rate = station.get('avg_visits_per_spot', 0)
            total_visits = station.get('total_visits', 0)
            spots = station.get('spots', 0)
            performance_tier = station.get('performance_tier', 'Unknown')
            opportunity_type = station.get('opportunity_type', 'Monitor')
            
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
                insight['expected_impact'] = f"Redirect spend to higher-performing stations"
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
                insight['expected_impact'] = f"Scale to capture additional visits"
                insight['action_type'] = 'increase_daypart_budget'
                insight['priority'] = 1
            elif 'Test Scale' in recommendation_priority:
                insight['recommendation'] = f"Test increasing {daypart_name} investment - shows efficiency potential"
                insight['expected_impact'] = f"Controlled test could yield more visits"
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
        
        for combo in combination_data[:15]:  # Top 15 combinations
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
                insight['expected_impact'] = f"High-confidence opportunity for additional visits"
                insight['action_type'] = 'scale_combination'
                insight['priority'] = 1
            elif combo_tier == 'Strong Combination':
                insight['recommendation'] = f"Increase investment in {station} + {daypart} - proven strong performance"
                insight['expected_impact'] = f"Medium-risk opportunity for additional visits"
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
            top_performers = sorted_stations[:2]
            bottom_performers = sorted_stations[-2:]
            
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
        
        return opportunities[:5]  # Top 5 opportunities
    
    def _generate_structured_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured recommendations for CSV export to Power BI"""
        
        recommendations = []
        findings = []
        
        # Station-level recommendations
        station_data = context.get('station_performance', [])
        for i, station in enumerate(station_data[:5], 1):  # Reduced from 10 to 5
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
                    'description': f"{station_name} is highly efficient with {visit_rate:.1f} visits per spot.",
                    'impact_level': 'High'
                })
        
        # Daypart-level recommendations (simplified)
        daypart_data = context.get('daypart_performance', [])
        for i, daypart in enumerate(daypart_data[:3], 1):  # Top 3 only
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
        
        # Count quadrant analysis
        quadrants = insights.get('performance_quadrants', {})
        for quadrant_data in quadrants.values():
            count += len(quadrant_data)
        
        # Count opportunity matrix
        count += len(insights.get('opportunity_matrix', []))
        
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
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    
    def _generate_executive_summary(self, context: Dict[str, Any]) -> str:
        """Generate executive-level summary"""
        campaign_overview = context.get('campaign_overview', {})
        
        total_spots = campaign_overview.get('total_spots', 0)
        total_visits = campaign_overview.get('total_visits', 0)
        total_revenue = campaign_overview.get('total_revenue', 0)
        total_orders = campaign_overview.get('total_orders', 0)
        
        # Create context-aware summary
        if total_revenue > 0:
            return f"TV campaign generated ${total_revenue:,.0f} in revenue through {total_orders:,} orders from {total_visits:,} website visits across {total_spots} TV spots."
        elif total_visits > 0:
            visits_per_spot = total_visits / total_spots if total_spots > 0 else 0
            performance_desc = "strong" if visits_per_spot > 2 else "solid" if visits_per_spot > 1 else "moderate"
            return f"TV campaign generated {total_visits:,} website visits from {total_spots} spots, achieving {performance_desc} audience engagement with {visits_per_spot:.1f} visits per spot."
        else:
            return f"Campaign analysis covers {total_spots} TV spots with limited attribution data available."
    
    def _extract_key_findings(self, context: Dict[str, Any]) -> List[str]:
        """Extract key findings focused on actionable insights"""
        findings = []
        
        campaign_overview = context.get('campaign_overview', {})
        station_data = context.get('station_performance', [])
        daypart_data = context.get('daypart_performance', [])
        
        # Overall performance finding
        total_spots = campaign_overview.get('total_spots', 0)
        total_visits = campaign_overview.get('total_visits', 0)
        if total_visits > 0 and total_spots > 0:
            visit_rate = total_visits / total_spots
            performance_level = "Strong" if visit_rate > 2 else "Solid" if visit_rate > 1 else "Moderate"
            findings.append(f"{performance_level} engagement: {visit_rate:.1f} visits per TV spot")
        
        # Top station finding
        if station_data:
            top_station = station_data[0]
            findings.append(f"Top station {top_station.get('station', 'Unknown')} generated {top_station.get('total_visits', 0):,} visits from {top_station.get('spots', 0)} spots")
        
        # Best daypart finding
        if daypart_data:
            best_daypart = daypart_data[0]
            findings.append(f"{best_daypart.get('daypart', 'Unknown')} daypart shows highest efficiency at {best_daypart.get('avg_visits_per_spot', 0):.1f} visits per spot")
        
        return findings[:3]  # Top 3 only
    
    def _identify_optimization_priorities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify top optimization priorities"""
        priorities = []
        
        station_data = context.get('station_performance', [])
        daypart_data = context.get('daypart_performance', [])
        
        # Station reallocation priority
        if len(station_data) >= 2:
            top_station = station_data[0]
            bottom_station = station_data[-1]
            
            if top_station.get('avg_visits_per_spot', 0) > bottom_station.get('avg_visits_per_spot', 0) * 1.5:
                priorities.append({
                    'priority': 1,
                    'area': 'Station Optimization',
                    'recommendation': f"Reallocate budget from low-performing stations to {top_station.get('station', 'top performer')}",
                    'impact': 'High',
                    'effort': 'Low'
                })
        
        # Daypart optimization priority
        if len(daypart_data) >= 2:
            best_daypart = daypart_data[0]
            worst_daypart = daypart_data[-1]
            
            if best_daypart.get('avg_visits_per_spot', 0) > worst_daypart.get('avg_visits_per_spot', 0) * 1.3:
                priorities.append({
                    'priority': 2,
                    'area': 'Daypart Optimization',
                    'recommendation': f"Shift budget to {best_daypart.get('daypart', 'high-performing')} dayparts",
                    'impact': 'High',
                    'effort': 'Medium'
                })
        
        return priorities[:2]  # Top 2 only
    
    def save_insights_csv(self, insights: Dict[str, Any], filename: str = None) -> str:
        """Save comprehensive insights as CSV for Power BI consumption with standardized structure"""
        
        if filename is None:
            client_name = insights['metadata']['client_name'].replace(' ', '_').lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{client_name}_insights_{timestamp}"
        
        output_dir = "output/reports"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{filename}.csv")
        
        try:
            insights_data = []
            
            # Key Findings (Executive Level)
            key_findings = insights.get('key_findings', [])
            for i, finding in enumerate(key_findings, 1):
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'insight_category': 'key_finding',
                    'insight_type': 'executive_summary',
                    'priority': i,
                    'impact_level': 'High',
                    'station': None,
                    'daypart': None,
                    'metric_type': 'overall_performance',
                    'finding_description': finding,
                    'recommendation': f"Key insight: {finding}",
                    'action_required': 'monitor_and_leverage',
                    'confidence': 'High',
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Key Optimizations (Executive Level)
            optimization_priorities = insights.get('optimization_priorities', [])
            for opt in optimization_priorities:
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'insight_category': 'key_optimization',
                    'insight_type': 'strategic_recommendation',
                    'priority': opt.get('priority', 999),
                    'impact_level': opt.get('impact', 'Medium'),
                    'station': None,
                    'daypart': None,
                    'metric_type': opt.get('area', 'optimization').lower().replace(' ', '_'),
                    'finding_description': opt.get('recommendation', ''),
                    'recommendation': opt.get('recommendation', ''),
                    'action_required': 'implement_immediately',
                    'confidence': 'High',
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Station Insights (Standardized)
            for insight in insights.get('station_insights', []):
                # Standardize opportunity types
                opportunity_type = insight.get('opportunity_type', 'Monitor')
                if opportunity_type == 'Scale Winner':
                    action_required = 'scale_immediately'
                    metric_type = 'high_volume_high_efficiency'
                elif opportunity_type == 'Hidden Gem':
                    action_required = 'test_scaling'
                    metric_type = 'low_volume_high_efficiency'
                elif opportunity_type == 'Optimize or Reduce':
                    action_required = 'optimize_or_reduce'
                    metric_type = 'high_volume_low_efficiency'
                else:
                    action_required = 'monitor'
                    metric_type = 'standard_performance'
                
                # Standardize performance tiers
                performance_tier = insight.get('performance_tier', 'Unknown')
                if 'High' in performance_tier:
                    standardized_tier = 'top_performer'
                elif 'Above' in performance_tier:
                    standardized_tier = 'above_average'
                elif 'Below' in performance_tier:
                    standardized_tier = 'below_average'
                elif 'Under' in performance_tier:
                    standardized_tier = 'underperformer'
                else:
                    standardized_tier = 'average'
                
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'insight_category': 'station_analysis',
                    'insight_type': 'station_optimization',
                    'priority': insight.get('priority', 999),
                    'impact_level': 'High' if insight.get('priority', 999) <= 2 else 'Medium',
                    'station': insight.get('station'),
                    'daypart': None,
                    'metric_type': metric_type,
                    'finding_description': f"{insight.get('station')} is a {standardized_tier} with {insight.get('visit_rate', 0):.1f} visits per spot",
                    'recommendation': insight.get('recommendation', ''),
                    'action_required': action_required,
                    'confidence': insight.get('confidence', 'Medium'),
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Daypart Insights (Standardized)
            for insight in insights.get('daypart_insights', []):
                # Standardize efficiency ratings
                efficiency_rating = insight.get('efficiency_rating', 'Unknown')
                if efficiency_rating == 'Excellent':
                    action_required = 'scale_immediately'
                    metric_type = 'prime_time_efficiency'
                elif efficiency_rating == 'Good':
                    action_required = 'increase_investment'
                    metric_type = 'strong_efficiency'
                elif efficiency_rating == 'Fair':
                    action_required = 'optimize'
                    metric_type = 'average_efficiency'
                else:
                    action_required = 'monitor'
                    metric_type = 'standard_efficiency'
                
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'insight_category': 'daypart_analysis',
                    'insight_type': 'daypart_optimization',
                    'priority': insight.get('priority', 999),
                    'impact_level': 'High' if insight.get('priority', 999) <= 2 else 'Medium',
                    'station': None,
                    'daypart': insight.get('daypart'),
                    'metric_type': metric_type,
                    'finding_description': f"{insight.get('daypart')} daypart shows {efficiency_rating.lower()} efficiency with {insight.get('visit_rate', 0):.1f} visits per spot",
                    'recommendation': insight.get('recommendation', ''),
                    'action_required': action_required,
                    'confidence': insight.get('confidence', 'Medium'),
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Station+Daypart Combination Insights (Standardized)
            for insight in insights.get('station_daypart_insights', [])[:10]:  # Top 10 only
                # Standardize combo tiers
                combo_tier = insight.get('combo_tier', 'Standard')
                if combo_tier == 'Golden Combination':
                    action_required = 'scale_immediately'
                    metric_type = 'golden_combination'
                elif combo_tier == 'Strong Combination':
                    action_required = 'increase_investment'
                    metric_type = 'strong_combination'
                else:
                    action_required = 'monitor'
                    metric_type = 'standard_combination'
                
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'insight_category': 'combination_analysis',
                    'insight_type': 'combination_optimization',
                    'priority': insight.get('priority', 999),
                    'impact_level': 'High' if insight.get('priority', 999) <= 2 else 'Medium',
                    'station': insight.get('station'),
                    'daypart': insight.get('daypart'),
                    'metric_type': metric_type,
                    'finding_description': f"{insight.get('station')} + {insight.get('daypart')} is a {combo_tier.lower()} with {insight.get('visit_rate', 0):.1f} visits per spot",
                    'recommendation': insight.get('recommendation', ''),
                    'action_required': action_required,
                    'confidence': insight.get('confidence', 'Medium'),
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Budget Reallocation Opportunities (Standardized)
            for i, opportunity in enumerate(insights.get('opportunity_matrix', [])[:5], 1):
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'insight_category': 'budget_opportunity',
                    'insight_type': 'reallocation_recommendation',
                    'priority': i,
                    'impact_level': 'High' if opportunity.get('confidence') == 'High' else 'Medium',
                    'station': f"{opportunity.get('from_station')} -> {opportunity.get('to_station')}",
                    'daypart': None,
                    'metric_type': 'budget_reallocation',
                    'finding_description': f"Move budget from {opportunity.get('from_station')} to {opportunity.get('to_station')} for {opportunity.get('projected_visit_gain', 0)} additional visits",
                    'recommendation': f"Reallocate {opportunity.get('potential_spots_to_move', 0)} spots from {opportunity.get('from_station')} to {opportunity.get('to_station')}",
                    'action_required': 'reallocate_budget',
                    'confidence': opportunity.get('confidence', 'Medium'),
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Write CSV with standardized structure
            if insights_data:
                fieldnames = ['client', 'insight_category', 'insight_type', 'priority', 'impact_level', 
                             'station', 'daypart', 'metric_type', 'finding_description', 'recommendation', 
                             'action_required', 'confidence', 'generated_date']
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(insights_data)
                
                print(f"📊 Insights CSV saved: {filepath}")
                return filepath
            else:
                print("⚠️  No insights available for CSV export")
                return ""
                
        except Exception as e:
            print(f"❌ Error saving insights CSV: {e}")
            return ""
    
    def _fallback_insights(self, kpis: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """Fallback insights when AI generation fails"""
        return {
            'metadata': {
                'generation_date': datetime.now().isoformat(),
                'ai_model': 'fallback',
                'client_name': client_name,
                'analysis_confidence': 0.7,
                'total_insights_generated': 1
            },
            'executive_summary': f'TV campaign analysis for {client_name or "client"} completed with limited AI insights.',
            'key_findings': ['AI analysis temporarily unavailable'],
            'optimization_priorities': [],
            'station_insights': [],
            'daypart_insights': [],
            'station_daypart_insights': [],
            'performance_quadrants': {},
            'opportunity_matrix': [],
            'prescriptive_recommendations': {
                'optimization_recommendations': [],
                'key_findings': []
            }
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
                print(f"📊 Testing insights for client: {client}")
                
                df = db.get_campaign_data(client=client, days=30)
                if not df.is_empty():
                    calculator = KPICalculator()
                    kpis = calculator.calculate_campaign_kpis(df)
                    
                    insight_generator = InsightGenerator()
                    insights = insight_generator.generate_comprehensive_insights(kpis, client)
                    
                    print(f"\n✅ AI insights test completed!")
                    print(f"📈 Total insights: {insights['metadata']['total_insights_generated']}")
                    
                    # Test CSV export
                    csv_path = insight_generator.save_insights_csv(insights)
                    if csv_path:
                        print(f"📁 CSV saved: {csv_path}")
                    
                else:
                    print("❌ No campaign data available")
            else:
                print("❌ No clients available")
                
    except ImportError as e:
        print(f"❌ Cannot import required modules: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")