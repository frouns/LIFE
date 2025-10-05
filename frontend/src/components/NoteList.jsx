import React from 'react';
import Search from './Search';

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
      <div className="sidebar-controls">
        <button onClick={onNewNote} style={{ width: '100%', marginBottom: '1rem' }}>
          New Note
        </button>
        <Search onSelectNote={onSelectNote} />
      </div>
      <div className="sidebar-note-list">
        <h2>All Notes</h2>
        {renderContent()}
      </div>
    </aside>
  );
};

export default NoteList;