"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, BookOpen } from "lucide-react";
import { cn } from "@/lib/utils";

interface Citation {
  source: string;
  page_number: int;
  excerpt: string;
}

interface Props {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}

export default function MessageBubble({ role, content, citations }: Props) {
  const isUser = role === "user";

  return (
    <div className={cn("flex w-full mb-6", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[85%] rounded-2xl p-5",
          isUser
            ? "bg-primary text-white rounded-tr-sm"
            : "glass rounded-tl-sm"
        )}
      >
        <div className="prose prose-invert max-w-none text-sm leading-relaxed whitespace-pre-wrap">
          {content}
        </div>

        {!isUser && citations && citations.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {citations.map((c, i) => (
              <CitationCard key={i} citation={c} index={i + 1} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function CitationCard({ citation, index }: { citation: Citation; index: number }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border border-border/50 rounded-lg overflow-hidden bg-background/50 max-w-full">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 p-2 text-xs text-text-muted hover:text-text hover:bg-surface-hover w-full transition-colors"
      >
        <span className="flex items-center justify-center bg-primary/20 text-primary rounded-full w-4 h-4 text-[10px] font-bold">
          {index}
        </span>
        <BookOpen className="w-3 h-3" />
        <span className="truncate">{citation.source} (p.{citation.page_number})</span>
        {open ? <ChevronUp className="w-3 h-3 ml-auto" /> : <ChevronDown className="w-3 h-3 ml-auto" />}
      </button>
      
      {open && (
        <div className="p-3 text-xs text-text-muted border-t border-border/50 bg-black/20 italic">
          "{citation.excerpt}..."
        </div>
      )}
    </div>
  );
}
