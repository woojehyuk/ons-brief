import { useMemo, useState } from 'react'
import type { Briefing, Card, Diagnosis, Evidence } from '../api'
import { Badge, CAT, Empty, GRADE, fmt, noEmoji, pct } from '../ui'
import Gate from './Gate'

const PAGE = 30

function EvItem({ e }: { e: Evidence }) {
  if (e.summary) return <li>{e.src}: {e.summary}</li>
  return <li>{e.src} 행 {e.row} · {e.date} · {e.cause} → {e.action} (재발 {e.recur}, {e.worker})</li>
}

function Dx({ d }: { d: Diagnosis }) {
  const c = d.cause, guess = c.level !== 'L1'
  const meta = c.level === 'L1' ? `${c.n}/${c.total} 건 근거` : c.level === 'L2' ? `전국 ${fmt(c.total)} 건 중 ${pct(c.ratio)}` : '근거 부족'
  return (
    <div className={`cause${guess ? ' guess' : ''}`}>
      <div className="t"><b>{c.text}</b><Badge tone={guess ? 'badge-warning' : 'badge-success'}>{c.label}</Badge></div>
      <div className="meta"><span className="muted number">{meta}</span>{d.signals.map(s => <span key={s} className="chip">{noEmoji(s)}</span>)}</div>
      <details><summary>근거 {d.evidence.length} 건 보기</summary><ul className="ev">{d.evidence.map((e, i) => <EvItem key={i} e={e} />)}</ul></details>
    </div>
  )
}

function BriefCard({ c, phone, onPrint }: { c: Card; phone?: string; onPrint: () => void }) {
  const [showPhone, setShowPhone] = useState(false)
  const s = c.site, t = c.today
  const p = c.diagnoses.find(d => d.primary)!, rest = c.diagnoses.filter(d => !d.primary), h = p.history
  const mats = [...new Set(c.diagnoses.flatMap(d => d.materials))]
  const [tone, label] = CAT[c.category_key]
  const m = c.equipment.matched
  return (
    <article className="card">
      <div className="card-h">
        <div><h3>{s.name}<span className="id">{c.site_id}</span></h3><div className="sub">{s.branch} · {s.addr} · {s.install_type}</div></div>
        <Badge tone={tone}>{label}</Badge>
      </div>
      <div className="reason">분류 사유: {noEmoji(c.category_reason)} · 점수 <span className="number">{c.score}</span></div>
      <div className="sec"><h4>오늘 알람</h4><div className="row">
        <span className="number">{t.count} 건</span>
        <Badge tone={GRADE[t.max_grade] ?? 'badge-neutral'}>최고 {t.max_grade}</Badge>
        {t.open ? <Badge tone="badge-error">미해제 {t.open} 건</Badge> : <Badge tone="badge-success">전부 해제</Badge>}
        {Object.entries(t.symptoms).map(([k, v]) => <span key={k} className="chip">{k} × {v}</span>)}
      </div></div>
      <div className="sec">
        <h4>대표 증상 {p.symptom} · 과거 동일 증상 {h.same_symptom} 회 (최근 90일 {h.last_90d} 회){h.recur_y ? ` · 재발 ${h.recur_y} 회` : ''}</h4>
        <Dx d={p} />
      </div>
      {rest.map(d => <div key={d.symptom} className="sec"><h4>추가 증상 {d.symptom} · 과거 {d.history.same_symptom} 회</h4><Dx d={d} /></div>)}
      <div className="sec"><h4>장비</h4>
        {m.length ? m.map((e, i) => (
          <div key={i} className="eq">{e.type} · {e.vendor} {e.model} · FW {e.fw} · 설치 <span className="number">{e.installed}</span>
            {e.replaced && <> · 교체 <span className="number">{e.replaced}</span></>} · 누적고장 <span className="number">{e.faults}</span> 회
            {e.note && <span className="muted"> · {e.note}</span>}</div>
        )) : <div className="row"><Badge tone="badge-warning">관련 장비 이력 없음</Badge>
          {c.equipment.reference_only.length > 0 && <span className="muted small">기타 장비 {c.equipment.reference_only.length} 건</span>}</div>}
      </div>
      <div className="sec"><h4>챙길 자재</h4><div className="row">
        {mats.map(x => <span key={x} className="chip">{x}</span>)}
        {c.diagnoses.some(d => d.materials_estimated) && <Badge tone="badge-warning">추정 · 기본세트 포함</Badge>}
      </div></div>
      {c.cautions.length > 0 && <div className="sec"><h4>주의사항</h4>
        {c.cautions.map(x => <div key={x} className="caution">{/^⚠/.test(x) && <Badge tone="badge-error">주의</Badge>}<span>{noEmoji(x)}</span></div>)}
      </div>}
      <div className="card-f">
        <span>담당 {s.manager} · <span className="number">{showPhone && phone ? phone : s.phone_masked}</span></span>
        <span>
          {phone && <button className="btn btn-sm" onClick={() => setShowPhone(v => !v)}>{showPhone ? '번호 숨김' : '번호 보기'}</button>}{' '}
          <button className="btn btn-sm" onClick={() => { setShowPhone(false); onPrint() }}>인쇄</button>
        </span>
      </div>
    </article>
  )
}

