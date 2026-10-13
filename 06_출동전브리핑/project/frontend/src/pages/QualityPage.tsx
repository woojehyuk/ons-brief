import { Badge } from '../ui'
import Gate from './Gate'

export default function QualityPage() {
  return (
    <Gate title="데이터 품질" desc="파일 간 연결(기지국ID) 확인 결과">
      {d => {
        const Q = d.quality
        const st = (v: number) => v ? <Badge tone="badge-warning">미매칭</Badge> : <Badge tone="badge-success">정상</Badge>
        const rows: [string, string | number, React.ReactNode, string][] = [
          ['알람 기지국', Q.sites, <Badge tone="badge-success">정상</Badge>, '-'],
          ['site_master 미매칭', Q.no_site, st(Q.no_site), '-'],
          ['장비이력 미매칭', Q.no_equip, st(Q.no_equip), '카드에 "관련 장비 이력 없음" 표시'],
          ['조치이력 미매칭', Q.no_hist, st(Q.no_hist), '전국 통계 추정(L2) / 근거 부족(L3)으로 처리'],
          ['알람명 → 증상그룹', `${Q.alarm_names} → ${Q.groups}`, <Badge tone="badge-success">정상</Badge>, '미등록 알람명 0개'],
        ]
        return (
          <div className="table-wrap"><table>
            <thead><tr><th>항목</th><th className="num">건수</th><th>상태</th><th>처리</th></tr></thead>
            <tbody>{rows.map(r => <tr key={r[0]}><td>{r[0]}</td><td className="num">{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>)}</tbody>
          </table></div>
        )
      }}
    </Gate>
  )
}
