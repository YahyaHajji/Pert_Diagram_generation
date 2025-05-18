import csv
import io
import base64
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def validate_task_input(task_id, duration_str, dependencies_str, existing_tasks):
    # Check if task ID is empty
    if not task_id:
        return False, "Task ID cannot be empty", None, None
    
    # Check if task ID already exists
    if task_id in existing_tasks:
        return False, f"Task ID '{task_id}' already exists", None, None
    
    # Validate duration
    try:
        duration = float(duration_str)
        if duration <= 0:
            return False, "Duration must be positive", None, None
    except ValueError:
        return False, "Duration must be a number", None, None
    
    # Parse dependencies
    if dependencies_str.strip():
        dependencies = [dep.strip() for dep in dependencies_str.split(',')]
        # Check that each dependency exists (except for the current task being added)
        for dep in dependencies:
            if dep and dep not in existing_tasks:
                return False, f"Dependency '{dep}' does not exist", None, None
    else:
        dependencies = []
    
    return True, "", duration, dependencies

def export_tasks_to_csv(tasks, critical_path=None):
    csv_buffer = io.StringIO()
    fieldnames = ['Task', 'Duration', 'Dependencies', 'EST', 'EFT', 'LST', 'LFT', 'Float', 'Critical']
    
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()
    
    for task_id, task_info in tasks.items():
        writer.writerow({
            'Task': task_id,
            'Duration': task_info['duration'],
            'Dependencies': ','.join(task_info['dependencies']),
            'EST': task_info['est'],
            'EFT': task_info['eft'],
            'LST': task_info['lst'],
            'LFT': task_info['lft'],
            'Float': task_info['float'],
            'Critical': task_id in (critical_path or [])
        })
    
    return csv_buffer.getvalue()

def export_tasks_to_txt(tasks, project_summary):
    txt_buffer = io.StringIO()
    
    # Write header
    txt_buffer.write("PERT DIAGRAM PROJECT REPORT\n")
    txt_buffer.write("=========================\n\n")
    txt_buffer.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Write project summary
    txt_buffer.write("PROJECT SUMMARY\n")
    txt_buffer.write(f"Total Duration: {project_summary['project_duration']} days\n")
    txt_buffer.write(f"Critical Path: {project_summary['critical_path']}\n")
    txt_buffer.write(f"Total Tasks: {project_summary['num_tasks']}\n")
    txt_buffer.write(f"Critical Tasks: {project_summary['num_critical_tasks']}\n\n")
    
    # Write task details
    txt_buffer.write("TASK DETAILS\n")
    txt_buffer.write("-----------\n\n")
    
    # Column headers
    txt_buffer.write(f"{'Task':<10} {'Duration':<10} {'EST':<8} {'EFT':<8} {'LST':<8} {'LFT':<8} {'Float':<8} {'Critical':<8} {'Dependencies':<20}\n")
    txt_buffer.write(f"{'-'*10} {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*20}\n")
    
    # Task data
    critical_path_tasks = project_summary['critical_path'].split(" → ") if project_summary['critical_path'] else []
    for task_id, task_info in tasks.items():
        critical = "Yes" if task_id in critical_path_tasks else "No"
        dependencies = ', '.join(task_info['dependencies'])
        txt_buffer.write(f"{task_id:<10} {task_info['duration']:<10.1f} {task_info['est']:<8.1f} {task_info['eft']:<8.1f} {task_info['lst']:<8.1f} {task_info['lft']:<8.1f} {task_info['float']:<8.1f} {critical:<8} {dependencies:<20}\n")
    
    return txt_buffer.getvalue()

def generate_pdf_report(tasks, project_summary, fig):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading1']
    normal_style = styles['Normal']
    
    # Add title
    elements.append(Paragraph("PERT Diagram Project Report", title_style))
    elements.append(Spacer(1, 12))
    
    # Add date
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 24))
    
    # Add project summary
    elements.append(Paragraph("Project Summary", heading_style))
    
    summary_data = [
        ["Total Duration", f"{project_summary['project_duration']} days"],
        ["Critical Path", project_summary['critical_path']],
        ["Total Tasks", str(project_summary['num_tasks'])],
        ["Critical Tasks", str(project_summary['num_critical_tasks'])]
    ]
    
    summary_table = Table(summary_data, colWidths=[120, 350])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(summary_table)
    elements.append(Spacer(1, 24))
    
    # Add task details
    elements.append(Paragraph("Task Details", heading_style))
    
    # Convert tasks to a list of lists for the table
    task_data = [['Task', 'Duration', 'EST', 'EFT', 'LST', 'LFT', 'Float', 'Critical', 'Dependencies']]
    
    critical_path_tasks = project_summary['critical_path'].split(" → ") if project_summary['critical_path'] else []
    for task_id, task_info in tasks.items():
        critical = "Yes" if task_id in critical_path_tasks else "No"
        task_data.append([
            task_id,
            str(task_info['duration']),
            str(task_info['est']),
            str(task_info['eft']),
            str(task_info['lst']),
            str(task_info['lft']),
            str(task_info['float']),
            critical,
            ', '.join(task_info['dependencies'])
        ])
    
    # Create the task table
    task_table = Table(task_data)
    task_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(task_table)
    
    # Build the PDF
    doc.build(elements)
    
    return buffer.getvalue()

def get_image_download_link(fig, filename, text="Download PERT diagram as PNG"):

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">📥 {text}</a>'
    return href

def get_file_download_link(data, filename, text):

    if isinstance(data, str):
        data = data.encode()
        
    b64 = base64.b64encode(data).decode()
    
    # Determine MIME type based on file extension
    mime_type = 'text/plain'
    if filename.endswith('.csv'):
        mime_type = 'text/csv'
    elif filename.endswith('.pdf'):
        mime_type = 'application/pdf'
    
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}">📥 {text}</a>'
    return href

def get_sample_data():

    sample_data = [
        {"task_id": "A", "duration": 3, "dependencies": []},
        {"task_id": "B", "duration": 4, "dependencies": ["A"]},
        {"task_id": "C", "duration": 2, "dependencies": ["A"]},
        {"task_id": "D", "duration": 5, "dependencies": ["B"]},
        {"task_id": "E", "duration": 6, "dependencies": ["C"]},
        {"task_id": "F", "duration": 4, "dependencies": ["D", "E"]},
        {"task_id": "G", "duration": 3, "dependencies": ["F"]}
    ]
    return sample_data

def format_duration(days):
    """Format duration in days to a more readable format"""
    if days == int(days):
        return str(int(days))
    return f"{days:.1f}"
