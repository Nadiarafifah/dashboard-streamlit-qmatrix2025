import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =====================================================
# 🧩 SETTINGS
# =====================================================
st.set_page_config(
    page_title="Dashboard Analisis Defect Es Krim",
    layout="wide",
    initial_sidebar_state="expanded"
)

sns.set_style("whitegrid")
st.title("📊 Dashboard Analisis Kualitas Produksi Es Krim (Q-MATRIX 2025)")
st.write("Dashboard untuk menganalisis defect produk es krim periode Januari–Maret 2025.")

# =====================================================
# 🧩 LOAD DATA
# =====================================================
def load_data():
    df = pd.read_csv("Q-MATRIX2025_cleaned.csv")
    df.columns = df.columns.str.strip()
    df["Production Date"] = pd.to_datetime(df["Production Date"], errors="coerce")
    df["Month"] = df["Production Date"].dt.to_period("M")
    return df

df = load_data()

# =====================================================
# 🧩 SIDEBAR FILTER
# =====================================================
st.sidebar.header("🔍 Filter Data")

produk = st.sidebar.multiselect(
    "Pilih Produk",
    options=df["Product Description"].unique().tolist(),
    default=df["Product Description"].unique().tolist()
)

mesin = st.sidebar.multiselect(
    "Pilih Mesin",
    options=df["Machine"].unique().tolist(),
    default=df["Machine"].unique().tolist()
)

severity = st.sidebar.multiselect(
    "Pilih Severity Grade",
    options=df["Defect Severity Grade"].unique().tolist(),
    default=df["Defect Severity Grade"].unique().tolist()
)

bulan = st.sidebar.multiselect(
    "Pilih Bulan Produksi",
    options=sorted(df["Month"].unique()),
    default=sorted(df["Month"].unique())
)

# FILTER
df_filtered = df[
    (df["Product Description"].isin(produk)) &
    (df["Machine"].isin(mesin)) &
    (df["Defect Severity Grade"].isin(severity)) &
    (df["Month"].isin(bulan))
]

if df_filtered.empty:
    st.warning("Filter menghasilkan 0 baris. Silakan ubah filter.")
    st.stop()

# =====================================================
# 🧩 TAB
# =====================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📦 Produk",
    "⚙ Mesin",
    "📅 Tren Waktu",
    "❗ Penyebab Defect",
    "📈 Korelasi",
    "📑 Rekomendasi"
])

# =====================================================
# TAB 1 — PRODUK
# =====================================================
with tab1:
    st.subheader("📦 Produk dengan Jumlah Defect Tertinggi")

    product_defects = df_filtered.groupby("Product Description").size().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(
        x=product_defects.values,
        y=product_defects.index,
        palette="Reds_r",
        ax=ax
    )
    ax.set_xlabel("Jumlah Defect")
    ax.set_ylabel("Produk")
    st.pyplot(fig)

    # INSIGHT PRODUK (DINAMIS)
    if len(product_defects) > 0:
        prod_name = product_defects.index[0]
        prod_value = product_defects.values[0]
        st.success(
            f"📌 *Insight:* Produk dengan defect tertinggi adalah *{prod_name}* "
            f"dengan *{prod_value} kasus*."
        )

    # ----- Severity per Produk -----
    if "Defect Severity Grade" in df_filtered.columns:
        severity_data = df_filtered.groupby(
            ["Product Description", "Defect Severity Grade"]
        ).size().reset_index(name="Count")

        fig2, ax2 = plt.subplots(figsize=(11, 4))
        sns.barplot(
            data=severity_data,
            x="Product Description",
            y="Count",
            hue="Defect Severity Grade",
            palette="viridis",
            ax=ax2
        )
        ax2.set_title("Severity Grade per Produk")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig2)

# =====================================================
# TAB 2 — MESIN
# =====================================================
with tab2:
    st.subheader("⚙ Mesin dengan Frekuensi Defect Tertinggi")

    machine_defects = df_filtered.groupby("Machine").size().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(
        x=machine_defects.index,
        y=machine_defects.values,
        palette="coolwarm",
        ax=ax
    )
    ax.set_xlabel("Mesin")
    ax.set_ylabel("Jumlah Defect")
    st.pyplot(fig)

    # INSIGHT MESIN (DINAMIS)
    if len(machine_defects) > 0:
        mach_name = machine_defects.index[0]
        mach_value = machine_defects.values[0]
        st.info(
            f"⚙ *Insight:* Mesin dengan defect tertinggi adalah *Mesin {mach_name}* "
            f"dengan *{mach_value} kasus*."
        )

