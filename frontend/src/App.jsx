import React, { useState } from 'react';
import DailyNote from './DailyNote';
import NoteList from './NoteList';
import NoteView from './NoteView';
import './App.css';

function App() {
  const [selectedNoteTitle, setSelectedNoteTitle] = useState(null);

  const handleSelectNote = (title) => {
    setSelectedNoteTitle(title);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>LIFE</h1>
        <p>Your Second Brain, Connected.</p>
      </header>
      <div className="app-container">
        <NoteList onSelectNote={handleSelectNote} />
        <main>
          {selectedNoteTitle ? (
            <NoteView noteTitle={selectedNoteTitle} />
          ) : (
            <DailyNote />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;