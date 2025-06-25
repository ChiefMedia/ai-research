"""
Database connection and query management for Media Buy AI Insights
Uses Polars for high-performance data processing and pg8000 for pure Python PostgreSQL connectivity
"""

import os
import pg8000.native
import polars as pl
import yaml
from dotenv import load_dotenv
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize database connection"""
        self.config_path = config_path
        self.connection = None
        self._load_config()
        self._connect()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            print(f"⚠️  Config file {self.config_path} not found, using defaults")
            self.config = {'database': {}}
    
    def _connect(self):
        """Establish database connection using pg8000 (pure Python, no compilation needed)"""
        try:
            print("📡 Connecting to database...")
            
            self.connection = pg8000.native.Connection(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', '5432')),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )
            
            # Test connection
            version = self.connection.run("SELECT version()")[0][0]
            print(f"✅ Database connected: {version[:50]}...")
                
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("💡 Check your .env file credentials")
            raise
    
    def execute_query(self, query: str, params: tuple = None, return_df: bool = True) -> pl.DataFrame:
        """Execute SQL query and return results as Polars DataFrame"""
        try:
            # Execute query with pg8000
            if params:
                # pg8000 expects parameters as individual arguments, not as a tuple
                results = self.connection.run(query, *params)
            else:
                results = self.connection.run(query)
            
            if not results:
                return pl.DataFrame() if return_df else []
            
            # Get column names from the connection after query execution
            columns = [col['name'] for col in self.connection.columns]
            
            # Convert to list of dictionaries
            dict_results = [dict(zip(columns, row)) for row in results]
            
            if return_df and dict_results:
                # Convert to Polars DataFrame
                df = pl.DataFrame(dict_results)
                # Optimize data types
                df = self._optimize_dtypes(df)
                return df
            elif return_df:
                return pl.DataFrame()
            else:
                return dict_results
                
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            print(f"Query: {query[:100]}...")
            print(f"Parameters: {params}")
            raise
    
    def _optimize_dtypes(self, df: pl.DataFrame) -> pl.DataFrame:
        """Optimize data types for better performance and memory usage"""
        if df.is_empty():
            return df
            
        try:
            # Convert string 'NULL' values to actual nulls for numeric columns
            numeric_columns = [
                'online_revenue', 'impressions',
                'online_visits', 'online_orders', 'online_leads'
            ]
            
            for col in numeric_columns:
                if col in df.columns:
                    # More robust NULL handling
                    df = df.with_columns([
                        pl.when(
                            (pl.col(col).is_null()) | 
                            (pl.col(col).cast(pl.Utf8, strict=False) == 'NULL') |
                            (pl.col(col).cast(pl.Utf8, strict=False) == '')
                        )
                        .then(None)
                        .otherwise(pl.col(col))
                        .alias(col)
                    ])
            
            # Cast revenue columns to Float64 for precise calculations
            revenue_cols = ['online_revenue']
            for col in revenue_cols:
                if col in df.columns:
                    df = df.with_columns([
                        pl.col(col).cast(pl.Float64, strict=False).alias(col)
                    ])
            
            # Cast impression and count columns to Int64
            count_cols = ['impressions', 'online_visits', 'online_orders', 'online_leads']
            for col in count_cols:
                if col in df.columns:
                    df = df.with_columns([
                        pl.col(col).cast(pl.Int64, strict=False).alias(col)
                    ])
            
            return df
            
        except Exception as e:
            print(f"⚠️  Data type optimization failed: {e}")
            return df  # Return original if optimization fails
    
    def get_campaign_data(self, client: str = None, days: int = 30) -> pl.DataFrame:
        """
        Get campaign performance data for analysis
        Returns Polars DataFrame for high-performance analytics with calculated metrics
        """
        print(f"📊 Fetching campaign data (last {days} days)...")
        
        try:
            # Load base SQL query
            query_file = "queries/campaign_performance.sql"
            with open(query_file, 'r') as file:
                base_query = file.read()
            
            # Replace the %s placeholder with actual days value for INTERVAL
            base_query = base_query.replace('%s', str(days))
            
            # Handle client filter properly by inserting before ORDER BY
            if client:
                # Find the ORDER BY clause and insert our filter before it
                if "ORDER BY" in base_query:
                    parts = base_query.split("ORDER BY")
                    where_part = parts[0].rstrip()
                    order_part = "ORDER BY" + parts[1]
                    
                    # Add client filter to the WHERE clause
                    where_part += f" AND cpt.client ILIKE '%{client}%'"
                    
                    # Reconstruct the query
                    base_query = where_part + "\n" + order_part
                else:
                    # If no ORDER BY, just append to the end
                    base_query += f" AND cpt.client ILIKE '%{client}%'"
            
            # Add limit for initial testing (remove later for production)  
            base_query += " LIMIT 1000"
            
            print(f"🔍 Query filters: days={days}, client={client or 'ALL'}")
            
            # Execute query without parameters since we're using string formatting
            df = self.execute_query(base_query)
            
            print(f"📈 Found {len(df)} records")
            
            if not df.is_empty():
                # Calculate derived metrics using Polars
                df = self._calculate_derived_metrics(df)
                
                # Show sample of what we found using Polars
                sample = df.row(0, named=True)
                print(f"📋 Sample record: client='{sample.get('client')}', date={sample.get('dtspot')}")
                
                # Data quality check using Polars - should be minimal now
                if 'online_visits' in df.columns:
                    # Count records with actual numeric online_visits values
                    valid_visits_count = df.filter(
                        (pl.col('online_visits').is_not_null()) & 
                        (pl.col('online_visits').cast(pl.Utf8) != 'NULL') &
                        (pl.col('online_visits').cast(pl.Utf8) != '')
                    ).height
                    
                    attribution_rate = (valid_visits_count / len(df)) * 100
                    print(f"✅ {valid_visits_count}/{len(df)} records have valid attribution data ({attribution_rate:.1f}%)")
                else:
                    print("⚠️  No attribution data in results (online_visits column missing)")
                
                # Show data quality summary
                self._print_data_summary(df)
            
            return df
            
        except FileNotFoundError:
            print(f"❌ SQL file not found: {query_file}")
            print("💡 Make sure you're running from the project root directory")
            raise
        except Exception as e:
            print(f"❌ Error fetching campaign data: {e}")
            raise
    
    def _calculate_derived_metrics(self, df: pl.DataFrame) -> pl.DataFrame:
        """Calculate all derived metrics using Polars for high performance"""
        try:
            print("🧮 Calculating derived metrics...")
            
            # Add cost column (assuming we'll get this from elsewhere or it's missing)
            # For now, we'll set cost to 0 since it's not in the current query
            if 'cost' not in df.columns:
                df = df.with_columns([
                    pl.lit(0.0).alias('cost')
                ])
            
            # Calculate CPM (Cost per 1000 impressions) 
            df = df.with_columns([
                pl.when(pl.col('impressions') > 0)
                .then((pl.col('cost') / pl.col('impressions')) * 1000)
                .otherwise(None)
                .alias('cpm')
            ])
            
            # Calculate CPV (Cost per Visit)
            df = df.with_columns([
                pl.when(pl.col('online_visits') > 0)
                .then(pl.col('cost') / pl.col('online_visits'))
                .otherwise(None)
                .alias('cpv')
            ])
            
            # Calculate CPO (Cost per Order)
            df = df.with_columns([
                pl.when(pl.col('online_orders') > 0)
                .then(pl.col('cost') / pl.col('online_orders'))
                .otherwise(None)
                .alias('cpo')
            ])
            
            # Calculate CPL (Cost per Lead)
            df = df.with_columns([
                pl.when(pl.col('online_leads') > 0)
                .then(pl.col('cost') / pl.col('online_leads'))
                .otherwise(None)
                .alias('cpl')
            ])
            
            # Calculate ROAS (Return on Ad Spend)
            df = df.with_columns([
                pl.when(pl.col('cost') > 0)
                .then(pl.col('online_revenue') / pl.col('cost'))
                .otherwise(None)
                .alias('roas')
            ])
            
            # Add conversion rates
            df = df.with_columns([
                # Visit to order conversion rate
                pl.when(pl.col('online_visits') > 0)
                .then(pl.col('online_orders') / pl.col('online_visits'))
                .otherwise(None)
                .alias('visit_to_order_rate'),
                
                # Lead to order conversion rate  
                pl.when(pl.col('online_leads') > 0)
                .then(pl.col('online_orders') / pl.col('online_leads'))
                .otherwise(None)
                .alias('lead_to_order_rate')
            ])
            
            print(f"✅ Calculated metrics for {len(df)} records")
            return df
            
        except Exception as e:
            print(f"❌ Error calculating derived metrics: {e}")
            return df  # Return original DataFrame if calculation fails
    
    def _print_data_summary(self, df: pl.DataFrame):
        """Print summary statistics using Polars"""
        try:
            print("\n📊 Data Summary:")
            print(f"   Records: {len(df):,}")
            print(f"   Columns: {len(df.columns)}")
            
            # Key metrics summary using Polars aggregation with NULL safety
            if 'cost' in df.columns:
                try:
                    total_cost = df.select(pl.col('cost').sum()).item() or 0
                    print(f"   Total Cost: ${total_cost:,.2f}")
                except:
                    print(f"   Total Cost: N/A (no valid cost data)")
            
            if 'online_revenue' in df.columns:
                try:
                    total_revenue = df.select(pl.col('online_revenue').sum()).item() or 0
                    print(f"   Total Revenue: ${total_revenue:,.2f}")
                except:
                    print(f"   Total Revenue: N/A (no valid revenue data)")
                    
                # Count non-null revenue records
                non_null_revenue = df.filter(pl.col('online_revenue').is_not_null()).height
                print(f"   Records with Revenue: {non_null_revenue}/{len(df)}")
            
            # Date range
            if 'dtspot' in df.columns:
                try:
                    date_stats = df.select([
                        pl.col('dtspot').min().alias('min_date'),
                        pl.col('dtspot').max().alias('max_date')
                    ]).row(0)
                    print(f"   Date Range: {date_stats[0]} to {date_stats[1]}")
                except:
                    print(f"   Date Range: N/A")
            
        except Exception as e:
            print(f"⚠️  Could not generate data summary: {e}")
    
    def test_connection(self) -> bool:
        """Test database connection and return basic table info"""
        try:
            print("🧪 Testing database connection and table access...")
            
            # Test core_post_time table - use string formatting for INTERVAL
            test_query = f"""
            SELECT COUNT(*) as total_spots,
                   MIN(date) as earliest_date,
                   MAX(date) as latest_date
            FROM core_post_time 
            WHERE date >= CURRENT_DATE - INTERVAL '7 days'
            """
            
            df = self.execute_query(test_query)
            
            if not df.is_empty():
                stats = df.row(0, named=True)
                print(f"✅ core_post_time: {stats['total_spots']} spots from {stats['earliest_date']} to {stats['latest_date']}")
            
            # Test linear_attribution_metrics table with safer query
            # Handle the string 'NULL' values more carefully
            attr_query = """
            SELECT COUNT(*) as total_attributed,
                   COUNT(CASE 
                       WHEN overall_revenue IS NOT NULL 
                       AND CAST(overall_revenue AS TEXT) != 'NULL' 
                       AND CAST(overall_revenue AS TEXT) != '' 
                       THEN 1 
                   END) as with_revenue
            FROM linear_attribution_metrics
            """
            
            attr_df = self.execute_query(attr_query)
            
            if not attr_df.is_empty():
                attr_stats = attr_df.row(0, named=True)
                print(f"✅ linear_attribution_metrics: {attr_stats['total_attributed']} records, {attr_stats['with_revenue']} with revenue")
            
            print("✅ Database test completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            return False
    
    def get_available_clients(self, days: int = 30) -> List[str]:
        """Get list of available clients for analysis - only clients with attribution data"""
        try:
            query = f"""
            SELECT DISTINCT cpt.client, COUNT(*) as spot_count
            FROM core_post_time cpt
            INNER JOIN linear_attribution_metrics lam 
                ON cpt.unique_key = lam.unique_key
            WHERE cpt.dtspot >= NOW() - INTERVAL '{days} days'
                AND cpt.client IS NOT NULL
                AND lam.online_visits IS NOT NULL
                AND CAST(lam.online_visits AS TEXT) != 'NULL'
            GROUP BY cpt.client
            ORDER BY spot_count DESC
            LIMIT 20
            """
            
            df = self.execute_query(query)
            
            if not df.is_empty():
                print(f"📋 Available clients with attribution data (last {days} days):")
                
                # Display top 10 clients using Polars
                top_clients = df.head(10)
                for row in top_clients.iter_rows(named=True):
                    print(f"   {row['client']}: {row['spot_count']} attributed spots")
                
                # Return list of client names
                return df.select('client').to_series().to_list()
            else:
                print(f"❌ No clients found with attribution data in last {days} days")
                return []
            
        except Exception as e:
            print(f"❌ Error getting client list: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("🔌 Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Test script - run this file directly to test database connection
if __name__ == "__main__":
    print("🧪 Testing Database Connection...")
    print("=" * 50)
    
    try:
        with DatabaseManager() as db:
            # Test basic connection
            if db.test_connection():
                print("\n📋 Available clients:")
                clients = db.get_available_clients(30)
                
                if clients:
                    print(f"\n🎯 Testing with client: {clients[0]}")
                    sample_data = db.get_campaign_data(client=clients[0], days=30)
                    print(f"✅ Successfully retrieved Polars DataFrame with {len(sample_data)} records")
                    
                    # Show Polars performance benefits
                    if not sample_data.is_empty():
                        print(f"📊 DataFrame shape: {sample_data.shape}")
                        print(f"💾 Memory usage: ~{sample_data.estimated_size('mb'):.1f} MB")
                else:
                    print("⚠️  No clients found - trying without client filter")
                    sample_data = db.get_campaign_data(days=30)
                    print(f"✅ Successfully retrieved Polars DataFrame with {len(sample_data)} records")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check .env file has correct database credentials")
        print("2. Ensure database server is accessible")
        print("3. Verify table names match your schema")