"""統合版スモークテスト: 全ページを AppTest で実行し、例外が出ないか確認する。"""
import sys
sys.path.insert(0, ".")
from streamlit.testing.v1 import AppTest

PAGES = [
    "🌍 STEP 1: 全社俯瞰",
    "🏭 STEP 2: 拠点内比較",
    "🎯 STEP 3: スキル構造",
    "📊 STEP 4: 相関分析",
    "🔍 STEP 5: ボトルネック",
    "👥 STEP 6: 個人・チーム",
    "📚 STEP 7: 教育効果",
    "📊 STEP 8: 改善効果",
    "🏆 STEP 9: ベンチマーク",
    "📊 STEP 10: 経営KPI",
    "📋 アクションプラン",
    "📉 継続モニタリング",
    "📁 生データ閲覧",
]

failed = 0
for page in PAGES:
    at = AppTest.from_file("app.py", default_timeout=120)
    at.run()
    # サイドバーのラジオ（ページ選択）を対象ページに切り替えて再実行
    for radio in at.radio:
        if set(radio.options) == set(PAGES):
            radio.set_value(page)
            break
    at.run()
    if at.exception:
        failed += 1
        print(f"FAIL {page}: {at.exception[0].value!r}")
    else:
        print(f"OK   {page}")

print("RESULT:", "ALL OK" if failed == 0 else f"{failed} pages failed")
sys.exit(1 if failed else 0)
