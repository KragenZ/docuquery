"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import UploadZone from "@/components/UploadZone";
import MessageBubble from "@/components/MessageBubble";
import { getDocuments, queryDocuments } from "@/lib/api";
import { Send, LayoutTemplate } from "lucide-react";

export default function ChatInterface() {
  const [docs, setDocs] = useState([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [messages, setMessages] = useState<{role: string, content: string, citations?: any[]}[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();

  const loadDocs = async () => {
    try {
      const data = await getDocuments();
      setDocs(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const toggleSelect = (id: string) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const handleSend = async () => {
    if (!input.trim() || selectedIds.length === 0) return;
    
    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const compareMode = selectedIds.length > 1;
      const res = await queryDocuments(userMsg, selectedIds, sessionId, compareMode);
      
      setSessionId(res.session_id);
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: res.answer,
        citations: res.citations 
      }]);
    } catch (e: any) {
      const errorMsg = e.response?.data?.detail || "An error occurred.";
      setMessages(prev => [...prev, { role: "assistant", content: `Error: ${errorMsg}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Sidebar 
        documents={docs} 
        selectedIds={selectedIds} 
        onToggleSelect={toggleSelect} 
        onRefresh={loadDocs}
      />
      
      <main className="flex-1 flex flex-col h-full relative">
        {/* Header (mobile friendly) */}
        <header className="p-4 border-b border-border glass z-10 flex items-center justify-between md:hidden">
          <h1 className="text-lg font-bold text-primary">DocMind AI</h1>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 scroll-smooth">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center max-w-xl mx-auto w-full gap-8">
              <div className="text-center space-y-2">
                <LayoutTemplate className="w-12 h-12 text-primary mx-auto opacity-50 mb-4" />
                <h2 className="text-2xl font-bold text-text">Welcome to DocMind</h2>
                <p className="text-text-muted">Upload a PDF and ask questions to get started.</p>
              </div>
              
              <div className="w-full">
                <UploadZone onUploadSuccess={loadDocs} />
              </div>

              {docs.length > 0 && selectedIds.length === 0 && (
                <div className="p-4 border border-yellow-500/30 bg-yellow-500/10 rounded-lg text-sm text-yellow-200">
                  Select at least one document from the sidebar to start chatting.
                </div>
              )}
            </div>
          ) : (
            <div className="max-w-3xl mx-auto pb-32">
              {messages.map((m, i) => (
                <MessageBubble key={i} role={m.role as any} content={m.content} citations={m.citations} />
              ))}
              {loading && (
                <MessageBubble role="assistant" content="Thinking..." />
              )}
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-background via-background to-transparent">
          <div className="max-w-3xl mx-auto relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSend()}
              placeholder={selectedIds.length === 0 ? "Select a document first..." : "Ask a question..."}
              disabled={selectedIds.length === 0 || loading}
              className="w-full bg-surface-hover border border-border rounded-xl py-4 pl-4 pr-12 text-text placeholder:text-text-muted focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all disabled:opacity-50"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || selectedIds.length === 0 || loading}
              className="absolute right-2 p-2 bg-primary hover:bg-primary-hover text-white rounded-lg transition-colors disabled:opacity-50 disabled:hover:bg-primary"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <div className="text-center mt-2">
            <span className="text-[10px] text-text-muted">DocMind AI can make mistakes. Verify important information.</span>
          </div>
        </div>
      </main>
    </div>
  );
}
