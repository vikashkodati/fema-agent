"""
Simple task management system for an AI agent
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class Task:
    id: int
    title: str
    priority: str
    completed: bool
    created_at: datetime

class TaskManager:
    """
    A task management system that stores tasks in a JSON file.
    Provides methods for adding, listing, and completing tasks and providing task statistics
    """ 
    def __init__(self, task_file="tasks.json")-> None:
        self.task_file = task_file
        self.tasks = self._load_tasks()

    def _load_tasks(self) -> List[Dict]:
        """
        Load tasks from the JSON file
        """
        try:
           with open(self.task_file, "r") as f:
               return json.load(f)
        except FileNotFoundError:
            return []
    
    #save tasks to the JSON file
    def _save_tasks(self) -> None:
        """
        Save tasks to the JSON file
        """
        with open(self.task_file, "w") as f:
            json.dump(self.tasks, f, indent=4)

    #add task
    def add_task(self, title: str, priority: str = "medium") -> str:
        """
        Add a new task to the json with an auto generated ID
        """
        task= {
            "id": len(self.tasks) + 1,  
            "title": title,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        self.tasks.append(task)
        self._save_tasks()
        return f"Task '{title}' added successfully with priority '{priority}'"
    
    #list all tasks
    def list_tasks(self) -> str:
     if not self.tasks:
         return "No tasks found"
     
     # Sort tasks by priority (high > medium > low) and completion status
     priority_order = {"high": 0, "medium": 1, "low": 2}
     sorted_tasks = sorted(self.tasks, 
                          key=lambda x: (x["completed"], priority_order[x["priority"]]))
     
     result = ""
     for task in sorted_tasks:
         # Map priorities to emojis
         priority_emoji = {
             "high": "🔴",
             "medium": "🟡",
             "low": "🟢"
         }
         status = "✅" if task["completed"] else "⏳"
         result += f"{task['id']}. {priority_emoji[task['priority']]} {task['title']} {status}\n"
     
     return result
    
    #complete a task
    def complete_task(self, task_id: int) -> str:
        """
        Mark a task as completed
        """
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                self._save_tasks()
                return f"Task '{task['title']}' marked as completed"
        return f"Task with ID {task_id} not found"
    
    #provide task statistics
    def get_task_statistics(self) -> str:
        """
        Calculate and return productivity statistics with encouraging messages
        """
        if not self.tasks:
            return "No tasks available for statistics"
            
        # Calculate basic statistics
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks if task["completed"])
        completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        # Count tasks by priority
        priority_counts = {
            "high": sum(1 for task in self.tasks if task["priority"] == "high"),
            "medium": sum(1 for task in self.tasks if task["priority"] == "medium"),
            "low": sum(1 for task in self.tasks if task["priority"] == "low")
        }
        
        # Generate encouraging message based on completion rate
        if completion_rate == 100:
            message = "🏆 You've completed all your tasks! You're a rockstar!"
        elif completion_rate >= 80:
            message = "🌟 Outstanding progress! You're crushing it!"
        elif completion_rate >= 50:
            message = "💪 Great job! Keep up the momentum!" 
        else:
            message = "🎯 You're making progress! Every task completed is a step forward!"
        #format statistics string
            
        # Format statistics string
        stats = f"""
📊 Task Statistics:
------------------
Total Tasks: {total_tasks}
Completed: {completed_tasks}
Completion Rate: {completion_rate:.1f}%

Priority Breakdown:
🔴 High: {priority_counts['high']}
🟡 Medium: {priority_counts['medium']}
🟢 Low: {priority_counts['low']}

{message}
"""
        return stats
    


