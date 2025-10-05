import React from 'react';
import WikiLink from '../WikiLink';

export const parseContent = (text, onLinkClick) => {
  if (!text) {
    return [];
  }

  const linkRegex = /\[\[(.*?)\]\]/g;
  const parts = text.split(linkRegex);

  // The parts array will look like: [ "text before", "link title", "text between", "another title", "text after" ]
  // We need to process it in chunks.

  const elements = [];
  let i = 0;
  while (i < parts.length) {
    // Plain text part
    if (parts[i]) {
      // To preserve line breaks from the original text, we need to wrap the text parts.
      // A simple way is to use a fragment with a <pre>-like style, or just let CSS handle it.
      // For now, let's just push the string and handle wrapping in the parent component.
      elements.push(parts[i]);
    }

    // Link title part
    const linkTitle = parts[i + 1];
    if (linkTitle) {
      elements.push(
        <WikiLink
          key={`${linkTitle}-${i}`}
          title={linkTitle}
          onClick={onLinkClick}
        />
      );
    }

    i += 2; // Move to the next chunk of (text, link)
  }

  return elements;
};