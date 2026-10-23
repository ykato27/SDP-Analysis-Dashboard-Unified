"""legacy_adapter の単体テスト。

特に「平均スキル予測値が拠点ごとの定数である」ことと、
推移判定を行ってよいかを決める has_skill_trend の挙動を固定する。
（定数の系列に対してモニタリング画面が常時「低下」と表示していた問題の回帰防止）
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from legacy_adapter import (
    SKILL_COLUMNS,
    build_daily_prod_df,
    build_skill_df,
    has_skill_trend,
    pick_priority_skill,
)


def make_employee():
    return pd.DataFrame(
        {
            "従業員ID": ["E1", "E2", "E3"],
            "拠点": ["拠点A", "拠点A", "拠点B"],
            "ライン": ["高炉1号", "高炉1号", "高炉2号"],
            "シフト": ["A班", "B班", "A班"],
            "総合スキルスコア": [3.0, 4.0, 5.0],
            "生産効率_個人": [90.0, 95.0, 99.0],
            "品質不良率_個人": [1.0, 2.0, 0.5],
            **{col: [3.0, 4.0, 5.0] for col in SKILL_COLUMNS},
        }
    )


def make_production():
    return pd.DataFrame(
        {
            "日付": ["2025-04-12", "2025-04-13", "2025-04-12"],
            "拠点": ["拠点A", "拠点A", "拠点B"],
            "ライン": ["高炉1号", "高炉1号", "高炉2号"],
            "シフト": ["A班", "A班", "A班"],
            "生産量_ton": [100.0, 110.0, 200.0],
            "生産効率_指数": [90.0, 92.0, 98.0],
            "品質不良率": [1.0, 1.5, 0.5],
            "歩留まり": [95.0, 96.0, 97.0],
        }
    )


def test_build_skill_df_renames_columns():
    out = build_skill_df(make_employee())
    assert out.loc[0, "組織・チーム"] == "高炉1号"
    assert out.loc[0, "生産効率 (%)"] == 90.0
    assert out.loc[0, "品質不良率 (%)"] == 1.0


def test_build_daily_prod_df_skill_is_location_constant():
    out = build_daily_prod_df(make_production(), make_employee())
    # 拠点Aの平均は (3.0+4.0)/2=3.5 で、日付が変わっても不変
    a = out[out["拠点"] == "拠点A"]["平均スキル予測値"]
    assert a.tolist() == [3.5, 3.5]
    b = out[out["拠点"] == "拠点B"]["平均スキル予測値"]
    assert b.tolist() == [5.0]
    # 列名変換と別名
    assert out.loc[0, "日次生産量 (t)"] == 100.0
    assert out.loc[0, "日次生産量 (Unit)"] == 100.0
    assert out.loc[0, "生産効率 (%)"] == 90.0


def test_has_skill_trend_rejects_constant_series():
    # 回帰防止: 定数系列では推移判定をしてはいけない
    assert has_skill_trend(pd.Series([3.5, 3.5, 3.5])) is False
    assert has_skill_trend(pd.Series([3.5, None, 3.5])) is False
    assert has_skill_trend(pd.Series([3.0, 3.5, 4.0])) is True


def test_pick_priority_skill_uses_max_gap():
    bn = pd.DataFrame(
        {
            "拠点": ["拠点A", "拠点A"],
            "スキルカテゴリ": ["操炉技術", "安全管理"],
            "スキルギャップ": [0.5, 1.8],
        }
    )
    assert pick_priority_skill(bn, make_employee(), "拠点A") == "安全管理"


def test_pick_priority_skill_fallback_lowest_mean():
    bn = pd.DataFrame({"拠点": [], "スキルカテゴリ": [], "スキルギャップ": []})
    # make_employee では全スキル列が同値なので、最低平均の列は先頭列と同点。
    # 拠点Bのみに絞ると値がすべて5.0で同点 -> idxmin は先頭を返す
    result = pick_priority_skill(bn, make_employee(), "拠点B")
    assert result in SKILL_COLUMNS


def test_pick_priority_skill_no_data_returns_default_with_warning(caplog):
    bn = pd.DataFrame({"拠点": [], "スキルカテゴリ": [], "スキルギャップ": []})
    emp = make_employee()
    with caplog.at_level("WARNING"):
        result = pick_priority_skill(bn, emp, "存在しない拠点")
    assert result == SKILL_COLUMNS[0]
    assert "存在しない拠点" in caplog.text


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
