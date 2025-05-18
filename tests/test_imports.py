"""
Test script to check if all the necessary modules can be imported.
"""

import sys
print(f"Python version: {sys.version}")

try:
    import streamlit
    print(f"Streamlit version: {streamlit.__version__}")
except Exception as e:
    print(f"Error importing streamlit: {e}")

try:
    import pandas as pd
    print(f"Pandas version: {pd.__version__}")
except Exception as e:
    print(f"Error importing pandas: {e}")

try:
    import matplotlib
    import matplotlib.pyplot as plt
    print("matplotlib version:", matplotlib.__version__)
except Exception as e:
    print(f"Error importing matplotlib: {e}")

try:
    import networkx as nx
    print(f"NetworkX version: {nx.__version__}")
except Exception as e:
    print(f"Error importing networkx: {e}")

try:
    import reportlab
    print(f"ReportLab version: {reportlab.Version}")
except Exception as e:
    print(f"Error importing reportlab: {e}")

try:
    from PIL import Image
    print(f"PIL version: {Image.__version__}")
except Exception as e:
    print(f"Error importing PIL: {e}")

# Now try to import the custom modules
try:
    from pert import PERTDiagram
    print("Successfully imported PERTDiagram from pert module")
except Exception as e:
    print(f"Error importing PERTDiagram: {e}")

try:
    import utils
    print("Successfully imported utils module")
except Exception as e:
    print(f"Error importing utils: {e}")
