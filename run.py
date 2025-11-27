import sys
import os

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from grammar_fixer.main import main

if __name__ == "__main__":
    main()
