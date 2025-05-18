"""
PERT Diagram Streamlit Application

This application allows users to create, visualize, and analyze PERT diagrams
for project management planning and control.
"""

import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image
import io

# Import custom modules
from pert import PERTDiagram
import utils

# Set page configuration
st.set_page_config(
    page_title="PERT Diagram Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define CSS styles
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .info-box {
        background-color: #E5F6FD;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .critical-text {
        color: #DC2626;
        font-weight: bold;
    }
    .non-critical-text {
        color: #2563EB;
    }
    .float-box {
        font-size: 0.9rem;
        padding: 0.5rem;
        background-color: #F3F4F6;
        border-radius: 0.25rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'pert_diagram' not in st.session_state:
    st.session_state.pert_diagram = PERTDiagram()
    
if 'tasks_added' not in st.session_state:
    st.session_state.tasks_added = False
    
if 'show_sample' not in st.session_state:
    st.session_state.show_sample = False
    
if 'error_message' not in st.session_state:
    st.session_state.error_message = ""

# Application Header
st.markdown('<div class="main-header">📊 PERT Diagram Analysis Tool</div>', unsafe_allow_html=True)

st.markdown("""
This application helps you create, visualize, and analyze PERT (Program Evaluation Review Technique) 
diagrams for project management. PERT diagrams are used to plan and coordinate tasks in a project, 
identifying the critical path and calculating project duration.
""")

# Sidebar for controls and information
with st.sidebar:
    st.markdown('<div class="section-header">🛠️ PERT Controls</div>', unsafe_allow_html=True)
    
    # Reset button
    if st.button("🔄 Reset Project"):
        st.session_state.pert_diagram = PERTDiagram()
        st.session_state.tasks_added = False
        st.rerun()    
    # Load sample data
    if st.button("📋 Load Sample Project"):
        # Clear existing data first
        st.session_state.pert_diagram = PERTDiagram()
        
        # Load sample data
        sample_data = utils.get_sample_data()
        for task in sample_data:
            st.session_state.pert_diagram.add_task(
                task["task_id"], 
                task["duration"], 
                task["dependencies"]
            )
        
        st.session_state.tasks_added = True
        st.session_state.show_sample = True
        st.rerun()    
    # Information box
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">ℹ️ About PERT Analysis</div>', unsafe_allow_html=True)
    st.markdown("""
    **Key Terms:**
    - **EST**: Earliest Start Time
    - **EFT**: Earliest Finish Time
    - **LST**: Latest Start Time
    - **LFT**: Latest Finish Time
    - **Float**: Available slack time
    
    **Critical Path** is the sequence of tasks that determines the minimum project duration. Tasks on the critical path have zero float.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Main content tabs
tab1, tab2, tab3 = st.tabs(["Task Input", "PERT Analysis", "Export Options"])

# Tab 1: Task Input
with tab1:
    st.markdown('<div class="section-header">📝 Task Input</div>', unsafe_allow_html=True)
    
    # Input form
    with st.form(key="task_input_form"):
        # Create columns for the form
        col1, col2 = st.columns(2)
        
        with col1:
            task_id = st.text_input("Task ID (unique identifier)", key="task_id")
            duration = st.text_input("Duration (days)", key="duration")
        
        with col2:
            dependencies = st.text_input("Dependencies (comma-separated list of task IDs)", key="dependencies")
        
        # Submit button
        submit_button = st.form_submit_button(label="➕ Add Task")
        
        if submit_button:
            # Validate input
            existing_tasks = list(st.session_state.pert_diagram.tasks.keys())
            is_valid, error_msg, parsed_duration, parsed_dependencies = utils.validate_task_input(
                task_id, duration, dependencies, existing_tasks
            )
            
            if is_valid:
                # Add task to PERT diagram
                st.session_state.pert_diagram.add_task(task_id, parsed_duration, parsed_dependencies)
                st.session_state.tasks_added = True
                st.session_state.error_message = ""
                st.rerun()
            else:
                st.session_state.error_message = error_msg
    
    # Display error message if there is one
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
    
    # Show current tasks
    if st.session_state.tasks_added:
        st.markdown('<div class="section-header">📋 Current Tasks</div>', unsafe_allow_html=True)
        
        # Create a pandas DataFrame from tasks
        task_data = []
        for task_id, task_info in st.session_state.pert_diagram.tasks.items():
            task_data.append({
                "Task ID": task_id,
                "Duration (days)": utils.format_duration(task_info["duration"]),
                "Dependencies": ", ".join(task_info["dependencies"]) if task_info["dependencies"] else "None"
            })
        
        if task_data:
            df = pd.DataFrame(task_data)
            st.dataframe(df, use_container_width=True)
        
        # Analyze button
        if st.button("🔍 Analyze Project"):
            success, error_msg = st.session_state.pert_diagram.analyze()
            if success:
                st.success("Project analyzed successfully! View results in the PERT Analysis tab.")
                # Switch to the analysis tab
                st.query_params.tab = "PERT Analysis"
            else:
                st.error(f"Error analyzing project: {error_msg}")

# Tab 2: PERT Analysis
with tab2:
    if not st.session_state.tasks_added:
        st.info("Please add tasks in the Task Input tab first.")
    else:
        # Check if analysis has been performed
        if not st.session_state.pert_diagram.project_duration:
            success, error_msg = st.session_state.pert_diagram.analyze()
            if not success:
                st.error(f"Error in project analysis: {error_msg}")
                st.stop()
        
        # Display project summary
        st.markdown('<div class="section-header">📋 Project Summary</div>', unsafe_allow_html=True)
        
        project_summary = st.session_state.pert_diagram.get_project_summary()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Project Duration:** {utils.format_duration(project_summary['project_duration'])} days")
            st.markdown(f"**Number of Tasks:** {project_summary['num_tasks']}")
        
        with col2:
            st.markdown(f"**Critical Path:** {project_summary['critical_path']}")
            st.markdown(f"**Critical Tasks:** {project_summary['num_critical_tasks']}")
        
        # Display PERT diagram
        st.markdown('<div class="section-header">🔄 PERT Diagram</div>', unsafe_allow_html=True)
        
        fig, ax = st.session_state.pert_diagram.draw_graph(figsize=(10, 6))
        st.pyplot(fig)
        
        # Display task analysis table
        st.markdown('<div class="section-header">📊 Task Analysis</div>', unsafe_allow_html=True)
        
        task_table = st.session_state.pert_diagram.get_task_table()
        task_df = pd.DataFrame(task_table)
        
        # Style the dataframe - highlight critical path tasks
        # First convert boolean critical column to string for safer processing
        task_df['Critical_Str'] = task_df['Critical'].map({True: 'Yes', False: 'No'})
        
        # Create a style function that doesn't rely on accessing the Critical column directly
        def highlight_critical_tasks(s):
            is_critical = task_df.loc[s.index, 'Critical'].tolist()
            return ['background-color: #FECACA; color: #DC2626; font-weight: bold' if c else '' for c in is_critical]
        
        # Apply the style
        styled_df = task_df.style.apply(
            highlight_critical_tasks,
            axis=0,  # Apply along columns
            subset=['Task']  # Only style the Task column
        )
        
        # Display the styled dataframe
        st.dataframe(
            styled_df,
            column_config={
                "Task": "Task ID",
                "Duration": st.column_config.NumberColumn("Duration (days)", format="%.1f"),
                "Dependencies": "Dependencies",
                "EST": st.column_config.NumberColumn("EST", format="%.1f"),
                "EFT": st.column_config.NumberColumn("EFT", format="%.1f"),
                "LST": st.column_config.NumberColumn("LST", format="%.1f"),
                "LFT": st.column_config.NumberColumn("LFT", format="%.1f"),
                "Float": st.column_config.NumberColumn("Float", format="%.1f"),
                "Critical": st.column_config.CheckboxColumn("Critical Path"),
                "Critical_Str": None  # Hide this column as we're using it just for styling
            },
            use_container_width=True
        )

# Tab 3: Export Options
with tab3:
    if not st.session_state.tasks_added:
        st.info("Please add tasks in the Task Input tab first.")
    else:
        # Check if analysis has been performed
        if not st.session_state.pert_diagram.project_duration:
            success, error_msg = st.session_state.pert_diagram.analyze()
            if not success:
                st.error(f"Error in project analysis: {error_msg}")
                st.stop()
        
        st.markdown('<div class="section-header">📤 Export Project Data</div>', unsafe_allow_html=True)
        
        # Get necessary data
        project_summary = st.session_state.pert_diagram.get_project_summary()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Export Diagram")
            
            # Export PERT diagram as PNG
            fig, ax = st.session_state.pert_diagram.draw_graph(figsize=(10, 6))
            download_png = utils.get_image_download_link(
                fig, "pert_diagram.png", "Download PERT Diagram (PNG)"
            )
            st.markdown(download_png, unsafe_allow_html=True)
            plt.close(fig)
            
            # Export project report as PDF
            # Create a new figure for the PDF report to avoid conflicts
            pdf_fig, pdf_ax = st.session_state.pert_diagram.draw_graph(figsize=(10, 6))
            pdf_data = utils.generate_pdf_report(
                st.session_state.pert_diagram.tasks,
                project_summary,
                pdf_fig
            )
            plt.close(pdf_fig)
            
            download_pdf = utils.get_file_download_link(
                pdf_data, "pert_project_report.pdf", "Download Project Report (PDF)"
            )
            st.markdown(download_pdf, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Export Task Data")
            
            # Export tasks as CSV
            csv_data = utils.export_tasks_to_csv(st.session_state.pert_diagram.tasks, st.session_state.pert_diagram.critical_path)
            download_csv = utils.get_file_download_link(
                csv_data, "pert_tasks.csv", "Download Task Data (CSV)"
            )
            st.markdown(download_csv, unsafe_allow_html=True)
            
            # Export tasks as TXT
            txt_data = utils.export_tasks_to_txt(
                st.session_state.pert_diagram.tasks,
                project_summary
            )
            download_txt = utils.get_file_download_link(
                txt_data, "pert_project.txt", "Download Project Report (TXT)"
            )
            st.markdown(download_txt, unsafe_allow_html=True)
        
        st.markdown("""
        ---
        ### What You Can Do With These Exports
        
        - **PNG Diagram**: Include in presentations, reports, or documentation
        - **PDF Report**: Share with stakeholders or print for project documentation
        - **CSV Data**: Import into spreadsheet software for further analysis
        - **TXT Report**: Simple text-based project summary for quick reference
        """)

# Show a nice footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.8rem;">
        Made with ❤️ By Hajji Yahya
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.8rem;">
    PERT Diagram Analysis Tool | Built with Streamlit, NetworkX, and Matplotlib
</div>
""", unsafe_allow_html=True)




# Handle initial load of sample data if needed
if st.session_state.show_sample and not st.session_state.pert_diagram.project_duration:
    success, _ = st.session_state.pert_diagram.analyze()
    if success:
        st.session_state.show_sample = False
        
# This allows the script to be run directly without Streamlit for debugging purposes
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        print("Running in debug mode")
        # Create a sample PERT diagram
        diagram = PERTDiagram()
        
        # Add some tasks
        sample_data = utils.get_sample_data()
        for task in sample_data:
            diagram.add_task(task["task_id"], task["duration"], task["dependencies"])
        
        # Analyze the diagram
        success, error_msg = diagram.analyze()
        if success:
            print(f"Project duration: {diagram.project_duration} days")
            print(f"Critical path: {' → '.join(diagram.critical_path)}")
            
            # Draw the graph
            fig, ax = diagram.draw_graph()
            plt.show()
        else:
            print(f"Error: {error_msg}")
    else:
        print("This script is intended to be run with Streamlit.")
        print("Run: streamlit run app.py")
        print("Or for debugging: python app.py --debug")
