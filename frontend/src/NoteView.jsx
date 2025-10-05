import React, { useState, useEffect } from 'react';
import axios from 'axios';

const NoteView = ({ noteTitle }) => {
  const [note, setNote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!noteTitle) {
      setLoading(false);
      setNote(null);
      return;
    }

    const fetchNote = async () => {
      setLoading(true);
      setError(null);
      try {
        const encodedTitle = encodeURIComponent(noteTitle);
        const response = await axios.get(`http://localhost:8000/api/notes/${encodedTitle}`);
        setNote(response.data);
      } catch (err) {
        setError(`Failed to fetch note: "${noteTitle}"`);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchNote();
  }, [noteTitle]); // Re-run the effect if the noteTitle prop changes.

  if (loading) {
    return <div>Loading note...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>{error}</div>;
  }

  if (!note) {
    // This case can be hit if noteTitle is null or the fetch is cleared.
    return <div>Select a note from the list to view its content.</div>;
  }

  return (
    <div>
      <h1>{note.title}</h1>
      <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
        {note.content}
      </pre>
    </div>
  );
};

export default NoteView;