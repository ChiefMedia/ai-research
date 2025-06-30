"""
AI Insights - Configuration Module
Handles Gemini API setup, configuration loading, and utility functions
"""

import os
import google.generativeai as genai
import yaml
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ConfigManager:
    """Manages configuration and API setup for AI Insights"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration manager"""
        self.config_path = config_path
        self.config = {}
        self.ai_settings = {}
        self.model = None
        
        self._load_config()
        self._setup_gemini()
    
    def _load_config(self):
        """Load configuration settings from YAML file"""
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
    
    def get_model(self):
        """Get the configured Gemini model"""
        return self.model
    
    def get_ai_settings(self) -> Dict[str, Any]:
        """Get AI configuration settings"""
        return self.ai_settings
    
    def get_config(self) -> Dict[str, Any]:
        """Get full configuration"""
        return self.config


class AnalysisConstants:
    """Constants used throughout the analysis"""
    
    # Performance thresholds
    HIGH_PERFORMANCE_THRESHOLD = 2.0
    GOOD_PERFORMANCE_THRESHOLD = 1.0
    
    # Volume thresholds
    HIGH_VOLUME_THRESHOLD = 1000
    LOW_VOLUME_THRESHOLD = 500
    
    # Trend analysis
    IMPROVING_THRESHOLD = 1.1
    DECLINING_THRESHOLD = 0.9
    
    # Confidence thresholds
    HIGH_CONFIDENCE_SPOTS = 20
    MEDIUM_CONFIDENCE_SPOTS = 10
    HIGH_CONFIDENCE_WEEKS = 2
    
    # CSV field names
    CSV_FIELDNAMES = [
        'client', 'insight_category', 'insight_type', 'priority', 'impact_level',
        'station', 'daypart', 'metric_type', 'finding_description', 'recommendation',
        'action_required', 'confidence', 'trend_context', 'time_based', 'generated_date'
    ]
    
    # Insight categories
    INSIGHT_CATEGORIES = {
        'KEY_FINDING': 'key_finding',
        'KEY_OPTIMIZATION': 'key_optimization',
        'STATION_ANALYSIS': 'station_analysis',
        'DAYPART_ANALYSIS': 'daypart_analysis',
        'COMBINATION_ANALYSIS': 'combination_analysis',
        'BUDGET_OPPORTUNITY': 'budget_opportunity'
    }
    
    # Action types
    ACTION_TYPES = {
        'SCALE_IMMEDIATELY': 'scale_immediately',
        'TEST_SCALING': 'test_scaling',
        'MONITOR_CLOSELY': 'monitor_closely',
        'OPTIMIZE_OR_REDUCE': 'optimize_or_reduce',
        'REALLOCATE_BUDGET': 'reallocate_budget',
        'MONITOR': 'monitor'
    }
    
    # Metric types
    METRIC_TYPES = {
        'HIGH_VOLUME_HIGH_EFFICIENCY': 'high_volume_high_efficiency',
        'LOW_VOLUME_HIGH_EFFICIENCY': 'low_volume_high_efficiency',
        'IMPROVING_TREND': 'improving_trend',
        'STANDARD_PERFORMANCE': 'standard_performance',
        'PRIME_TIME_EFFICIENCY': 'prime_time_efficiency',
        'STRONG_EFFICIENCY': 'strong_efficiency',
        'AVERAGE_EFFICIENCY': 'average_efficiency',
        'GOLDEN_COMBINATION': 'golden_combination',
        'STRONG_COMBINATION': 'strong_combination',
        'BUDGET_REALLOCATION': 'budget_reallocation'
    }


