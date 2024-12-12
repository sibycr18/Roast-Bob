from typing import Optional, Dict, List
import json
import asyncio
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
import logging
from config.settings import (
    OPENAI_API_KEY, 
    GPT_MODEL, 
    GPT_TEMPERATURE, 
    MAX_TOKENS,
    BOT_PERSONA,
    CONTENT_LOG
)

class OpenAIClient:
    def __init__(self, timeout: int = 30):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY, timeout=timeout)
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self.timeout = timeout

    def _setup_logging(self):
        """Configure logging for OpenAI client"""
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(CONTENT_LOG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.setLevel(logging.INFO)

    def _create_prompt(self, context: Dict, is_roast: bool = False) -> str:
        """Create appropriate prompt based on context and whether it's a roast"""
        base_prompt = BOT_PERSONA
        
        if is_roast:
            base_prompt += "\nROAST MODE ACTIVATED: Deliver a savage, no-holds-barred roast of the content."
        
        if context.get('parent_post'):
            prompt = (f"{base_prompt}\n\nParent Post: {context['parent_post']}\n"
                     f"Responding to: {context['current_post']}")
        else:
            prompt = f"{base_prompt}\n\nResponding to: {context['current_post']}"
            
        return prompt

    async def _make_api_call(self, messages: List[Dict]) -> ChatCompletion:
        """Make API call with timeout and retries"""
        max_retries = 3
        current_retry = 0
        
        while current_retry < max_retries:
            try:
                # Use asyncio.wait_for to implement timeout
                response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model=GPT_MODEL,
                        messages=messages,
                        temperature=GPT_TEMPERATURE,
                        max_tokens=MAX_TOKENS,
                        n=1
                    ),
                    timeout=self.timeout
                )
                return response
                
            except asyncio.TimeoutError:
                current_retry += 1
                self.logger.warning(f"API call timed out (attempt {current_retry}/{max_retries})")
                if current_retry == max_retries:
                    raise TimeoutError("OpenAI API call timed out after multiple retries")
                await asyncio.sleep(1)  # Wait before retry
                
            except Exception as e:
                self.logger.error(f"API call failed: {str(e)}")
                raise

    async def generate_response(
        self, 
        context: Dict,
        is_roast: bool = False
    ) -> str:
        """Generate a response using GPT model"""
        try:
            prompt = self._create_prompt(context, is_roast)
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Generate a response within 280 characters:"}
            ]
            
            response = await self._make_api_call(messages)
            generated_text = response.choices[0].message.content.strip()
            
            # Log the interaction
            self.logger.info(f"Generated response for context: {context.get('current_post')[:50]}...")
            
            return generated_text

        except TimeoutError as e:
            self.logger.error(f"Response generation timed out: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            raise

    async def generate_trend_analysis(self, post_content: str) -> Dict:
        """Analyze a post and generate thoughts/opinions for memory storage"""
        try:
            prompt = f"""
            {BOT_PERSONA}
            
            Analyze this post and provide:
            1. Your opinion on it
            2. Key topics/themes
            3. Ideas for future posts related to this
            
            Post: {post_content}
            
            Format your response as JSON with keys: 'opinion', 'topics', 'future_post_ideas'
            """
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Provide analysis in JSON format:"}
            ]
            
            response = await self._make_api_call(messages)
            analysis = response.choices[0].message.content.strip()
            
            # Parse JSON response safely
            try:
                analysis_dict = json.loads(analysis)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse analysis JSON: {e}")
                raise
            
            # Log the analysis
            self.logger.info(f"Generated analysis for post: {post_content[:50]}...")
            
            return analysis_dict

        except TimeoutError as e:
            self.logger.error(f"Trend analysis timed out: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to generate trend analysis: {e}")
            raise

    async def generate_post(self, trends: List[Dict]) -> str:
        """Generate a new post based on stored trends and opinions"""
        try:
            trends_prompt = "\n".join([
                f"Topic: {t['topics']}\nOpinion: {t['opinion']}\nIdeas: {t['future_post_ideas']}"
                for t in trends[:5]  # Use last 5 trends
            ])
            
            prompt = f"""
            {BOT_PERSONA}
            
            Based on these recent trends and opinions:
            {trends_prompt}
            
            Generate a unique, engaging post (max 280 characters) that:
            1. References one or more of these topics
            2. Adds a fresh perspective
            3. Is humorous and opinionated
            """
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Generate a post within 280 characters:"}
            ]
            
            response = await self._make_api_call(messages)
            generated_post = response.choices[0].message.content.strip()
            
            # Log the generated post
            self.logger.info(f"Generated new post: {generated_post}")
            
            return generated_post

        except TimeoutError as e:
            self.logger.error(f"Post generation timed out: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to generate post: {e}")
            raise