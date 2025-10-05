import React from 'react';

const WikiLink = ({ title, onClick }) => {
  const handleClick = (e) => {
    e.preventDefault(); // Prevent the default <a> tag behavior
    onClick(title);
  };

  return (
    <a href="#" onClick={handleClick} className="wiki-link">
      {title}
    </a>
  );
};

export default WikiLink;