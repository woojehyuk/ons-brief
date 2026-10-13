import { Link } from 'react-router-dom'
import { useData } from '../App'
import type { Briefing } from '../api'
import { Empty } from '../ui'

// 데이터가 없을 때(연결 중·실패) 공통 안내
export default function Gate({ title, desc, children }: {
  title: string; desc: string; children: (d: Briefing) => React.ReactNode
}) {
  const { data, status, error, beUrl } = useData()
  return (
    <section className="container">
      <div className="page-h"><h2>{title}</h2><p className="muted">{desc}</p></div>
      {data?.source === 'sample' && (
        <div className="notice">원본 데이터를 읽지 못해 <b>가상 샘플 데이터</b>를 표시 중입니다. 원인은 BE 연결 화면에서 확인할 수 있습니다.</div>
      )}
      {data ? children(data)
        : status === 'loading' ? <Empty>데이터를 불러오는 중입니다</Empty>
        : <Empty>BE({beUrl})에 연결하지 못했습니다 · {error}<br /><br /><Link to="/connect">BE 연결 화면으로 이동</Link></Empty>}
    </section>
  )
}
