import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DailyNote from './DailyNote';
import NoteList from './NoteList';
import NoteView from './NoteView';
import NoteEditor from './NoteEditor';
import './App.css';

function App() {
  const [notes, setNotes] = useState([]);
  const [loadingNotes, setLoadingNotes] = useState(true);
  const [errorNotes, setErrorNotes] = useState(null);
  const [selectedNoteTitle, setSelectedNoteTitle] = useState(null);
  const [viewMode, setViewMode] = useState('view'); // 'view', 'create'

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
    fetchNotes();
  }, []);

  const handleSelectNote = (title) => {
    setSelectedNoteTitle(title);
    setViewMode('view');
  };

  const handleNewNoteClick = () => {
    setSelectedNoteTitle(null);
    setViewMode('create');
  };

  const handleSaveNote = async (noteData) => {
    try {
      await axios.post('http://localhost:8000/api/notes', noteData);
      await fetchNotes(); // Refresh the note list
      handleSelectNote(noteData.title); // Select the new note
    } catch (error) {
      console.error('Failed to save note:', error);
      alert('Error: Could not save the note. Please check the console for details.');
    }
  };

  const renderMainContent = () => {
    if (viewMode === 'create') {
      return <NoteEditor onSave={handleSaveNote} />;
    }

    if (selectedNoteTitle) {
      return <NoteView noteTitle={selectedNoteTitle} />;
    }

    return <DailyNote />;
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>LIFE</h1>
        <p>Your Second Brain, Connected.</p>
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