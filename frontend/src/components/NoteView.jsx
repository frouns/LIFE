import React, { useState, useEffect } from 'react';
import apiClient from './api';
import { parseContent } from './utils/contentParser';

const NoteView = ({ noteTitle, onEdit, onSelectNote }) => {
  const [note, setNote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchNote = async () => {
    if (!noteTitle) {
      setLoading(false);
      setNote(null);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const encodedTitle = encodeURIComponent(noteTitle);
      const response = await apiClient.get(`/api/notes/${encodedTitle}`);
      setNote(response.data);
    } catch (err) {
      setError(`Failed to fetch note: "${noteTitle}"`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNote();
  }, [noteTitle]);

  const handleToggleTaskStatus = async (taskId, currentStatus) => {
    const newStatus = currentStatus === 'done' ? 'todo' : 'done';
    try {
      await apiClient.put(`/api/tasks/${taskId}`, { status: newStatus });
      fetchNote();
    } catch (error) {
      console.error('Failed to update task status:', error);
      alert('Could not update task. Please try again.');
    }
  };

  if (loading) return <div>Loading note...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!note) return <div>Select a note from the list to view its content.</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>{note.title}</h1>
        <button onClick={() => onEdit(note)}>Edit</button>
      </div>
      <div className="note-content">
        {parseContent(note.content, onSelectNote)}
      </div>

      {note.tasks && note.tasks.length > 0 && (
        <>
          <hr style={{ margin: '2rem 0' }} />
          <h3>Tasks</h3>
          <div className="task-list">
            {note.tasks.map((task) => (
              <div key={task.id} className="task-item">
                <input
                  type="checkbox"
                  checked={task.status === 'done'}
                  onChange={() => handleToggleTaskStatus(task.id, task.status)}
                />
                <span style={{ textDecoration: task.status === 'done' ? 'line-through' : 'none' }}>
                  {task.description}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default NoteView;