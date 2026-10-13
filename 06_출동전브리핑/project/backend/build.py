"""출동 전 브리핑 카드 빌드 파이프라인 (SPEC.md v0.3).

실행: python build.py [--config config.yaml]
단계:
  1 load            로드·정규화·미등록 알람명 검사
  2 join            기지국 단위 집계 + 조인 + 품질 리포트
  3 infer           원인 추론 L1/L2/L3 (§4.3)
  4 materials       자재·주의사항 (§4.4)
  5 classify/score  분류·점수 (§4.5, §4.6)
  6 render          json / md / app.json (§5)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).parent
GRADE_ORDER = ["Critical", "Major", "Minor", "Warning"]
CATEGORIES = {"r": "지금 바로 출동", "y": "원격 조치 먼저", "g": "다음 정기점검 때"}
CAT_EMOJI = {"r": "🔴", "y": "🟡", "g": "🟢"}
LEVEL_LABEL = {"L1": "확정근거", "L2": "추정 · 전국 통계", "L3": "추정 · 근거 부족"}
# L3: 장비구분별 일반 원인 (SPEC §4.3)
GENERIC_CAUSE = {
    "RU": "RU 하드웨어 불량", "DU": "보드 불량", "정류기": "정류모듈 불량",
    "전송장비": "포트 불량", "광모듈": "SFP 불량",
}
FIRMWARE_RE = re.compile(r"(\d{4})-(\d{2})\s*펌웨어\s*업그레이드")


class BuildError(Exception):
    pass


# ---------- 1. load ----------
def load_config(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _norm(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.upper()


def load_data(cfg: dict) -> dict[str, pd.DataFrame]:
    p = {k: ROOT / v for k, v in cfg["paths"].items()}
    data = {
        "alarm": pd.read_csv(p["alarm"], encoding="utf-8-sig", parse_dates=["발생시각", "해제시각"]),
        "site": pd.read_excel(p["site"], dtype={"담당자연락처": str}),
        "equip": pd.read_excel(p["equipment"]),
        "hist": pd.read_excel(p["history"]),
        "symptom_map": pd.read_csv(p["symptom_map"], encoding="utf-8"),
        "material_map": pd.read_csv(p["material_map"], encoding="utf-8"),
    }
    for df, cols in ((data["equip"], ["설치일", "최근교체일"]), (data["hist"], ["조치일"])):
        for c in cols:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    # 원본 행 번호 보존 (근거 표시용, 엑셀 기준 헤더=1행 → 데이터 2행부터)
    data["hist"]["_row"] = data["hist"].index + 2
    data["equip"]["_row"] = data["equip"].index + 2
    data["hist"]["재발여부"] = data["hist"]["재발여부"].astype(str).str.strip().str.upper()
    return data


def normalize(data: dict) -> None:
    """알람명·증상 → 증상그룹. 미등록 알람명은 빌드 실패 (SPEC §3)."""
    sm = data["symptom_map"].copy()
    sm["_key"] = _norm(sm["원본명"])
    lookup = sm.set_index("_key")

    for name, col in (("alarm", "알람명"), ("hist", "증상")):
        df = data[name]
        key = _norm(df[col])
        unknown = sorted(set(df.loc[~key.isin(lookup.index), col]))
        if unknown:
            raise BuildError(f"[{name}] 정규화 사전 미등록 {col}: {unknown}")
        for c in ("증상그룹", "계열", "원격조치가능"):
            df[c] = key.map(lookup[c])
        df["증상장비"] = key.map(lookup["장비구분"])
    data["group_info"] = (sm.drop_duplicates("증상그룹").set_index("증상그룹")
                          [["장비구분", "계열", "원격조치가능"]].to_dict("index"))


# ---------- 2. join ----------
def summarize_today(alarm: pd.DataFrame) -> pd.DataFrame:
    """기지국 단위 오늘 알람 요약 (SPEC §4.2)."""
    a = alarm.copy()
    a["_grade_rank"] = a["등급"].map({g: i for i, g in enumerate(GRADE_ORDER)})
    a["_open"] = a["상태"].str.strip() != "해제"
    rows = []
    for sid, g in a.groupby("기지국ID"):
        sym_cnt = g.groupby("증상그룹").agg(n=("알람ID", "size"), best=("_grade_rank", "min"))
        primary = sym_cnt.sort_values(["best", "n"], ascending=[True, False]).index[0]
        rows.append({
            "기지국ID": sid,
            "count": len(g),
            "max_grade": GRADE_ORDER[g["_grade_rank"].min()],
            "open": int(g["_open"].sum()),
            "open_alarms": g.loc[g["_open"], ["등급", "증상그룹", "계열"]].to_dict("records"),
            "grades": g["등급"].tolist(),
            "symptoms": {k: int(v) for k, v in sym_cnt.sort_values(["best", "n"], ascending=[True, False])["n"].items()},
            "primary_symptom": primary,
            "first_at": g["발생시각"].min(),
            "last_clear_at": g["해제시각"].max(),
        })
    return pd.DataFrame(rows)


def quality_report(data: dict, today: pd.DataFrame) -> str:
    ids = set(today["기지국ID"])
    no_site = sorted(ids - set(data["site"]["기지국ID"]))
    no_equip = sorted(ids - set(data["equip"]["기지국ID"]))
    no_hist = sorted(ids - set(data["hist"]["기지국ID"]))
    lines = [
        "# 데이터 품질 리포트", "",
        f"- 알람 기지국: {len(ids)}곳",
        f"- site_master 미매칭: {len(no_site)}곳",
        f"- 장비이력 미매칭: {len(no_equip)}곳",
        f"- 조치이력 미매칭: {len(no_hist)}곳",
        f"- 날짜 변환 실패: 장비 설치일 {int(data['equip']['설치일'].isna().sum())}건, "
        f"조치일 {int(data['hist']['조치일'].isna().sum())}건", "",
        "## 장비이력 미매칭", ", ".join(no_equip) or "-", "",
        "## 조치이력 미매칭", ", ".join(no_hist) or "-", "",
    ]
    if no_site:
        raise BuildError(f"site_master 미매칭 기지국: {no_site}")
    return "\n".join(lines)


# ---------- 3. infer ----------
def _evidence(rows: pd.DataFrame) -> list[dict]:
    return [{
        "src": "조치이력.xlsx", "row": int(r["_row"]),
        "date": r["조치일"].strftime("%Y-%m-%d") if pd.notna(r["조치일"]) else None,
        "symptom": r["증상"], "cause": r["실제원인"], "action": r["조치내용"],
        "recur": r["재발여부"], "worker": r["작업자"],
    } for _, r in rows.sort_values("조치일", ascending=False).iterrows()]


def _pick_cause(rows: pd.DataFrame) -> str:
    """최빈 원인. 동률 → 재발 Y 포함 → 최근 조치일 (SPEC §4.3)."""
    stat = rows.groupby("실제원인").agg(
        n=("_row", "size"),
        recur=("재발여부", lambda s: (s == "Y").any()),
        last=("조치일", "max"),
    )
    return stat.sort_values(["n", "recur", "last"], ascending=False).index[0]


def equipment_signals(equip: pd.DataFrame, cfg: dict) -> list[str]:
    base = pd.Timestamp(cfg["base_date"])
    sc = cfg["signals"]
    fw_since = base - pd.DateOffset(months=sc["firmware_months"])
    out = []
    for _, e in equip.iterrows():
        m = FIRMWARE_RE.search(str(e.get("비고", "")))
        if m and pd.Timestamp(int(m.group(1)), int(m.group(2)), 1) >= fw_since.replace(day=1):
            out.append(f"🔧 펌웨어({m.group(1)}-{m.group(2)} 업그레이드)")
        if e["누적고장횟수"] >= sc["fault_count_min"]:
            out.append(f"📈 고장多({int(e['누적고장횟수'])}회)")
        basis = e["최근교체일"] if pd.notna(e["최근교체일"]) else e["설치일"]
        if pd.notna(basis):
            years = (base - basis).days / 365.25
            if years >= sc["aging_years"]:
                out.append(f"⏳ 노후({int(years)}년)")
    return list(dict.fromkeys(out))


def infer_causes(site_id: str, symptom: str, data: dict, cfg: dict) -> dict:
    """L1/L2/L3 원인 추론 + 근거 + 보조신호 (SPEC §4.3)."""
    ic = cfg["inference"]
    base = pd.Timestamp(cfg["base_date"])
    equip_type = data["group_info"][symptom]["장비구분"]
    h = data["hist"][data["hist"]["증상그룹"] == symptom]
    local = h[h["기지국ID"] == site_id]

    history = {
        "same_symptom": len(local),
        "last_90d": int((local["조치일"] >= base - pd.Timedelta(days=cfg["history"]["recent_days"])).sum()),
        "recur_y": int((local["재발여부"] == "Y").sum()),
    }

    if len(local) >= ic["l1_min"]:
        text = _pick_cause(local)
        n = int((local["실제원인"] == text).sum())
        cause = {"text": text, "level": "L1", "n": n, "total": len(local), "ratio": round(n / len(local), 2)}
        evidence = _evidence(local)
    else:
        top = _pick_cause(h) if len(h) else None
        n = int((h["실제원인"] == top).sum()) if top else 0
        ratio = n / len(h) if len(h) else 0.0
        if len(h) >= ic["l2_min"] and ratio >= ic["l2_min_ratio"]:
            cause = {"text": top, "level": "L2", "n": n, "total": len(h), "ratio": round(ratio, 2)}
            evidence = [{"src": "조치이력.xlsx", "row": None, "date": None,
                         "summary": f"전국 {symptom} {len(h)}건 중 '{top}' {n}건 ({ratio:.0%})"}]
            evidence += _evidence(h[h["실제원인"] == top].head(3))
        else:
            cause = {"text": GENERIC_CAUSE[equip_type], "level": "L3", "n": 0, "total": len(h),
                     "ratio": round(ratio, 2)}
            note = (f"전국 {symptom} {len(h)}건, 최빈 '{top}' {ratio:.0%} → L2 기준"
                    f"(≥{ic['l2_min']}건·≥{ic['l2_min_ratio']:.0%}) 미달" if top else f"전국 {symptom} 이력 없음")
            evidence = [{"src": "규칙", "row": None, "date": None,
                         "summary": f"{note} → 장비구분({equip_type}) 일반 원인"}]
    cause["label"] = LEVEL_LABEL[cause["level"]]

    eq = data["equip"]
    site_eq = eq[eq["기지국ID"] == site_id]
    matched = site_eq[site_eq["장비구분"] == equip_type]
    signals = (["🔁 재발(이전 조치 효과 없음)"] if history["recur_y"] else []) + equipment_signals(matched, cfg)

    return {
        "symptom": symptom, "equip_type": equip_type,
        "family": data["group_info"][symptom]["계열"],
        "remote": data["group_info"][symptom]["원격조치가능"] == "Y",
        "history": history, "cause": cause, "evidence": evidence, "signals": signals,
    }


# ---------- 4. materials ----------
def materials_for(cause: str | None, equip_type: str, data: dict) -> tuple[list[str], bool]:
    """(자재 목록, 추정 여부). 매핑 없거나 '기본세트 사용' → 장비구분 기본세트 + 추정 (SPEC §4.4)."""
    mm = data["material_map"]
    hit = mm[(mm["구분"] == "원인") & (mm["키"] == cause)]
    if len(hit) and "기본세트" not in hit.iloc[0]["자재"]:
        return hit.iloc[0]["자재"].split("|"), False
    base = mm[(mm["구분"] == "기본") & (mm["키"] == equip_type)]
    return (base.iloc[0]["자재"].split("|") if len(base) else []), True


def cautions_for(site: dict, families: set[str]) -> list[str]:
    out = []
    if site["high_work"]:
        out.append("⚠️ 고소작업: 안전벨트·안전모, 2인 1조, 기상 확인")
    if site["install_type"] in ("철탑", "옥탑"):
        out.append(f"{site['install_type']}: 출입 승인 사전 확인")
    if "POWER" in families:
        out.append("전기 안전: 절연장갑 착용, 차단기 상태 확인")
    return out


# ---------- 5. classify / score ----------
def classify(card: dict, cfg: dict) -> tuple[str, str]:
    """(분류키 r/y/g, 사유) — 🔴 > 🟡 > 🟢 (SPEC §4.5)."""
    cc = cfg["category"]
    t = card["today"]
    red = []
    for g in cc["red_open_grades"]:
        n = sum(1 for a in t["open_alarms"] if a["등급"] == g)
        if n:
            red.append(f"미해제 {g} {n}건")
    n = sum(1 for a in t["open_alarms"] if a["등급"] == "Major" and a["계열"] in cc["red_open_major_families"])
    if n:
        red.append(f"미해제 Major(HW/POWER) {n}건")
    for d in card["diagnoses"]:
        if d["cause"]["level"] == "L1" and d["family"] == "HW" and d["history"]["recur_y"]:
            red.append(f"{d['symptom']} HW 원인 재발")
    if red:
        return "r", " · ".join(red)

    yellow = []
    remote = [d["symptom"] for d in card["diagnoses"] if d["remote"]]
    if remote:
        yellow.append(f"원격조치 가능({', '.join(remote)})")
    if t["max_grade"] in ("Critical", "Major"):
        yellow.append(f"해제됐지만 {t['max_grade']}")
    for s, k in t["symptoms"].items():
        if k >= cc["yellow_repeat_min"]:
            yellow.append(f"{s} 당일 반복 {k}회")
    if yellow:
        return "y", " · ".join(yellow)
    return "g", f"해제 · {t['max_grade']} · 반복 없음"


def score(card: dict, cfg: dict) -> int:
    """우선순위 점수 (SPEC §4.6)."""
    sc = cfg["score"]
    t = card["today"]
    hist = sum(d["history"]["same_symptom"] for d in card["diagnoses"])
    recur = sum(d["history"]["recur_y"] for d in card["diagnoses"])
    return int(sum(sc["grade_weight"][g] for g in t["grades"]) + t["open"] * sc["open"]
               + min(hist, sc["history_cap"]) * sc["history"] + recur * sc["recur"])


# ---------- 카드 조립 ----------
def mask_phone(phone: str) -> str:
    return re.sub(r"^(\d{2,3})-(\d{3,4})-(\d{4})$", r"\1-****-\3", str(phone))


def _equip_view(rows: pd.DataFrame) -> list[dict]:
    return [{
        "serial": e["장비시리얼"], "type": e["장비구분"], "vendor": e["제조사"], "model": e["모델"],
        "fw": str(e["펌웨어"]), "installed": e["설치일"].strftime("%Y-%m-%d") if pd.notna(e["설치일"]) else None,
        "replaced": e["최근교체일"].strftime("%Y-%m-%d") if pd.notna(e["최근교체일"]) else None,
        "faults": int(e["누적고장횟수"]), "note": None if pd.isna(e["비고"]) else e["비고"],
    } for _, e in rows.iterrows()]


def build_cards(data: dict, today: pd.DataFrame, cfg: dict) -> tuple[list[dict], dict]:
    site_idx = data["site"].set_index("기지국ID")
    cards, phones = [], {}
    for _, t in today.iterrows():
        sid = t["기지국ID"]
        s = site_idx.loc[sid]
        site = {
            "name": s["기지국명"], "branch": s["지사"], "addr": s["주소"],
            "install_type": s["설치형태"], "install_year": int(s["설치연도"]),
            "high_work": str(s["고소작업여부"]).strip().upper() == "Y",
            "manager": s["담당자"], "phone_masked": mask_phone(s["담당자연락처"]),
        }
        phones[sid] = str(s["담당자연락처"])

        diagnoses = []
        for sym in t["symptoms"]:
            d = infer_causes(sid, sym, data, cfg)
            d["primary"] = sym == t["primary_symptom"]
            d["materials"], d["materials_estimated"] = materials_for(d["cause"]["text"], d["equip_type"], data)
            diagnoses.append(d)

        eq = data["equip"][data["equip"]["기지국ID"] == sid]
        types = {d["equip_type"] for d in diagnoses}
        card = {
            "site_id": sid, "site": site,
            "today": {k: t[k] for k in ("count", "max_grade", "open", "open_alarms", "grades", "symptoms")},
            "today_window": {"first_at": str(t["first_at"]), "last_clear_at": str(t["last_clear_at"])},
            "diagnoses": diagnoses,
            "equipment": {
                "matched": _equip_view(eq[eq["장비구분"].isin(types)]),
                "reference_only": _equip_view(eq[~eq["장비구분"].isin(types)]),
            },
            "cautions": cautions_for(site, {d["family"] for d in diagnoses}),
        }
        cat, reason = classify(card, cfg)
        card.update(category_key=cat, category=CATEGORIES[cat], category_reason=reason, score=score(card, cfg))
        cards.append(card)
    cards.sort(key=lambda c: ("ryg".index(c["category_key"]), -c["score"], c["site_id"]))
    return cards, phones


# ---------- 분석 탭 (§4.6, §4.7) ----------
def repeat_ranking(data: dict, cards: list[dict], top: int = 20) -> list[dict]:
    h = data["hist"]
    today_cnt = {c["site_id"]: c["today"]["count"] for c in cards}
    names = data["site"].set_index("기지국ID")
    rows = []
    for sid, g in h.groupby("기지국ID"):
        rows.append({
            "site_id": sid, "name": names.loc[sid, "기지국명"] if sid in names.index else "",
            "branch": names.loc[sid, "지사"] if sid in names.index else "",
            "count": len(g), "recur_rate": round((g["재발여부"] == "Y").mean(), 2),
            "top_cause": _pick_cause(g), "today": today_cnt.get(sid, 0),
        })
    rows.sort(key=lambda r: (-r["count"], -r["recur_rate"], r["site_id"]))
    return rows[:top]


def firmware_compare(data: dict, cfg: dict) -> dict:
    eq = data["equip"].copy()
    alarm_keys = set(zip(data["alarm"]["기지국ID"], data["alarm"]["증상장비"]))
    hist = data["hist"]
    eq["_today"] = [(s, t) in alarm_keys for s, t in zip(eq["기지국ID"], eq["장비구분"])]
    yr = eq["설치일"].dt.year
    eq["_age_bucket"] = pd.cut(yr, [0, 2015, 2020, 9999], labels=["≤2015", "2016–2020", "≥2021"]).astype(str)
    eq["_fw"] = eq["제조사"] + " · " + eq["모델"].astype(str) + " · " + eq["펌웨어"].astype(str)
    overall = eq["누적고장횟수"].mean()
    cc = cfg["compare"]

    def group(key: str) -> list[dict]:
        out = []
        for k, g in eq.groupby(key):
            row = {"group": k, "n": len(g)}
            if len(g) < cc["min_group"]:
                row.update(small=True)
            else:
                keys = set(zip(g["기지국ID"], g["장비구분"]))
                hh = hist[[(s, t) in keys for s, t in zip(hist["기지국ID"], hist["증상장비"])]]
                mean = g["누적고장횟수"].mean()
                row.update(small=False, mean_faults=round(mean, 2), today_ratio=round(g["_today"].mean(), 2),
                           top_cause=_pick_cause(hh) if len(hh) else None,
                           flag=bool(overall and mean >= overall * cc["ratio_flag"]))
            out.append(row)
        out.sort(key=lambda r: (r["small"], -r.get("mean_faults", 0), -r["n"]))
        return out

    return {"overall_mean_faults": round(overall, 2), "firmware": group("_fw"), "age": group("_age_bucket")}


# ---------- 6. render ----------
def _md_dx(d: dict, head: str) -> list[str]:
    c, h = d["cause"], d["history"]
    meta = (f"{c['n']}/{c['total']}건 근거" if c["level"] == "L1"
            else f"전국 {c['total']}건 중 {c['ratio']:.0%}" if c["level"] == "L2" else "근거 부족")
    lines = [f"## {head}: {d['symptom']} ({d['equip_type']})", "",
             f"- 과거 동일 증상: **{h['same_symptom']}회** (최근 90일 {h['last_90d']}회, 재발 Y {h['recur_y']}회)",
             f"- 유력 원인: **{c['text']}** `[{c['label']}]` — {meta}"]
    if d["signals"]:
        lines.append(f"- 보조 신호: {' '.join(d['signals'])}")
    lines.append("- 근거:")
    for e in d["evidence"]:
        if e.get("summary"):
            lines.append(f"  - {e['src']}: {e['summary']}")
        else:
            lines.append(f"  - {e['src']} 행 {e['row']} · {e['date']} · {e['cause']} → {e['action']}"
                         f" (재발 {e['recur']}, {e['worker']})")
    lines.append(f"- 자재{' `[추정 · 기본세트]`' if d['materials_estimated'] else ''}: {', '.join(d['materials'])}")
    return lines + [""]


def render_md(card: dict) -> str:
    s, t = card["site"], card["today"]
    em = CAT_EMOJI[card["category_key"]]
    lines = [f"# {em} {s['name']} ({card['site_id']}) — {card['category']}", "",
             f"- {s['branch']} · {s['addr']} · {s['install_type']} · 고소작업 {'Y' if s['high_work'] else 'N'}",
             f"- 담당: {s['manager']} {s['phone_masked']}",
             f"- 분류 사유: {card['category_reason']} · 점수 {card['score']}", "",
             "## 오늘 알람", "",
             f"- {t['count']}건 · 최고 {t['max_grade']} · 미해제 {t['open']}건",
             f"- 증상: {', '.join(f'{k}×{v}' for k, v in t['symptoms'].items())}", ""]
    for d in card["diagnoses"]:
        lines += _md_dx(d, "대표 증상" if d["primary"] else "추가 증상")
    lines += ["## 장비", ""]
    eqs = card["equipment"]["matched"]
    if eqs:
        lines += [f"- {e['type']} · {e['vendor']} {e['model']} · FW {e['fw']} · 설치 {e['installed']}"
                  f"{' · 교체 ' + e['replaced'] if e['replaced'] else ''} · 누적고장 {e['faults']}"
                  f"{' · ' + e['note'] if e['note'] else ''}" for e in eqs]
    else:
        lines.append("- ⚠️ 관련 장비 이력 없음"
                     + (f" (기지국 기타 장비 {len(card['equipment']['reference_only'])}건 참고)"
                        if card["equipment"]["reference_only"] else ""))
    lines += ["", "## 주의사항", ""] + ([f"- {c}" for c in card["cautions"]] or ["- 특이사항 없음"])
    return "\n".join(lines) + "\n"


def render_index(cards: list[dict]) -> str:
    lines = ["# 출동 전 브리핑 목록", "",
             " · ".join(f"{CAT_EMOJI[k]} {v} {sum(c['category_key'] == k for c in cards)}곳"
                        for k, v in CATEGORIES.items()), "",
             "| 분류 | 점수 | 기지국 | 지사 | 대표 증상 | 유력 원인 | 사유 |", "|---|---|---|---|---|---|---|"]
    for c in cards:
        p = next(d for d in c["diagnoses"] if d["primary"])
        lines.append(f"| {CAT_EMOJI[c['category_key']]} | {c['score']} | [{c['site']['name']}]({c['site_id']}.md) "
                     f"| {c['site']['branch']} | {p['symptom']} | {p['cause']['text']} ({p['cause']['label']}) "
                     f"| {c['category_reason']} |")
    return "\n".join(lines) + "\n"


def render(cards: list[dict], phones: dict, analysis: dict, quality: dict, cfg: dict, out: Path) -> None:
    """briefing.json / cards/*.md / app.json(FE·BE용 전체 데이터) (SPEC §5)."""
    (out / "briefing.json").write_text(
        json.dumps(cards, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    cards_dir = out / "cards"
    for old in cards_dir.glob("*.md"):
        old.unlink()
    for c in cards:
        (cards_dir / f"{c['site_id']}.md").write_text(render_md(c), encoding="utf-8")
    (cards_dir / "index.md").write_text(render_index(cards), encoding="utf-8")

    payload = {"base_date": str(cfg["base_date"]), "cards": cards, "phones": phones,
               "analysis": analysis, "quality": quality, "mask_phone": cfg["privacy"]["mask_phone"]}
    (out / "app.json").write_text(json.dumps(payload, ensure_ascii=False, default=str), encoding="utf-8")


# ---------- main ----------
def run(cfg: dict) -> list[dict]:
    out = ROOT / cfg["paths"]["out_dir"]
    (out / "cards").mkdir(parents=True, exist_ok=True)
    data = load_data(cfg)
    normalize(data)
    today = summarize_today(data["alarm"])
    (out / "quality_report.md").write_text(quality_report(data, today), encoding="utf-8")
    cards, phones = build_cards(data, today, cfg)
    analysis = {"ranking": repeat_ranking(data, cards), "compare": firmware_compare(data, cfg)}
    ids = set(today["기지국ID"])
    quality = {
        "sites": len(ids), "no_site": len(ids - set(data["site"]["기지국ID"])),
        "no_equip": len(ids - set(data["equip"]["기지국ID"])), "no_hist": len(ids - set(data["hist"]["기지국ID"])),
        "alarm_names": int(data["alarm"]["알람명"].nunique()), "groups": int(data["alarm"]["증상그룹"].nunique()),
    }
    render(cards, phones, analysis, quality, cfg, out)
    return cards


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config.yaml"))
    args = ap.parse_args()
    cfg = load_config(Path(args.config))
    try:
        cards = run(cfg)
    except BuildError as e:
        print(f"❌ 빌드 실패: {e}", file=sys.stderr)
        return 1
    cnt = {k: sum(c["category_key"] == k for c in cards) for k in CATEGORIES}
    lv = pd.Series([d["cause"]["level"] for c in cards for d in c["diagnoses"]]).value_counts().to_dict()
    print(f"✅ 카드 {len(cards)}장 · 🔴 {cnt['r']} 🟡 {cnt['y']} 🟢 {cnt['g']} · 원인 {lv}")
    print(f"   → {ROOT / cfg['paths']['out_dir']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
