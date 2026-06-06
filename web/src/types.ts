/** data.json 的完整结构 */
export interface DexData {
  meta: Meta
  series: Record<string, TimePoint[]>
  summary: Record<string, Summary>
}

export interface Meta {
  updated_at: string
  tags: string[]
  authors: AuthorInfo[]
}

export interface AuthorInfo {
  id: number
  name: string
  platform: string
  tags: string[]
}

export interface TimePoint {
  time: string
  value: number
}

export interface Summary {
  latest: number
  change_1d: number
  change_1d_pct: number
  change_7d: number
  change_7d_pct: number
}

/** 行情面板中一个条目 */
export interface StockItem {
  key: string
  name: string
  latest: number
  change_pct: number
  kind: 'tag' | 'author' | 'index'
}

/** 时间范围选项 */
export type TimeRange = '1d' | '1w' | '1m' | '3m' | '6m' | 'all'
