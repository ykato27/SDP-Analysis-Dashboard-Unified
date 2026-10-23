import streamlit as st
import pandas as pd

def show_raw_data(df_skill, df_daily_prod):
    """元データの閲覧とダウンロード"""
    
    st.markdown("""
    <div class="header-container">
        <div class="header-title">📁 生データ閲覧</div>
        <div class="header-subtitle">元データの参照・フィルタリング・ダウンロード</div>
    </div>
    """, unsafe_allow_html=True)
    
    # データタイプ選択
    data_type = st.radio(
        "表示データ",
        ["従業員スキルデータ", "日次生産データ"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if data_type == "従業員スキルデータ":
        st.markdown("""
        <div class="section-header">
            <h2 class="section-title">👥 従業員スキルデータ</h2>
            <p class="section-subtitle">全拠点の従業員スキル評価データ</p>
        </div>
        """, unsafe_allow_html=True)
        
        # フィルタリングオプション
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            selected_locations = st.multiselect(
                "拠点フィルタ",
                options=df_skill['拠点'].unique().tolist(),
                default=df_skill['拠点'].unique().tolist()
            )
        
        with col_filter2:
            selected_teams = st.multiselect(
                "組織・チームフィルタ",
                options=df_skill['組織・チーム'].unique().tolist(),
                default=df_skill['組織・チーム'].unique().tolist()
            )
        
        with col_filter3:
            selected_shifts = st.multiselect(
                "シフトフィルタ",
                options=df_skill['シフト'].unique().tolist(),
                default=df_skill['シフト'].unique().tolist()
            )
        
        # フィルタリング適用
        df_filtered = df_skill[
            df_skill['拠点'].isin(selected_locations) &
            df_skill['組織・チーム'].isin(selected_teams) &
            df_skill['シフト'].isin(selected_shifts)
        ].copy()
        
        # データサマリー
        col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
        
        with col_sum1:
            st.metric("フィルタ後の従業員数", f"{len(df_filtered)}名")
        
        with col_sum2:
            avg_skill = df_filtered['総合スキルスコア'].mean()
            st.metric("平均スキルスコア", f"{avg_skill:.2f}")
        
        with col_sum3:
            avg_efficiency = df_filtered['生産効率 (%)'].mean()
            st.metric("平均生産効率", f"{avg_efficiency:.1f}%")
        
        with col_sum4:
            avg_defect = df_filtered['品質不良率 (%)'].mean()
            st.metric("平均品質不良率", f"{avg_defect:.2f}%")
        
        st.markdown("---")
        
        # データテーブル表示
        st.dataframe(
            df_filtered,
            use_container_width=True,
            height=500
        )
        
        # ダウンロードボタン
        csv_skill = df_filtered.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 フィルタ済みデータをCSVダウンロード",
            data=csv_skill,
            file_name=f"skill_data_filtered.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # データ説明
        with st.expander("📚 データ項目の説明"):
            st.markdown("""
            | 項目名 | 説明 |
            |--------|------|
            | 拠点 | 製造拠点の所在地（日本、タイ、米国、メキシコ） |
            | 組織・チーム | 所属する組織・チーム（T1:成形、T2:加工、T3:組立、T4:検査） |
            | シフト | 勤務シフト（日勤、夜勤） |
            | 従業員ID | 従業員の一意識別子 |
            | 評価日 | スキル評価を実施した日付 |
            | 成形技術 | 成形工程の難易度設定能力（1-5段階） |
            | NCプログラム | 加工工程のプログラム作成・修正能力（1-5段階） |
            | 品質検査 | 製品の最終検査基準の遵守と判断能力（1-5段階） |
            | 設備保全 | 日常的な設備点検と簡易修理能力（1-5段階） |
            | 安全管理 | 危険予知・手順遵守能力（1-5段階） |
            | 総合スキルスコア | 上記5スキルの平均値 |
            | 生産効率 (%) | 標準時間に対する実際の生産効率 |
            | 品質不良率 (%) | 全生産数に対する不良品の割合 |
            """)
    
    else:  # 日次生産データ
        st.markdown("""
        <div class="section-header">
            <h2 class="section-title">📊 日次生産データ</h2>
            <p class="section-subtitle">過去30日間の生産実績データ</p>
        </div>
        """, unsafe_allow_html=True)
        
        # フィルタリングオプション
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            selected_locations_daily = st.multiselect(
                "拠点フィルタ",
                options=df_daily_prod['拠点'].unique().tolist(),
                default=df_daily_prod['拠点'].unique().tolist(),
                key="daily_location_filter"
            )
        
        with col_filter2:
            selected_shifts_daily = st.multiselect(
                "シフトフィルタ",
                options=df_daily_prod['シフト'].unique().tolist(),
                default=df_daily_prod['シフト'].unique().tolist(),
                key="daily_shift_filter"
            )
        
        # フィルタリング適用
        df_daily_filtered = df_daily_prod[
            df_daily_prod['拠点'].isin(selected_locations_daily) &
            df_daily_prod['シフト'].isin(selected_shifts_daily)
        ].copy()
        
        # データサマリー
        col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
        
        with col_sum1:
            st.metric("データ件数", f"{len(df_daily_filtered)}件")
        
        with col_sum2:
            avg_production = df_daily_filtered['日次生産量 (Unit)'].mean()
            st.metric("平均日次生産量", f"{avg_production:,.0f} Unit")
        
        with col_sum3:
            avg_efficiency_daily = df_daily_filtered['生産効率 (%)'].mean()
            st.metric("平均生産効率", f"{avg_efficiency_daily:.1f}%")
        
        with col_sum4:
            avg_defect_daily = df_daily_filtered['品質不良率 (%)'].mean()
            st.metric("平均品質不良率", f"{avg_defect_daily:.2f}%")
        
        st.markdown("---")
        
        # データテーブル表示
        st.dataframe(
            df_daily_filtered.sort_values('日付', ascending=False),
            use_container_width=True,
            height=500
        )
        
        # ダウンロードボタン
        csv_daily = df_daily_filtered.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 フィルタ済みデータをCSVダウンロード",
            data=csv_daily,
            file_name=f"daily_production_data_filtered.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # データ説明
        with st.expander("📚 データ項目の説明"):
            st.markdown("""
            | 項目名 | 説明 |
            |--------|------|
            | 日付 | 生産実績の日付 |
            | 拠点 | 製造拠点の所在地 |
            | シフト | 勤務シフト（日勤、夜勤） |
            | 日次生産量 (Unit) | その日の総生産数量 |
            | 生産効率 (%) | 標準時間に対する実際の生産効率 |
            | 品質不良率 (%) | 全生産数に対する不良品の割合 |
            | 平均スキル予測値 | 拠点の従業員スキル平均（評価時点の参考値。日次では変動しない） |
            """)
    
    st.markdown("---")
    
    # データ活用のヒント
    st.info(
        "💡 **データ活用のヒント**:\n\n"
        "- **従業員スキルデータ**: 特定のスキルが低い従業員を抽出し、個別の教育計画を立案\n"
        "- **日次生産データ**: 生産効率が低下した日のシフトメンバーを特定し、原因を分析\n"
        "- **組み合わせ分析**: スキルデータと生産データを紐付けて、スキルと生産性の相関を検証",
        icon="📊"
    )
    
    # 他の分析への誘導
    st.markdown("---")
    
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    
    with col_nav1:
        if st.button("📊 エグゼクティブサマリー", use_container_width=True):
            st.session_state.selected_menu = "📊 エグゼクティブサマリー"
            st.rerun()
    
    with col_nav2:
        if st.button("🔬 根本原因分析", use_container_width=True):
            st.session_state.selected_menu = "🔬 根本原因分析"
            st.rerun()
    
    with col_nav3:
        if st.button("📋 アクションプラン", use_container_width=True):
            st.session_state.selected_menu = "📋 アクションプラン"
            st.rerun()