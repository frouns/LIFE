import React from 'react';
import DailyNote from './DailyNote';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>LIFE</h1>
        <p>Your Second Brain, Connected.</p>
      </header>
      <main>
        <DailyNote />
      </main>
    </div>
  );
}

export default App;