# SocialDex 股票风格 UI 重设计

## 概述

将 SocialDex 前端从单 HTML 文件重写为 Vue 3 SPA，采用股票软件风格的交互界面，支持按 tag / 单账号查看粉丝曲线、涨跌幅排行、时间区间调整。

## 技术栈

- **运行时/包管理**：Bun
- **框架**：Vue 3 Composition API + TypeScript
- **构建**：Vite
- **UI**：DaisyUI + Tailwind CSS
- **图表**：Lightweight Charts（TradingView 开源）
- **后端**：Python generate.py 改造

## 项目结构

```
SocialDex/
├── web/                        # Vue 3 项目源码
│   ├── src/
│   │   ├── App.vue             # 根组件：侧边栏 + 图表区
│   │   ├── components/
│   │   │   ├── Sidebar.vue     # 左侧行情面板
│   │   │   ├── StockCard.vue   # 行情卡片（名称、粉丝数、涨跌幅）
│   │   │   ├── ChartPanel.vue  # 右侧主图表区
│   │   │   └── TimeControl.vue # 时间区间控制栏
│   │   ├── composables/
│   │   │   └── useData.ts      # 数据加载与处理
│   │   ├── types.ts            # TS 类型定义
│   │   └── main.ts
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── package.json
├── frontend/                   # build 输出目录
│   ├── index.html
│   ├── assets/
│   └── data.json               # 后端生成的数据
├── src/                        # Python 后端
│   ├── generate.py
│   └── ...
└── data/
    └── config.json
```

## 数据结构 (data.json)

```json
{
  "meta": {
    "updated_at": "2026-06-05T02:06:30",
    "tags": ["二游", "米哈游", "库洛", "鹰角网络", "网易", "腾讯", "Galgame", "二次元"],
    "authors": [
      {"id": 1, "name": "原神", "platform": "bilibili", "tags": ["二游", "米哈游"]}
    ]
  },
  "series": {
    "tag:米哈游": [{"time": "2026-02-18T19:08:19", "value": 1234.56}],
    "author:原神": [{"time": "2026-02-18T19:08:19", "value": 890.12}],
    "index:蓝筹100": [{"time": "2026-02-18T19:08:19", "value": 4567.89}]
  },
  "summary": {
    "tag:米哈游": {
      "latest": 5066.45,
      "change_1d": 23.5,
      "change_1d_pct": 0.47,
      "change_7d": 156.3,
      "change_7d_pct": 3.18
    },
    "author:原神": {
      "latest": 890.12,
      "change_1d": 5.2,
      "change_1d_pct": 0.59,
      "change_7d": 32.1,
      "change_7d_pct": 3.74
    }
  }
}
```

**key 前缀约定**：`tag:` = tag 汇总，`author:` = 单账号，`index:` = 蓝筹100

## UI 布局

```
┌────────────────────────────────────────────────────┐
│  SocialDex                    更新至 2026-06-05     │
├──────────┬─────────────────────────────────────────┤
│ 自选行情  │   [米哈游] [原神] [崩铁] [库洛]  ← 标签栏  │
│          │                                         │
│ ▲ 蓝筹100│        ╭─────────────────────────╮      │
│  5066.45 │        │                          │      │
│  +0.47%  │        │     Lightweight Charts   │      │
│──────────│        │       面积图/折线图       │      │
│ ▲ 米哈游  │        │                          │      │
│  3210.00 │        ╰─────────────────────────╯      │
│  +1.23%  │                                        │
│──────────│  [1天] [1周] [1月] [3月] [6月] [全部]   │
│ ▼ 库洛    │  ════════════════════════════════        │
│   856.30 │  时间轴缩放条                            │
│  -0.52%  │                                         │
└──────────┴─────────────────────────────────────────┘
```

## 交互设计

### 左侧边栏 (Sidebar)
- 按涨跌幅排序，A 股配色（红涨绿跌）
- 点击 → 右侧图表切到对应曲线
- 显示：名称、最新粉丝总量(万)、日涨跌幅(%)
- 顶部筛选 tab：全部 / 标签 / 账号

### 图表标签栏 (Legend)
- 当前活跃曲线，可点击显示/隐藏
- 默认显示当前选中项，可多选叠加对比

### 主图表 (ChartPanel)
- Lightweight Charts 面积图，深色主题
- 十字线 + tooltip（时间、粉丝量、涨跌）
- 鼠标滚轮缩放、拖拽平移

### 时间控制 (TimeControl)
- 快捷按钮：1天 / 1周 / 1月 / 3月 / 6月 / 全部
- 底部可拖拽时间轴缩放条

## 后端改造 (generate.py)

1. 保留现有 tag 汇总曲线和蓝筹100
2. 新增每个 author 单独粉丝曲线
3. 新增 summary 涨跌幅（日/周）计算
4. 新增 meta 元信息
5. 输出统一 data.json

## 构建流程

```bash
# 前端开发
cd web && bun dev

# 构建
cd web && bun run build  # 输出到 frontend/

# 后端数据生成
python -m src.generate  # 输出 frontend/data.json
```
