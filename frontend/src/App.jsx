import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DailyNote from './DailyNote';
import NoteList from './NoteList';
import NoteView from './NoteView';
import NoteEditor from './NoteEditor';
import TasksView from './TasksView';
import './App.css';

function App() {
  const [notes, setNotes] = useState([]);
  const [loadingNotes, setLoadingNotes] = useState(true);
  const [errorNotes, setErrorNotes] = useState(null);
  const [selectedNoteTitle, setSelectedNoteTitle] = useState(null);
  const [viewMode, setViewMode] = useState('view'); // 'view', 'create', 'edit', 'tasks'
  const [editingNote, setEditingNote] = useState(null);

  const fetchNotes = async () => {
    try {
      setLoadingNotes(true);
      const response = await axios.get('http://localhost:8000/api/notes');
      setNotes(response.data);
      setErrorNotes(null);
    } catch (err) {
      setErrorNotes('Failed to fetch notes.');
      console.error(err);
    } finally {
      setLoadingNotes(false);
    }
  };

  useEffect(() => {
    if (viewMode !== 'tasks') {
      fetchNotes();
    }
  }, [viewMode]);

  const handleSelectNote = (title) => {
    setSelectedNoteTitle(title);
    setViewMode('view');
    setEditingNote(null);
  };

  const handleNewNoteClick = () => {
    setViewMode('create');
    setEditingNote(null);
    setSelectedNoteTitle(null);
  };

  const handleEditNote = (note) => {
    setEditingNote(note);
    setViewMode('edit');
  };

  const handleSaveNote = async (noteData) => {
    try {
      if (viewMode === 'edit') {
        const encodedTitle = encodeURIComponent(editingNote.title);
        await axios.put(`http://localhost:8000/api/notes/${encodedTitle}`, { content: noteData.content });
      } else {
        await axios.post('http://localhost:8000/api/notes', noteData);
      }
      await fetchNotes();
      handleSelectNote(noteData.title);
    } catch (error) {
      console.error('Failed to save note:', error);
      alert('Error: Could not save the note.');
    }
  };

  const renderMainContent = () => {
    if (viewMode === 'tasks') {
      return <TasksView />;
    }
    if (viewMode === 'create') {
      return <NoteEditor onSave={handleSaveNote} />;
    }
    if (viewMode === 'edit') {
      return <NoteEditor onSave={handleSaveNote} note={editingNote} />;
    }
    if (selectedNoteTitle) {
      return <NoteView noteTitle={selectedNoteTitle} onEdit={handleEditNote} onSelectNote={handleSelectNote} />;
    }
    return <DailyNote />;
  };

  return (
    <div className="App">
      <header className="App-header">
        <div>
          <h1 onClick={() => setViewMode('view')} style={{cursor: 'pointer'}}>LIFE</h1>
          <p>Your Second Brain, Connected.</p>
        </div>
        <nav>
          <a href="#" onClick={() => setViewMode('tasks')}>All Tasks</a>
        </nav>
      </header>
      <div className="app-container">
        <NoteList
          notes={notes}
          loading={loadingNotes}
          error={errorNotes}
          onSelectNote={handleSelectNote}
          onNewNote={handleNewNoteClick}
        />
        <main>
          {renderMainContent()}
        </main>
      </div>
    </div>
  );
}

export default App;