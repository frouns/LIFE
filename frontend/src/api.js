import axios from 'axios';

// Create an axios instance with a pre-configured base URL.
// Vite exposes environment variables on the `import.meta.env` object.
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
});

export default apiClient;