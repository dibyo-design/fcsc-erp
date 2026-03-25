import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import datetime

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FCSC ERP",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── THEME ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Base */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background-color: #F7F8FA; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #1A1A2E;
    padding-top: 1rem;
}
section[data-testid="stSidebar"] * { color: #E0E0E0 !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] p { color: #A0A8B8 !important; font-size: 13px; }
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { color: #E0E0E0 !important; }

/* Headings */
h1 { color: #C00000 !important; font-size: 1.8rem !important; font-weight: 700 !important; }
h2 { color: #1A1A2E !important; font-size: 1.3rem !important; font-weight: 600 !important; }
h3 { color: #333 !important; font-size: 1.05rem !important; font-weight: 600 !important; }

/* KPI Metric Cards */
div[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #E8EAF0;
    border-top: 3px solid #C00000;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
div[data-testid="metric-container"] label { font-size: 12px !important; color: #888 !important; text-transform: uppercase; letter-spacing: 0.05em; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] { font-size: 1.6rem !important; font-weight: 700 !important; color: #1A1A2E !important; }

/* Buttons */
.stButton > button {
    background-color: #C00000;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.4rem;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.02em;
    transition: background 0.2s;
}
.stButton > button:hover { background-color: #A00000; color: white; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: #EEF0F6; border-radius: 10px; padding: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 0.4rem 1rem; font-size: 14px; font-weight: 500; color: #555; }
.stTabs [aria-selected="true"] { background-color: #ffffff !important; color: #C00000 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }

/* Inputs */
.stTextInput input, .stNumberInput input, .stDateInput input {
    border-radius: 8px !important;
    border: 1px solid #DDE1EA !important;
    font-size: 14px !important;
}
.stTextInput input:focus, .stNumberInput input:focus { border-color: #C00000 !important; box-shadow: 0 0 0 2px rgba(192,0,0,0.1) !important; }

/* Dividers */
hr { border: none; border-top: 1px solid #E8EAF0; margin: 1.5rem 0; }

/* Success / Warning / Error */
.stSuccess { border-radius: 8px; }
.stWarning { border-radius: 8px; }
.stError { border-radius: 8px; }

/* Dataframe */
.stDataFrame { border-radius: 10px; border: 1px solid #E8EAF0; overflow: hidden; }

/* Section cards */
.section-card {
    background: white;
    border: 1px solid #E8EAF0;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
}
</style>
""", unsafe_allow_html=True)

# ── FILE PATHS ────────────────────────────────────────────────────────────────
PROD_FILE  = "production.csv"
SAND_FILE  = "sand.csv"
STOCK_FILE = "stock.csv"

# ── HELPERS ───────────────────────────────────────────────────────────────────
def load_data(file, cols):
    if os.path.exists(file):
        df = pd.read_csv(file)
        for col in cols:
            if col not in df.columns:
                df[col] = 0
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.normalize()
        return df
    return pd.DataFrame(columns=cols)

def save_csv(df, path):
    df.to_csv(path, index=False)

def format_number(n, decimals=0):
    if pd.isna(n):
        return "—"
    return f"{n:,.{decimals}f}"

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
prod_df  = load_data(PROD_FILE,  ["Date","Factory","Product","Labour","Hours","Production","Efficiency"])
sand_df  = load_data(SAND_FILE,  ["Date","Factory","Sand","Efficiency"])
stock_df = load_data(STOCK_FILE, ["Date","Factory","Product","Material","Received","Used","Closing_Stock"])

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 0.5rem 0 1.5rem;'>
        <div style='font-size:2rem;'>🏭</div>
        <div style='font-size:1.1rem; font-weight:700; color:#fff; letter-spacing:0.05em;'>FCSC ERP</div>
        <div style='font-size:11px; color:#6C7A99; margin-top:2px;'>Factory Management System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    factory = st.selectbox(
        "Active Factory",
        ["Belda", "Mogra", "Singur", "Siliguri"],
        key="factory_select"
    )

    st.markdown("---")

    view = st.radio(
        "Section",
        ["📥  Data Entry", "📊  Analysis"],
        key="view_select"
    )

    st.markdown("---")

    st.markdown("<p style='font-size:12px; color:#6C7A99; margin-bottom:6px;'>DATE RANGE</p>", unsafe_allow_html=True)

    if not prod_df.empty and "Date" in prod_df.columns:
        try:
            valid_dates = prod_df["Date"].dropna()
            min_d = valid_dates.min().date()
            max_d = valid_dates.max().date()
        except Exception:
            min_d = datetime.date(2026, 1, 1)
            max_d = datetime.date(2026, 1, 31)
    else:
        min_d = datetime.date(2026, 1, 1)
        max_d = datetime.date(2026, 1, 31)

    date_range = st.date_input("", [min_d, max_d], key="date_filter", label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"<p style='font-size:11px; color:#6C7A99; text-align:center;'>Last updated: {datetime.date.today()}</p>", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"# 🏭 FCSC ERP Dashboard")
    st.markdown(f"<p style='color:#888; font-size:14px; margin-top:-10px;'>Factory: <strong style='color:#C00000;'>{factory}</strong> &nbsp;|&nbsp; {datetime.date.today().strftime('%d %B %Y')}</p>", unsafe_allow_html=True)
with col_h2:
    if not prod_df.empty:
        total = int(prod_df["Production"].sum())
        st.metric("All-Time Production", f"{total:,}")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
#  DATA ENTRY
# ─────────────────────────────────────────────────────────────────────────────
if "Data Entry" in view:

    tab1, tab2, tab3 = st.tabs([
        "📊  Production",
        "🏗️  Sand",
        "🧱  Raw Material"
    ])

    # ── PRODUCTION ENTRY ──────────────────────────────────────────────────────
    with tab1:
        st.markdown("#### Log Production")

        with st.container():
            c1, c2, c3 = st.columns(3)
            with c1:
                date    = st.date_input("Date", key="prod_date")
                product = st.text_input("Product name", placeholder="e.g. Brick A1", key="prod_product")
            with c2:
                labour     = st.number_input("Labour (workers)", min_value=0, step=1, key="prod_labour")
                hours      = st.number_input("Hours worked", min_value=0.0, step=0.5, key="prod_hours")
            with c3:
                production = st.number_input("Units produced", min_value=0, step=1, key="prod_production")
                eff_preview = production / (labour * hours) if (labour and hours) else 0.0
                st.metric("Efficiency preview", round(eff_preview, 3))

        saved_prod = st.button("💾 Save Production Record", key="prod_save")
        if saved_prod:
            if not product.strip():
                st.warning("Please enter a product name.")
            else:
                new = pd.DataFrame([{
                    "Date": pd.Timestamp(date), "Factory": factory, "Product": product,
                    "Labour": labour, "Hours": hours,
                    "Production": production, "Efficiency": round(eff_preview, 3)
                }])
                prod_df = pd.concat([prod_df, new], ignore_index=True)
                prod_df["Date"] = pd.to_datetime(prod_df["Date"], errors="coerce").dt.normalize()
                save_csv(prod_df, PROD_FILE)
                st.success(f"✅ Saved — {production} units of {product} on {date}")

        st.markdown("---")
        st.markdown("#### Production Log")

        # Filter to factory
        disp = prod_df[prod_df["Factory"] == factory] if not prod_df.empty else prod_df
        if disp.empty:
            st.info("No production records for this factory yet.")
        else:
            st.dataframe(
                disp.sort_values("Date", ascending=False).reset_index(drop=True),
                use_container_width=True,
                height=280
            )

    # ── SAND ENTRY ────────────────────────────────────────────────────────────
    with tab2:
        st.markdown("#### Log Sand Usage")

        c1, c2 = st.columns(2)
        with c1:
            date2 = st.date_input("Date", key="sand_date")
        with c2:
            sand = st.number_input("Sand quantity (units)", min_value=0, step=1, key="sand_qty")

        if st.button("💾 Save Sand Record", key="sand_save"):
            new = pd.DataFrame([{
                "Date": pd.Timestamp(date2), "Factory": factory,
                "Sand": sand, "Efficiency": sand
            }])
            sand_df = pd.concat([sand_df, new], ignore_index=True)
            sand_df["Date"] = pd.to_datetime(sand_df["Date"], errors="coerce").dt.normalize()
            save_csv(sand_df, SAND_FILE)
            st.success(f"✅ Saved — {sand} units of sand on {date2}")

        st.markdown("---")
        st.markdown("#### Sand Log")
        disp_sand = sand_df[sand_df["Factory"] == factory] if not sand_df.empty else sand_df
        if disp_sand.empty:
            st.info("No sand records for this factory yet.")
        else:
            st.dataframe(
                disp_sand.sort_values("Date", ascending=False).reset_index(drop=True),
                use_container_width=True,
                height=280
            )

    # ── STOCK ENTRY ───────────────────────────────────────────────────────────
    with tab3:
        st.markdown("#### Log Raw Material Stock")

        c1, c2, c3 = st.columns(3)
        with c1:
            date3    = st.date_input("Date", key="stock_date")
            product3 = st.text_input("Product", placeholder="e.g. Brick A1", key="stock_product")
        with c2:
            material = st.text_input("Material name", placeholder="e.g. Clay", key="stock_material")
            received = st.number_input("Received (units)", min_value=0, step=1, key="stock_received")
        with c3:
            used = st.number_input("Used (units)", min_value=0, step=1, key="stock_used")
            # Preview closing stock
            prev_rows = stock_df[(stock_df["Factory"] == factory) & (stock_df["Material"] == material)] if not stock_df.empty else pd.DataFrame()
            last_close = int(prev_rows.iloc[-1]["Closing_Stock"]) if not prev_rows.empty else 0
            closing_preview = last_close + received - used
            st.metric("Closing stock preview", f"{closing_preview:,}")

        if st.button("💾 Save Stock Record", key="stock_save"):
            if not material.strip():
                st.warning("Please enter a material name.")
            else:
                new = pd.DataFrame([{
                    "Date": pd.Timestamp(date3), "Factory": factory, "Product": product3,
                    "Material": material, "Received": received,
                    "Used": used, "Closing_Stock": closing_preview
                }])
                stock_df = pd.concat([stock_df, new], ignore_index=True)
                stock_df["Date"] = pd.to_datetime(stock_df["Date"], errors="coerce").dt.normalize()
                save_csv(stock_df, STOCK_FILE)
                st.success(f"✅ Closing stock for {material}: {closing_preview:,} units")

        st.markdown("---")
        st.markdown("#### Stock Log")
        disp_stock = stock_df[stock_df["Factory"] == factory] if not stock_df.empty else stock_df
        if disp_stock.empty:
            st.info("No stock records for this factory yet.")
        else:
            st.dataframe(
                disp_stock.sort_values("Date", ascending=False).reset_index(drop=True),
                use_container_width=True,
                height=280
            )


# ─────────────────────────────────────────────────────────────────────────────
#  ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
if "Analysis" in view:

    if prod_df.empty:
        st.info("No production data found. Add records via Data Entry first.")
        st.stop()

    prod_df["Date"] = pd.to_datetime(prod_df["Date"], errors="coerce").dt.normalize()

    # Apply date filter (handle single-date selections)
    try:
        d_start = pd.Timestamp(date_range[0])
        d_end   = pd.Timestamp(date_range[1])
    except (IndexError, TypeError):
        d_start = prod_df["Date"].min()
        d_end   = prod_df["Date"].max()

    df = prod_df[
        (prod_df["Factory"] == factory) &
        (prod_df["Date"] >= d_start) &
        (prod_df["Date"] <= d_end)
    ].copy()

    # ── KPI CARDS ─────────────────────────────────────────────────────────────
    total_prod    = int(df["Production"].sum())
    avg_eff       = df["Efficiency"].mean() if not df.empty else 0
    total_labour  = int(df["Labour"].sum())
    avg_hours     = df["Hours"].mean() if not df.empty else 0
    record_count  = len(df)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Production",  f"{total_prod:,}")
    k2.metric("Avg Efficiency",    f"{avg_eff:.3f}")
    k3.metric("Total Labour Days", f"{total_labour:,}")
    k4.metric("Avg Hours / Entry", f"{avg_hours:.1f}")
    k5.metric("Records in Range",  record_count)

    st.markdown("---")

    if df.empty:
        st.warning("No data for the selected factory and date range.")
        st.stop()

    # ── ALERTS (inline, not buried below) ────────────────────────────────────
    latest = df.sort_values("Date").tail(1)
    if not latest.empty:
        alerts = []
        le = latest.iloc[0]
        if le["Efficiency"] < 0.5:
            alerts.append(("error", f"Low efficiency on latest entry: {le['Efficiency']:.3f}"))
        if df["Labour"].mean() > 0 and le["Labour"] > df["Labour"].mean() * 1.5:
            alerts.append(("warning", "Labour headcount unusually high in latest entry"))
        if df["Production"].mean() > 0 and le["Production"] < df["Production"].mean() * 0.7:
            alerts.append(("warning", "Production volume below 70% of average"))

        if alerts:
            st.markdown("#### ⚠️ Active Alerts")
            for kind, msg in alerts:
                if kind == "error":
                    st.error(msg)
                else:
                    st.warning(msg)
            st.markdown("---")

    # ── CHARTS ────────────────────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Production over time")
        ts = df.groupby("Date")["Production"].sum().reset_index()
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.fill_between(ts["Date"], ts["Production"], alpha=0.15, color="#C00000")
        ax.plot(ts["Date"], ts["Production"], color="#C00000", linewidth=2)
        ax.set_xlabel("Date", fontsize=10)
        ax.set_ylabel("Units", fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col_right:
        st.markdown("#### Efficiency over time")
        es = df.groupby("Date")["Efficiency"].mean().reset_index()
        fig2, ax2 = plt.subplots(figsize=(6, 3))
        ax2.fill_between(es["Date"], es["Efficiency"], alpha=0.12, color="#1A3C8B")
        ax2.plot(es["Date"], es["Efficiency"], color="#1A3C8B", linewidth=2)
        ax2.axhline(y=0.5, color="#C00000", linestyle="--", linewidth=1, label="Threshold (0.5)")
        ax2.legend(fontsize=9)
        ax2.set_xlabel("Date", fontsize=10)
        ax2.set_ylabel("Efficiency", fontsize=10)
        ax2.spines[["top", "right"]].set_visible(False)
        ax2.grid(axis="y", linestyle="--", alpha=0.4)
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    st.markdown("---")

    # ── HEATMAPS ─────────────────────────────────────────────────────────────
    st.markdown("#### Heatmaps")
    hm1, hm2 = st.columns(2)

    with hm1:
        st.markdown("**Production**")
        heat_prod = df.pivot_table(index="Product", columns="Date", values="Production", fill_value=0)
        if not heat_prod.empty:
            fig3, ax3 = plt.subplots(figsize=(7, max(2, len(heat_prod) * 0.7)))
            sns.heatmap(heat_prod, annot=True, fmt=".0f", cmap="Reds", linewidths=0.5,
                        linecolor="#eee", ax=ax3, cbar_kws={"shrink": 0.8})
            ax3.set_xlabel("")
            ax3.set_ylabel("")
            fig3.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)

    with hm2:
        st.markdown("**Efficiency**")
        heat_eff = df.pivot_table(index="Product", columns="Date", values="Efficiency", fill_value=0)
        if not heat_eff.empty:
            fig4, ax4 = plt.subplots(figsize=(7, max(2, len(heat_eff) * 0.7)))
            sns.heatmap(heat_eff, annot=True, fmt=".2f", cmap="Blues", linewidths=0.5,
                        linecolor="#eee", ax=ax4, cbar_kws={"shrink": 0.8})
            ax4.set_xlabel("")
            ax4.set_ylabel("")
            fig4.tight_layout()
            st.pyplot(fig4)
            plt.close(fig4)

    st.markdown("---")

    # ── RANKINGS ─────────────────────────────────────────────────────────────
    rank1, rank2 = st.columns(2)

    with rank1:
        st.markdown("#### Factory ranking (all time)")
        ranking = (
            prod_df
            .groupby("Factory")
            .agg(Production=("Production", "sum"), Efficiency=("Efficiency", "mean"))
            .sort_values("Efficiency", ascending=False)
            .reset_index()
        )
        ranking["Production"] = ranking["Production"].apply(lambda x: f"{int(x):,}")
        ranking["Efficiency"] = ranking["Efficiency"].apply(lambda x: f"{x:.3f}")
        st.dataframe(ranking, use_container_width=True, hide_index=True)

    with rank2:
        st.markdown(f"#### Product ranking — {factory}")
        prod_rank = (
            df.groupby("Product")
            .agg(Production=("Production","sum"), Efficiency=("Efficiency","mean"))
            .sort_values("Production", ascending=False)
            .reset_index()
        )
        prod_rank["Production"] = prod_rank["Production"].apply(lambda x: f"{int(x):,}")
        prod_rank["Efficiency"] = prod_rank["Efficiency"].apply(lambda x: f"{x:.3f}")
        st.dataframe(prod_rank, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── BEST PERFORMANCE DAYS ────────────────────────────────────────────────
    st.markdown("#### Best performance days")
    factories_all = prod_df["Factory"].unique()

    for fac in factories_all:
        with st.expander(f"🏭 {fac}", expanded=(fac == factory)):
            f_df = prod_df[
                (prod_df["Factory"] == fac) &
                (prod_df["Date"] >= d_start) &
                (prod_df["Date"] <= d_end)
            ]
            if f_df.empty:
                st.info("No data in selected range.")
                continue
            daily = f_df.groupby("Date").agg({
                "Production": "sum",
                "Labour": "sum",
                "Hours": "mean",
                "Efficiency": "mean"
            })
            b1, b2, b3, b4 = st.columns(4)
            b1.metric("Best production day",  str(daily["Production"].idxmax().date()))
            b2.metric("Highest labour day",   str(daily["Labour"].idxmax().date()))
            b3.metric("Longest hours day",    str(daily["Hours"].idxmax().date()))
            b4.metric("Best efficiency day",  str(daily["Efficiency"].idxmax().date()))

    st.markdown("---")

    # ── SMART INSIGHTS ────────────────────────────────────────────────────────
    st.markdown("#### Smart insights")
    df_sorted = df.sort_values("Date")
    if len(df_sorted) >= 2:
        last = df_sorted.iloc[-1]
        prev = df_sorted.iloc[-2]
        insights = []
        if last["Production"] < prev["Production"]:
            drop_pct = (1 - last["Production"] / prev["Production"]) * 100 if prev["Production"] else 0
            insights.append(("warning", f"Production fell by {drop_pct:.1f}% vs previous entry"))
        if last["Labour"] > prev["Labour"] and last["Production"] <= prev["Production"]:
            insights.append(("warning", "More workers deployed but output did not increase — review allocation"))
        if last["Hours"] > prev["Hours"] and last["Efficiency"] < prev["Efficiency"]:
            insights.append(("warning", "Longer hours but lower efficiency — fatigue or process issue?"))
        if last["Efficiency"] > prev["Efficiency"]:
            gain = ((last["Efficiency"] / prev["Efficiency"]) - 1) * 100 if prev["Efficiency"] else 0
            insights.append(("success", f"Efficiency up by {gain:.1f}% vs previous entry"))

        if insights:
            for kind, msg in insights:
                if kind == "success":
                    st.success(msg)
                else:
                    st.warning(msg)
        else:
            st.success("Operations appear stable — no issues detected")
    else:
        st.info("Need at least 2 entries in range to generate trend insights.")

    st.markdown("---")

    # ── EXPORT ───────────────────────────────────────────────────────────────
    st.markdown("#### Export")
    ecol1, ecol2 = st.columns([2, 3])
    with ecol1:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Production", index=False)
            if not sand_df.empty:
                sand_df[sand_df["Factory"] == factory].to_excel(writer, sheet_name="Sand", index=False)
            if not stock_df.empty:
                stock_df[stock_df["Factory"] == factory].to_excel(writer, sheet_name="Stock", index=False)
        buffer.seek(0)
        st.download_button(
            label="📥 Download report (Excel)",
            data=buffer,
            file_name=f"FCSC_{factory}_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with ecol2:
        st.caption("Exports all three sheets — Production, Sand, and Stock — for the selected factory and date range.")