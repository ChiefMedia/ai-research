"""
KPI Calculator - Transform spot-level data into executive-ready campaign metrics
Uses Polars for high-performance aggregations and calculations
"""

import polars as pl
import yaml
from typing import Dict, Any, Optional
from datetime import datetime

class KPICalculator:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize KPI Calculator with target benchmarks"""
        self.config_path = config_path
        self._load_config()
    
    def _load_config(self):
        """Load configuration including KPI targets"""
        try:
            with open(self.config_path, 'r') as file:
                self.config = yaml.safe_load(file)
                self.targets = self.config.get('kpi_targets', {})
        except FileNotFoundError:
            print(f"⚠️  Config file {self.config_path} not found, using defaults")
            self.targets = {
                'roas_target': 3.5,
                'cpo_target': 25.0,
                'cpm_benchmark': 15.0,
                'min_revenue_threshold': 500
            }
    
    def calculate_campaign_kpis(self, df: pl.DataFrame) -> Dict[str, Any]:
        """
        Main method: Calculate comprehensive campaign KPIs from spot-level data
        Input: Polars DataFrame with spot-level data (from database.py)
        Output: Structured KPI dictionary ready for AI analysis
        """
        if df.is_empty():
            return self._empty_results()
        
        print(f"🧮 Calculating campaign KPIs for {len(df)} spots...")
        
        # Calculate core aggregations
        totals = self._calculate_totals(df)
        efficiency_metrics = self._calculate_efficiency_metrics(df, totals)
        performance_grades = self._calculate_performance_grades(efficiency_metrics)
        dimensional_analysis = self._calculate_dimensional_breakdowns(df)
        time_analysis = self._calculate_time_patterns(df)
        
        # Compile comprehensive results
        kpis = {
            'metadata': {
                'calculation_date': datetime.now().isoformat(),
                'spots_analyzed': len(df),
                'date_range': self._get_date_range(df),
                'clients_analyzed': self._get_unique_values(df, 'client'),
                'data_quality_score': self._assess_data_quality(df)
            },
            'totals': totals,
            'efficiency': efficiency_metrics,
            'performance_vs_targets': performance_grades,
            'dimensional_analysis': dimensional_analysis,
            'time_patterns': time_analysis,
            'targets': self.targets,
            'summary': self._generate_executive_summary(totals, efficiency_metrics, performance_grades)
        }
        
        print(f"✅ KPI calculation complete - {len(kpis)} metric categories")
        return kpis
    
    def _calculate_totals(self, df: pl.DataFrame) -> Dict[str, float]:
        """Calculate campaign totals with robust NULL handling and cost inclusion"""
        try:
            totals = {
                'total_spots': len(df),
                'total_cost': 0.0,
                'total_revenue': 0.0,
                'total_impressions': 0,
                'total_visits': 0,
                'total_orders': 0,
                'total_leads': 0
            }
            
            # Debug: Check what columns we have
            print(f"🔍 Debug: Available columns: {df.columns}")
            
            # Cost aggregation (spot_cost from buyrate)
            if 'spot_cost' in df.columns:
                # Debug: Check cost data
                cost_sample = df.select('spot_cost').head(5)
                print(f"🔍 Debug: Sample spot_cost values: {cost_sample.to_dicts()}")
                
                cost_sum = df.select(
                    pl.col('spot_cost').sum()
                ).item()
                totals['total_cost'] = float(cost_sum or 0)
                print(f"🔍 Debug: Total cost calculated: ${totals['total_cost']:,.2f}")
            else:
                print("⚠️  Warning: spot_cost column not found in dataframe")
            
            # Revenue aggregation with NULL safety
            if 'online_revenue' in df.columns:
                revenue_sum = df.select(
                    pl.col('online_revenue').sum()
                ).item()
                totals['total_revenue'] = float(revenue_sum or 0)
            
            # Visits aggregation
            if 'online_visits' in df.columns:
                visits_sum = df.select(
                    pl.col('online_visits').sum()
                ).item()
                totals['total_visits'] = int(visits_sum or 0)
            
            # Orders aggregation  
            if 'online_orders' in df.columns:
                orders_sum = df.select(
                    pl.col('online_orders').sum()
                ).item()
                totals['total_orders'] = int(orders_sum or 0)
            
            # Leads aggregation
            if 'online_leads' in df.columns:
                leads_sum = df.select(
                    pl.col('online_leads').sum()
                ).item()
                totals['total_leads'] = int(leads_sum or 0)
            
            # Impressions aggregation
            if 'impressions' in df.columns:
                impressions_sum = df.select(
                    pl.col('impressions').sum()
                ).item()
                totals['total_impressions'] = int(impressions_sum or 0)
            
            return totals
            
        except Exception as e:
            print(f"❌ Error calculating totals: {e}")
            return {
                'total_spots': len(df),
                'total_cost': 0.0,
                'total_revenue': 0.0,
                'total_impressions': 0,
                'total_visits': 0,
                'total_orders': 0,
                'total_leads': 0
            }
    
    def _calculate_efficiency_metrics(self, df: pl.DataFrame, totals: Dict[str, float]) -> Dict[str, Optional[float]]:
        """Calculate efficiency metrics (CPM, ROAS, conversion rates, etc.)"""
        metrics = {}
        
        # ROAS (Return on Ad Spend)
        if totals['total_cost'] > 0:
            metrics['roas'] = totals['total_revenue'] / totals['total_cost']
        else:
            metrics['roas'] = None
        
        # CPM (Cost per 1000 impressions)
        if totals['total_impressions'] > 0 and totals['total_cost'] > 0:
            metrics['cpm'] = (totals['total_cost'] / totals['total_impressions']) * 1000
        else:
            metrics['cpm'] = None
        
        # CPV (Cost per Visit)
        if totals['total_visits'] > 0 and totals['total_cost'] > 0:
            metrics['cpv'] = totals['total_cost'] / totals['total_visits']
        else:
            metrics['cpv'] = None
        
        # CPO (Cost per Order)
        if totals['total_orders'] > 0 and totals['total_cost'] > 0:
            metrics['cpo'] = totals['total_cost'] / totals['total_orders']
        else:
            metrics['cpo'] = None
        
        # CPL (Cost per Lead)
        if totals['total_leads'] > 0 and totals['total_cost'] > 0:
            metrics['cpl'] = totals['total_cost'] / totals['total_leads']
        else:
            metrics['cpl'] = None
        
        # Conversion Rates
        if totals['total_visits'] > 0:
            metrics['visit_to_order_rate'] = totals['total_orders'] / totals['total_visits']
            if totals['total_leads'] > 0:
                metrics['visit_to_lead_rate'] = totals['total_leads'] / totals['total_visits']
            else:
                metrics['visit_to_lead_rate'] = 0.0
        else:
            metrics['visit_to_order_rate'] = None
            metrics['visit_to_lead_rate'] = None
        
        # Lead to Order conversion
        if totals['total_leads'] > 0:
            metrics['lead_to_order_rate'] = totals['total_orders'] / totals['total_leads']
        else:
            metrics['lead_to_order_rate'] = None
        
        # Average Order Value
        if totals['total_orders'] > 0:
            metrics['average_order_value'] = totals['total_revenue'] / totals['total_orders']
        else:
            metrics['average_order_value'] = None
        
        # Revenue per Visit
        if totals['total_visits'] > 0:
            metrics['revenue_per_visit'] = totals['total_revenue'] / totals['total_visits']
        else:
            metrics['revenue_per_visit'] = None
        
        return metrics
    
    def _calculate_performance_grades(self, efficiency: Dict[str, Optional[float]]) -> Dict[str, Dict[str, Any]]:
        """Compare metrics to targets and assign performance grades"""
        grades = {}
        
        # ROAS vs Target
        if efficiency['roas'] is not None:
            roas_target = self.targets.get('roas_target', 3.5)
            performance_ratio = efficiency['roas'] / roas_target
            grades['roas'] = {
                'current': efficiency['roas'],
                'target': roas_target,
                'performance_ratio': performance_ratio,
                'grade': self._assign_grade(performance_ratio),
                'status': 'exceeds' if performance_ratio >= 1.0 else 'below'
            }
        
        # CPO vs Target
        if efficiency['cpo'] is not None:
            cpo_target = self.targets.get('cpo_target', 25.0)
            # For CPO, lower is better, so we invert the ratio
            performance_ratio = cpo_target / efficiency['cpo']
            grades['cpo'] = {
                'current': efficiency['cpo'],
                'target': cpo_target,
                'performance_ratio': performance_ratio,
                'grade': self._assign_grade(performance_ratio),
                'status': 'exceeds' if efficiency['cpo'] <= cpo_target else 'below'
            }
        
        # CPM vs Benchmark
        if efficiency['cpm'] is not None:
            cpm_benchmark = self.targets.get('cpm_benchmark', 15.0)
            # For CPM, lower is generally better
            performance_ratio = cpm_benchmark / efficiency['cpm']
            grades['cpm'] = {
                'current': efficiency['cpm'],
                'benchmark': cpm_benchmark,
                'performance_ratio': performance_ratio,
                'grade': self._assign_grade(performance_ratio),
                'status': 'efficient' if efficiency['cpm'] <= cpm_benchmark else 'expensive'
            }
        
        return grades
    
    def _assign_grade(self, ratio: float) -> str:
        """Assign letter grade based on performance ratio"""
        if ratio >= 1.2:
            return 'A'
        elif ratio >= 1.0:
            return 'B'
        elif ratio >= 0.8:
            return 'C'
        elif ratio >= 0.6:
            return 'D'
        else:
            return 'F'
    
    def _calculate_dimensional_breakdowns(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Calculate performance by market, station, daypart, etc. - Focus on actionable insights"""
        breakdowns = {}
        
        try:
            # Performance by Station (TOP PRIORITY for optimization)
            if 'station' in df.columns and 'online_visits' in df.columns:
                station_performance = df.group_by('station').agg([
                    pl.count().alias('spots'),
                    pl.col('online_visits').sum().alias('total_visits'),
                    pl.col('online_visits').mean().alias('avg_visits_per_spot'),
                    pl.col('online_revenue').sum().alias('total_revenue'),
                    pl.col('impressions').sum().alias('total_impressions'),
                    pl.col('spot_cost').sum().alias('total_cost')
                ]).with_columns([
                    # Calculate efficiency metrics per station
                    pl.when(pl.col('total_impressions') > 0)
                    .then(pl.col('total_visits') / pl.col('total_impressions') * 1000)
                    .otherwise(None)
                    .alias('visits_per_thousand_impressions'),
                    # Calculate CPM per station
                    pl.when(pl.col('total_impressions') > 0)
                    .then(pl.col('total_cost') / pl.col('total_impressions') * 1000)
                    .otherwise(None)
                    .alias('cpm')
                ]).sort('total_visits', descending=True)
                
                breakdowns['station_performance'] = station_performance.to_dicts()
            
            # Performance by Daypart (KEY for media optimization)
            if 'daypart' in df.columns and 'online_visits' in df.columns:
                daypart_performance = df.group_by('daypart').agg([
                    pl.count().alias('spots'),
                    pl.col('online_visits').sum().alias('total_visits'),
                    pl.col('online_visits').mean().alias('avg_visits_per_spot'),
                    pl.col('online_revenue').sum().alias('total_revenue'),
                    pl.col('impressions').sum().alias('total_impressions'),
                    pl.col('spot_cost').sum().alias('total_cost')
                ]).with_columns([
                    # Calculate visit rate efficiency by daypart
                    (pl.col('total_visits') / pl.col('spots')).alias('visit_efficiency'),
                    pl.when(pl.col('total_impressions') > 0)
                    .then(pl.col('total_visits') / pl.col('total_impressions') * 1000)
                    .otherwise(None)
                    .alias('visits_per_thousand_impressions'),
                    # Calculate CPM by daypart
                    pl.when(pl.col('total_impressions') > 0)
                    .then(pl.col('total_cost') / pl.col('total_impressions') * 1000)
                    .otherwise(None)
                    .alias('cpm')
                ]).sort('visit_efficiency', descending=True)
                
                breakdowns['daypart_performance'] = daypart_performance.to_dicts()
            
            # Station x Daypart Cross-Analysis (PREMIUM INSIGHT)
            if 'station' in df.columns and 'daypart' in df.columns and 'online_visits' in df.columns:
                station_daypart_performance = df.group_by(['station', 'daypart']).agg([
                    pl.count().alias('spots'),
                    pl.col('online_visits').sum().alias('total_visits'),
                    pl.col('online_visits').mean().alias('avg_visits_per_spot'),
                    pl.col('spot_cost').sum().alias('total_cost')
                ]).filter(pl.col('spots') >= 5).sort('avg_visits_per_spot', descending=True).head(20)
                
                breakdowns['station_daypart_combinations'] = station_daypart_performance.to_dicts()
            
            # Performance by Market (Secondary priority)
            if 'market' in df.columns and 'online_visits' in df.columns:
                market_performance = df.group_by('market').agg([
                    pl.count().alias('spots'),
                    pl.col('online_visits').sum().alias('total_visits'),
                    pl.col('online_visits').mean().alias('avg_visits_per_spot'),
                    pl.col('online_revenue').sum().alias('total_revenue'),
                    pl.col('spot_cost').sum().alias('total_cost')
                ]).sort('total_visits', descending=True).head(10)
                
                breakdowns['market_performance'] = market_performance.to_dicts()
            
        except Exception as e:
            print(f"⚠️  Error calculating dimensional breakdowns: {e}")
            breakdowns['error'] = str(e)
        
        return breakdowns
    
    def _calculate_time_patterns(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Analyze time-based performance patterns"""
        patterns = {}
        
        try:
            if 'dtspot' in df.columns and 'online_revenue' in df.columns:
                # Daily performance trends
                daily_performance = df.with_columns([
                    pl.col('dtspot').dt.date().alias('date')
                ]).group_by('date').agg([
                    pl.count().alias('spots'),
                    pl.col('online_revenue').sum().alias('revenue'),
                    pl.col('online_visits').sum().alias('visits')
                ]).sort('date')
                
                patterns['daily_trends'] = daily_performance.to_dicts()
                
                # Hour of day analysis (if we have time data)
                hourly_performance = df.with_columns([
                    pl.col('dtspot').dt.hour().alias('hour')
                ]).group_by('hour').agg([
                    pl.count().alias('spots'),
                    pl.col('online_revenue').sum().alias('revenue'),
                    pl.col('online_visits').sum().alias('visits')
                ]).sort('hour')
                
                patterns['hourly_trends'] = hourly_performance.to_dicts()
                
        except Exception as e:
            print(f"⚠️  Error calculating time patterns: {e}")
            patterns['error'] = str(e)
        
        return patterns
    
    def _assess_data_quality(self, df: pl.DataFrame) -> float:
        """Assess data quality as a percentage score"""
        try:
            total_fields = len(df.columns)
            quality_score = 0.0
            
            # Check key fields for completeness
            key_fields = ['online_revenue', 'online_visits', 'impressions', 'dtspot']
            
            for field in key_fields:
                if field in df.columns:
                    non_null_count = df.filter(pl.col(field).is_not_null()).height
                    completeness = (non_null_count / len(df)) if len(df) > 0 else 0
                    quality_score += completeness * 25  # Each key field worth 25 points
            
            return min(quality_score, 100.0)  # Cap at 100%
            
        except Exception as e:
            print(f"⚠️  Error assessing data quality: {e}")
            return 0.0
    
    def _generate_executive_summary(self, totals: Dict, efficiency: Dict, grades: Dict) -> Dict[str, str]:
        """Generate executive-friendly summary statements"""
        summary = {}
        
        # Overall performance assessment
        if efficiency.get('roas') and grades.get('roas'):
            roas_grade = grades['roas']['grade']
            if roas_grade in ['A', 'B']:
                summary['overall_performance'] = "Strong campaign performance exceeding targets"
            elif roas_grade == 'C':
                summary['overall_performance'] = "Solid campaign performance meeting expectations"
            else:
                summary['overall_performance'] = "Campaign performance below expectations, optimization needed"
        
        # Volume assessment
        if totals['total_spots'] >= 100:
            summary['campaign_scale'] = f"Large-scale campaign with {totals['total_spots']} TV spots"
        elif totals['total_spots'] >= 50:
            summary['campaign_scale'] = f"Medium-scale campaign with {totals['total_spots']} TV spots"
        else:
            summary['campaign_scale'] = f"Small-scale campaign with {totals['total_spots']} TV spots"
        
        # Attribution quality
        if totals['total_visits'] > 0:
            summary['attribution_quality'] = "Strong attribution tracking with measurable online impact"
        else:
            summary['attribution_quality'] = "Limited attribution data - consider measurement improvements"
        
        return summary
    
    def _get_date_range(self, df: pl.DataFrame) -> Dict[str, str]:
        """Get campaign date range"""
        try:
            if 'dtspot' in df.columns:
                date_stats = df.select([
                    pl.col('dtspot').min().alias('start_date'),
                    pl.col('dtspot').max().alias('end_date')
                ]).row(0)
                
                return {
                    'start_date': str(date_stats[0]),
                    'end_date': str(date_stats[1])
                }
        except:
            pass
        
        return {'start_date': 'Unknown', 'end_date': 'Unknown'}
    
    def _get_unique_values(self, df: pl.DataFrame, column: str) -> list:
        """Get unique values from a column"""
        try:
            if column in df.columns:
                return df.select(column).unique().to_series().to_list()
        except:
            pass
        return []
    
    def _empty_results(self) -> Dict[str, Any]:
        """Return empty results structure when no data available"""
        return {
            'metadata': {
                'calculation_date': datetime.now().isoformat(),
                'spots_analyzed': 0,
                'data_quality_score': 0.0
            },
            'totals': {
                'total_spots': 0,
                'total_cost': 0.0,
                'total_revenue': 0.0,
                'total_impressions': 0,
                'total_visits': 0,
                'total_orders': 0,
                'total_leads': 0
            },
            'efficiency': {},
            'performance_vs_targets': {},
            'dimensional_analysis': {},
            'time_patterns': {},
            'targets': self.targets,
            'summary': {'overall_performance': 'No data available for analysis'}
        }
    
    def print_kpi_summary(self, kpis: Dict[str, Any]):
        """Print executive-friendly KPI summary to console"""
        print("\n" + "="*60)
        print("📊 CAMPAIGN KPI SUMMARY")
        print("="*60)
        
        # Metadata
        metadata = kpis['metadata']
        print(f"\n📅 Analysis Period: {metadata.get('date_range', {}).get('start_date', 'N/A')} to {metadata.get('date_range', {}).get('end_date', 'N/A')}")
        print(f"📺 Total Spots Analyzed: {metadata['spots_analyzed']:,}")
        print(f"📊 Data Quality Score: {metadata['data_quality_score']:.1f}%")
        
        # Totals
        totals = kpis['totals']
        print(f"\n💰 CAMPAIGN TOTALS")
        print(f"   Revenue: ${totals['total_revenue']:,.2f}")
        print(f"   Visits: {totals['total_visits']:,}")
        print(f"   Orders: {totals['total_orders']:,}")
        print(f"   Impressions: {totals['total_impressions']:,}")
        
        # Efficiency Metrics
        efficiency = kpis['efficiency']
        print(f"\n📈 EFFICIENCY METRICS")
        
        if efficiency.get('roas'):
            print(f"   ROAS: {efficiency['roas']:.2f}")
        if efficiency.get('cpo'):
            print(f"   CPO: ${efficiency['cpo']:.2f}")
        if efficiency.get('cpm'):
            print(f"   CPM: ${efficiency['cpm']:.2f}")
        if efficiency.get('visit_to_order_rate'):
            print(f"   Conversion Rate: {efficiency['visit_to_order_rate']:.2%}")
        
        # Performance Grades
        grades = kpis['performance_vs_targets']
        if grades:
            print(f"\n🎯 PERFORMANCE vs TARGETS")
            for metric, grade_info in grades.items():
                status_emoji = "✅" if grade_info['status'] in ['exceeds', 'efficient'] else "⚠️"
                print(f"   {metric.upper()}: {grade_info['grade']} {status_emoji}")
        
        # Executive Summary
        summary = kpis['summary']
        print(f"\n📋 EXECUTIVE SUMMARY")
        for key, message in summary.items():
            print(f"   • {message}")
        
        print("="*60)


# Test the KPI Calculator
if __name__ == "__main__":
    print("🧪 Testing KPI Calculator...")
    print("=" * 50)
    
    # Import database manager to get real data
    try:
        import sys
        sys.path.append('.')
        from src.database import DatabaseManager
        
        with DatabaseManager() as db:
            # Get sample data
            clients = db.get_available_clients(30)
            if clients:
                client = clients[0]
                print(f"📊 Testing KPI calculation for client: {client}")
                
                # Get campaign data
                df = db.get_campaign_data(client=client, days=30)
                
                if not df.is_empty():
                    # Calculate KPIs
                    calculator = KPICalculator()
                    kpis = calculator.calculate_campaign_kpis(df)
                    
                    # Print summary
                    calculator.print_kpi_summary(kpis)
                    
                    print(f"\n✅ KPI calculation test completed successfully!")
                    print(f"📊 Generated {len(kpis)} KPI categories")
                else:
                    print("❌ No data available for testing")
            else:
                print("❌ No clients available for testing")
                
    except ImportError as e:
        print(f"❌ Cannot import database module: {e}")
        print("💡 Run this test from the project root directory")
    except Exception as e:
        print(f"❌ Test failed: {e}")