function CardsView({ d }: { d: Briefing }) {
  const [q, setQ] = useState(''), [branch, setBranch] = useState(''), [cat, setCat] = useState('')
  const [grade, setGrade] = useState(''), [lv, setLv] = useState('')
  const [shown, setShown] = useState(PAGE)
  const [printId, setPrintId] = useState<string | null>(null)
  const branches = useMemo(() => [...new Set(d.cards.map(c => c.site.branch))].sort(), [d])
  const list = d.cards.filter(c => (!q || (c.site_id + c.site.name).toLowerCase().includes(q.trim().toLowerCase()))
    && (!branch || c.site.branch === branch) && (!cat || c.category_key === cat)
    && (!grade || c.today.max_grade === grade) && (!lv || c.diagnoses.find(x => x.primary)!.cause.level === lv))
  const cnt = (k: string) => fmt(d.cards.filter(c => c.category_key === k).length)
  const on = <T,>(set: (v: T) => void) => (v: T) => { set(v); setShown(PAGE) }

  const print = (id: string) => {
    setPrintId(id)
    setTimeout(() => { window.print(); setPrintId(null) }, 50)
  }

  return <>
    <div className="kpis">
      {(['r', 'y', 'g'] as const).map(k => (
        <div key={k} className="kpi"><div className="label">
          <Badge tone={CAT[k][0]}>{k === 'r' ? '위험' : k === 'y' ? '주의' : '정상'}</Badge>{CAT[k][1]}</div>
          <div className="display number">{cnt(k)} <span className="unit">곳</span></div></div>
      ))}
    </div>
    <div className="filters">
      <div className="f-q"><label htmlFor="q">검색</label><input id="q" value={q} onChange={e => on(setQ)(e.target.value)} placeholder="예: BSN-0001" /></div>
      <div><label htmlFor="f-branch">지사</label><select id="f-branch" value={branch} onChange={e => on(setBranch)(e.target.value)}>
        <option value="">전체</option>{branches.map(b => <option key={b}>{b}</option>)}</select></div>
      <div><label htmlFor="f-cat">분류</label><select id="f-cat" value={cat} onChange={e => on(setCat)(e.target.value)}>
        <option value="">전체</option>{(['r', 'y', 'g'] as const).map(k => <option key={k} value={k}>{CAT[k][1]}</option>)}</select></div>
      <div><label htmlFor="f-grade">최고 등급</label><select id="f-grade" value={grade} onChange={e => on(setGrade)(e.target.value)}>
        <option value="">전체</option>{['Critical', 'Major', 'Minor', 'Warning'].map(g => <option key={g}>{g}</option>)}</select></div>
      <div><label htmlFor="f-lv">원인 근거</label><select id="f-lv" value={lv} onChange={e => on(setLv)(e.target.value)}>
        <option value="">전체</option><option value="L1">확정근거</option><option value="L2">추정 · 전국 통계</option><option value="L3">추정 · 근거 부족</option></select></div>
    </div>
    <p className="muted small" style={{ margin: 0 }}>{fmt(list.length)}곳 표시 (전체 {fmt(d.cards.length)}곳) · 분류 → 점수 높은 순</p>
    {list.length ? <div className="cards">
      {list.slice(0, shown).map(c => (
        <div key={c.site_id} className={printId && printId !== c.site_id ? 'print-hide' : ''} style={{ display: 'contents' }}>
          <BriefCard c={c} phone={d.phones[c.site_id]} onPrint={() => print(c.site_id)} />
        </div>
      ))}
    </div> : <Empty>조건에 맞는 기지국이 없습니다</Empty>}
    {list.length > shown && <div className="more">
      <button className="btn btn-primary" onClick={() => setShown(s => s + PAGE)}>더 보기 ({fmt(list.length - shown)}곳 남음)</button></div>}
  </>
}

export default function CardsPage() {
  return <Gate title="출동 브리핑 카드" desc="오늘 알람 기지국별 예상 원인 · 근거 · 챙길 자재">{d => <CardsView d={d} />}</Gate>
}
