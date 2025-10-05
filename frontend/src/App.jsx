import React from 'react';
import DailyNote from './DailyNote';
import NoteList from './NoteList';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>LIFE</h1>
        <p>Your Second Brain, Connected.</p>
      </header>
      <div className="app-container">
        <NoteList />
        <main>
          <DailyNote />
        </main>
      </div>
    </div>
  );
}

export default App;