import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TasksView = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/tasks');
      setTasks(response.data);
    } catch (err) {
      setError('Failed to fetch tasks.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleToggleTaskStatus = async (taskId, currentStatus) => {
    const newStatus = currentStatus === 'done' ? 'todo' : 'done';
    try {
      await axios.put(`http://localhost:8000/api/tasks/${taskId}`, { status: newStatus });
      // Refresh the task list to show the updated status
      fetchTasks();
    } catch (error) {
      console.error('Failed to update task status:', error);
      alert('Could not update task. Please try again.');
    }
  };

  if (loading) return <div>Loading all tasks...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div>
      <h1>All Tasks</h1>
      <div className="task-list">
        {tasks.length > 0 ? (
          tasks.map((task) => (
            <div key={task.id} className="task-item">
              <input
                type="checkbox"
                checked={task.status === 'done'}
                onChange={() => handleToggleTaskStatus(task.id, task.status)}
              />
              <span style={{ textDecoration: task.status === 'done' ? 'line-through' : 'none' }}>
                {task.description}
              </span>
              <span style={{ marginLeft: '1rem', fontSize: '0.8rem', color: '#777' }}>
                (from: {task.source_note_title})
              </span>
            </div>
          ))
        ) : (
          <p>No tasks found.</p>
        )}
      </div>
    </div>
  );
};

export default TasksView;