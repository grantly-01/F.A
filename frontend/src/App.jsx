import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Stats from './components/Stats'
import GrantCard from './components/GrantCard'
import { Loader2 } from 'lucide-react'

function App() {
  const [grants, setGrants] = useState([])
  const [allGrants, setAllGrants] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  const API_URL = 'http://127.0.0.1:8000'

  const loadData = async () => {
    const statsRes = await fetch(`${API_URL}/stats`)
    const statsData = await statsRes.json()
    setStats(statsData)

    const grantsRes = await fetch(`${API_URL}/grants`)
    const grantsData = await grantsRes.json()
    setGrants(grantsData)
    setAllGrants(grantsData)
  }

  useEffect(() => {
    const init = async () => {
      setLoading(true)
      try {
        await loadData()
      } catch (error) {
        console.error("Failed to fetch data:", error)
      } finally {
        setLoading(false)
      }
    }

    init()
  }, [])

  useEffect(() => {
    if (!searchQuery) {
      setGrants(allGrants)
      return
    }

    const controller = new AbortController()

    const search = async () => {
      try {
        const res = await fetch(
          `${API_URL}/grants?search=${encodeURIComponent(searchQuery)}`,
          { signal: controller.signal },
        )
        const data = await res.json()
        setGrants(data)
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.error("Failed to search grants:", error)
        }
      }
    }

    search()

    return () => controller.abort()
  }, [searchQuery, allGrants])

  const handleCollectClick = async () => {
    setLoading(true)
    try {
      await fetch(`${API_URL}/collect/full`, {
        method: 'POST',
      })
      await loadData()
    } catch (error) {
      console.error("Failed to run collection:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#070b14] text-white">
      <Navbar searchValue={searchQuery} onSearch={setSearchQuery} />

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
  )
}

export default App