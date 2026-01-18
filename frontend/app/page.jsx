"use client";

import { useState, useRef, useEffect } from "react";
import { cloneRepo, askQuestionStream } from "@/lib/api";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isRepoCloned, setIsRepoCloned] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages, currentAnswer]);

  async function handleCloneRepo() {
    setLoading(true);
    try {
      console.log("Cloning repo:", repoUrl);
      const data = await cloneRepo(repoUrl);
      console.log("Clone response:", data);
      console.log("Setting sessionId:", data.session_id);
      setSessionId(data.session_id);
      setIsRepoCloned(true);
      setMessages([
        {
          role: "assistant",
          content: `Repository cloned successfully! You can now ask questions about the codebase.`,
          timestamp: new Date().toISOString()
        }
      ]);
    } catch (error) {
      console.error("Error cloning repo:", error);
      setMessages([
        {
          role: "assistant",
          content: `Error cloning repository: ${error.message}`,
          timestamp: new Date().toISOString()
        }
      ]);
    }
    setLoading(false);
  }

  async function handleAsk() {
    console.log("handleAsk called - sessionId:", sessionId, "question:", `"${question}"`, "question.trim():", `"${question.trim()}"`);
    
    if (!sessionId) {
      console.log("Early return - missing sessionId:", sessionId);
      return;
    }
    
    if (!question.trim()) {
      console.log("Early return - empty question:", `"${question}"`);
      return;
    }

    // Add user message
    const userMessage = {
      role: "user",
      content: question,
      timestamp: new Date().toISOString()
    };
    
    console.log("Adding user message:", userMessage);
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    setCurrentAnswer("");

    const currentQuestion = question;
    setQuestion(""); // Clear immediately to prevent re-submission

    try {
      console.log("Starting stream...");
      let fullAnswer = "";
      await askQuestionStream(sessionId, currentQuestion, (token) => {
        console.log("Received token:", token);
        fullAnswer += token;
        console.log("Full answer so far:", fullAnswer);
        setCurrentAnswer(fullAnswer);
      });
      
      console.log("Stream completed, final answer:", fullAnswer);
      // Add assistant message when streaming is complete
      setMessages(prev => [...prev, {
        role: "assistant",
        content: fullAnswer,
        timestamp: new Date().toISOString()
      }]);
      
    } catch (err) {
      console.error("Error asking question:", err);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: `Error: ${err.message}`,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      console.log("Cleaning up...");
      setCurrentAnswer("");
      setLoading(false);
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  return (
    <main className="min-h-screen bg-gray-50">
      {!isRepoCloned ? (
        <div className="min-h-screen flex items-center justify-center p-6">
          <Card className="w-full max-w-md p-6 space-y-4">
            <h1 className="text-2xl font-bold text-center">RepoLens</h1>
            <p className="text-sm text-gray-600 text-center">
              Clone a repository to start asking questions about the codebase
            </p>
            <Input
              placeholder="GitHub Repository URL"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleCloneRepo()}
            />
            <Button
              onClick={handleCloneRepo}
              disabled={loading || !repoUrl.trim()}
              className="w-full"
            >
              {loading ? "Cloning Repository..." : "Clone Repository"}
            </Button>
          </Card>
        </div>
      ) : (
        <div className="flex flex-col h-screen">
          {/* Header */}
          <div className="bg-white border-b px-6 py-4 flex justify-between items-center">
            <div>
              <h1 className="text-xl font-bold">RepoLens</h1>
              <p className="text-sm text-gray-600">{repoUrl}</p>
            </div>
            <Button
              variant="outline"
              onClick={() => {
                setIsRepoCloned(false);
                setRepoUrl("");
                setQuestion("");
                setMessages([]);
                setCurrentAnswer("");
                setSessionId(null);
              }}
            >
              New Repository
            </Button>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message, index) => (
              <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[70%] rounded-lg p-4 ${
                  message.role === 'user' 
                    ? 'bg-blue-500 text-white ml-4' 
                    : 'bg-white border shadow-sm mr-4'
                }`}>
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  <div className={`text-xs mt-2 opacity-70`}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            
            {/* Show streaming response */}
            {loading && currentAnswer && (
              <div className="flex justify-start">
                <div className="max-w-[70%] rounded-lg p-4 bg-white border shadow-sm mr-4">
                  <div className="whitespace-pre-wrap">{currentAnswer}</div>
                  <div className="text-xs mt-2 opacity-70">
                    Thinking...
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="bg-white border-t p-4">
            <div className="flex gap-2 max-w-4xl mx-auto">
              <Input
                placeholder="Ask about the codebase..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={loading}
                className="flex-1"
              />
              <Button
                onClick={(e) => {
                  console.log("Button clicked - sessionId:", sessionId, "question:", `"${question}"`, "loading:", loading);
                  e.preventDefault();
                  handleAsk();
                }}
                disabled={loading || !question.trim()}
                type="button"
              >
                {loading ? "..." : "Ask"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
