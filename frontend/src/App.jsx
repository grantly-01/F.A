import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Stats from './components/Stats'
import GrantCard from './components/GrantCard'
import { Loader2 } from 'lucide-react'

function App() {
  const [grants, setGrants] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  // URL бэкенда (проксируется через Vite или прямой CORS)
  const API_URL = 'http://127.0.0.1:8000';

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Загрузка статистики
        const statsRes = await fetch(`${API_URL}/stats`);
        const statsData = await statsRes.json();
        setStats(statsData);

        // Загрузка грантов
        const grantsRes = await fetch(`${API_URL}/grants`);
        const grantsData = await grantsRes.json();
        setGrants(grantsData);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Фильтрация на клиенте (для мгновенного поиска)
  const filteredGrants = grants.filter(grant => {
    const query = searchQuery.toLowerCase();
    return (
      grant.title.toLowerCase().includes(query) ||
      (grant.description && grant.description.toLowerCase().includes(query)) ||
      (grant.funder && grant.funder.toLowerCase().includes(query))
    );
  });

  return (
    <div className="min-h-screen pb-20">
      <Navbar onSearch={setSearchQuery} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-10">

        {/* Заголовок секции */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-4">
            Финансирование науки и бизнеса
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-secondary-400 mt-2">
              в Казахстане
            </span>
          </h1>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Агрегатор грантов, конкурсов и субсидий с использованием искусственного интеллекта.
          </p>
        </div>

        {/* Статистика */}
        {loading ? (
          <div className="flex justify-center py-20">
            <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
          </div>
        ) : (
          <>
            <Stats stats={stats} />

            <div className="flex items-center justify-between mb-8">
              <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                Актуальные предложения
                <span className="px-3 py-1 bg-dark-800 rounded-full text-xs text-slate-400 border border-slate-700">
                  {filteredGrants.length}
                </span>
              </h2>
            </div>

            {/* Сетка грантов */}
            {filteredGrants.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredGrants.map((grant) => (
                  <GrantCard key={grant.id} grant={grant} />
                ))}
              </div>
            ) : (
              <div className="text-center py-20 bg-dark-800/50 rounded-2xl border border-slate-800 border-dashed">
                <p className="text-slate-400 text-lg">По вашему запросу ничего не найдено.</p>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default App