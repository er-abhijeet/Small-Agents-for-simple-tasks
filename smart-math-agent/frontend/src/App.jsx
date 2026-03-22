// import './App.css'
// import {useState} from 'react'

// function App() {

//   const [tasks,setTasks]=useState([]);
//   const [newTask, setNewTask]=useState("");
//   const [key,setKey]=useState(1);
//   const [editId,setEditId]=useState(null);
  
//   const handleAdd = () => {
//     if(newTask=="")return;
//     if(!editId){
//       setTasks([...tasks,{task:newTask,key:key}]);
//       setKey(key+1);
//     }else{
//       setTasks(
//         tasks.map((task)=>
//           task.key==editId?{...task,task:newTask}:task
//         )
//       );
//       setEditId(null);
//     }
//     setNewTask("");
//   }
//   const handleDelete = (e) => {
//     setTasks(tasks.filter((task)=>e!=task.key))
//   }
//   const handleEdit = (e) => {
//     setNewTask(tasks.find(k=>k.key==e).task);
//     // handleDelete(e);
//     setEditId(e);    
//   }

//   return (
//     <>
//       <div>
//         <h1>
//           TO DO
//         </h1>
//         <input type="text" value={newTask} onChange={(e)=>setNewTask(e.target.value)}/>
//         <button onClick={handleAdd}>add task</button>
//         <div>
//           <ul>            
//             {tasks.map((task,index)=>
//               (
//               <li key={task.key}>{task.task}
//               <button onClick={()=>handleDelete(task.key)}>delete</button>
//               <button onClick={()=>handleEdit(task.key)}>Edit</button>
//               </li>
//               )
//             )}
//           </ul>
//         </div>
//       </div>
//     </>
//   )
// }

// export default App



import React, { useState, useEffect } from 'react';
import { Send, Terminal } from 'lucide-react';

const AgentChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');

  // Simulating pipeline steps to keep user engaged during the synchronous API call
  const loadingMessages = [
    "Analyzing query...",
    "Drafting optimal Python code...",
    "Enforcing hardcoded constraints...",
    "Sending script to execution server...",
    "Awaiting output..."
  ];

  useEffect(() => {
    let interval;
    if (isProcessing) {
      let stepIndex = 0;
      setLoadingStep(loadingMessages[0]);
      interval = setInterval(() => {
        stepIndex++;
        if (stepIndex < loadingMessages.length) {
          setLoadingStep(loadingMessages[stepIndex]);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [isProcessing]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userQuery = input;
    setMessages(prev => [...prev, { role: 'user', content: userQuery }]);
    setInput('');
    setIsProcessing(true);

    try {
      const response = await fetch('http://localhost:5001/api/agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userQuery })
      });

      const data = await response.json();

      if (!response.ok) {
        setMessages(prev => [...prev, { 
          role: 'system', 
          error: true,
          content: `Error: ${data.error || 'Unknown error'}\nDetails: ${data.details || data.output || ''}` 
        }]);
      } else {
        setMessages(prev => [...prev, { 
          role: 'agent', 
          code: data.generated_code,
          output: data.output 
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'system', 
        error: true,
        content: `Network error: Failed to reach the backend.${error}` 
      }]);
    } finally {
      setIsProcessing(false);
      setLoadingStep('');
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto p-4 bg-gray-50">
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map((msg, index) => (
          <div key={index} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`p-4 rounded-lg max-w-[85%] ${
              msg.role === 'user' ? 'bg-blue-600 text-white' : 
              msg.error ? 'bg-red-100 text-red-800 border border-red-300' : 
              'bg-white border border-gray-200 shadow-sm'
            }`}>
              {msg.role === 'user' ? (
                <span>{msg.content}</span>
              ) : msg.error ? (
                <pre className="whitespace-pre-wrap font-mono text-sm">{msg.content}</pre>
              ) : (
                <div className="space-y-3 w-full">
                  <div className="bg-gray-900 rounded p-3">
                    <div className="flex items-center text-xs text-gray-400 mb-2 pb-2 border-b border-gray-700">
                      <Terminal size={14} className="mr-2" />
                      Generated Code
                    </div>
                    <pre className="text-gray-100 font-mono text-sm overflow-x-auto">
                      {msg.code}
                    </pre>
                  </div>
                  <div className="bg-black rounded p-3">
                    <div className="text-xs text-green-500 mb-1">Execution Output:</div>
                    <pre className="text-white font-mono text-sm overflow-x-auto">
                      {msg.output}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isProcessing && (
          <div className="flex items-center space-x-3 text-gray-500 p-4">
            <div className="animate-spin h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full"></div>
            <span className="text-sm font-medium animate-pulse">{loadingStep}</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the agent to solve a problem..."
          disabled={isProcessing}
          className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
        <button 
          type="submit" 
          disabled={isProcessing}
          className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:bg-blue-300 flex items-center justify-center min-w-[3rem]"
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default AgentChatbot;