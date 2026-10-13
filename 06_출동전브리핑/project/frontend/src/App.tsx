import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { HashRouter, NavLink, Route, Routes } from 'react-router-dom'
import { api, getBeUrl, setBeUrl, type Briefing } from './api'
import { Badge, Icon } from './ui'
import CardsPage from './pages/CardsPage'
import RankPage from './pages/RankPage'
import ComparePage from './pages/ComparePage'
import QualityPage from './pages/QualityPage'
import ConnectPage from './pages/ConnectPage'

type Status = 'loading' | 'ok' | 'fail'
interface Ctx {
  beUrl: string; data: Briefing | null; status: Status; error: string
  connect: (url: string) => void; reload: () => void
}
const DataCtx = createContext<Ctx>(null!)
export const useData = () => useContext(DataCtx)

const NAV = [
  { to: '/', icon: 'cards', label: '카드' },
  { to: '/rank', icon: 'rank', label: '반복순위' },
  { to: '/compare', icon: 'compare', label: '장비비교' },
  { to: '/quality', icon: 'quality', label: '데이터품질' },
  { to: '/connect', icon: 'connect', label: 'BE 연결' },
]

export default function App() {
  const [beUrl, setUrl] = useState(getBeUrl)
  const [data, setData] = useState<Briefing | null>(null)
  const [status, setStatus] = useState<Status>('loading')
  const [error, setError] = useState('')

  const load = useCallback(async (url: string) => {
    setStatus('loading')
    try {
      setData(await api.briefing(url)); setStatus('ok'); setError('')
    } catch (e) {
      setData(null); setStatus('fail'); setError(e instanceof Error ? e.message : String(e))
    }
  }, [])

  useEffect(() => { load(beUrl) }, [beUrl, load])

  const connect = (url: string) => { setBeUrl(url); setUrl(url); if (url === beUrl) load(url) }
  const statusBadge = status === 'ok' ? <Badge tone="badge-success">BE 연결됨</Badge>
    : status === 'fail' ? <Badge tone="badge-error">BE 연결 실패</Badge> : <Badge tone="badge-neutral">연결 중</Badge>

  return (
    <DataCtx.Provider value={{ beUrl, data, status, error, connect, reload: () => load(beUrl) }}>
      <HashRouter>
        <header className="topbar">
          <span className="logo">SK ONS</span><span className="divider" />
          <h1>출동 전 브리핑</h1>
          <span className="aside">
            {data && <span className="hide-sm">기준일 <span className="number">{data.base_date}</span></span>}
            {data?.source === 'sample' && <Badge tone="badge-warning">샘플 데이터</Badge>}
            {statusBadge}
          </span>
        </header>
        <div className="layout">
          <nav className="rail" aria-label="화면 이동">
            {NAV.map(n => (
              <NavLink key={n.to} to={n.to} end>
                <span className="pill"><Icon name={n.icon} /></span>{n.label}
              </NavLink>
            ))}
          </nav>
          <main>
            <Routes>
              <Route path="/" element={<CardsPage />} />
              <Route path="/rank" element={<RankPage />} />
              <Route path="/compare" element={<ComparePage />} />
              <Route path="/quality" element={<QualityPage />} />
              <Route path="/connect" element={<ConnectPage />} />
            </Routes>
          </main>
        </div>
      </HashRouter>
    </DataCtx.Provider>
  )
}
