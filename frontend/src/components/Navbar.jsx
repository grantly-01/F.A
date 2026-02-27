import React from 'react';
import { Rocket, Search } from 'lucide-react';

const Navbar = ({ onSearch }) => {
  return (
    <nav className="sticky top-0 z-50 backdrop-blur-md bg-[#0b0f19]/70 border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-20">

          {/* Логотип */}
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-slate-800 border border-slate-700">
              <Rocket className="w-5 h-5 text-blue-400" />
            </div>

            <span className="text-xl font-semibold tracking-tight text-white">
              GrantHub<span className="text-blue-400">.kz</span>
            </span>
          </div>

          {/* Поиск */}
          <div className="hidden md:flex flex-1 max-w-md mx-10 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-slate-500" />
            </div>

            <input
              type="text"
              onChange={(e) => onSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition"
              placeholder="Поиск грантов..."
            />
          </div>

          {/* Кнопка */}
          <button className="px-5 py-2.5 rounded-xl bg-blue-500 hover:bg-blue-600 text-sm font-medium transition">
            Войти
          </button>

        </div>
      </div>
    </nav>
  );
};

export default Navbar;