
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Runalyze Dashboard", layout="wide")

st.title("🏃 Runalyze Dashboard")

uploaded = st.file_uploader("Upload do CSV do Runalyze", type=["csv"])

if uploaded:
    df = pd.read_csv(uploaded)

    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna(subset=["time"])

    df["distance_km"] = pd.to_numeric(df["distance"], errors="coerce")
    df["duration_s"] = pd.to_numeric(df["s"], errors="coerce")
    df["pace_min_km"] = (df["duration_s"] / 60) / df["distance_km"]

    period = st.selectbox(
        "Período",
        ["30 dias", "90 dias", "365 dias", "Tudo"]
    )

    if period != "Tudo":
        days = int(period.split()[0])
        df = df[df["time"] >= (df["time"].max() - pd.Timedelta(days=days))]

    total_distance = df["distance_km"].sum()
    total_time_h = df["duration_s"].sum() / 3600
    avg_hr = df["pulseAvg"].mean()
    avg_pace = df["pace_min_km"].mean()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Distância Total", f"{total_distance:.1f} km")
    c2.metric("Tempo Total", f"{total_time_h:.1f} h")
    c3.metric("FC Média", f"{avg_hr:.0f} bpm")
    c4.metric("Pace Médio", f"{avg_pace:.2f} min/km")

    weekly = (
        df.set_index("time")
        .resample("W")
        .agg({
            "distance_km": "sum",
            "pulseAvg": "mean",
            "pace_min_km": "mean",
            "vo2max": "mean"
        })
        .reset_index()
    )

    monthly = (
        df.set_index("time")
        .resample("M")
        .agg({"distance_km": "sum"})
        .reset_index()
    )

    st.subheader("Distância Semanal")
    st.plotly_chart(
        px.bar(weekly, x="time", y="distance_km"),
        use_container_width=True
    )

    st.subheader("Distância Mensal")
    st.plotly_chart(
        px.bar(monthly, x="time", y="distance_km"),
        use_container_width=True
    )

    st.subheader("Pace ao Longo do Tempo")
    st.plotly_chart(
        px.line(weekly, x="time", y="pace_min_km"),
        use_container_width=True
    )

    st.subheader("FC Média ao Longo do Tempo")
    st.plotly_chart(
        px.line(weekly, x="time", y="pulseAvg"),
        use_container_width=True
    )

    st.subheader("VO2max")
    st.plotly_chart(
        px.line(weekly, x="time", y="vo2max"),
        use_container_width=True
    )

else:
    st.info("Faça upload do CSV exportado do Runalyze.")
