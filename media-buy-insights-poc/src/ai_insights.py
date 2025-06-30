"""
AI Insights Engine - Generate comprehensive insights for Power BI Dashboard
Produces station-level, daypart-level, and combination-level insights with time-based analysis
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
        """Generate comprehensive insights for Power BI dashboard with time-based analysis"""
        print(f"🤖 Generating AI insights for {client_name or 'campaign'}...")
        
        try:
            # Prepare context data with time-based analysis
            context = self._prepare_context(kpis, client_name)
            
            # Generate all insight categories
            insights = {
                'metadata': {
                    'generation_date': datetime.now().isoformat(),
                    'ai_model': self.ai_settings.get('model', 'gemini-2.0-flash'),
                    'client_name': client_name,
                    'analysis_confidence': self._assess_analysis_confidence(kpis),
                    'total_insights_generated': 0
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
                
                # Time-based analysis
                'recent_vs_historical': context.get('recent_vs_historical', {}),
                'weekly_trends': context.get('weekly_trends', {}),
                
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
        """Prepare comprehensive context data for AI analysis with time-based insights"""
        
        totals = kpis.get('totals', {})
        efficiency = kpis.get('efficiency', {})
        dimensional = kpis.get('dimensional_analysis', {})
        time_patterns = kpis.get('time_patterns', {})
        metadata = kpis.get('metadata', {})
        
        # Extract product information from metadata if available
        default_product = metadata.get('primary_product', 'DEFAULT')
        
        # Enhanced context with time-based analysis
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
            
            # Enhanced with time-based processing
            'station_performance': self._process_station_data_with_trends(
                dimensional.get('station_performance', []), time_patterns, default_product),
            'daypart_performance': self._process_daypart_data_with_trends(
                dimensional.get('daypart_performance', []), time_patterns, default_product),
            'combination_performance': self._process_combination_data(
                dimensional.get('station_daypart_combinations', []), default_product),
            
            # Weekly trends analysis
            'weekly_trends': self._analyze_weekly_trends(time_patterns),
            'recent_vs_historical': self._compare_recent_vs_historical(time_patterns),
            
            'targets': kpis.get('targets', {}),
            'time_patterns': time_patterns
        }
        
        return context
    
    def _process_station_data_with_trends(self, station_data: List[Dict], 
                                        time_patterns: Dict, default_product: str = 'DEFAULT') -> List[Dict]:
        """Process station data with weekly trend analysis"""
        if not station_data:
            return []
        
        processed_stations = []
        
        # Get weekly trends if available
        daily_trends = time_patterns.get('daily_trends', [])
        weekly_data = self._aggregate_to_weekly(daily_trends) if daily_trends else []
        
        # Calculate benchmarks
        visit_rates = [s.get('avg_visits_per_spot', 0) for s in station_data 
                      if s.get('avg_visits_per_spot', 0) > 0]
        if not visit_rates:
            return station_data
        
        visit_rates.sort()
        top_quartile = visit_rates[int(len(visit_rates) * 0.75)] if len(visit_rates) > 3 else visit_rates[-1]
        median = visit_rates[int(len(visit_rates) * 0.5)]
        
        for station in station_data:
            station_processed = station.copy()
            station_processed['product'] = default_product
            visit_rate = station.get('avg_visits_per_spot', 0)
            station_name = station.get('station', 'Unknown')
            
            # Add weekly trend analysis
            weekly_trend = self._calculate_weekly_trend(weekly_data)
            station_processed.update(weekly_trend)
            
            # Performance classification with trend context
            if visit_rate >= top_quartile:
                base_tier = 'High Performer'
            elif visit_rate >= median:
                base_tier = 'Above Average'
            else:
                base_tier = 'Below Average'
            
            # Adjust classification based on trends
            trend_direction = weekly_trend.get('trend_direction', 'stable')
            if trend_direction == 'improving':
                station_processed['performance_tier'] = f'{base_tier} (Improving)'
            elif trend_direction == 'declining':
                station_processed['performance_tier'] = f'{base_tier} (Declining)'
            else:
                station_processed['performance_tier'] = base_tier
            
            # Opportunity classification with trend context
            total_visits = station.get('total_visits', 0)
            recent_performance = weekly_trend.get('recent_avg_efficiency', visit_rate)
            
            if total_visits > 1000 and recent_performance > median and trend_direction != 'declining':
                station_processed['opportunity_type'] = 'Scale Winner'
            elif total_visits < 500 and recent_performance > top_quartile and trend_direction == 'improving':
                station_processed['opportunity_type'] = 'Hidden Gem'
            elif trend_direction == 'improving':
                station_processed['opportunity_type'] = 'Rising Star'
            elif total_visits > 1000 and trend_direction == 'declining':
                station_processed['opportunity_type'] = 'Optimize or Reduce'
            else:
                station_processed['opportunity_type'] = 'Monitor'
            
            processed_stations.append(station_processed)
        
        return processed_stations
    
    def _process_daypart_data_with_trends(self, daypart_data: List[Dict], 
                                        time_patterns: Dict, default_product: str = 'DEFAULT') -> List[Dict]:
        """Process daypart data with weekly trend analysis"""
        if not daypart_data:
            return []
        
        dayparts_processed = []
        
        # Get weekly trends if available
        daily_trends = time_patterns.get('daily_trends', [])
        weekly_data = self._aggregate_to_weekly(daily_trends) if daily_trends else []
        
        # Calculate daypart benchmarks
        daypart_rates = [d.get('avg_visits_per_spot', 0) for d in daypart_data 
                        if d.get('avg_visits_per_spot', 0) > 0]
        if not daypart_rates:
            return daypart_data
        
        avg_performance = sum(daypart_rates) / len(daypart_rates)
        
        for daypart in daypart_data:
            daypart_processed = daypart.copy()
            daypart_processed['product'] = default_product
            visit_rate = daypart.get('avg_visits_per_spot', 0)
            
            # Add weekly trend analysis for daypart
            weekly_trend = self._calculate_weekly_trend(weekly_data)
            daypart_processed.update(weekly_trend)
            
            # Performance relative to other dayparts with trend context
            trend_direction = weekly_trend.get('trend_direction', 'stable')
            recent_performance = weekly_trend.get('recent_avg_efficiency', visit_rate)
            
            if recent_performance >= avg_performance * 1.2:
                base_rating = 'Excellent'
            elif recent_performance >= avg_performance:
                base_rating = 'Good'
            else:
                base_rating = 'Fair'
            
            # Adjust based on trends
            if trend_direction == 'improving':
                daypart_processed['efficiency_rating'] = f'{base_rating} - Trending Up'
            elif trend_direction == 'declining':
                daypart_processed['efficiency_rating'] = f'{base_rating} - Trending Down'
            else:
                daypart_processed['efficiency_rating'] = base_rating
            
            # Recommendation priority with trend context
            total_spots = daypart.get('spots', 0)
            if total_spots > 50 and recent_performance > avg_performance and trend_direction != 'declining':
                daypart_processed['recommendation_priority'] = 'High - Scale Up'
            elif trend_direction == 'declining':
                daypart_processed['recommendation_priority'] = 'Medium - Investigate Decline'
            elif recent_performance > avg_performance:
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
        combo_rates = [c.get('avg_visits_per_spot', 0) for c in combination_data 
                      if c.get('avg_visits_per_spot', 0) > 0]
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
    
    def _aggregate_to_weekly(self, daily_trends: List[Dict]) -> List[Dict]:
        """Aggregate daily data to weekly for trend analysis"""
        if not daily_trends:
            return []
        
        weekly_data = []
        current_week = []
        
        for i, day in enumerate(daily_trends):
            current_week.append(day)
            
            # Every 7 days or at the end, create a week summary
            if len(current_week) >= 7 or i == len(daily_trends) - 1:
                if current_week:
                    week_summary = {
                        'week_start': current_week[0].get('date', 'Unknown'),
                        'week_end': current_week[-1].get('date', 'Unknown'),
                        'total_spots': sum(d.get('spots', 0) for d in current_week),
                        'total_visits': sum(d.get('visits', 0) for d in current_week),
                        'avg_daily_efficiency': (sum(d.get('visits', 0) for d in current_week) / 
                                               max(sum(d.get('spots', 1) for d in current_week), 1))
                    }
                    weekly_data.append(week_summary)
                current_week = []
        
        return weekly_data
    
    def _calculate_weekly_trend(self, weekly_data: List[Dict]) -> Dict:
        """Calculate weekly trend for trend analysis"""
        if len(weekly_data) < 2:
            return {
                'trend_direction': 'stable',
                'recent_avg_efficiency': 0,
                'weeks_analyzed': len(weekly_data)
            }
        
        # Use overall weekly trends
        recent_weeks = weekly_data[-2:] if len(weekly_data) >= 2 else weekly_data
        earlier_weeks = weekly_data[:-2] if len(weekly_data) > 2 else []
        
        recent_avg = sum(w.get('avg_daily_efficiency', 0) for w in recent_weeks) / len(recent_weeks)
        
        if earlier_weeks:
            earlier_avg = sum(w.get('avg_daily_efficiency', 0) for w in earlier_weeks) / len(earlier_weeks)
            if recent_avg > earlier_avg * 1.1:
                trend_direction = 'improving'
            elif recent_avg < earlier_avg * 0.9:
                trend_direction = 'declining'
            else:
                trend_direction = 'stable'
        else:
            trend_direction = 'stable'
        
        return {
            'trend_direction': trend_direction,
            'recent_avg_efficiency': recent_avg,
            'weeks_analyzed': len(weekly_data)
        }
    
    def _analyze_weekly_trends(self, time_patterns: Dict) -> Dict:
        """Analyze overall weekly trends"""
        daily_trends = time_patterns.get('daily_trends', [])
        if not daily_trends:
            return {'trend_analysis': 'insufficient_data'}
        
        weekly_data = self._aggregate_to_weekly(daily_trends)
        
        if len(weekly_data) < 2:
            return {'trend_analysis': 'insufficient_weeks'}
        
        # Calculate week-over-week changes
        week_over_week_changes = []
        for i in range(1, len(weekly_data)):
            prev_week = weekly_data[i-1]
            curr_week = weekly_data[i]
            
            efficiency_change = ((curr_week.get('avg_daily_efficiency', 0) - 
                                prev_week.get('avg_daily_efficiency', 0)) / 
                               max(prev_week.get('avg_daily_efficiency', 1), 1)) * 100
            
            week_over_week_changes.append({
                'week': i + 1,
                'efficiency_change_pct': efficiency_change
            })
        
        return {
            'weekly_data': weekly_data,
            'week_over_week_changes': week_over_week_changes,
            'trend_analysis': 'completed'
        }
    
    def _compare_recent_vs_historical(self, time_patterns: Dict) -> Dict:
        """Compare recent performance vs historical average"""
        daily_trends = time_patterns.get('daily_trends', [])
        if not daily_trends or len(daily_trends) < 14:
            return {'comparison': 'insufficient_data'}
        
        # Split into recent (last 7 days) and historical (everything else)
        recent_days = daily_trends[-7:]
        historical_days = daily_trends[:-7]
        
        recent_avg_efficiency = (sum(d.get('visits', 0) for d in recent_days) / 
                               max(sum(d.get('spots', 1) for d in recent_days), 1))
        historical_avg_efficiency = (sum(d.get('visits', 0) for d in historical_days) / 
                                    max(sum(d.get('spots', 1) for d in historical_days), 1))
        
        performance_change = ((recent_avg_efficiency - historical_avg_efficiency) / 
                            max(historical_avg_efficiency, 1)) * 100
        
        if performance_change > 10:
            trend_assessment = 'significantly_improved'
        elif performance_change > 5:
            trend_assessment = 'improved'
        elif performance_change < -10:
            trend_assessment = 'significantly_declined'
        elif performance_change < -5:
            trend_assessment = 'declined'
        else:
            trend_assessment = 'stable'
        
        return {
            'recent_avg_efficiency': recent_avg_efficiency,
            'historical_avg_efficiency': historical_avg_efficiency,
            'performance_change_pct': performance_change,
            'trend_assessment': trend_assessment
        }
    
    def _generate_executive_summary(self, context: Dict[str, Any]) -> str:
        """Generate executive-level summary with time-based context"""
        campaign_overview = context.get('campaign_overview', {})
        recent_vs_historical = context.get('recent_vs_historical', {})
        
        total_spots = campaign_overview.get('total_spots', 0)
        total_visits = campaign_overview.get('total_visits', 0)
        total_revenue = campaign_overview.get('total_revenue', 0)
        total_orders = campaign_overview.get('total_orders', 0)
        
        # Get trend context
        trend_assessment = recent_vs_historical.get('trend_assessment', 'stable')
        performance_change = recent_vs_historical.get('performance_change_pct', 0)
        
        # Create time-aware summary
        if total_revenue > 0:
            base_summary = f"TV campaign generated ${total_revenue:,.0f} in revenue through {total_orders:,} orders from {total_visits:,} website visits across {total_spots} TV spots."
            
            if trend_assessment in ['significantly_improved', 'improved']:
                trend_context = f" Recent performance shows {performance_change:.1f}% improvement."
            elif trend_assessment in ['significantly_declined', 'declined']:
                trend_context = f" Performance has declined {abs(performance_change):.1f}% recently - optimization needed."
            else:
                trend_context = f" Performance remains stable."
                
            return base_summary + trend_context
            
        elif total_visits > 0:
            visits_per_spot = total_visits / total_spots if total_spots > 0 else 0
            performance_desc = "strong" if visits_per_spot > 2 else "solid" if visits_per_spot > 1 else "moderate"
            base_summary = f"TV campaign generated {total_visits:,} website visits from {total_spots} spots, achieving {performance_desc} audience engagement."
            
            if trend_assessment in ['significantly_improved', 'improved']:
                trend_context = f" Campaign shows {performance_change:.1f}% improvement in efficiency."
            elif trend_assessment in ['significantly_declined', 'declined']:
                trend_context = f" Campaign efficiency declined {abs(performance_change):.1f}% recently."
            else:
                trend_context = f" Campaign maintains consistent performance."
                
            return base_summary + trend_context
        else:
            return f"Campaign analysis covers {total_spots} TV spots with limited attribution data available."
    
    def _extract_key_findings(self, context: Dict[str, Any]) -> List[str]:
        """Extract key findings with time-based insights"""
        findings = []
        
        campaign_overview = context.get('campaign_overview', {})
        station_data = context.get('station_performance', [])
        daypart_data = context.get('daypart_performance', [])
        recent_vs_historical = context.get('recent_vs_historical', {})
        
        # Overall performance finding with trend
        total_spots = campaign_overview.get('total_spots', 0)
        total_visits = campaign_overview.get('total_visits', 0)
        trend_assessment = recent_vs_historical.get('trend_assessment', 'stable')
        performance_change = recent_vs_historical.get('performance_change_pct', 0)
        
        if total_visits > 0 and total_spots > 0:
            visit_rate = total_visits / total_spots
            performance_level = "Strong" if visit_rate > 2 else "Solid" if visit_rate > 1 else "Moderate"
            
            if trend_assessment in ['significantly_improved', 'improved']:
                findings.append(f"{performance_level} engagement trending up: {visit_rate:.1f} visits per spot with {performance_change:.1f}% recent improvement")
            elif trend_assessment in ['significantly_declined', 'declined']:
                findings.append(f"{performance_level} engagement declining: {visit_rate:.1f} visits per spot down {abs(performance_change):.1f}% recently")
            else:
                findings.append(f"{performance_level} engagement stable: {visit_rate:.1f} visits per TV spot")
        
        # Top station finding with trend context
        if station_data:
            top_station = station_data[0]
            station_name = top_station.get('station', 'Unknown')
            station_visits = top_station.get('total_visits', 0)
            station_spots = top_station.get('spots', 0)
            trend_direction = top_station.get('trend_direction', 'stable')
            
            if trend_direction == 'improving':
                findings.append(f"Top station {station_name} accelerating: {station_visits:,} visits from {station_spots} spots with improving trends")
            elif trend_direction == 'declining':
                findings.append(f"Top station {station_name} declining: {station_visits:,} visits from {station_spots} spots but efficiency dropping")
            else:
                findings.append(f"Top station {station_name} consistent: {station_visits:,} visits from {station_spots} spots")
        
        # Best daypart finding with trend
        if daypart_data:
            best_daypart = daypart_data[0]
            daypart_name = best_daypart.get('daypart', 'Unknown')
            daypart_efficiency = best_daypart.get('avg_visits_per_spot', 0)
            trend_direction = best_daypart.get('trend_direction', 'stable')
            
            if trend_direction == 'improving':
                findings.append(f"{daypart_name} daypart strengthening: {daypart_efficiency:.1f} visits per spot and improving")
            elif trend_direction == 'declining':
                findings.append(f"{daypart_name} daypart weakening: {daypart_efficiency:.1f} visits per spot but declining")
            else:
                findings.append(f"{daypart_name} daypart leads efficiency: {daypart_efficiency:.1f} visits per spot")
        
        return findings[:4]  # Top 4 findings with time context
    
    def _generate_station_insights(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific insights for each station with weekly trend context"""
        
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
            
            # Get trend context
            trend_direction = station.get('trend_direction', 'stable')
            recent_efficiency = station.get('recent_avg_efficiency', visit_rate)
            weeks_analyzed = station.get('weeks_analyzed', 0)
            
            insight = {
                'station': station_name,
                'product': product,
                'insight_type': 'station_analysis',
                'performance_tier': performance_tier,
                'opportunity_type': opportunity_type,
                'visit_rate': visit_rate,
                'recent_efficiency': recent_efficiency,
                'total_visits': total_visits,
                'spots': spots,
                'trend_direction': trend_direction,
                'confidence': 'High' if spots >= 20 and weeks_analyzed >= 2 else 'Medium' if spots >= 10 else 'Low'
            }
            
            # Generate time-contextualized recommendations
            if trend_direction == 'improving' and opportunity_type in ['Hidden Gem', 'Rising Star']:
                insight['recommendation'] = f"Scale {station_name} immediately - showing strong improvement trend"
                insight['expected_impact'] = f"Capitalize on improving trend: {recent_efficiency:.1f} recent vs {visit_rate:.1f} overall visits/spot"
                insight['action_type'] = 'scale_trending_winner'
                insight['priority'] = 1
                
            elif trend_direction == 'declining' and opportunity_type == 'Scale Winner':
                insight['recommendation'] = f"Investigate {station_name} performance decline - was top performer but trending down"
                insight['expected_impact'] = f"Address declining trend: {recent_efficiency:.1f} recent vs {visit_rate:.1f} overall visits/spot"
                insight['action_type'] = 'investigate_decline'
                insight['priority'] = 1
                
            elif opportunity_type == 'Scale Winner' and trend_direction != 'declining':
                insight['recommendation'] = f"Continue scaling {station_name} - consistent high performer"
                insight['expected_impact'] = f"Reliable performance: {recent_efficiency:.1f} recent efficiency"
                insight['action_type'] = 'scale_stable_winner'
                insight['priority'] = 2
                
            elif opportunity_type == 'Optimize or Reduce':
                if trend_direction == 'improving':
                    insight['recommendation'] = f"Monitor {station_name} closely - poor overall but recent improvement detected"
                    insight['expected_impact'] = f"Potential turnaround: {recent_efficiency:.1f} recent vs {visit_rate:.1f} overall"
                    insight['action_type'] = 'monitor_improvement'
                    insight['priority'] = 3
                else:
                    insight['recommendation'] = f"Reduce spend on {station_name} - poor performance with no improvement"
                    insight['expected_impact'] = f"Redirect budget from underperformer"
                    insight['action_type'] = 'reduce_spend'
                    insight['priority'] = 1
                
            else:
                insight['recommendation'] = f"Monitor {station_name} - {trend_direction} performance trend"
                insight['expected_impact'] = f"Track {trend_direction} trend"
                insight['action_type'] = 'monitor'
                insight['priority'] = 3
            
            insights.append(insight)
        
        return insights
    
    def _generate_daypart_insights(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific insights for each daypart with weekly trend context"""
        
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
            
            # Get trend context
            trend_direction = daypart.get('trend_direction', 'stable')
            recent_efficiency = daypart.get('recent_avg_efficiency', visit_rate)
            weeks_analyzed = daypart.get('weeks_analyzed', 0)
            
            insight = {
                'daypart': daypart_name,
                'product': product,
                'insight_type': 'daypart_analysis',
                'efficiency_rating': efficiency_rating,
                'recommendation_priority': recommendation_priority,
                'visit_rate': visit_rate,
                'recent_efficiency': recent_efficiency,
                'total_visits': total_visits,
                'spots': spots,
                'trend_direction': trend_direction,
                'confidence': 'High' if spots >= 30 and weeks_analyzed >= 2 else 'Medium' if spots >= 15 else 'Low'
            }
            
            # Generate time-contextualized daypart recommendations
            if 'Scale Up' in recommendation_priority and trend_direction != 'declining':
                insight['recommendation'] = f"Immediately increase {daypart_name} budget - top efficiency with {trend_direction} trend"
                insight['action_type'] = 'increase_daypart_budget'
                insight['priority'] = 1
            elif 'Scale Up' in recommendation_priority and trend_direction == 'declining':
                insight['recommendation'] = f"Investigate {daypart_name} decline - was top performer but efficiency dropping"
                insight['action_type'] = 'investigate_daypart_decline'
                insight['priority'] = 1
            elif 'Test Scale' in recommendation_priority and trend_direction == 'improving':
                insight['recommendation'] = f"Test increasing {daypart_name} investment - efficiency improving"
                insight['action_type'] = 'test_daypart_increase'
                insight['priority'] = 2
            else:
                insight['recommendation'] = f"Monitor {daypart_name} trends - {trend_direction} performance"
                insight['action_type'] = 'monitor_daypart'
                insight['priority'] = 3
            
            insight['expected_impact'] = f"Track {trend_direction} trend: {recent_efficiency:.1f} recent efficiency"
            
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
                insight['recommendation'] = f"Scale {station} + {daypart} immediately - golden combination"
                insight['action_type'] = 'scale_combination'
                insight['priority'] = 1
            elif combo_tier == 'Strong Combination':
                insight['recommendation'] = f"Increase investment in {station} + {daypart} - strong performance"
                insight['action_type'] = 'increase_combination'
                insight['priority'] = 2
            else:
                insight['recommendation'] = f"Monitor {station} + {daypart} and test optimization"
                insight['action_type'] = 'monitor_combination'
                insight['priority'] = 3
            
            insight['expected_impact'] = f"Combination performance: {visit_rate:.1f} visits/spot"
            
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
                'spots': station.get('spots', 0)
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
    
    def _generate_structured_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured recommendations for CSV export to Power BI"""
        
        recommendations = []
        findings = []
        
        # Station-level recommendations
        station_data = context.get('station_performance', [])
        for i, station in enumerate(station_data[:5], 1):
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
                    'recommendation': f"Reallocate budget to {station_name} due to high efficiency",
                    'expected_impact': f"Increase overall visits by {int(visit_rate * 10)}%",
                    'confidence': '95%',
                    'action_type': 'reallocate_budget'
                })
        
        return {
            'optimization_recommendations': recommendations,
            'key_findings': findings
        }
    
    def _count_total_insights(self, insights: Dict[str, Any]) -> int:
        """Count total insights generated across all categories"""
        count = 0
        count += len(insights.get('key_findings', []))
        count += len(insights.get('optimization_priorities', []))
        count += len(insights.get('station_insights', []))
        count += len(insights.get('daypart_insights', []))
        count += len(insights.get('station_daypart_insights', []))
        
        # Count quadrant analysis
        quadrants = insights.get('performance_quadrants', {})
        for quadrant_data in quadrants.values():
            count += len(quadrant_data)
        
        count += len(insights.get('opportunity_matrix', []))
        
        # Count structured recommendations
        structured = insights.get('prescriptive_recommendations', {})
        count += len(structured.get('optimization_recommendations', []))
        count += len(structured.get('key_findings', []))
        
        return count
    
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
        else:
            confidence_factors.append(0.6)
        
        # Attribution coverage factor
        visits = totals.get('total_visits', 0)
        confidence_factors.append(0.9 if visits > 0 else 0.3)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    
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
            
            # Key Findings (Executive Level)
            key_findings = insights.get('key_findings', [])
            trend_assessment = insights.get('recent_vs_historical', {}).get('trend_assessment', 'stable')
            
            for i, finding in enumerate(key_findings, 1):
                is_trend_finding = any(word in finding.lower() for word in ['trending', 'improving', 'declining'])
                
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'insight_category': 'key_finding',
                    'insight_type': 'executive_summary',
                    'priority': i,
                    'impact_level': 'High',
                    'station': None,
                    'daypart': None,
                    'metric_type': 'trend_analysis' if is_trend_finding else 'overall_performance',
                    'finding_description': finding,
                    'recommendation': f"Key insight: {finding}",
                    'action_required': 'leverage_trend' if is_trend_finding else 'monitor_and_leverage',
                    'confidence': 'High',
                    'trend_context': trend_assessment,
                    'time_based': 'yes' if is_trend_finding else 'no',
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Station Insights
            for insight in insights.get('station_insights', []):
                opportunity_type = insight.get('opportunity_type', 'Monitor')
                trend_direction = insight.get('trend_direction', 'stable')
                
                if opportunity_type == 'Scale Winner':
                    action_required = 'scale_immediately'
                    metric_type = 'high_volume_high_efficiency'
                elif opportunity_type == 'Hidden Gem':
                    action_required = 'test_scaling'
                    metric_type = 'low_volume_high_efficiency'
                elif opportunity_type == 'Rising Star':
                    action_required = 'monitor_closely'
                    metric_type = 'improving_trend'
                else:
                    action_required = 'monitor'
                    metric_type = 'standard_performance'
                
                recent_efficiency = insight.get('recent_efficiency', insight.get('visit_rate', 0))
                
                insights_data.append({
                    'client': insights['metadata']['client_name'],
                    'insight_category': 'station_analysis',
                    'insight_type': 'station_optimization',
                    'priority': insight.get('priority', 999),
                    'impact_level': 'High' if insight.get('priority', 999) <= 2 else 'Medium',
                    'station': insight.get('station'),
                    'daypart': None,
                    'metric_type': metric_type,
                    'finding_description': f"{insight.get('station')} shows {trend_direction} trend: {recent_efficiency:.1f} recent vs {insight.get('visit_rate', 0):.1f} overall",
                    'recommendation': insight.get('recommendation', ''),
                    'action_required': action_required,
                    'confidence': insight.get('confidence', 'Medium'),
                    'trend_context': trend_direction,
                    'time_based': 'yes' if trend_direction != 'stable' else 'no',
                    'generated_date': insights['metadata']['generation_date'][:10]
                })
            
            # Write CSV
            if insights_data:
                fieldnames = ['client', 'insight_category', 'insight_type', 'priority', 'impact_level', 
                             'station', 'daypart', 'metric_type', 'finding_description', 'recommendation', 
                             'action_required', 'confidence', 'trend_context', 'time_based', 'generated_date']
                
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
            'executive_summary': f'TV campaign analysis for {client_name or "client"} completed.',
            'key_findings': ['AI analysis temporarily unavailable'],
            'optimization_priorities': [],
            'station_insights': [],
            'daypart_insights': [],
            'station_daypart_insights': [],
            'performance_quadrants': {},
            'opportunity_matrix': [],
            'recent_vs_historical': {},
            'weekly_trends': {},
            'prescriptive_recommendations': {
                'optimization_recommendations': [],
                'key_findings': []
            }
        }


# Test the AI Insights Engine
if __name__ == "__main__":
    print("🧪 Testing AI Insights Engine...")
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
                    
                    print(f"✅ Test completed! Total insights: {insights['metadata']['total_insights_generated']}")
                    
                    csv_path = insight_generator.save_insights_csv(insights)
                    if csv_path:
                        print(f"📁 CSV saved: {csv_path}")
                else:
                    print("❌ No campaign data available")
            else:
                print("❌ No clients available")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")