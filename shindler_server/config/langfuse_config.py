"""
Langfuse Configuration for Shindler Server
Handles Langfuse observability setup for AI agents and workflows
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LangfuseConfig(BaseSettings):
    """Langfuse configuration settings"""
    
    # Langfuse credentials (optional - will use defaults if not set)
    langfuse_secret_key: Optional[str] = Field(
        default=None,
        description="Langfuse secret key for authentication"
    )
    langfuse_public_key: Optional[str] = Field(
        default=None,
        description="Langfuse public key for authentication"
    )
    langfuse_host: Optional[str] = Field(
        default="https://cloud.langfuse.com",
        description="Langfuse host URL"
    )
    
    # Langfuse project settings
    langfuse_project_name: str = Field(
        default="shindler-safety-analytics",
        description="Langfuse project name"
    )
    
    # Enable/disable Langfuse
    langfuse_enabled: bool = Field(
        default=True,
        description="Whether to enable Langfuse observability"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

# Global configuration instance
langfuse_config = LangfuseConfig()

def initialize_langfuse():
    """Initialize Langfuse for observability"""
    try:
        from langfuse import Langfuse
        
        # Only initialize if Langfuse is enabled and credentials are provided
        if not langfuse_config.langfuse_enabled:
            print("Langfuse is disabled - skipping initialization")
            return None
            
        # Check if we have the minimum required credentials
        if not langfuse_config.langfuse_secret_key:
            print("Langfuse secret key not provided - using default configuration")
            # Use default configuration (local development)
            langfuse = Langfuse(
                project_name=langfuse_config.langfuse_project_name
            )
        else:
            # Use provided credentials
            langfuse = Langfuse(
                secret_key=langfuse_config.langfuse_secret_key,
                public_key=langfuse_config.langfuse_public_key,
                host=langfuse_config.langfuse_host,
                project_name=langfuse_config.langfuse_project_name
            )
        
        print(f"Langfuse initialized successfully for project: {langfuse_config.langfuse_project_name}")
        return langfuse
        
    except ImportError:
        print("Langfuse not installed - observability will be disabled")
        return None
    except Exception as e:
        print(f"Failed to initialize Langfuse: {str(e)}")
        return None

def get_langfuse_client():
    """Get the Langfuse client instance"""
    return initialize_langfuse()

# Initialize Langfuse on module import
langfuse_client = get_langfuse_client()
