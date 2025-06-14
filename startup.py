"""
Azure App Service startup script for Advanced AI Agent
This file is used by the web.config to start the application
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main startup function for Azure App Service"""
    try:
        # Set environment variables for production
        os.environ.setdefault('ENVIRONMENT', 'production')
        os.environ.setdefault('DEBUG', 'False')
        
        # Get port from Azure App Service
        port = int(os.environ.get('PORT', 8000))
        
        logger.info(f"🚀 Starting Advanced AI Agent on port {port}")
        
        # Import and run the FastAPI application
        import uvicorn
        from main import app
        
        # Run with uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True,
            workers=1  # Azure App Service works better with single worker
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()