# =====================================================
# TAB 3 — TREN WAKTU
# =====================================================
with tab3:
    st.subheader("📅 Tren Defect Januari – Maret 2025")

    trend = df_filtered.groupby("Month").size().sort_index()

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(trend.index.astype(str), trend.values, marker="o", color="teal")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Jumlah Defect")
    st.pyplot(fig)

    # INSIGHT TREN WAKTU (DINAMIS)
    if len(trend) >= 2:
        first = trend.iloc[0]
        last = trend.iloc[-1]
        diff = last - first

        if diff > 0:
            st.warning(f"📈 *Trend naik:* Defect meningkat *{diff} kasus* dibanding awal periode.")
        elif diff < 0:
            st.success(f"📉 *Trend turun:* Defect menurun *{abs(diff)} kasus* dibanding awal periode.")
        else:
            st.info("➖ *Stabil:* Tidak ada perubahan signifikan jumlah defect.")

# =====================================================
# TAB 4 — PENYEBAB DEFECT
# =====================================================
with tab4:
    st.subheader("❗ Penyebab Defect Berdasarkan Level (1–4)")

    levels = ["Level (1)", "Level (2)", "Level (3)", "Level (4)"]
    col1, col2 = st.columns(2)

    for idx, level in enumerate(levels):
        if level not in df_filtered.columns:
            continue

        top_val = df_filtered[level].value_counts().head(5)

        fig, ax = plt.subplots(figsize=(8, 3))
        sns.barplot(
            x=top_val.values,
            y=top_val.index,
            palette="viridis",
            ax=ax
        )
        ax.set_title(level)
        ax.set_xlabel("Frekuensi")

        if idx % 2 == 0:
            col1.pyplot(fig)
        else:
            col2.pyplot(fig)

        # INSIGHT LEVEL DEFECT (DINAMIS)
        if not top_val.empty:
            cause = top_val.index[0]
            count = top_val.values[0]
            st.success(f"🔍 *Insight {level}:* Penyebab terbanyak adalah *{cause}* sebanyak *{count} kasus*.")

# =====================================================
# TAB 5 — KORELASI
# =====================================================
with tab5:
    st.subheader("📈 Korelasi antar Variabel (Product Code & Machine)")

    corr_df = df_filtered[["Product Code", "Machine"]].astype("category").apply(lambda x: x.cat.codes)

    fig, ax = plt.subplots(figsize=(6, 3))
    sns.heatmap(corr_df.corr(), annot=True, cmap="YlOrRd", ax=ax)
    ax.set_title("Heatmap Korelasi")
    st.pyplot(fig)

    # INSIGHT KORELASI (DINAMIS)
    corr_val = corr_df.corr().iloc[0, 1]
    if abs(corr_val) < 0.2:
        st.info("🔎 *Insight:* Korelasi lemah → distribusi produk ke mesin bersifat acak.")
    elif abs(corr_val) < 0.5:
        st.warning("🔎 *Insight:* Terdapat korelasi sedang antara produk dan mesin.")
    else:
        st.success("🔎 *Insight:* Korelasi kuat → pola distribusi produk ke mesin signifikan.")

# =====================================================
# TAB 6 — REKOMENDASI (DINAMIS)
# =====================================================
with tab6:
    st.subheader("📑 Rekomendasi Hasil Analisis Defect")

    # --- Produk teratas berdasarkan filter ---
    top_products = df_filtered["Product Description"].value_counts().head(3)
    produk_list = ", ".join(top_products.index.tolist())

    # --- Mesin dengan defect terbanyak ---
    top_machine = df_filtered["Machine"].value_counts().idxmax()

    # --- Penyebab dominan Level 1–3 ---
    level1 = df_filtered["Level (1)"].value_counts().idxmax()
    level2 = df_filtered["Level (2)"].value_counts().idxmax()
    level3 = df_filtered["Level (3)"].value_counts().idxmax()

    # --- Severity paling dominan ---
    top_severity = df_filtered["Defect Severity Grade"].value_counts().idxmax()

    # --- Bulan dengan kenaikan defect ---
    trend = df_filtered.groupby("Month").size().sort_index()
    if len(trend) > 1:
        max_month = trend.idxmax()
        bulan_naik = str(max_month)
    else:
        bulan_naik = "-"

    st.markdown(f"""
    - Fokuskan inspeksi dan kontrol kualitas pada *produk {produk_list}* yang memiliki defect tertinggi.
    - Lakukan pengecekan rutin pada *Mesin {top_machine}* karena menyumbang defect paling besar.
    - Evaluasi ulang penyebab utama defect: *{level1} → {level2} → {level3}*.
    - Tingkatkan SOP penanganan untuk defect dengan *Severity Grade {top_severity}*.
    - Analisis penyebab kenaikan defect pada bulan *{bulan_naik}* untuk mencegah tren berulang.
    """)

    st.info("⚡ Rekomendasi ini otomatis menyesuaikan data yang sedang difilter.")

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.write("Dashboard Final by Kelompok Trinaya © 2025")