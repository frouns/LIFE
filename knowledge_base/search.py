import os
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh.highlight import Highlighter, HtmlFormatter

# Define the schema for the search index
# TEXT is for full-text search, ID is for unique identifiers
SEARCH_SCHEMA = Schema(
    title=ID(stored=True, unique=True),
    content=TEXT(stored=True)
)

def get_search_index(index_dir: str = "search_index"):
    """
    Opens an existing Whoosh index or creates a new one.
    """
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
        return create_in(index_dir, SEARCH_SCHEMA)

    # If the index exists but is empty/corrupted, open_dir might fail.
    # A more robust solution could handle this, but for now, we assume it's valid.
    try:
        return open_dir(index_dir)
    except Exception:
        # If opening fails, it might be an empty directory. Try creating again.
        return create_in(index_dir, SEARCH_SCHEMA)

def add_note_to_index(index, note):
    """
    Adds a single note to the search index.
    The writer is a transactional object for adding/updating documents.
    """
    writer = index.writer()
    writer.update_document(
        title=note.title,
        content=note.content
    )
    writer.commit()

def search_notes(index, query_str: str):
    """
    Searches the index for a given query string.
    """
    # Use QueryParser to understand the user's query
    with index.searcher() as searcher:
        parser = QueryParser("content", index.schema)
        query = parser.parse(query_str)

        results = searcher.search(query, limit=10)

        # Use a highlighter to create contextual snippets
        highlighter = Highlighter(formatter=HtmlFormatter(tagname="mark"))

        # Format the results
        formatted_results = []
        for hit in results:
            # The 'content' field was stored, so we can access it.
            snippet = highlighter.highlight_hit(hit, "content")
            formatted_results.append({
                "title": hit["title"],
                "snippet": snippet,
                "score": hit.score,
            })

        return formatted_results