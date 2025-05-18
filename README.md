# PERT Diagram Analysis Tool

A web-based tool for creating, analyzing, and visualizing Program Evaluation and Review Technique (PERT) diagrams for project management.

## Features

- Add tasks with durations and dependencies
- Automatic calculation of:
  - Earliest Start Time (EST)
  - Earliest Finish Time (EFT)
  - Latest Start Time (LST)
  - Latest Finish Time (LFT)
  - Task Float
- Critical path identification and visualization
- Interactive PERT diagram with custom styling
- Export options:
  - Download diagram as PNG
  - Export task data as CSV
  - Generate PDF report
- Sample project loading for demonstration

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd RO_Project
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

- `app.py` - Main Streamlit application interface
- `pert.py` - PERT diagram implementation and analysis logic
- `utils.py` - Utility functions for exports and data manipulation

## Usage

1. Go to the "Task Input" tab to add your project tasks
2. For each task provide:
   - Task ID (unique identifier)
   - Duration (in days)
   - Dependencies (other tasks that must be completed first)
3. After adding tasks, go to the "PERT Analysis" tab to visualize and analyze your project
4. Use the "Export Options" tab to export your analysis in different formats

## Dependencies

- streamlit
- networkx
- matplotlib
- pandas
- reportlab
- base64
- io
- datetime

## License

[MIT](LICENSE)
