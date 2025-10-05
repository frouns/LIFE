import React from 'react';

const NoteList = ({ notes, loading, error, onSelectNote, onNewNote }) => {
  const renderContent = () => {
    if (loading) {
      return <div>Loading notes...</div>;
    }
    if (error) {
      return <div style={{ color: 'red' }}>{error}</div>;
    }
    return (
      <ul>
        {notes.map((note) => (
          <li key={note.title} onClick={() => onSelectNote(note.title)}>
            {note.title}
          </li>
        ))}
      </ul>
    );
  };

  return (
    <aside className="note-list-sidebar">
      <div style={{ padding: '0 1rem', borderBottom: '1px solid #ccc', marginBottom: '1rem' }}>
        <button onClick={onNewNote} style={{ width: '100%', marginBottom: '1rem' }}>
          New Note
        </button>
      </div>
      {renderContent()}
    </aside>
  );
};

export default NoteList;