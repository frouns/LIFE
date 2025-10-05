import React, { useState, useEffect } from 'react';
import axios from 'axios';

const NoteList = () => {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNotes = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/notes');
        setNotes(response.data);
      } catch (err) {
        setError('Failed to fetch notes.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchNotes();
  }, []);

  if (loading) {
    return <div>Loading notes...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>{error}</div>;
  }

  return (
    <aside className="note-list-sidebar">
      <h2>All Notes</h2>
      <ul>
        {notes.map((note) => (
          <li key={note.title}>
            {note.title}
          </li>
        ))}
      </ul>
    </aside>
  );
};

export default NoteList;