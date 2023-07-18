import axios from 'axios';
import React, { useState } from 'react';
import { Button } from 'react-bootstrap';

const ChatBox = () => {
  const [pageId, setPageId] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

  const sendPageInfo = () => {
    axios
      .post('/api/aichat', {
        userInput: pageId,
      })
      .then(response => {
        console.log('Success:', response.data);
        const userQuestion = `Q: ${pageId}`;
        const aiResponse = `A: ${response.data.message}`;

        const newChatEntry = { user: userQuestion, ai: aiResponse };
        const updatedChatHistory = [...chatHistory, newChatEntry];
        const trimmedChatHistory = updatedChatHistory.slice(-5);

        setChatHistory(trimmedChatHistory);
        setPageId('');
      })
      .catch(error => {
        console.error('Error:', error);
      });
  };

  return (
    <div className="main-content">
      <h2 className="text-center">Chat with Kyll's Resume</h2>
      <div className="chatbox-div">
        <textarea
          className="textarea"
          readOnly
          value={chatHistory.map(entry => entry.user + '\n' + entry.ai).join('\n\n')} // Add two newline characters between each entry
        />
      </div>
      <div className="input-group">
        <input
          type="text"
          placeholder="What would you like to ask?"
          value={pageId}
          onChange={e => setPageId(e.target.value)}
        />
        <Button onClick={sendPageInfo}>Send Message</Button>
      </div>
    </div>
  );
};

export default ChatBox;