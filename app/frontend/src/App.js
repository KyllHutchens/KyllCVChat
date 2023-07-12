import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import axios from 'axios';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatBox from './components/ChatBox'; 
import AddCalendar from './components/AddCalendar'; 
import './App.css';
function App() {
useEffect(() => {
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

  axios.post('/api/set_timezone', { timezone })  // make a POST request to '/api/set_timezone' with the timezone
    .then(response => {
      console.log(response.data);
      console.log(response.status);

    })
    .catch(error => {
      console.error(error);
    });
}, []);




  return (
    <Router>
      <Header />
      <div className="container-fluid">
        <div className="row">
          <Sidebar />
          <main className="col-md-9 ml-sm-auto col-lg-10 px-md-4">
            <Routes>
              <Route path="/" element={<ChatBox />} />
              <Route path="/add-calendar" element={<AddCalendar />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;