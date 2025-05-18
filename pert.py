import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import deque

class PERTDiagram:

    def __init__(self):
        self.tasks = {}
        self.graph = nx.DiGraph()
        self.critical_path = []
        self.project_duration = 0
        
    def add_task(self, task_id, duration, dependencies=None):
        if dependencies is None:
            dependencies = []
            
        self.tasks[task_id] = {
            'duration': duration,
            'dependencies': dependencies,
            'est': 0,  # Earliest start time
            'eft': 0,  # Earliest finish time
            'lst': 0,  # Latest start time
            'lft': 0,  # Latest finish time
            'float': 0  # Float/slack time
        }
    
    def validate_tasks(self):

        for task_id, task_info in self.tasks.items():
            for dep in task_info['dependencies']:
                if dep not in self.tasks:
                    return False, f"Task '{task_id}' depends on non-existent task '{dep}'"
        
        try:
            # This will raise NetworkXUnfeasible if the graph has cycles
            task_ids = list(self.tasks.keys())
            g = nx.DiGraph()
            
            # Add all tasks as nodes
            for task_id in task_ids:
                g.add_node(task_id)
            
            # Add dependencies as edges
            for task_id, task_info in self.tasks.items():
                for dep in task_info['dependencies']:
                    g.add_edge(dep, task_id)
            
            nx.find_cycle(g)
            return False, "Circular dependency detected in the project"
        except nx.NetworkXNoCycle:
            # No cycle found, which is good
            return True, ""
        
    def _build_graph(self):
        """Build a directed graph from tasks."""
        self.graph = nx.DiGraph()
        
        # Add all tasks as nodes with their attributes
        for task_id, task_info in self.tasks.items():
            self.graph.add_node(task_id, **task_info)
        
        # Add dependencies as edges
        for task_id, task_info in self.tasks.items():
            for dep in task_info['dependencies']:
                self.graph.add_edge(dep, task_id)
    
    def calculate_earliest_times(self):
        """Calculate earliest start and finish times for each task."""
        # Start with tasks that have no dependencies
        no_deps_tasks = [task_id for task_id, task_info in self.tasks.items() 
                        if not task_info['dependencies']]
        
        # Process tasks in topological order
        for task_id in nx.topological_sort(self.graph):
            task_info = self.tasks[task_id]
            
            # If no dependencies, EST is 0
            if not task_info['dependencies']:
                task_info['est'] = 0
            else:
                # EST is the maximum EFT of all predecessor tasks
                max_eft = 0
                for dep in task_info['dependencies']:
                    dep_eft = self.tasks[dep]['eft']
                    max_eft = max(max_eft, dep_eft)
                task_info['est'] = max_eft
            
            # EFT = EST + Duration
            task_info['eft'] = task_info['est'] + task_info['duration']
        
        # Project duration is the maximum EFT of all tasks
        if self.tasks:
            self.project_duration = max(task_info['eft'] for task_info in self.tasks.values())
    
    def calculate_latest_times(self):
        """Calculate latest start and finish times for each task."""
        # Start with tasks that have no successors
        for task_id in self.tasks:
            self.tasks[task_id]['lft'] = self.project_duration
        
        # Process tasks in reverse topological order
        for task_id in reversed(list(nx.topological_sort(self.graph))):
            task_info = self.tasks[task_id]
            
            # Get successors of this task
            successors = list(self.graph.successors(task_id))
            
            if successors:
                # LFT is the minimum LST of all successor tasks
                min_lst = float('inf')
                for succ in successors:
                    succ_lst = self.tasks[succ]['lst']
                    min_lst = min(min_lst, succ_lst)
                task_info['lft'] = min_lst
            
            # LST = LFT - Duration
            task_info['lst'] = task_info['lft'] - task_info['duration']
            
            # Calculate float time
            task_info['float'] = task_info['lst'] - task_info['est']
    
    def identify_critical_path(self):
        """
        Identify the critical path in the PERT diagram.
        """
        self.critical_path = []
        
        # First find all tasks with zero float (critical tasks)
        critical_tasks = [task_id for task_id, task_info in self.tasks.items() 
                        if task_info['float'] == 0]
        
        # Now we need to order them in the execution order
        if critical_tasks:
            critical_subgraph = self.graph.subgraph(critical_tasks)
            
            # Find a starting point (a task with no incoming edges in the critical subgraph)
            start_tasks = [t for t in critical_tasks if critical_subgraph.in_degree(t) == 0]
            
            if start_tasks:
                # Use BFS to traverse the critical path
                visited = set()
                queue = deque(start_tasks)
                
                while queue:
                    task_id = queue.popleft()
                    if task_id not in visited:
                        visited.add(task_id)
                        self.critical_path.append(task_id)
                        
                        # Add unvisited critical successors to the queue
                        for succ in critical_subgraph.successors(task_id):
                            if succ not in visited:
                                queue.append(succ)
    
    def analyze(self):
        """
        Perform full PERT analysis:
        1. Build the graph
        2. Calculate earliest times
        3. Calculate latest times
        4. Identify the critical path
        
        Returns:
            bool: True if analysis was successful, False otherwise
        """
        # First validate the tasks
        is_valid, error_message = self.validate_tasks()
        if not is_valid:
            return False, error_message
        
        try:
            self._build_graph()
            self.calculate_earliest_times()
            self.calculate_latest_times()
            self.identify_critical_path()
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def get_task_table(self):
        """
        Generate a table of task information including:
        - Task ID
        - Duration
        - EST
        - EFT
        - LST
        - LFT
        - Float
        - Critical (True/False)
        
        Returns:
            list: List of dictionaries with task information
        """
        table = []
        for task_id, task_info in self.tasks.items():
            table.append({
                'Task': task_id,
                'Duration': task_info['duration'],
                'Dependencies': ', '.join(task_info['dependencies']),
                'EST': task_info['est'],
                'EFT': task_info['eft'],
                'LST': task_info['lst'],
                'LFT': task_info['lft'],
                'Float': task_info['float'],
                'Critical': task_id in self.critical_path
            })
        return table
    
    def draw_graph(self, figsize=(12, 8)):
        """
        Draw the PERT diagram using matplotlib.
        
        Args:
            figsize (tuple): Figure size (width, height) in inches
            
        Returns:
            tuple: (fig, ax) matplotlib figure and axes objects
        """
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create a layout for the graph
        pos = nx.spring_layout(self.graph, seed=42, k=1.5)
        
        # Draw the non-critical nodes
        non_critical = [n for n in self.graph.nodes if n not in self.critical_path]
        nx.draw_networkx_nodes(self.graph, pos, nodelist=non_critical, 
                            node_color='skyblue', node_size=1800, alpha=0.8)
        
        # Draw the critical nodes
        nx.draw_networkx_nodes(self.graph, pos, nodelist=self.critical_path, 
                            node_color='red', node_size=1800, alpha=0.8)
        
        # Draw edges without arrows (just lines)
        nx.draw_networkx_edges(self.graph, pos, width=2, alpha=0.7, 
                            arrows=False, edge_color='black')
        
        # Draw custom arrows that are visible outside the node circles
        for u, v in self.graph.edges():
            # Get node positions
            pos_u = pos[u]
            pos_v = pos[v]
            
            # Calculate vector from u to v
            dx = pos_v[0] - pos_u[0]
            dy = pos_v[1] - pos_u[1]
            
            # Normalize the vector
            dist = (dx**2 + dy**2)**0.5
            if dist > 0:  # Avoid division by zero
                dx, dy = dx/dist, dy/dist
            
            # Reduce the arrow length to stop just outside the node (which has radius ~20)
            node_radius = 25  # Approximate node radius in points
            end_x = pos_v[0] - dx * node_radius / 72  # Convert from points to figure coordinates
            end_y = pos_v[1] - dy * node_radius / 72
            
            # Create arrow
            arrow = mpatches.FancyArrowPatch(
                posA=pos_u, 
                posB=(end_x, end_y),
                arrowstyle='-|>',
                color='aquamarine',  # Arrowhead color
                mutation_scale=20,
                linewidth=2,
                connectionstyle='arc3,rad=0.0'
            )
            ax.add_patch(arrow)
        
        # Draw labels for each node
        node_labels = {}
        for node in self.graph.nodes:
            task = self.tasks[node]
            label = f"{node}\nDur: {task['duration']}\nEST: {task['est']}\nLST: {task['lst']}"
            node_labels[node] = label
        
        nx.draw_networkx_labels(self.graph, pos, labels=node_labels, font_size=9)
        
        # Add legend
        critical_patch = mpatches.Patch(color='red', label='Critical Path')
        non_critical_patch = mpatches.Patch(color='skyblue', label='Non-Critical Tasks')
        plt.legend(handles=[critical_patch, non_critical_patch], loc='upper right')
        
        # Set title and remove axis
        plt.title(f"PERT Diagram (Project Duration: {self.project_duration} days)", fontsize=16)
        plt.axis('off')
        
        return fig, ax
        
    def get_project_summary(self):
        """
        Get a summary of the project.
        
        Returns:
            dict: Summary information including project duration and critical path
        """
        return {
            'project_duration': self.project_duration,
            'critical_path': ' → '.join(self.critical_path),
            'num_tasks': len(self.tasks),
            'num_critical_tasks': len(self.critical_path)
        }
