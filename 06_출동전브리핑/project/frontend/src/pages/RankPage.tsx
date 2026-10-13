import { Badge, pct } from '../ui'
import Gate from './Gate'

export default function RankPage() {
  return (
    <Gate title="반복 장애 순위" desc={'조치이력 기준 기지국별 조치 건수 · 재발률 상위 20곳 · 재발률 40 % 이상은 "재발 多" 배지'}>
      {d => {
        const R = d.analysis.ranking, max = Math.max(1, ...R.map(r => r.count))
        return (
          <div className="table-wrap"><table>
            <thead><tr><th className="num">순위</th><th>기지국</th><th>지사</th><th className="num">조치 건수</th><th className="num">재발률</th><th>최빈 원인</th><th className="num">오늘 알람</th></tr></thead>
            <tbody>
              {R.length ? R.map((r, i) => (
                <tr key={r.site_id}>
                  <td className="num">{i + 1}</td><td>{r.name} <span className="muted">{r.site_id}</span></td><td>{r.branch}</td>
                  <td className="num"><span className="bar" style={{ width: r.count / max * 80, animationDelay: `${i * 40}ms` }} />{r.count}</td>
                  <td className="num">{r.recur_rate >= 0.4 && <><Badge tone="badge-warning">재발 多</Badge> </>}{pct(r.recur_rate)}</td>
                  <td>{r.top_cause}</td><td className="num">{r.today}</td>
                </tr>
              )) : <tr><td colSpan={7} className="muted">조치이력이 없습니다</td></tr>}
            </tbody>
          </table></div>
        )
      }}
    </Gate>
  )
}
