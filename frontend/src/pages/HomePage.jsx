import { useEffect, useState } from "react";
import Stats from "../components/Stats";
import GrantCard from "../components/GrantCard";
import { Loader2 } from "lucide-react";
import { getGrants, getStats, collectFull } from "../api";

export default function HomePage({ searchValue }) {
  const [grants, setGrants] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const s = await getStats();
      setStats(s);

      const g = await getGrants(searchValue);
      setGrants(g);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    const t = setTimeout(() => {
      getGrants(searchValue).then(setGrants).catch(() => setGrants([]));
    }, 250);
    return () => clearTimeout(t);
  }, [searchValue]);

  const handleCollectClick = async () => {
    setLoading(true);
    try {
      await collectFull();
      await loadData();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#070b14] text-white">
      <main className="max-w-7xl mx-auto px-6 pt-16 pb-24">
        {/* Hero */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight mb-4">
            GrantHub.kz
          </h1>

          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Платформа мониторинга грантов и конкурсов в Казахстане.
          </p>

          <div className="flex justify-center mt-8">
            <button
              onClick={handleCollectClick}
              disabled={loading}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-500 hover:bg-blue-600 disabled:opacity-60 disabled:cursor-not-allowed text-sm font-medium transition"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Обновляем данные...
                </>
              ) : (
                <>
                  <Loader2 className="w-4 h-4" />
                  Обновить данные (запустить парсинг)
                </>
              )}
            </button>
          </div>
        </div>

        {/* Контент */}
        {loading ? (
          <div className="flex justify-center py-24">
            <Loader2 className="w-10 h-10 text-blue-500 animate-spin" />
          </div>
        ) : (
          <>
            <Stats stats={stats} />

            <div className="flex items-center justify-between mb-10 mt-16">
              <h2 className="text-2xl font-semibold text-white">
                Актуальные предложения
              </h2>

              <span className="px-3 py-1 bg-slate-800 border border-slate-700 rounded-full text-sm text-slate-400">
                {grants.length}
              </span>
            </div>

            {grants.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {grants.map((grant) => (
                  <GrantCard key={grant.id} grant={grant} />
                ))}
              </div>
            ) : (
              <div className="text-center py-24 bg-slate-900 rounded-2xl border border-slate-800">
                <p className="text-slate-400 text-lg">
                  По вашему запросу ничего не найдено.
                </p>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}