class UtilityFunctions:
    """Utility functions used across modules"""
    
    @staticmethod
    def calculate_performance_quartile(data: list, percentile: float) -> float:
        """Calculate performance quartile for benchmarking"""
        if not data:
            return 0.0
        
        values = [item.get('avg_visits_per_spot', 0) for item in data 
                 if item.get('avg_visits_per_spot', 0) > 0]
        if not values:
            return 0.0
        
        values.sort()
        index = int(len(values) * percentile)
        return values[min(index, len(values) - 1)]
    
    @staticmethod
    def assess_analysis_confidence(kpis: Dict[str, Any]) -> float:
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
        confidence_factors.append(0.9 if visits > 0 else 0.3)
        
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
    
    @staticmethod
    def standardize_opportunity_type(opportunity_type: str) -> tuple:
        """Standardize opportunity types to action and metric type"""
        if opportunity_type == 'Scale Winner':
            return AnalysisConstants.ACTION_TYPES['SCALE_IMMEDIATELY'], AnalysisConstants.METRIC_TYPES['HIGH_VOLUME_HIGH_EFFICIENCY']
        elif opportunity_type == 'Hidden Gem':
            return AnalysisConstants.ACTION_TYPES['TEST_SCALING'], AnalysisConstants.METRIC_TYPES['LOW_VOLUME_HIGH_EFFICIENCY']
        elif opportunity_type == 'Rising Star':
            return AnalysisConstants.ACTION_TYPES['MONITOR_CLOSELY'], AnalysisConstants.METRIC_TYPES['IMPROVING_TREND']
        elif opportunity_type == 'Optimize or Reduce':
            return AnalysisConstants.ACTION_TYPES['OPTIMIZE_OR_REDUCE'], 'high_volume_low_efficiency'
        else:
            return AnalysisConstants.ACTION_TYPES['MONITOR'], AnalysisConstants.METRIC_TYPES['STANDARD_PERFORMANCE']
    
    @staticmethod
    def standardize_performance_tier(performance_tier: str) -> str:
        """Standardize performance tier names"""
        if 'High' in performance_tier:
            return 'top_performer'
        elif 'Above' in performance_tier:
            return 'above_average'
        elif 'Below' in performance_tier:
            return 'below_average'
        elif 'Under' in performance_tier:
            return 'underperformer'
        else:
            return 'average'
    
    @staticmethod
    def determine_confidence_level(spots: int, weeks_analyzed: int = 0) -> str:
        """Determine confidence level based on sample size"""
        if spots >= AnalysisConstants.HIGH_CONFIDENCE_SPOTS and weeks_analyzed >= AnalysisConstants.HIGH_CONFIDENCE_WEEKS:
            return 'High'
        elif spots >= AnalysisConstants.MEDIUM_CONFIDENCE_SPOTS:
            return 'Medium'
        else:
            return 'Low'
    
    @staticmethod
    def is_trend_finding(finding_text: str) -> bool:
        """Determine if a finding is trend-related"""
        trend_keywords = ['trending', 'improving', 'declining', 'momentum', 'surge', 'drop', 'accelerating', 'strengthening', 'weakening']
        return any(word in finding_text.lower() for word in trend_keywords)
    
    @staticmethod
    def count_total_insights(insights: Dict[str, Any]) -> int:
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


# Test the config module
if __name__ == "__main__":
    print("🧪 Testing Config Module...")
    
    try:
        # Test configuration manager
        config_manager = ConfigManager()
        print(f"✅ Config loaded: {len(config_manager.get_config())} settings")
        print(f"✅ AI settings: {config_manager.get_ai_settings()}")
        
        # Test model
        model = config_manager.get_model()
        print(f"✅ Model initialized: {type(model)}")
        
        # Test constants
        print(f"✅ Constants loaded: {len(AnalysisConstants.CSV_FIELDNAMES)} CSV fields")
        
        # Test utility functions
        test_data = [{'avg_visits_per_spot': 10}, {'avg_visits_per_spot': 20}, {'avg_visits_per_spot': 30}]
        quartile = UtilityFunctions.calculate_performance_quartile(test_data, 0.75)
        print(f"✅ Utility functions work: 75th percentile = {quartile}")
        
        print("✅ Config module test completed successfully!")
        
    except Exception as e:
        print(f"❌ Config module test failed: {e}")