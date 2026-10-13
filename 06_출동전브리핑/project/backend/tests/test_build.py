"""SPEC §7 인수 기준 테스트. 실행: python -m pytest tests"""
import json
import re
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402

PHONE_RE = re.compile(r"\b01\d-\d{3,4}-\d{4}\b")


@pytest.fixture(scope="module")
def ctx():
    cfg = build.load_config(build.ROOT / "config.yaml")
    data = build.load_data(cfg)
    build.normalize(data)
    today = build.summarize_today(data["alarm"])
    return cfg, data, today


@pytest.fixture(scope="module")
def cards(ctx):
    cfg = ctx[0]
    return build.run(cfg)


@pytest.fixture(scope="module")
def out_dir(ctx, cards):
    return build.ROOT / ctx[0]["paths"]["out_dir"]


# ---------- 정규화 · 조인 ----------
def test_no_unmapped_alarm_names(ctx):
    _, data, _ = ctx
    assert data["alarm"]["증상그룹"].notna().all()
    assert data["hist"]["증상그룹"].notna().all()


def test_unmapped_alarm_fails_build(ctx):
    cfg, data, _ = ctx
    d = {k: v.copy() for k, v in data.items() if isinstance(v, pd.DataFrame)}
    d["alarm"].loc[0, "알람명"] = "UNKNOWN ALARM X"
    with pytest.raises(build.BuildError, match="UNKNOWN ALARM X"):
        build.normalize(d)


def test_all_alarm_sites_summarized(ctx):
    _, data, today = ctx
    assert set(today["기지국ID"]) == set(data["alarm"]["기지국ID"])


def test_quality_report_counts(ctx):
    _, data, today = ctx
    rep = build.quality_report(data, today)
    assert "장비이력 미매칭: 71곳" in rep
    assert "조치이력 미매칭: 44곳" in rep


def test_mask_phone():
    assert build.mask_phone("010-1234-5678") == "010-****-5678"


# ---------- 인수 기준 (§7) ----------
def test_card_per_alarm_site(ctx, cards, out_dir):
    _, data, _ = ctx
    ids = set(data["alarm"]["기지국ID"])
    assert {c["site_id"] for c in cards} == ids
    assert {p.stem for p in (out_dir / "cards").glob("*.md")} - {"index"} == ids


def test_every_today_symptom_diagnosed(ctx, cards):
    _, data, _ = ctx
    expected = data["alarm"].groupby("기지국ID")["증상그룹"].apply(set).to_dict()
    for c in cards:
        assert {d["symptom"] for d in c["diagnoses"]} == expected[c["site_id"]]
        assert sum(d["primary"] for d in c["diagnoses"]) == 1


def test_l1_evidence_matches_source(ctx, cards):
    """L1 근거 행이 원본 조치이력과 100% 일치."""
    raw = pd.read_excel(build.ROOT / ctx[0]["paths"]["history"])
    sm = ctx[1]["symptom_map"].assign(_k=lambda d: d["원본명"].str.strip().str.upper()).set_index("_k")["증상그룹"]
    checked = 0
    for c in cards:
        for d in c["diagnoses"]:
            if d["cause"]["level"] != "L1":
                continue
            assert d["evidence"], c["site_id"]
            assert any(e["cause"] == d["cause"]["text"] for e in d["evidence"])
            for e in d["evidence"]:
                r = raw.iloc[e["row"] - 2]
                assert r["기지국ID"] == c["site_id"]
                assert sm[r["증상"].strip().upper()] == d["symptom"]
                assert r["실제원인"] == e["cause"] and r["조치내용"] == e["action"]
                assert str(pd.to_datetime(r["조치일"]).date()) == e["date"]
                checked += 1
    assert checked > 0


def test_l1_cause_is_mode(cards):
    for c in cards:
        for d in c["diagnoses"]:
            if d["cause"]["level"] == "L1":
                counts = pd.Series([e["cause"] for e in d["evidence"]]).value_counts()
                assert counts[d["cause"]["text"]] == counts.max()


