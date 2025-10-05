import React, { useState, useEffect } from 'react';

const NoteEditor = ({ onSave, note = null }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  useEffect(() => {
    if (note) {
      setTitle(note.title);
      setContent(note.content);
    } else {
      setTitle('');
      setContent('');
    }
  }, [note]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) {
      alert('Title is required.');
      return;
    }
    onSave({ title, content });
  };

  const isEditing = note !== null;

  return (
    <form onSubmit={handleSubmit}>
      <h2>{isEditing ? 'Edit Note' : 'Create a New Note'}</h2>
      <div style={{ marginBottom: '1rem' }}>
        <label htmlFor="note-title" style={{ display: 'block', marginBottom: '0.5rem' }}>
          Title
        </label>
        <input
          id="note-title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          style={{ width: '100%', padding: '0.5rem' }}
          required
          disabled={isEditing}
        />
      </div>
      <div style={{ marginBottom: '1rem' }}>
        <label htmlFor="note-content" style={{ display: 'block', marginBottom: '0.5rem' }}>
          Content
        </label>
        <textarea
          id="note-content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          style={{ width: '100%', height: '300px', padding: '0.5rem' }}
        />
      </div>
      <button type="submit">Save Note</button>
    </form>
  );
};

export default NoteEditor;