"""
legacy_adapter.py
v1（SDP-Analysis-Dashboard）由来の画面モジュールが期待する
データ形式へ、v2のデータフレームを変換するアダプタ。

v1の画面（action_plan / monitoring / raw_data）は以下の列名を前提にしている:
  df_skill:      拠点, 組織・チーム, シフト, 総合スキルスコア,
                 生産効率 (%), 品質不良率 (%), およびスキル列（数値）
  df_daily_prod: 日付, 拠点, シフト, 日次生産量 (t) / (Unit),
                 生産効率 (%), 品質不良率 (%), 平均スキル予測値

v2の実データとの対応:
  従業員スキル: 生産効率_個人 -> 生産効率 (%), 品質不良率_個人 -> 品質不良率 (%)
                ライン -> 組織・チーム（v1のチーム概念に対応付け）
  日次生産:     生産量_ton -> 日次生産量, 生産効率_指数 -> 生産効率 (%),
                品質不良率 -> 品質不良率 (%),
                平均スキル予測値 は拠点別の従業員スキル平均で補完する

注意（平均スキル予測値の意味）:
  従業員スキルデータの評価日は単一時点しかないため、日別のスキル推移は
  元データに存在しない。平均スキル予測値 は拠点ごとに不変の「参考値」
  （評価時点の拠点平均）であり、日次で変動する実測値ではない。
  呼び出し側は has_skill_trend() で変動の有無を確認し、変動がない場合は
  スキルの推移判定（向上／低下）を行わないこと。
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)

# v2のスキルカテゴリ列（そのまま v1 の「スキル列」として使う）
SKILL_COLUMNS = ["操炉技術", "成分制御", "異常対応", "設備保全", "品質検査", "安全管理"]


def build_skill_df(df_employee: pd.DataFrame) -> pd.DataFrame:
    """v2の従業員データを v1形式の df_skill に変換する。"""
    df = df_employee.copy()
    df["組織・チーム"] = df["ライン"]
    df = df.rename(columns={
        "生産効率_個人": "生産効率 (%)",
        "品質不良率_個人": "品質不良率 (%)",
    })
    return df


def build_daily_prod_df(df_production: pd.DataFrame, df_employee: pd.DataFrame) -> pd.DataFrame:
    """v2の日次生産データを v1形式の df_daily_prod に変換する。"""
    df = df_production.copy()
    df = df.rename(columns={
        "生産量_ton": "日次生産量 (t)",
        "生産効率_指数": "生産効率 (%)",
        "品質不良率": "品質不良率 (%)",
        "歩留まり": "歩留まり (%)",
    })
    # raw_data 側が参照する別名も用意する
    df["日次生産量 (Unit)"] = df["日次生産量 (t)"]
    df["チーム"] = df["シフト"]
    df["工程"] = df["ライン"]
    # 拠点ごとの平均スキルを「平均スキル予測値」として補完する。
    # 評価日が単一時点のため、これは日次で変動しない参考値（拠点平均）。
    loc_skill = df_employee.groupby("拠点")["総合スキルスコア"].mean().round(2)
    df["平均スキル予測値"] = df["拠点"].map(loc_skill)
    return df


def has_skill_trend(values: pd.Series) -> bool:
    """スキル系列に推移判定できる変動があるかを返す。

    ユニークな値が2つ以上ある場合のみ True。拠点平均で補完した
    平均スキル予測値 のように一定値の系列では False になり、
    呼び出し側は「低下／向上」といった推移判定をすべきではない。
    """
    return values.nunique(dropna=True) > 1


def pick_priority_skill(df_bottleneck: pd.DataFrame, df_employee: pd.DataFrame, location: str) -> str:
    """対象拠点で最も優先すべきスキルカテゴリを返す。

    ボトルネックデータのスキルギャップ最大のカテゴリを優先し、
    無ければ従業員スキル平均が最も低いカテゴリを返す。
    """
    bn = df_bottleneck[df_bottleneck["拠点"] == location]
    if not bn.empty:
        return bn.loc[bn["スキルギャップ"].idxmax(), "スキルカテゴリ"]
    emp = df_employee[df_employee["拠点"] == location]
    if not emp.empty:
        return emp[SKILL_COLUMNS].mean().idxmin()
    # データ不備時の無言フォールバックは避け、記録に残す
    logger.warning(
        "pick_priority_skill: 拠点 %s のボトルネック／従業員データが無いため既定値 %s を返します",
        location,
        SKILL_COLUMNS[0],
    )
    return SKILL_COLUMNS[0]
