"""
Application settings and configuration (env only)
"""

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings (env only)"""
    # Database settings
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str
    
    # Application settings
    app_name: str
    app_version: str
    app_description: str
    debug: bool
    app_host: str
    app_port: int
    
    # File upload settings
    max_file_size: str
    allowed_extensions: str
    
    # Logging settings
    log_level: str
    log_file: str
    log_max_bytes: int
    log_backup_count: int

    # S3 settings
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    s3_bucket_name: str

    # Azure OpenAI settings
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_api_version: str
    azure_openai_deployment_name: str

    # JWT Authentication settings
    jwt_secret_key: str
    jwt_algorithm: str 

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields in .env file (needed for POSTGRES_* variables)

    @property
    def database_url(self) -> str:
        """Construct database URL from individual components"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size to bytes"""
        size_str = self.max_file_size.upper()
        if size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        else:
            return int(size_str)

    @property
    def allowed_extensions_list(self) -> list:
        """Convert allowed extensions string to list"""
        return [ext.strip() for ext in self.allowed_extensions.split(',')]

# Global settings instance
settings = Settings()
