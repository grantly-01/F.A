import React from 'react';
import { Rocket, Search } from 'lucide-react';

const Navbar = ({ onSearch }) => {
  return (
    <nav className="sticky top-0 z-50 backdrop-blur-lg border-b border-slate-800/60 bg-dark-900/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">

          {/* Логотип */}
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-primary-600 to-secondary-500 rounded-lg shadow-[0_0_15px_rgba(168,85,247,0.5)]">
              <Rocket className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">
              Grant<span className="text-primary-400">Hub</span>.kz
            </span>
          </div>

          {/* Поиск */}
          <div className="hidden md:flex flex-1 max-w-md mx-8 relative group">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-slate-500 group-focus-within:text-primary-400 transition-colors" />
            </div>
            <input
              type="text"
              onChange={(e) => onSearch(e.target.value)}
              className="block w-full pl-10 pr-3 py-2.5 bg-dark-800/50 border border-slate-700 rounded-xl leading-5 text-slate-300 placeholder-slate-500 focus:outline-none focus:bg-dark-800 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 sm:text-sm transition-all shadow-inner"
              placeholder="Поиск грантов, фондов..."
            />
          </div>

          {/* Кнопка (можно подключить логин позже) */}
          <button className="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-sm font-medium transition-all hover:text-white hover:border-secondary-500 hover:shadow-[0_0_10px_rgba(34,211,238,0.3)]">
            Войти
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;