def test_no_unlabeled_guess(cards):
    """L1이 아닌 원인은 모두 '추정' 라벨, L1은 근거행 보유."""
    for c in cards:
        for d in c["diagnoses"]:
            lv, label = d["cause"]["level"], d["cause"]["label"]
            if lv == "L1":
                assert "추정" not in label and all(e["row"] for e in d["evidence"])
            else:
                assert "추정" in label
                assert d["history"]["same_symptom"] == 0


def test_l2_thresholds(ctx, cards):
    ic = ctx[0]["inference"]
    for c in cards:
        for d in c["diagnoses"]:
            cz = d["cause"]
            if cz["level"] == "L2":
                assert cz["total"] >= ic["l2_min"] and cz["ratio"] >= ic["l2_min_ratio"]


def test_open_critical_is_red(cards):
    for c in cards:
        if any(a["등급"] == "Critical" for a in c["today"]["open_alarms"]):
            assert c["category_key"] == "r", c["site_id"]


def test_category_rules(cards):
    for c in cards:
        if c["category_key"] == "g":
            assert c["today"]["max_grade"] in ("Minor", "Warning")
            assert not any(d["remote"] for d in c["diagnoses"])
            assert max(c["today"]["symptoms"].values()) < 3
        assert c["category_reason"]


def test_high_work_has_safety_caution(cards):
    for c in cards:
        has = any("고소작업" in x for x in c["cautions"])
        assert has == c["site"]["high_work"], c["site_id"]


def test_materials_never_empty(cards):
    for c in cards:
        for d in c["diagnoses"]:
            assert d["materials"], (c["site_id"], d["cause"]["text"])


def test_no_unmasked_phone_in_outputs(out_dir):
    files = [out_dir / "briefing.json", *(out_dir / "cards").glob("*.md")]
    for f in files:
        assert not PHONE_RE.search(f.read_text(encoding="utf-8")), f.name


def test_app_json_has_data(out_dir, cards):
    payload = json.loads((out_dir / "app.json").read_text(encoding="utf-8"))
    assert len(payload["cards"]) == len(cards)


def test_cards_sorted(cards):
    keys = [("ryg".index(c["category_key"]), -c["score"]) for c in cards]
    assert keys == sorted(keys)


# ---------- 단위 ----------
def test_score_formula(ctx):
    cfg = ctx[0]
    card = {"today": {"grades": ["Critical", "Minor"], "open": 1},
            "diagnoses": [{"history": {"same_symptom": 15, "recur_y": 2}}]}
    assert build.score(card, cfg) == 4 + 2 + 5 + 10 * 2 + 2 * 3


def test_materials_fallback(ctx):
    data = ctx[1]
    assert build.materials_for("SFP 불량", "광모듈", data) == (["SFP 예비품", "광파워미터", "광 클리너"], False)
    mats, guess = build.materials_for("원인 미상(자연복구)", "RU", data)
    assert guess and "RU 예비품" in mats
    assert build.materials_for("없는 원인", "DU", data)[1] is True


def test_firmware_signal_window(ctx):
    cfg = ctx[0]
    eq = pd.DataFrame([
        {"비고": "2026-09 펌웨어 업그레이드", "누적고장횟수": 0, "설치일": pd.Timestamp("2024-01-01"), "최근교체일": pd.NaT},
        {"비고": "2026-03 펌웨어 업그레이드", "누적고장횟수": 3, "설치일": pd.Timestamp("2010-01-01"), "최근교체일": pd.NaT},
    ])
    sig = build.equipment_signals(eq, cfg)
    assert any("2026-09" in s for s in sig)
    assert not any("2026-03" in s for s in sig)
    assert any("고장多" in s for s in sig) and any("노후" in s for s in sig)


def test_aging_uses_replacement_date(ctx):
    eq = pd.DataFrame([{"비고": None, "누적고장횟수": 0, "설치일": pd.Timestamp("2010-01-01"),
                        "최근교체일": pd.Timestamp("2025-01-01")}])
    assert not any("노후" in s for s in build.equipment_signals(eq, ctx[0]))
