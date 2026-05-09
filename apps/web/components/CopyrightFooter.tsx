'use client';

import Link from 'next/link';

interface CopyrightFooterProps {
  showBrand?: boolean;
  className?: string;
}

export default function CopyrightFooter({ showBrand = true, className = '' }: CopyrightFooterProps) {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className={`border-t border-slate-700 bg-slate-900/50 ${className}`}>
      <div className="max-w-7xl mx-auto px-6 py-8">
        {showBrand && (
          <div className="text-center mb-4">
            <p className="text-sm font-medium text-blue-400">
              Kloud Cloud Research Series
            </p>
          </div>
        )}
        
        <div className="text-center text-slate-400 text-sm space-y-2">
          <p>
            © {currentYear} Ledjan Ahmati. All rights reserved.
          </p>
          <p className="text-slate-500">
            Unauthorized reproduction, distribution, or commercial use is strictly prohibited.
          </p>
          <div className="flex justify-center gap-4 mt-4">
            <Link 
              href="/terms" 
              className="text-slate-400 hover:text-white transition-colors"
            >
              Terms of Use
            </Link>
            <span className="text-slate-600">|</span>
            <Link 
              href="/privacy" 
              className="text-slate-400 hover:text-white transition-colors"
            >
              Privacy Policy
            </Link>
            <span className="text-slate-600">|</span>
            <a 
              href="https://creativecommons.org/licenses/by-nc-nd/4.0/" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-white transition-colors"
            >
              CC BY-NC-ND 4.0
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

