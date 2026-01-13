import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <h1>Chatbot Widget Test Site</h1>
      <p>Running on port 3000</p>
      Add iframe here
      {/* <iframe
        src={`http://localhost:3000/embed/325606cb-3e80-4815-8190-20afe12537e0`}
        width="400"
        height="600"
        style={{
          border: 0,
          width: '100%',
          minWidth: '320px',
          minHeight: '420px',
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          zIndex: 9999,
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }}
        title="Chatbot"
      /> */}
      <div className="card">
        <h2>Widget Testing Instructions</h2>
        <p>
          The chatbot widget is embedded using the code from the Install tab.
        </p>
        <p>
          <strong>To test with your chatbot:</strong>
        </p>
        <ol style={{ textAlign: 'left', maxWidth: '600px', margin: '0 auto' }}>
          <li>Go to your chatbot dashboard → <strong>Install</strong> tab</li>
          <li>Copy your <strong>chatbot ID</strong> from the embed code</li>
          <li>Open <code>test/index.html</code> in your editor</li>
          <li>Replace <code>YOUR_CHATBOT_ID_HERE</code> with your actual chatbot ID</li>
          <li>Make sure Docker services are running:
            <ul style={{ marginTop: '5px' }}>
              <li>Widget service on port 3001</li>
              <li>API service on port 8000</li>
            </ul>
          </li>
          <li>Refresh this page - the widget should appear in the bottom-right corner</li>
        </ol>
        <p style={{ marginTop: '20px' }}>
          <strong>Embed Code Used (matches Install tab format):</strong>
        </p>
        <pre style={{ 
          background: '#f5f5f5', 
          padding: '15px', 
          borderRadius: '4px',
          textAlign: 'left',
          maxWidth: '700px',
          margin: '0 auto',
          fontSize: '12px',
          overflow: 'auto'
        }}>
        </pre>
        <p style={{ marginTop: '15px', fontSize: '14px', color: '#666' }}>
          <strong>Note:</strong> This embed code matches the format shown in the Install tab. 
          The widget will automatically fetch appearance settings (colors, position, etc.) from your dashboard.
        </p>
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
      </div>
    </div>
  )
}

export default App
