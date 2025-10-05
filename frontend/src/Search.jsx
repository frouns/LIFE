import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Search = ({ onSelectNote }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Don't search on an empty query
    if (query.trim() === '') {
      setResults([]);
      return;
    }

    // Set a timer to wait for the user to stop typing
    const timerId = setTimeout(() => {
      setLoading(true);
      axios.get(`http://localhost:8000/api/search?q=${query}`)
        .then(response => {
          setResults(response.data);
        })
        .catch(error => {
          console.error("Search failed:", error);
          // Optionally, set an error state to show in the UI
        })
        .finally(() => {
          setLoading(false);
        });
    }, 300); // 300ms debounce delay

    // Cleanup function to clear the timer if the user types again
    return () => {
      clearTimeout(timerId);
    };
  }, [query]);

  const handleResultClick = (title) => {
    // Use the onSelectNote function passed from App.jsx to switch views
    onSelectNote(title);
    setQuery(''); // Clear the search bar after selection
    setResults([]);
  };

  return (
    <div className="search-container">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search notes..."
        className="search-input"
      />
      {loading && <div>Searching...</div>}
      {results.length > 0 && (
        <ul className="search-results">
          {results.map((result) => (
            <li key={result.title} onClick={() => handleResultClick(result.title)}>
              <div className="result-title">{result.title}</div>
              <div
                className="result-snippet"
                dangerouslySetInnerHTML={{ __html: result.snippet }}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Search;