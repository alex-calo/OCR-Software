"""
DocCamOCR - Application Launcher with proper Unicode support
"""
import sys
import os
import logging

def setup_logging():
    """Configure logging with proper Unicode support."""
    # Create logs directory
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging with UTF-8 encoding
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "doc_cam_ocr.log"), 
                              encoding='utf-8'),
            # Use a stream handler that supports Unicode
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Fix console encoding for Windows
    if sys.platform == "win32":
        try:
            # Try to set UTF-8 console output
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

def main():
    """Main application entry point."""
    # Set up logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting DocCamOCR application...")
        
        # Import and run main application
        from main import main as app_main
        return app_main()
        
    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())