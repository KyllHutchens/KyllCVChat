import axios from 'axios';
import React, { useState } from 'react';
import { Button } from 'react-bootstrap';  // import Button from react-bootstrap

const ChatBox = () => {
  const [pageId, setPageId] = useState('');
  const [outputText, setOutputText] = useState('');  // New state for output text
  const [status, setStatus] = useState('');  // New state for status

  const sendPageInfo = () => {
    axios.post('/api/aichat', {
      userInput: pageId
    })
    .then(response => {
      console.log('Success:', response);
      setStatus(response.data.message); // Update status with response message
      setOutputText(response.data.message); // Update output text with server response
      setPageId(''); // Clear the text box
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  };

  return (
    <div className="main-content">
      <h2 className="text-center">Chat with your AI Calendar</h2>
      <div className ="chatbox-div">
        <textarea
          className="textarea"
          readOnly
          value={outputText}
        />
      </div>
      <div className="input-group">
        <input
          type="text"
          placeholder="What would you like to ask?"
          value={pageId}
          onChange={e => setPageId(e.target.value)}
        />
        <Button onClick={sendPageInfo}>Send Message</Button>  {/* Use Bootstrap Button */}
      </div>
    </div>
  );
};

export default ChatBox;