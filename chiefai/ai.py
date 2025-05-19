import os
from typing import Dict, Any, Optional, Union
from google import genai
from chiefai.utils import get_config

def make_gemini_request(
    request_text: Union[str, Dict[str, Any]],
    model: str = "gemini-2.0-flash",
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    api_key: Optional[str] = None,
    return_full_response: bool = False
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
    
    try:
        # Initialize client
        client = genai.Client(api_key=api_key)
        
        # Build the parameters for the API call
        params = {
            "model": model,
            "contents": request_text
        }
        
        # Add optional parameters if provided
        if temperature is not None:
            params["temperature"] = temperature
        if max_output_tokens is not None:
            params["max_output_tokens"] = max_output_tokens
        if top_p is not None:
            params["top_p"] = top_p
        if top_k is not None:
            params["top_k"] = top_k
        
        # Make the request with parameters directly included
        response = client.models.generate_content(**params)
        
        # Return full response or just text based on parameter
        if return_full_response:
            return response
        else:
            return response.text
            
    except Exception as e:
        # Log the error (in a real implementation, use proper logging)
        print(f"Error calling Gemini API: {str(e)}")
        raise