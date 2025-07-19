# evaluate.py
import streamlit as st
import pandas as pd
import io, os, csv

# ── タイトル＋Refreshボタン ──
st.title("📊 Prediction vs. Label Accuracy Checker")
if st.button("↻ Refresh"):
    try:
        st.experimental_rerun()
    except AttributeError:
        # 古いバージョンでは存在しないことがあるので無視
        pass

# ── ファイルアップローダー（key不要） ──
uploaded = st.file_uploader(
    "🔥 Upload your prediction CSV (1列目→Number, 2列目→Predict)",
    type="csv"
)

if uploaded is not None:
    # ── ヘッダー行の有無を判定して読み込み ──
    raw_csv    = uploaded.getvalue().decode("utf-8")
    has_header = csv.Sniffer().has_header(raw_csv)
    df_pred    = pd.read_csv(io.StringIO(raw_csv), header=0 if has_header else None)

    # ── 1列目→Number, 2列目→Predict ──
    cols = df_pred.columns.tolist()
    if len(cols) < 2:
        st.error("CSV に少なくとも 2 列必要です。")
        st.stop()
    df_pred = df_pred.rename(columns={cols[0]:"Number", cols[1]:"Predict"})[["Number","Predict"]]

    # ── 正解ラベル読み込み ──
    user_home      = os.path.expanduser("~")
    global_sec     = os.path.join(user_home, ".streamlit", "secrets.toml")
    local_sec_file = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")

    if os.path.exists(global_sec) or os.path.exists(local_sec_file):
        raw = st.secrets["label"]["data"]
        df_label = pd.read_csv(io.StringIO(raw))
    elif os.path.exists("label.csv"):
        df_label = pd.read_csv("label.csv")
    else:
        st.error("正解データが見つかりません。（secrets.toml / label.csv をご確認ください）")
        st.stop()

    df_label = df_label.rename(columns={
        df_label.columns[0]:"Number",
        df_label.columns[1]:"Label"
    })[["Number","Label"]]

    # ── マージ＆ソート＆インデックス設定 ──
    df = pd.merge(df_pred, df_label, on="Number", how="inner")
    df = df.sort_values("Number").set_index("Number")

    # ── 結果表示 ──
    acc = (df["Predict"] == df["Label"]).mean()
    st.subheader(f"🔍 Accuracy: {acc:.2%}")
    st.subheader("📝 First 10 Comparisons")
    st.table(df[["Predict","Label"]].head(10))
