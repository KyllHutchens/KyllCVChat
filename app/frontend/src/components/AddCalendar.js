import React, { useState } from 'react';
import axios from 'axios';

function AddCalendar() {
    const [name, setName] = useState('');
    const [id, setId] = useState('');
    const [message, setMessage] = useState('');
  
    const handleSubmit = (event) => {
      event.preventDefault();
      const data = {
        name,
        id
      };
    
    axios.post('/api/add_calendar', data)
      .then(res => {
        console.log(res);
        setMessage("Calendar added successfully!");
        setName(''); 
        setId(''); 
      })
      .catch(err => {
        console.error(err);
      });
  };

  return (
    <div>
      {message && <div className="alert alert-success">{message}</div>} 
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Calendar Name</label>
          <input type="text" className="form-control" value={name} onChange={e => setName(e.target.value)} />
        </div>
        <div className="form-group">
          <label>Calendar ID</label>
          <input type="text" className="form-control" value={id} onChange={e => setId(e.target.value)} />
        </div>
        <button type="submit" className="btn btn-primary">Add Calendar</button>
      </form>
    </div>
  );

  }
export default AddCalendar;