'use client';

interface ResearchHeaderProps {
  title?: string;
  author?: string;
}

export default function ResearchHeader({ 
  title = 'Kloud Cloud Research Series',
  author = 'Ledjan Ahmati'
}: ResearchHeaderProps) {
  return (
    <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border-b border-blue-500/20">
      <div className="max-w-7xl mx-auto px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-blue-400 text-sm font-medium">
              📚 {title}
            </span>
            <span className="text-slate-500">—</span>
            <span className="text-slate-400 text-sm">
              Authored by {author}
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="px-2 py-1 bg-slate-800 rounded">CC BY-NC-ND 4.0</span>
            <span>© 2026</span>
          </div>
        </div>
      </div>
    </div>
  );
}

