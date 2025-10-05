import React, { useState, useEffect } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import apiClient from '../api';

const CalendarView = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuthStatusAndFetchEvents = async () => {
      try {
        // First, check if the user is authenticated with our backend
        await apiClient.get('/api/users/me');

        // If that succeeds, we know we have a session.
        // Now, let's try to fetch calendar events.
        // The backend will handle checking for Google credentials.
        const today = new Date();
        const startDate = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0];
        const endDate = new Date(today.getFullYear(), today.getMonth() + 1, 0).toISOString().split('T')[0];

        const response = await apiClient.get(`/api/calendar/events?start_date=${startDate}&end_date=${endDate}`);

        const formattedEvents = response.data.map(event => ({
          title: event.summary,
          start: event.start.dateTime || event.start.date,
          end: event.end.dateTime || event.end.date,
          id: event.id,
        }));

        setEvents(formattedEvents);
        setIsAuthenticated(true);
      } catch (error) {
        // A 401 from /api/users/me or a 403 from /api/calendar/events means not authenticated with Google.
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
          setIsAuthenticated(false);
        } else {
          console.error("An error occurred:", error);
        }
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatusAndFetchEvents();
  }, []);

  if (loading) {
    return <div>Loading Calendar...</div>;
  }

  if (!isAuthenticated) {
    return (
      <div style={{ textAlign: 'center', marginTop: '50px' }}>
        <h2>Connect Your Calendar</h2>
        <p>To use the scheduling features, please connect your Google Calendar account.</p>
        <a href="/api/auth/google/authorize" className="button">
          Connect Google Calendar
        </a>
      </div>
    );
  }

  return (
    <div className="calendar-container">
      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="dayGridMonth"
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,timeGridDay'
        }}
        events={events}
      />
    </div>
  );
};

export default CalendarView;