import os
from typing import Dict, Any, Optional, Union, List, Tuple
from google import genai
import polars as pl
import numpy as np
import json
from datetime import datetime
import warnings
import time

# Import get_config from utils
from chiefai.utils import get_config

# ============================================================================
# GEMINI API FUNCTIONS
# ============================================================================

def make_gemini_request(
    request_text: Union[str, Dict[str, Any]],
    model: str = "gemini-2.5-flash-preview-05-20",
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    api_key: Optional[str] = None,
    return_full_response: bool = False,
    max_retries: int = 3,
    retry_delay: int = 5,
    use_generation_config: bool = True
) -> Union[str, Dict[str, Any]]:
    """
    Make a request to Google's Generative AI API (Gemini).
    
    Parameters:
    -----------
    request_text : str or dict
        The content to send to the model. Can be a string or a structured prompt.
    model : str, optional
        The model to use (default: "gemini-2.0-flash")
    temperature : float, optional
        Controls randomness of output (0.0-1.0)
    max_output_tokens : int, optional
        Maximum number of tokens to generate
    top_p : float, optional
        Nucleus sampling parameter (0.0-1.0)
    top_k : int, optional
        Top-k sampling parameter
    api_key : str, optional
        Google API key. If None, tries to read from config file, then environment variable.
    return_full_response : bool, optional
        If True, returns the full response object instead of just the text.
    max_retries : int, optional
        Maximum number of retries for 503 errors (default: 3)
    use_generation_config : bool, optional
        Whether to attempt using generation config parameters (default: True).
        Set to False to ignore generation parameters if they cause issues.
        
    Returns:
    --------
    str or dict
        Generated text or full response object if return_full_response=True
        
    Raises:
    -------
    Exception
        If the API request fails
    """
    # Get API key from parameters, config file, or environment variable
    if api_key is None:
        try:
            # Try to get API key from config file
            config = get_config()
            api_key = config.get("GEMINI_KEY")
        except Exception as e:
            # If config file reading fails, log the error
            print(f"Error reading config file for Gemini API key: {str(e)}")
        
        # If API key is still None, try environment variable
        if not api_key:
            api_key = os.environ.get("GOOGLE_API_KEY")
        
        # If API key is still None, raise error
        if not api_key:
            raise ValueError("API key not provided, not found in config, and GOOGLE_API_KEY environment variable not set")
    
    # Retry logic for handling 503 errors
    for attempt in range(max_retries):
        try:
            # Initialize client
            client = genai.Client(api_key=api_key)
            
            # For now, let's make the call without generation parameters
            # to ensure basic functionality works
            if not use_generation_config or all(p is None for p in [temperature, max_output_tokens, top_p, top_k]):
                # Simple call without generation config
                response = client.models.generate_content(
                    model=model,
                    contents=request_text
                )
            else:
                # Log that we're ignoring generation parameters for now
                if any(p is not None for p in [temperature, max_output_tokens, top_p, top_k]):
                    print("Note: Generation parameters (temperature, etc.) are currently disabled due to API compatibility issues.")
                
                response = client.models.generate_content(
                    model=model,
                    contents=request_text
                )
            
            # Return full response or just text based on parameter
            if return_full_response:
                return response
            else:
                # Access the text from the response
                extracted_text = None
                
                if hasattr(response, 'text'):
                    extracted_text = response.text
                elif hasattr(response, 'candidates') and response.candidates:
                    # Navigate the response structure
                    try:
                        extracted_text = response.candidates[0].content.parts[0].text
                    except (IndexError, AttributeError):
                        # Try alternative access patterns
                        if hasattr(response, 'result'):
                            extracted_text = response.result
                        else:
                            extracted_text = str(response)
                
                # Check if we got a valid response
                if not extracted_text or extracted_text.strip() == "":
                    raise ValueError(f"Empty response from Gemini API. Response object: {response}")
                
                return extracted_text
                    
        except Exception as e:
            error_str = str(e)
            # Check if it's a 503 overloaded error
            if "503" in error_str and "overloaded" in error_str.lower():
                if attempt < max_retries - 1:
                    print(f"Model overloaded (attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"Model overloaded after {max_retries} attempts.")
                    raise
            else:
                # For other errors, raise immediately
                print(f"Error calling Gemini API: {error_str}")
                raise


# ============================================================================
# TV CAMPAIGN ANALYSIS FUNCTIONS
# ============================================================================

def round_nested_dict(d: Dict[str, Any], decimal_places: int = 2) -> Dict[str, Any]:
    """Recursively round all float values in a nested dictionary."""
    rounded = {}
    for key, value in d.items():
        if isinstance(value, float):
            rounded[key] = round(value, decimal_places)
        elif isinstance(value, dict):
            rounded[key] = round_nested_dict(value, decimal_places)
        elif isinstance(value, list):
            rounded[key] = [
                round_nested_dict(item, decimal_places) if isinstance(item, dict)
                else round(item, decimal_places) if isinstance(item, float)
                else item
                for item in value
            ]
        else:
            rounded[key] = value
    return rounded


def calculate_confidence_interval(data: List[float], confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate confidence interval for a dataset.
    
    Note: This uses a simplified t-distribution calculation. For production use,
    consider adding scipy as a dependency for more accurate calculations.
    """
    if len(data) < 2:
        return (None, None)
    
    # Convert to float to handle decimal.Decimal values
    data_float = [float(x) for x in data if x is not None]
    
    if len(data_float) < 2:
        return (None, None)
    
    mean = np.mean(data_float)
    std_err = np.std(data_float, ddof=1) / np.sqrt(len(data_float))
    
    # Simplified t-value approximation for common confidence levels
    # For more accurate results, use scipy.stats.t.ppf
    t_values = {
        0.90: 1.645,
        0.95: 1.96,
        0.99: 2.576
    }
    
    t_value = t_values.get(confidence, 1.96)  # Default to 95% confidence
    
    margin = t_value * std_err
    return (mean - margin, mean + margin)


def calculate_correlation_matrix(df: pl.DataFrame, metrics: List[str]) -> Dict[str, Dict[str, float]]:
    """Calculate correlation matrix for specified metrics."""
    correlations = {}
    
    for metric1 in metrics:
        correlations[metric1] = {}
        for metric2 in metrics:
            if metric1 != metric2:
                # Filter out null values
                clean_df = df.filter(
                    (pl.col(metric1).is_not_null()) & 
                    (pl.col(metric2).is_not_null())
                )
                
                if len(clean_df) > 2:
                    corr = clean_df.select(pl.corr(metric1, metric2)).item()
                    correlations[metric1][metric2] = round(corr, 3) if corr is not None else None
    
    return correlations


def generate_analytical_prompt(analysis_results: Dict[str, Any], df: pl.DataFrame, verbose: bool = True) -> str:
    """Generate a comprehensive prompt for Gemini based on statistical analysis."""
    
    if verbose:
        # Full detailed prompt
        prompt = f"""You are analyzing TV campaign attribution data for media buyers and account managers. 
The campaign has run {analysis_results['metadata']['total_spots']} spots with ${analysis_results['metadata']['total_spend']:,.2f} in spend over the last 4 weeks.

CRITICAL CONTEXT:
1. Target demo impressions are a SUBSET of all demo impressions - they should never be compared as related metrics
2. Overnight (ON) daypart is cheap but does not scale well - be cautious about recommending budget shifts to ON
3. Statistical significance requires at least {analysis_results['metadata']['min_sample_size']} spots - recommendations based on fewer spots are unreliable
4. Focus on specific, actionable insights rather than generic marketing advice

IMPORTANT ANALYSIS GUIDELINES:
- DO NOT mention obvious correlations like "more spend = more responses" or "spend correlates with visits"
- FOCUS on efficiency metrics: cost per order, cost per lead, cost per visit, ROI, CPM efficiency
- IDENTIFY performance variations: which segments deliver better/worse cost efficiency and why
- LOOK FOR anomalies: segments where efficiency metrics deviate significantly from average
- CONSIDER fatigue indicators: if sequential time periods show declining efficiency at similar spend levels
- PRIORITIZE insights about which stations/dayparts/days deliver the best cost efficiency

SUMMARY STATISTICS:
{json.dumps(analysis_results['summary_statistics'], indent=2)}

PERFORMANCE BY DIMENSION:
{json.dumps(analysis_results['dimensional_analysis'], indent=2)}

CORRELATION ANALYSIS:
{json.dumps(analysis_results['correlations'], indent=2)}

STATISTICAL FINDINGS:
{json.dumps(analysis_results['statistical_insights'], indent=2)}

Based on this data, provide a JSON response with the following structure:
{{
    "insights": [
        {{
            "finding": "Clear, specific observation about cost efficiency or performance",
            "evidence": "Data points supporting this finding (focus on cost-per metrics, ROI)",
            "confidence": "high/medium/low",
            "impact": "Quantified business impact in terms of efficiency improvement"
        }}
    ],
    "recommendations": [
        {{
            "action": "Specific action to improve cost efficiency",
            "rationale": "Data-driven justification based on efficiency metrics",
            "expected_impact": "Quantified efficiency improvement (e.g., 'reduce cost per order by $X')",
            "priority": "high/medium/low",
            "sample_size_caveat": "Note if based on limited data"
        }}
    ]
}}

Focus on:
1. Cost efficiency variations across stations, dayparts, and weekdays
2. ROI optimization opportunities based on performance differences
3. CPM efficiency vs. response rate trade-offs
4. Segments with unusually high/low cost per acquisition
5. Performance consistency - which segments deliver reliable efficiency

AVOID:
- Stating obvious relationships (spend vs. volume metrics)
- Generic marketing advice
- Recommendations based purely on volume rather than efficiency
- Absolute performance metrics without efficiency context
"""
    else:
        # Condensed prompt with only key metrics
        # Extract top performers and key insights
        top_stations = []
        if 'station' in analysis_results['dimensional_analysis']:
            stations = analysis_results['dimensional_analysis']['station']
            significant_stations = [s for s in stations if s.get('statistically_significant', False)]
            if significant_stations:
                # Sort by cost per order (lower is better)
                top_stations = sorted(
                    [s for s in significant_stations if s.get('cost_per_order') is not None],
                    key=lambda x: x.get('cost_per_order', float('inf'))
                )[:3]
        
        # Focus on efficiency metrics
        efficiency_metrics = {}
        for metric in ['cost_per_order', 'cost_per_lead', 'cost_per_visit', 'roi']:
            if metric in analysis_results['summary_statistics']:
                efficiency_metrics[metric] = {
                    'mean': analysis_results['summary_statistics'][metric]['mean'],
                    'std_dev': analysis_results['summary_statistics'][metric]['std_dev']
                }
        
        prompt = f"""Analyze TV campaign efficiency: {analysis_results['metadata']['total_spots']} spots, ${analysis_results['metadata']['total_spend']:,.2f} spend.

KEY RULES:
- Target demo ⊂ all demo impressions
- Overnight cheap but doesn't scale
- Need {analysis_results['metadata']['min_sample_size']}+ spots for significance
- FOCUS ON COST EFFICIENCY, NOT VOLUME

TOP PERFORMERS (by cost per order):
{json.dumps(top_stations[:3], indent=2)}

EFFICIENCY METRICS:
{json.dumps(efficiency_metrics, indent=2)}

SIGNIFICANT FINDINGS:
{json.dumps(analysis_results['statistical_insights'], indent=2)}

Return JSON:
{{
    "insights": [3-5 efficiency-focused findings],
    "recommendations": [3-5 actions to improve cost-per metrics]
}}

Focus on cost efficiency variations and ROI optimization. Avoid obvious volume correlations."""
    
    # Print prompt length info
    prompt_length = len(prompt)
    print(f"Prompt length: {prompt_length} characters (~{prompt_length//4} tokens)")
    
    return prompt


def analyze_tv_campaign_attribution(
    df: pl.DataFrame,
    # Gemini parameters
    temperature: float = 0.3,
    max_output_tokens: int = 8192,
    top_p: float = 0.95,
    top_k: int = 40,
    # Analysis parameters
    min_sample_size: int = 5,
    confidence_level: float = 0.95,
    include_correlations: bool = True,
    include_rankings: bool = True,
    verbose_prompt: bool = False,
    api_key: Optional[str] = None,
    # Debug parameters
    save_debug_files: bool = False,
    debug_dir: str = "./debug_output"
) -> Dict[str, Any]:
    """
    Comprehensive TV campaign attribution analysis with statistical significance.
    
    Parameters:
    -----------
    df : pl.DataFrame
        Campaign data with stations, dayparts, weekdays, and performance metrics
    temperature : float
        Controls randomness of Gemini output (0.0-1.0)
    max_output_tokens : int
        Maximum tokens for Gemini response
    top_p : float
        Nucleus sampling parameter
    top_k : int
        Top-k sampling parameter
    min_sample_size : int
        Minimum spots required for statistical significance
    confidence_level : float
        Confidence level for statistical calculations (e.g., 0.95 for 95%)
    include_correlations : bool
        Whether to calculate metric correlations
    save_debug_files : bool
        Whether to save debug files (prompt and response) (default: False)
    debug_dir : str
        Directory to save debug files (default: "./debug_output")
    api_key : str, optional
        Gemini API key
        
    Returns:
    --------
    Dict containing structured analysis results
    """
    
    # Step 1: Data Validation and Preprocessing
    required_cols = ['station', 'weekday', 'daypart', 'spot_count', 'total_spend', 
                     'total_visits', 'total_leads', 'total_orders', 'total_revenue']
    
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Step 2: Calculate derived metrics and statistics
    analysis_results = {
        "metadata": {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_spots": df['spot_count'].sum(),
            "total_spend": round(float(df['total_spend'].sum()), 2),
            "date_range": "Last 4 weeks",
            "confidence_level": confidence_level,
            "min_sample_size": min_sample_size
        },
        "summary_statistics": {},
        "dimensional_analysis": {},
        "correlations": {},
        "statistical_insights": [],
        "recommendations": []
    }
    
    # Calculate key performance metrics
    df = df.with_columns([
        # Response rates
        (pl.col('total_visits') / pl.col('spot_count')).alias('visits_per_spot'),
        (pl.col('total_leads') / pl.col('spot_count')).alias('leads_per_spot'),
        (pl.col('total_orders') / pl.col('spot_count')).alias('orders_per_spot'),
        (pl.col('total_revenue') / pl.col('spot_count')).alias('revenue_per_spot'),
        
        # Conversion funnel
        (pl.col('total_leads') / pl.col('total_visits')).alias('lead_conversion_rate'),
        (pl.col('total_orders') / pl.col('total_leads')).alias('order_conversion_rate'),
        
        # Cost efficiency
        (pl.col('total_spend') / pl.col('total_visits')).alias('cost_per_visit'),
        (pl.col('total_spend') / pl.col('total_leads')).alias('cost_per_lead'),
        (pl.col('total_spend') / pl.col('total_orders')).alias('cost_per_order'),
        
        # ROI metric
        ((pl.col('total_revenue') - pl.col('total_spend')) / pl.col('total_spend')).alias('roi'),
        
        # Sample size flag
        (pl.col('spot_count') >= min_sample_size).alias('statistically_significant')
    ])
    
    # Step 3: Summary Statistics
    performance_metrics = ['visits_per_spot', 'leads_per_spot', 'orders_per_spot', 
                          'revenue_per_spot', 'cost_per_visit', 'cost_per_lead', 
                          'cost_per_order', 'roi', 'cpm_target_demo', 'cpm_all_demo']
    
    for metric in performance_metrics:
        if metric in df.columns:
            valid_data = df.filter(pl.col(metric).is_not_null())[metric].to_list()
            if valid_data:
                # Convert to float to handle decimal.Decimal values
                valid_data_float = [float(x) for x in valid_data if x is not None]
                if valid_data_float:
                    analysis_results["summary_statistics"][metric] = {
                        "mean": round(float(np.mean(valid_data_float)), 2),
                        "median": round(float(np.median(valid_data_float)), 2),
                        "std_dev": round(float(np.std(valid_data_float)), 2),
                        "min": round(float(np.min(valid_data_float)), 2),
                        "max": round(float(np.max(valid_data_float)), 2),
                        "sample_size": len(valid_data_float)
                    }
    
    # Step 4: Dimensional Analysis
    dimensions = ['station', 'daypart', 'weekday']
    
    for dimension in dimensions:
        dim_analysis = []
        
        # Group by dimension
        grouped = df.group_by(dimension).agg([
            pl.sum('spot_count'),
            pl.sum('total_spend'),
            pl.sum('total_visits'),
            pl.sum('total_leads'),
            pl.sum('total_orders'),
            pl.sum('total_revenue'),
            pl.mean('cpm_target_demo'),
            pl.mean('cpm_all_demo')
        ])
        
        # Calculate performance metrics for each group
        grouped = grouped.with_columns([
            (pl.col('total_revenue') / pl.col('total_spend')).alias('roi'),
            (pl.col('total_spend') / pl.col('total_orders')).alias('cost_per_order'),
            (pl.col('total_orders') / pl.col('spot_count')).alias('orders_per_spot')
        ])
        
        # Sort by ROI for rankings
        grouped = grouped.sort('roi', descending=True)
        
        for row in grouped.iter_rows(named=True):
            dim_data = {
                "value": row[dimension],
                "spot_count": row['spot_count'],
                "total_spend": round(float(row['total_spend']), 2),
                "roi": round(float(row['roi']), 2) if row['roi'] is not None else None,
                "cost_per_order": round(float(row['cost_per_order']), 2) if row['cost_per_order'] is not None else None,
                "orders_per_spot": round(float(row['orders_per_spot']), 2) if row['orders_per_spot'] is not None else None,
                "cpm_target_demo": round(float(row['cpm_target_demo']), 2) if row['cpm_target_demo'] is not None else None,
                "statistically_significant": row['spot_count'] >= min_sample_size
            }
            
            # Add confidence intervals for key metrics if enough data
            if row['spot_count'] >= min_sample_size:
                # Get individual spot data for this dimension value
                spot_data = df.filter(pl.col(dimension) == row[dimension])
                
                if 'revenue_per_spot' in spot_data.columns:
                    revenue_data = spot_data['revenue_per_spot'].drop_nulls().to_list()
                    if len(revenue_data) >= 2:
                        ci_low, ci_high = calculate_confidence_interval(revenue_data, confidence_level)
                        dim_data['revenue_per_spot_ci'] = {
                            "lower": round(float(ci_low), 2) if ci_low is not None else None,
                            "upper": round(float(ci_high), 2) if ci_high is not None else None
                        }
            
            dim_analysis.append(dim_data)
        
        analysis_results["dimensional_analysis"][dimension] = dim_analysis
    
    # Step 5: Correlation Analysis
    if include_correlations:
        # Focus on efficiency metrics, not volume metrics
        correlation_metrics = ['cost_per_order', 'cost_per_lead', 'cost_per_visit', 
                              'roi', 'cpm_target_demo', 'lead_conversion_rate', 
                              'order_conversion_rate']
        
        # Only calculate correlations for metrics that exist
        available_metrics = [m for m in correlation_metrics if m in df.columns]
        
        if available_metrics:
            correlation_matrix = calculate_correlation_matrix(df, available_metrics)
            analysis_results["correlations"] = correlation_matrix
            
            # Find meaningful correlations (exclude obvious ones)
            meaningful_correlations = []
            obvious_pairs = [
                ('total_spend', 'total_visits'),
                ('total_spend', 'total_leads'),
                ('total_spend', 'total_orders'),
                ('total_visits', 'total_leads'),
                ('total_leads', 'total_orders')
            ]
            
            for metric1, correlations in correlation_matrix.items():
                for metric2, corr in correlations.items():
                    # Skip obvious correlations
                    if (metric1, metric2) in obvious_pairs or (metric2, metric1) in obvious_pairs:
                        continue
                        
                    if corr is not None and abs(corr) > 0.7:
                        meaningful_correlations.append({
                            "metric1": metric1,
                            "metric2": metric2,
                            "correlation": round(corr, 3),
                            "strength": "strong positive" if corr > 0 else "strong negative"
                        })
            
            if meaningful_correlations:
                analysis_results["statistical_insights"].append({
                    "type": "correlation",
                    "finding": "Meaningful correlations detected",
                    "details": meaningful_correlations
                })
    
    # Step 6: Statistical Insights
    
    # Check for daypart efficiency patterns
    daypart_perf = analysis_results["dimensional_analysis"]["daypart"]
    significant_dayparts = [d for d in daypart_perf if d["statistically_significant"]]
    
    if significant_dayparts:
        best_roi_daypart = max(significant_dayparts, key=lambda x: x["roi"] or float('-inf'))
        worst_roi_daypart = min(significant_dayparts, key=lambda x: x["roi"] or float('inf'))
        
        if best_roi_daypart["roi"] is not None and worst_roi_daypart["roi"] is not None:
            roi_diff = best_roi_daypart["roi"] - worst_roi_daypart["roi"]
            if roi_diff > 0.5:  # 50% ROI difference
                analysis_results["statistical_insights"].append({
                    "type": "performance_gap",
                    "dimension": "daypart",
                    "finding": f"Significant ROI variance across dayparts",
                    "details": {
                        "best_performer": best_roi_daypart["value"],
                        "best_roi": best_roi_daypart["roi"],
                        "worst_performer": worst_roi_daypart["value"],
                        "worst_roi": worst_roi_daypart["roi"],
                        "difference": roi_diff
                    }
                })
    
    # Check for sample size issues
    low_sample_segments = []
    for dimension in dimensions:
        for segment in analysis_results["dimensional_analysis"][dimension]:
            if not segment["statistically_significant"]:
                low_sample_segments.append({
                    "dimension": dimension,
                    "value": segment["value"],
                    "spot_count": segment["spot_count"]
                })
    
    if low_sample_segments:
        analysis_results["statistical_insights"].append({
            "type": "sample_size_warning",
            "finding": "Segments with insufficient data for reliable analysis",
            "details": low_sample_segments
        })
    
    # Step 7: Generate Prompt for Gemini
    prompt = generate_analytical_prompt(analysis_results, df, verbose=verbose_prompt)
    
    # Save prompt to file if requested
    if save_debug_files:
        import os
        os.makedirs(debug_dir, exist_ok=True)
        
        # Save prompt
        prompt_file = os.path.join(debug_dir, f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(prompt_file, 'w') as f:
            f.write(prompt)
        print(f"Prompt saved to: {prompt_file}")
    
    # Step 8: Call Gemini for insights
    try:
        gemini_response = make_gemini_request(
            request_text=prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
            top_k=top_k,
            api_key=api_key,
            use_generation_config=False  # Disable generation config due to API issues
        )
        
        # Debug: Print response info
        print(f"Gemini response type: {type(gemini_response)}")
        if isinstance(gemini_response, str):
            print(f"Response length: {len(gemini_response)} characters")
            print(f"First 200 chars: {gemini_response[:200]}")
            
            # Save full response if debug enabled
            if save_debug_files:
                response_file = os.path.join(debug_dir, f"gemini_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                with open(response_file, 'w') as f:
                    f.write(gemini_response)
                print(f"Full Gemini response saved to: {response_file}")
        
        # Try to parse Gemini's JSON response
        try:
            if isinstance(gemini_response, str) and gemini_response.strip():
                # Remove any potential markdown code blocks
                cleaned_response = gemini_response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]  # Remove ```json
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]  # Remove ```
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]  # Remove ```
                
                gemini_insights = json.loads(cleaned_response.strip())
            else:
                raise ValueError(f"Empty or invalid response from Gemini: {gemini_response}")
                
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response. Raw response: {gemini_response[:500]}")
            raise
        
        # Merge Gemini insights with statistical analysis
        if "insights" in gemini_insights:
            analysis_results["ai_insights"] = gemini_insights["insights"]
        
        if "recommendations" in gemini_insights:
            analysis_results["recommendations"] = gemini_insights["recommendations"]
            
    except Exception as e:
        analysis_results["error"] = f"Gemini API error: {str(e)}"
        warnings.warn(f"Gemini API call failed: {str(e)}")
        
        # Still return the statistical analysis even if Gemini fails
        print("\nNote: Gemini API call failed, but statistical analysis is still available.")
        print("You can access the statistical results in the returned dictionary.")
    
    # Save final results if debug enabled
    if save_debug_files:
        results_file = os.path.join(debug_dir, f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        print(f"Full analysis results saved to: {results_file}")
    
    return analysis_results


# Convenience wrapper for easier imports
def analyze_campaign_data(
    df: pl.DataFrame,
    **kwargs
) -> Dict[str, Any]:
    """
    Wrapper function for easy campaign analysis.
    
    Example:
        from chiefai.ai import analyze_campaign_data
        
        results = analyze_campaign_data(
            df,
            temperature=0.3,
            min_sample_size=10,
            confidence_level=0.95
        )
    """
    return analyze_tv_campaign_attribution(df, **kwargs)