"""
Gemini Client - Clean API Integration
Handles direct communication with Google Gemini API for campaign insights
"""

import os
import time
import google.generativeai as genai
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class GeminiInsightGenerator:
    """Clean Gemini client for TV campaign insights"""
    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        self.model_name = model_name
        self.model = None
        self._setup_client()
    
    def _setup_client(self):
        """Setup Gemini API client"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini: {e}")
    
    def generate_campaign_insights(self, prompt: str, temperature: float = 0.2) -> str:
        """
        Generate campaign insights from prompt
        
        Args:
            prompt: Campaign analysis prompt with JSON schema
            temperature: Model creativity (0.0-1.0, lower = more structured)
            
        Returns:
            JSON response from Gemini
            
        Raises:
            RuntimeError: If API call fails
            ValueError: If prompt is invalid
        """
        if not self.model:
            raise RuntimeError("Gemini client not initialized")
        
        if not prompt or len(prompt.strip()) < 100:
            raise ValueError(f"Invalid prompt: too short ({len(prompt)} chars)")
        
        config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=8000,
            top_p=0.9,
            top_k=40
        )
        
        return self._generate_with_retry(prompt, config)
    
    def _generate_with_retry(self, prompt: str, config: genai.types.GenerationConfig, max_retries: int = 3) -> str:
        """Generate with retry logic"""
        
        for attempt in range(max_retries + 1):
            try:
                response = self.model.generate_content(prompt, generation_config=config)
                
                if response.text and len(response.text.strip()) > 50:
                    return response.text
                else:
                    raise ValueError(f"Insufficient response: {len(response.text) if response.text else 0} chars")
                    
            except Exception as e:
                if attempt < max_retries:
                    wait_time = 2 ** (attempt + 1)
                    print(f"⚠️  Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(f"Gemini API failed after {max_retries + 1} attempts: {e}")
    
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            test_prompt = "Respond with exactly: 'Connection successful'"
            response = self.generate_campaign_insights(test_prompt, temperature=0.0)
            return "successful" in response.lower()
        except:
            return False


# Test the clean client
if __name__ == "__main__":
    print("🧪 Testing Clean Gemini Client...")
    
    try:
        client = GeminiInsightGenerator()
        
        if client.test_connection():
            print("✅ API connection successful")
            
            # Test insight generation
            test_prompt = """
            Campaign: TEST | Spots: 100 | Visits: 250
            
            Respond with ONLY valid JSON:
            {"executive_summary": {"summary": "Test campaign analysis", "confidence": "High", "urgency": "Low"}}
            """
            
            response = client.generate_campaign_insights(test_prompt)
            print(f"✅ Generated response ({len(response)} chars)")
            
        print("✅ Clean Gemini client test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("💡 Check GEMINI_API_KEY in .env file")