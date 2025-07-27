import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class AzureOpenAIConfig(BaseSettings):
    """Azure OpenAI configuration settings"""
    
    # Azure OpenAI credentials
    azure_openai_endpoint: str = Field(
        default="",
        description="Azure OpenAI endpoint URL"
    )
    azure_openai_api_key: str = Field(
        default="",
        description="Azure OpenAI API key"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview",
        description="Azure OpenAI API version"
    )
    azure_openai_deployment_name: str = Field(
        default="",
        description="Azure OpenAI deployment name"
    )
    
    # Model configuration
    max_tokens: int = Field(default=1000, description="Maximum tokens for responses")
    temperature: float = Field(default=0.7, description="Temperature for AI responses")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields in .env file


# Global configuration instance
azure_config = AzureOpenAIConfig()


def get_azure_openai_client():
    """Get configured Azure OpenAI client"""
    from openai import AzureOpenAI
    
    return AzureOpenAI(
        azure_endpoint=azure_config.azure_openai_endpoint,
        api_key=azure_config.azure_openai_api_key,
        api_version=azure_config.azure_openai_api_version,
    ) 