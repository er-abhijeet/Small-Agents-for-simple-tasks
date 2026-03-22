import React, { useState, useRef, useEffect } from 'react';

export default function App() {
  const [file, setFile] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  // Loading and engagement states
  const [isUploading, setIsUploading] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const [statusStep, setStatusStep] = useState('');
  
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, statusStep]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setStatusStep('Uploading document to secure server...');
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Simulate step progression for user engagement
      setTimeout(() => setStatusStep('Extracting text and chunking data...'), 1500);
      setTimeout(() => setStatusStep('Generating embeddings and building vector graph...'), 3000);

      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        setStatusStep('Knowledge base ready!');
        setMessages([{ role: 'system', content: `Document "${file.name}" ingested successfully. You can now ask questions.` }]);
      } else {
        const errorData = await response.json();
        alert(`Upload failed: ${errorData.error}`);
      }
    } catch (error) {
      alert(`Connection error: ${error.message}`);
    } finally {
      setTimeout(() => {
        setIsUploading(false);
        setStatusStep('');
      }, 2000);
    }
  };

  const handleQuery = async (e) => {
    e.preventDefault();
    if (!input.trim() || isQuerying) return;

    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsQuerying(true);
    setStatusStep('Retrieving relevant context from knowledge base...');

    try {
      setTimeout(() => setStatusStep('Synthesizing response via Gemini API...'), 1500);

      const response = await fetch('http://localhost:5000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: data.answer,
          citations: data.citations
        }]);
      } else {
        setMessages(prev => [...prev, { role: 'error', content: data.error }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'error', content: 'Failed to connect to backend.' }]);
    } finally {
      setIsQuerying(false);
      setStatusStep('');
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 font-sans">
      {/* Header */}
      <header className="bg-slate-900 text-white p-4 shadow-md flex justify-between items-center">
        <h1 className="text-xl font-bold tracking-tight">AI Research Assistant</h1>
        
        {/* Document Upload Section */}
        <div className="flex items-center space-x-3">
          <input 
            type="file" 
            accept=".pdf" 
            onChange={handleFileChange}
            className="text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-slate-800 file:text-white hover:file:bg-slate-700 cursor-pointer"
          />
          <button 
            onClick={handleUpload} 
            disabled={!file || isUploading}
            className="bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
          >
            {isUploading ? 'Processing...' : 'Build Knowledge Base'}
          </button>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto p-6 max-w-4xl w-full mx-auto">
        {messages.length === 0 && !isUploading && (
          <div className="h-full flex items-center justify-center text-gray-400">
            Upload a PDF document to begin.
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-6 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-4 rounded-lg shadow-sm ${
              msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 
              msg.role === 'system' ? 'bg-green-100 text-green-800 w-full text-center' :
              msg.role === 'error' ? 'bg-red-100 text-red-800' :
              'bg-white text-gray-800 border border-gray-200 rounded-bl-none'
            }`}>
              <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              
              {/* Citations Block */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-4 pt-3 border-t border-gray-100">
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Sources & Citations</p>
                  <div className="space-y-2">
                    {msg.citations.map((cite, i) => (
                      <div key={i} className="bg-gray-50 p-2 rounded text-xs border border-gray-100">
                        <span className="font-bold text-blue-600 mr-2">Page {cite.page}</span>
                        <span className="text-gray-600 italic">"...{cite.content.substring(0, 150)}..."</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {/* Dynamic Status Indicator */}
        {(isUploading || isQuerying) && (
          <div className="flex justify-start mb-4">
            <div className="bg-white border border-gray-200 text-gray-600 p-3 rounded-lg rounded-bl-none flex items-center space-x-3 shadow-sm">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-sm font-medium">{statusStep}</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </main>

      {/* Input Area */}
      <footer className="bg-white border-t border-gray-200 p-4">
        <div className="max-w-4xl mx-auto flex gap-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleQuery(e)}
            placeholder="Ask a question about the document..."
            disabled={isUploading || isQuerying || messages.length === 0}
            className="flex-1 border border-gray-300 rounded-md px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          />
          <button 
            onClick={handleQuery}
            disabled={!input.trim() || isUploading || isQuerying || messages.length === 0}
            className="bg-slate-900 hover:bg-slate-800 disabled:bg-gray-300 text-white px-6 py-3 rounded-md font-medium transition-colors"
          >
            Send
          </button>
        </div>
      </footer>
    </div>
  );
}