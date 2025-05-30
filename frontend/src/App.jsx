import { useState } from 'react';
import axios from 'axios';
import './App.css';
import ReactMarkdown from 'react-markdown';

function App() {
  const [userInput, setUserInput] = useState('');
  const [role, setRole] = useState('Finance');
  const [region, setRegion] = useState('Global');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/query/', {
        user_input: userInput,
        user_role: role,
        region: region,
      });
      setResponse(res.data);
    } catch (err) {
      setResponse({ type: 'error', message: err.message });
    }
    setLoading(false);
  };

  return (
    <div className="app">
      <h1>AI Supply Chain Assistant</h1>
      <textarea
        rows="4"
        placeholder="Ask a question..."
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
      />
      <div className="controls">
        <select value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="Finance">Finance</option>
          <option value="Planner">Planner</option>
          <option value="Manager">Manager</option>
        </select>
        <select value={region} onChange={(e) => setRegion(e.target.value)}>
          <option value="India">India</option>
          <option value="Global">Global</option>
        </select>
        <button onClick={handleQuery} disabled={loading}>
          {loading ? 'Loading...' : 'Ask'}
        </button>
      </div>

      {response && (
        <div className="response">
          <h2>Response</h2>
          {response.type === 'doc' && (
            <div className="markdown">
              <ReactMarkdown>{response.answer}</ReactMarkdown>
            </div>
          )}
          {response.type === 'data' && (
            <table>
              <thead>
                <tr>
                  {Object.keys(response.data[0] || {}).map((key) => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {response.data.map((row, i) => (
                  <tr key={i}>
                    {Object.values(row).map((val, j) => (
                      <td key={j}>{val}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {response.type === 'hybrid' && (
            <>
              <p><strong>Definition:</strong> {response.definition}</p>
              <table>
                <thead>
                  <tr>
                    {Object.keys(response.data[0] || {}).map((key) => (
                      <th key={key}>{key}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {response.data.map((row, i) => (
                    <tr key={i}>
                      {Object.values(row).map((val, j) => (
                        <td key={j}>{val}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
          {response.type === 'error' && <p className="error">{response.message}</p>}
        </div>
      )}
    </div>
  );
}

export default App;