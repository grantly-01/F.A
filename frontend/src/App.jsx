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

  const API_URL = 'http://127.0.0.1:8000'

  useEffect(() => {
    const fetchData = async () => {
      try {
        const statsRes = await fetch(`${API_URL}/stats`)
        const statsData = await statsRes.json()
        setStats(statsData)

        const grantsRes = await fetch(`${API_URL}/grants`)
        const grantsData = await grantsRes.json()
        setGrants(grantsData)
      } catch (error) {
        console.error("Failed to fetch data:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const filteredGrants = grants.filter(grant => {
    const query = searchQuery.toLowerCase()
    return (
      grant.title.toLowerCase().includes(query) ||
      (grant.description && grant.description.toLowerCase().includes(query)) ||
      (grant.funder && grant.funder.toLowerCase().includes(query))
    )
  })

  return (
    <div className="min-h-screen bg-[#070b14] text-white">
      <Navbar onSearch={setSearchQuery} />

      <main className="max-w-7xl mx-auto px-6 pt-16 pb-24">

        {/* Hero */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight mb-4">
            GrantHub.kz
          </h1>

          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Платформа мониторинга грантов и конкурсов в Казахстане.
          </p>
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
                {filteredGrants.length}
              </span>
            </div>

            {filteredGrants.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {filteredGrants.map((grant) => (
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