// 공통 UI 조각
import type { CatKey } from './api'

export const CAT: Record<CatKey, [string, string]> = {
  r: ['badge-error', '지금 바로 출동'],
  y: ['badge-warning', '원격 조치 먼저'],
  g: ['badge-success', '다음 정기점검 때'],
}
export const GRADE: Record<string, string> = { Critical: 'badge-error', Major: 'badge-warning' }

export const fmt = (n: number) => n.toLocaleString('ko-KR')
export const pct = (v: number) => `${Math.round(v * 100)} %`
export const noEmoji = (s: string) => s.replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]️?\s*/gu, '').trim()

export function Badge({ tone, children }: { tone: string; children: React.ReactNode }) {
  return <span className={`badge ${tone}`}>{children}</span>
}

const ICONS: Record<string, React.ReactNode> = {
  cards: <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></>,
  rank: <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" />,
  compare: <><rect x="4" y="4" width="16" height="16" rx="2" /><path d="M9 9h6v6H9zM9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" /></>,
  quality: <><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z" /><path d="M8.5 12l2.5 2.5 4.5-5" /></>,
  connect: <><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1" /><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1" /></>,
}
export function Icon({ name }: { name: string }) {
  return <svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>
}

export function Empty({ children }: { children: React.ReactNode }) {
  return <div className="empty">{children}</div>
}
