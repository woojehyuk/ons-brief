import { useState } from 'react'
import { useData } from '../App'
import { api, DEFAULT_URL, normalizeUrl, type Health } from '../api'
import { Badge } from '../ui'

type Test = { state: 'idle' | 'testing' } | { state: 'ok'; h: Health; ms: number } | { state: 'fail'; msg: string }

export default function ConnectPage() {
  const { beUrl, connect, data, status } = useData()
  const [input, setInput] = useState(beUrl)
  const [err, setErr] = useState('')
  const [test, setTest] = useState<Test>({ state: 'idle' })
  const [building, setBuilding] = useState(false)

  const run = async () => {
    const url = normalizeUrl(input)
    if (!url) { setErr('http:// 또는 https:// 로 시작하는 주소를 입력하세요'); return }
    setErr(''); setInput(url); setTest({ state: 'testing' })
    const t0 = performance.now()
    try {
      const h = await api.health(url)
      setTest({ state: 'ok', h, ms: Math.round(performance.now() - t0) })
      connect(url)
    } catch (e) {
      setTest({ state: 'fail', msg: e instanceof Error ? (e.name === 'AbortError' ? '응답 시간 초과 (10초)' : e.message) : String(e) })
    }
  }

  const rebuild = async () => {
    setBuilding(true)
    try { const h = await api.rebuild(beUrl); setTest({ state: 'ok', h, ms: 0 }); connect(beUrl) }
    catch (e) { setTest({ state: 'fail', msg: e instanceof Error ? e.message : String(e) }) }
    finally { setBuilding(false) }
  }

  return (
    <section className="container">
      <div className="page-h"><h2>BE 연결</h2><p className="muted">브리핑 데이터를 보내 주는 서버(BE) 주소 입력 · 연결 테스트</p></div>

      <div className="panel">
        <h3>서버 주소</h3>
        <div className="form-row">
          <div>
            <label htmlFor="be-url">BE 주소</label>
            <input id="be-url" value={input} aria-invalid={!!err} placeholder={DEFAULT_URL}
              onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && run()} />
          </div>
          <button className="btn btn-primary" onClick={run} disabled={test.state === 'testing'}>
            {test.state === 'testing' ? '테스트 중…' : '연결 테스트'}</button>
        </div>
        {err ? <div className="field-msg err">{err}</div> : <div className="field-msg muted">
          내 PC: <code>{DEFAULT_URL}</code> · 외부 접속: tunnel.bat 실행 후 표시되는 <code>https://….trycloudflare.com</code> 주소</div>}

        {test.state === 'ok' && <div className="row"><Badge tone="badge-success">연결 성공</Badge>
          <span className="muted small number">{test.ms ? `${test.ms} ms · ` : ''}저장됨</span></div>}
        {test.state === 'fail' && <div className="row"><Badge tone="badge-error">연결 실패</Badge><span className="small">{test.msg}</span>
          <span className="muted small">· BE 실행 여부, 주소 오타, 방화벽 확인</span></div>}
      </div>

      <div className="panel">
        <h3>현재 연결 상태</h3>
        <dl className="kv">
          <dt>연결 주소</dt><dd>{beUrl}</dd>
          <dt>상태</dt><dd>{status === 'ok' ? <Badge tone="badge-success">연결됨</Badge> : status === 'fail' ? <Badge tone="badge-error">실패</Badge> : <Badge tone="badge-neutral">연결 중</Badge>}</dd>
          {data && <><dt>데이터</dt><dd>{data.source === 'data' ? <Badge tone="badge-success">원본 데이터</Badge> : <Badge tone="badge-warning">가상 샘플</Badge>} · 카드 {data.cards.length} 장</dd>
            <dt>전체 연락처</dt><dd>{Object.keys(data.phones).length ? '내 PC 접속 · 전체 번호 표시 가능' : '외부 접속 · 가린 번호만 제공'}</dd></>}
          {test.state === 'ok' && <><dt>마지막 계산</dt><dd className="number">{test.h.built_at}</dd>
            {test.h.error && <><dt>원본 읽기 오류</dt><dd className="small">{test.h.error}</dd></>}</>}
        </dl>
        <div><button className="btn" onClick={rebuild} disabled={building || status !== 'ok'}>{building ? '계산 중…' : '데이터 다시 계산'}</button></div>
      </div>
    </section>
  )
}
