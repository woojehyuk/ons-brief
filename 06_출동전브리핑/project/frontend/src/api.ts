// BE 주소 저장 · API 호출
export type Level = 'L1' | 'L2' | 'L3'
export type CatKey = 'r' | 'y' | 'g'

export interface Evidence {
  src: string; row: number | null; date: string | null; summary?: string
  cause?: string; action?: string; recur?: string; worker?: string
}
export interface Diagnosis {
  symptom: string; primary: boolean; signals: string[]; evidence: Evidence[]
  materials: string[]; materials_estimated: boolean
  history: { same_symptom: number; last_90d: number; recur_y: number }
  cause: { text: string; level: Level; n: number; total: number; ratio: number; label: string }
}
export interface Equip {
  type: string; vendor: string; model: string; fw: string; installed: string
  replaced: string | null; faults: number; note: string
}
export interface Card {
  site_id: string; category_key: CatKey; category_reason: string; score: number
  site: { name: string; branch: string; addr: string; install_type: string; manager: string; phone_masked: string }
  today: { count: number; max_grade: string; open: number; symptoms: Record<string, number> }
  diagnoses: Diagnosis[]; cautions: string[]
  equipment: { matched: Equip[]; reference_only: unknown[] }
}
export interface CompareRow {
  group: string; n: number; small: boolean; mean_faults: number; today_ratio: number; top_cause: string | null; flag: boolean
}
export interface Briefing {
  base_date: string; cards: Card[]; phones: Record<string, string>; source: 'data' | 'sample'
  analysis: {
    ranking: { site_id: string; name: string; branch: string; count: number; recur_rate: number; top_cause: string; today: number }[]
    compare: { overall_mean_faults: number; firmware: CompareRow[]; age: CompareRow[] }
  }
  quality: { sites: number; no_site: number; no_equip: number; no_hist: number; alarm_names: number; groups: number }
}
export interface Health { ok: boolean; source: 'data' | 'sample'; error: string | null; built_at: string; local: boolean }

const KEY = 'ons-brief.be-url'
export const DEFAULT_URL = 'http://localhost:8100'

export function getBeUrl(): string {
  try { return localStorage.getItem(KEY) || DEFAULT_URL } catch { return DEFAULT_URL }
}
export function setBeUrl(url: string): void {
  try { localStorage.setItem(KEY, url) } catch { /* 저장 불가 환경 무시 */ }
}
export function normalizeUrl(raw: string): string | null {
  const v = raw.trim().replace(/\/+$/, '')
  try {
    const u = new URL(v)
    return u.protocol === 'http:' || u.protocol === 'https:' ? v : null
  } catch { return null }
}

async function call<T>(base: string, path: string, init?: RequestInit): Promise<T> {
  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), 10000)
  try {
    const res = await fetch(base + path, { ...init, signal: ctrl.signal })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return (await res.json()) as T
  } finally { clearTimeout(timer) }
}

export const api = {
  health: (base: string) => call<Health>(base, '/api/health'),
  briefing: (base: string) => call<Briefing>(base, '/api/briefing'),
  rebuild: (base: string) => call<Health>(base, '/api/build', { method: 'POST' }),
}
