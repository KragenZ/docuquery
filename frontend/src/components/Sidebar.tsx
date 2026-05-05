"use client";

import { Trash2, FileText } from "lucide-react";
import { deleteDocument } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Doc {
  id: string;
  filename: string;
  status: string;
}

interface Props {
  documents: Doc[];
  selectedIds: string[];
  onToggleSelect: (id: string) => void;
  onRefresh: () => void;
}

export default function Sidebar({ documents, selectedIds, onToggleSelect, onRefresh }: Props) {
  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation(); // prevent selecting when clicking delete
    try {
      await deleteDocument(id);
      onRefresh();
    } catch (err) {
      console.error("Failed to delete", err);
    }
  };

  return (
    <div className="w-64 glass border-r border-border h-screen flex flex-col hidden md:flex">
      <div className="p-6 border-b border-border">
        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-cyan-400">
          DocMind AI
        </h1>
        <p className="text-sm text-text-muted mt-1">Your personal knowledge base</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        <h2 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">
          Your Documents
        </h2>
        
        {documents.length === 0 ? (
          <p className="text-sm text-text-muted italic">No documents uploaded yet.</p>
        ) : (
          documents.map((doc) => {
            const isSelected = selectedIds.includes(doc.id);
            return (
              <div
                key={doc.id}
                onClick={() => onToggleSelect(doc.id)}
                className={cn(
                  "flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all",
                  isSelected ? "bg-primary/20 border border-primary/50" : "hover:bg-surface-hover border border-transparent"
                )}
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  <FileText className={cn("w-4 h-4 shrink-0", isSelected ? "text-primary" : "text-text-muted")} />
                  <span className="text-sm truncate text-text">{doc.filename}</span>
                </div>
                
                <button
                  onClick={(e) => handleDelete(e, doc.id)}
                  className="p-1 hover:bg-red-500/20 rounded text-text-muted hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                  style={{ opacity: 1 }} // kept it always visible for simplicity, styling later
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
