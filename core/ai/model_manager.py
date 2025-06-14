"""
AI Model Manager
Centralized management of all OpenAI models with intelligent routing and optimization
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from openai import AsyncAzureOpenAI
import tiktoken

from core.config import settings
from core.logging import get_logger, performance_logger
from core.exceptions import (
    ModelInitializationError, 
    ModelInferenceError, 
    TokenLimitExceededError,
    RateLimitExceededError
)

logger = get_logger(__name__)


class ModelType(Enum):
    """Available model types"""
    CHAT = "chat"
    VISION = "vision"
    AUDIO = "audio"
    REASONING = "reasoning"
    FAST_REASONING = "fast_reasoning"
    EMBEDDINGS = "embeddings"


@dataclass
class ModelConfig:
    """Model configuration"""
    name: str
    deployment: str
    max_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    capabilities: List[str]
    context_window: int
    supports_functions: bool = True
    supports_streaming: bool = True


@dataclass
class ModelUsage:
    """Model usage tracking"""
    total_requests: int = 0
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    total_cost: float = 0.0
    average_latency_ms: float = 0.0
    error_count: int = 0


class ModelManager:
    """Advanced model manager with intelligent routing"""
    
    def __init__(self):
        self.client: Optional[AsyncAzureOpenAI] = None
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.models: Dict[ModelType, ModelConfig] = {}
        self.usage_stats: Dict[str, ModelUsage] = {}
        self.initialized = False
        
        # Model configurations
        self._setup_model_configs()
    
    def _setup_model_configs(self):
        """Setup model configurations"""
        self.models = {
            ModelType.CHAT: ModelConfig(
                name="gpt-4o-mini",
                deployment=settings.AZURE_CHAT_DEPLOYMENT,
                max_tokens=128000,
                cost_per_1k_input=0.000150,
                cost_per_1k_output=0.000600,
                capabilities=["text", "vision"],
                context_window=128000,
                supports_functions=True,
                supports_streaming=True
            ),
            ModelType.VISION: ModelConfig(
                name="gpt-4o-mini-vision",
                deployment=settings.AZURE_VISION_DEPLOYMENT,
                max_tokens=128000,
                cost_per_1k_input=0.000150,
                cost_per_1k_output=0.000600,
                capabilities=["text", "vision", "image_analysis"],
                context_window=128000,
                supports_functions=True,
                supports_streaming=True
            ),
            ModelType.AUDIO: ModelConfig(
                name="gpt-4o-mini-audio",
                deployment=settings.AZURE_AUDIO_DEPLOYMENT,
                max_tokens=128000,
                cost_per_1k_input=0.000150,
                cost_per_1k_output=0.000600,
                capabilities=["text", "audio", "speech_recognition"],
                context_window=128000,
                supports_functions=True,
                supports_streaming=False
            ),
            ModelType.REASONING: ModelConfig(
                name="o1",
                deployment=settings.AZURE_REASONING_DEPLOYMENT,
                max_tokens=100000,
                cost_per_1k_input=0.015,
                cost_per_1k_output=0.060,
                capabilities=["advanced_reasoning", "complex_analysis"],
                context_window=200000,
                supports_functions=False,
                supports_streaming=False
            ),
            ModelType.FAST_REASONING: ModelConfig(
                name="o3-mini",
                deployment=settings.AZURE_FAST_REASONING_DEPLOYMENT,
                max_tokens=65536,
                cost_per_1k_input=0.006,
                cost_per_1k_output=0.024,
                capabilities=["reasoning", "analysis", "decision_making"],
                context_window=128000,
                supports_functions=True,
                supports_streaming=True
            ),
            ModelType.EMBEDDINGS: ModelConfig(
                name="text-embedding-3-small",
                deployment=settings.AZURE_EMBEDDINGS_DEPLOYMENT,
                max_tokens=8191,
                cost_per_1k_input=0.000020,
                cost_per_1k_output=0.0,
                capabilities=["embeddings", "semantic_search"],
                context_window=8191,
                supports_functions=False,
                supports_streaming=False
            )
        }
        
        # Initialize usage stats
        for model_type in self.models:
            self.usage_stats[model_type.value] = ModelUsage()
    
    async def initialize(self):
        """Initialize the model manager and test connections"""
        try:
            logger.info("Initializing AI Model Manager...")
            
            # Create Azure OpenAI client
            self.client = AsyncAzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_API_KEY,
                api_version=settings.AZURE_OPENAI_VERSION,
                timeout=30.0,
                max_retries=3
            )
            
            # Test basic connectivity
            await self._test_models()
            
            self.initialized = True
            logger.info("✅ AI Model Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Model Manager: {e}")
            raise ModelInitializationError("ModelManager", str(e))
    
    async def _test_models(self):
        """Test connectivity to all models"""
        test_tasks = []
        
        # Test chat model
        test_tasks.append(self._test_chat_model())
        
        # Test embeddings model
        test_tasks.append(self._test_embeddings_model())
        
        # Run tests concurrently
        results = await asyncio.gather(*test_tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Model test {i} failed: {result}")
    
    async def _test_chat_model(self):
        """Test chat model connectivity"""
        try:
            response = await self.client.chat.completions.create(
                model=self.models[ModelType.CHAT].deployment,
                messages=[{"role": "user", "content": "Test connectivity"}],
                max_tokens=5
            )
            logger.info("✅ Chat model connectivity test passed")
            return True
        except Exception as e:
            logger.warning(f"Chat model test failed: {e}")
            return False
    
    async def _test_embeddings_model(self):
        """Test embeddings model connectivity"""
        try:
            response = await self.client.embeddings.create(
                model=self.models[ModelType.EMBEDDINGS].deployment,
                input="Test connectivity"
            )
            logger.info("✅ Embeddings model connectivity test passed")
            return True
        except Exception as e:
            logger.warning(f"Embeddings model test failed: {e}")
            return False
    
    def select_optimal_model(self, task_type: str, complexity: str = "medium", 
                           speed_requirement: str = "normal") -> ModelType:
        """Select optimal model based on task requirements"""
        
        if task_type == "embedding":
            return ModelType.EMBEDDINGS
        
        elif task_type == "vision" or "image" in task_type.lower():
            return ModelType.VISION
        
        elif task_type == "audio" or "speech" in task_type.lower():
            return ModelType.AUDIO
        
        elif task_type == "reasoning" or complexity == "high":
            if speed_requirement == "fast":
                return ModelType.FAST_REASONING
            else:
                return ModelType.REASONING
        
        elif complexity == "low" and speed_requirement == "fast":
            return ModelType.FAST_REASONING
        
        else:
            return ModelType.CHAT
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            return len(self.encoding.encode(text))
        except Exception:
            # Fallback estimation
            return len(text.split()) * 1.3
    
    def validate_input_length(self, messages: List[Dict], model_type: ModelType) -> bool:
        """Validate input doesn't exceed model limits"""
        total_tokens = 0
        
        for message in messages:
            if isinstance(message.get("content"), str):
                total_tokens += self.count_tokens(message["content"])
            elif isinstance(message.get("content"), list):
                # Handle multimodal content
                for content_item in message["content"]:
                    if content_item.get("type") == "text":
                        total_tokens += self.count_tokens(content_item.get("text", ""))
        
        max_tokens = self.models[model_type].context_window
        
        if total_tokens > max_tokens:
            raise TokenLimitExceededError(
                model_name=self.models[model_type].name,
                token_count=total_tokens,
                max_tokens=max_tokens
            )
        
        return True
    
    async def chat_completion(self, messages: List[Dict], model_type: ModelType = None,
                             temperature: float = 0.7, max_tokens: int = None,
                             functions: List[Dict] = None, stream: bool = False) -> Dict[str, Any]:
        """Generate chat completion with automatic model selection"""
        
        if not self.initialized:
            raise ModelInitializationError("ModelManager", "Manager not initialized")
        
        # Auto-select model if not specified
        if model_type is None:
            model_type = self.select_optimal_model("chat")
        
        model_config = self.models[model_type]
        
        # Validate input length
        self.validate_input_length(messages, model_type)
        
        start_time = time.time()
        
        try:
            # Prepare request parameters
            request_params = {
                "model": model_config.deployment,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 1000
            }
            
            # Add functions if supported and provided
            if functions and model_config.supports_functions:
                request_params["tools"] = [
                    {"type": "function", "function": func} for func in functions
                ]
            
            # Add streaming if supported
            if stream and model_config.supports_streaming:
                request_params["stream"] = True
            
            # Make API call
            response = await self.client.chat.completions.create(**request_params)
            
            processing_time = time.time() - start_time
            
            # Extract response data
            if stream:
                return {"stream": response, "processing_time": processing_time}
            else:
                content = response.choices[0].message.content
                usage = response.usage
                
                # Update usage statistics
                await self._update_usage_stats(
                    model_type.value,
                    usage.prompt_tokens,
                    usage.completion_tokens,
                    processing_time
                )
                
                # Log performance
                performance_logger.log_model_inference(
                    model_name=model_config.name,
                    operation="chat_completion",
                    input_tokens=usage.prompt_tokens,
                    output_tokens=usage.completion_tokens,
                    processing_time=processing_time,
                    cost=self._calculate_cost(model_config, usage.prompt_tokens, usage.completion_tokens)
                )
                
                return {
                    "content": content,
                    "usage": {
                        "prompt_tokens": usage.prompt_tokens,
                        "completion_tokens": usage.completion_tokens,
                        "total_tokens": usage.total_tokens
                    },
                    "processing_time": processing_time,
                    "model": model_config.name
                }
        
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Update error statistics
            self.usage_stats[model_type.value].error_count += 1
            
            # Handle specific error types
            if "rate limit" in str(e).lower():
                raise RateLimitExceededError("Azure OpenAI")
            
            logger.error(f"Chat completion failed: {e}")
            raise ModelInferenceError(model_config.name, str(e), {"messages": messages})
    
    async def generate_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """Generate embeddings for text(s)"""
        
        if not self.initialized:
            raise ModelInitializationError("ModelManager", "Manager not initialized")
        
        model_config = self.models[ModelType.EMBEDDINGS]
        
        # Ensure input is a list
        if isinstance(texts, str):
            texts = [texts]
        
        start_time = time.time()
        
        try:
            response = await self.client.embeddings.create(
                model=model_config.deployment,
                input=texts
            )
            
            processing_time = time.time() - start_time
            
            # Extract embeddings
            embeddings = [item.embedding for item in response.data]
            
            # Calculate token usage
            total_tokens = sum(self.count_tokens(text) for text in texts)
            
            # Update usage statistics
            await self._update_usage_stats(
                ModelType.EMBEDDINGS.value,
                total_tokens,
                0,
                processing_time
            )
            
            # Log performance
            performance_logger.log_model_inference(
                model_name=model_config.name,
                operation="embeddings",
                input_tokens=total_tokens,
                output_tokens=0,
                processing_time=processing_time,
                cost=self._calculate_cost(model_config, total_tokens, 0)
            )
            
            return embeddings
        
        except Exception as e:
            self.usage_stats[ModelType.EMBEDDINGS.value].error_count += 1
            
            logger.error(f"Embeddings generation failed: {e}")
            raise ModelInferenceError(model_config.name, str(e), {"texts": texts})
    
    async def analyze_image(self, image_data: str, prompt: str = None) -> str:
        """Analyze image using vision model"""
        
        if not self.initialized:
            raise ModelInitializationError("ModelManager", "Manager not initialized")
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt or "Analyze this image and describe what you see."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
        
        response = await self.chat_completion(
            messages=messages,
            model_type=ModelType.VISION,
            max_tokens=1000
        )
        
        return response["content"]
    
    async def _update_usage_stats(self, model_name: str, input_tokens: int, 
                                 output_tokens: int, processing_time: float):
        """Update usage statistics for a model"""
        stats = self.usage_stats[model_name]
        
        stats.total_requests += 1
        stats.total_tokens_input += input_tokens
        stats.total_tokens_output += output_tokens
        
        # Update average latency
        total_time = stats.average_latency_ms * (stats.total_requests - 1) + (processing_time * 1000)
        stats.average_latency_ms = total_time / stats.total_requests
        
        # Update cost
        model_config = next(
            config for config in self.models.values() 
            if config.name.replace("-", "_") in model_name
        )
        stats.total_cost += self._calculate_cost(model_config, input_tokens, output_tokens)
    
    def _calculate_cost(self, model_config: ModelConfig, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for model usage"""
        input_cost = (input_tokens / 1000) * model_config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * model_config.cost_per_1k_output
        return input_cost + output_cost
    
    async def get_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        if not self.initialized:
            return {"status": "not_initialized"}
        
        model_status = {}
        
        for model_type, config in self.models.items():
            stats = self.usage_stats[model_type.value]
            
            model_status[config.name] = {
                "status": "ready",
                "deployment": config.deployment,
                "capabilities": config.capabilities,
                "usage": {
                    "total_requests": stats.total_requests,
                    "total_cost": round(stats.total_cost, 4),
                    "average_latency_ms": round(stats.average_latency_ms, 2),
                    "error_rate": round(
                        stats.error_count / max(stats.total_requests, 1) * 100, 2
                    )
                }
            }
        
        return model_status
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.close()
        
        logger.info("Model Manager cleanup completed")


# Global instance
model_manager = ModelManager()