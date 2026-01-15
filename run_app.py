"""
Entry point to run the Cribbage Trainer Streamlit app.
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cribbage_trainer.app import main

if __name__ == "__main__":
    main()