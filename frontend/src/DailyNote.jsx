import React, { useState, useEffect } from 'react';
import axios from 'axios';

const DailyNote = () => {
  const [note, setNote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDailyNote = async () => {
      try {
        // The backend runs on port 8000, so we need to specify the full URL.
        // We'll configure a proxy later to simplify this.
        const response = await axios.get('http://localhost:8000/api/notes/daily');
        setNote(response.data);
      } catch (err) {
        setError('Failed to fetch the daily note. Is the backend server running?');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDailyNote();
  }, []); // The empty dependency array ensures this runs only once on mount.

  if (loading) {
    return <div>Loading your daily note...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>{error}</div>;
  }

  if (!note) {
    return <div>No daily note found.</div>;
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

export default DailyNote;