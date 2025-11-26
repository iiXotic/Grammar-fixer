import sys
import os

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from file_scanner.main import main

if __name__ == "__main__":
    main()
