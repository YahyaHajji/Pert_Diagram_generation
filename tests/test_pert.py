"""
Test script for the PERT diagram functionality.
This script will create a sample PERT diagram and run the analysis independently of Streamlit.
"""

import matplotlib.pyplot as plt
import networkx as nx
from pert import PERTDiagram
import utils

def main():
    print("Creating PERT diagram...")
    diagram = PERTDiagram()
    
    # Add sample tasks
    sample_data = utils.get_sample_data()
    for task in sample_data:
        print(f"Adding task: {task['task_id']}, duration: {task['duration']}, dependencies: {task['dependencies']}")
        diagram.add_task(task["task_id"], task["duration"], task["dependencies"])
    
    # Validate the diagram
    is_valid, error_msg = diagram.validate_tasks()
    if not is_valid:
        print(f"Error validating tasks: {error_msg}")
        return
    
    # Analyze the diagram
    print("\nAnalyzing PERT diagram...")
    success, error_msg = diagram.analyze()
    if not success:
        print(f"Error analyzing diagram: {error_msg}")
        return
    
    # Print results
    print("\nAnalysis results:")
    print(f"Project duration: {diagram.project_duration} days")
    print(f"Critical path: {' -> '.join(diagram.critical_path)}")
    
    # Print task details
    print("\nTask details:")
    print(f"{'Task':<10} {'Duration':<10} {'EST':<8} {'EFT':<8} {'LST':<8} {'LFT':<8} {'Float':<8} {'Critical':<8}")
    print(f"{'-'*10} {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    
    for task_id, task_info in diagram.tasks.items():
        critical = "Yes" if task_id in diagram.critical_path else "No"
        print(f"{task_id:<10} {task_info['duration']:<10.1f} {task_info['est']:<8.1f} {task_info['eft']:<8.1f} {task_info['lst']:<8.1f} {task_info['lft']:<8.1f} {task_info['float']:<8.1f} {critical:<8}")
    
    # Draw the graph
    print("\nDrawing PERT diagram...")
    fig, ax = diagram.draw_graph()
    plt.show()

if __name__ == "__main__":
    main()
