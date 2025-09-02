import React, { useState } from 'react';
import './App.css';

function App() {
  const [videoUrl, setVideoUrl] = useState('');
  const [videoTitle, setVideoTitle] = useState('');
  const [videoId, setVideoId] = useState('');
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [videoSaved, setVideoSaved] = useState(false);

  const handleSaveVideo = async (e) => {
    e.preventDefault();
    if (!videoUrl || !videoTitle) return;
    setLoading(true);
    try {
      const match = videoUrl.match(/[?&]v=([^&#]+)/);
      const extractedId = match ? match[1] : '';

      if (!extractedId) throw new Error('Invalid YouTube URL');
      const response = await fetch('http://localhost:8000/videos/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: videoTitle, url: videoUrl }),
      });

      const data = await response.json();

      if (data && data.video && data.video.id) {
        setVideoId(data.video.id);
        console.log('Saved video_id:', data.video.id);
        setVideoSaved(true);
        setMessages((prev) => [...prev, { role: 'bot', text: 'Video saved! You can now ask a question.' }]);
      } else {
        setMessages((prev) => [...prev, { role: 'bot', text: 'Error: No video ID returned from backend.' }]);
      }
    } catch {
      setMessages((prev) => [...prev, { role: 'bot', text: 'Error saving video.' }]);
    }
    setLoading(false);
  };

  const handleAskQuestion = async (e) => {
    e.preventDefault();

    if (!videoId || !question) return;

    setLoading(true);
    setMessages((prev) => [...prev, { role: 'user', text: question }]);

    try {
      const payload = { video_id: String(videoId), question_text: question };
      console.log('Sending question payload:', payload);

      const response = await fetch('http://localhost:8000/questions/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      console.log('Response status:', response.status);

      const responseText = await response.text();
      console.log('Raw response text:', responseText);

      let data = {};

      try {
        data = JSON.parse(responseText);
      } catch (err) {
        console.log('Error parsing response JSON:', err);
      }
      setMessages((prev) => [...prev, { role: 'bot', text: data.answer?.answer_text || 'No answer received.' }]);
    } catch {
      setMessages((prev) => [...prev, { role: 'bot', text: 'Error fetching answer.' }]);
    }
    setQuestion('');
    setLoading(false);
  };

  return (
    <div className="app-container">
      <img src="/logo_dark.png" alt="App Logo" style={{ width: '120px', marginBottom: '1rem' }} />
      <div className="header">YouTube Q&A</div>
      <div className="chat-box">
        {videoUrl && (
          <div style={{ fontSize: '0.9em', color: '#d10000', marginBottom: '0.5em' }}>
            <span style={{ fontWeight: 'bold' }}>Video:</span> {videoUrl}
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={msg.role === 'user' ? 'user-message' : 'bot-message'}>
            {msg.text}
          </div>
        ))}
      </div>
      {!videoSaved ? (
        <form className="input-bar" onSubmit={handleSaveVideo} autoComplete="off">
          <input
            type="text"
            placeholder="Video Title"
            value={videoTitle}
            onChange={e => setVideoTitle(e.target.value)}
            style={{ maxWidth: '30%' }}
            required
          />
          <input
            type="text"
            placeholder="YouTube Video URL"
            value={videoUrl}
            onChange={e => setVideoUrl(e.target.value)}
            style={{ maxWidth: '40%' }}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? '...' : 'Save Video'}
          </button>
        </form>
      ) : (
        <>
          <form className="input-bar" onSubmit={handleAskQuestion} autoComplete="off">
            <input
              type="text"
              placeholder="Ask a question..."
              value={question}
              onChange={e => setQuestion(e.target.value)}
              required
            />
            <button type="submit" disabled={loading}>
              {loading ? '...' : 'Send'}
            </button>
          </form>
          <button
            style={{ marginTop: '1em', background: '#d10000', color: 'white', padding: '0.5em 1em', border: 'none', borderRadius: '4px' }}
            disabled={loading}
            onClick={async () => {
              setLoading(true);
              try {
                const response = await fetch(`http://localhost:8000/videos/${videoId}`, {
                  method: 'DELETE',
                });
                const result = await response.text();
                console.log('Delete response:', result);
                setMessages([]);
                setVideoSaved(false);
                setVideoId('');
                setVideoUrl('');
                setVideoTitle('');
              } catch {
                setMessages((prev) => [...prev, { role: 'bot', text: 'Error deleting video.' }]);
              }
              setLoading(false);
            }}
          >
            Delete Video
          </button>
        </>
      )}
    </div>
  );
}

export default App;
