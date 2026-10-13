import type { CompareRow } from '../api'
import { Badge, pct } from '../ui'
import Gate from './Gate'

function CmpTable({ rows }: { rows: CompareRow[] }) {
  return (
    <div className="table-wrap"><table>
      <thead><tr><th>그룹</th><th className="num">장비 수</th><th className="num">평균 누적고장</th><th className="num">오늘 알람 비율</th><th>최빈 원인</th><th>판정</th></tr></thead>
      <tbody>
        {!rows.length && <tr><td colSpan={6} className="muted">비교할 그룹이 없습니다</td></tr>}
        {rows.map(f => f.small
          ? <tr key={f.group}><td>{f.group}</td><td className="num">{f.n}</td><td colSpan={4} className="muted">표본 부족 (5대 미만)</td></tr>
          : <tr key={f.group}><td>{f.group}</td><td className="num">{f.n}</td><td className="num">{f.mean_faults}</td><td className="num">{pct(f.today_ratio)}</td>
              <td>{f.top_cause ?? '-'}</td>
              <td>{f.flag ? <Badge tone="badge-warning">공통 원인 의심 · 추정</Badge> : <Badge tone="badge-neutral">평균 수준</Badge>}</td></tr>)}
      </tbody>
    </table></div>
  )
}

export default function ComparePage() {
  return (
    <Gate title="펌웨어 · 연식 비교" desc={'장비 5대 이상 그룹만 비교 · 평균 누적고장의 1.5배 이상이면 "공통 원인 의심"(추정)'}>
      {d => <>
        <p className="muted small" style={{ margin: 0 }}>전체 평균 누적고장 <span className="number">{d.analysis.compare.overall_mean_faults}</span> 회</p>
        <h3 className="sec-t">제조사 · 모델 · 펌웨어</h3><CmpTable rows={d.analysis.compare.firmware} />
        <h3 className="sec-t">설치 연식</h3><CmpTable rows={d.analysis.compare.age} />
      </>}
    </Gate>
  )
}
