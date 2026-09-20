import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="GNSS-Denied Navigation Analysis", layout="wide")
st.title("UAS GNSS-Denied Navigation Performance")
st.markdown("Analyzing state estimation drift across visual odometry (VIO) and pure IMU fallback (IMU_ONLY) modes.")

# 2. Data Ingress
@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "../data/synthetic_flight_logs.csv")
    return pd.read_csv(data_path)

df = load_data()

# 3. Data Processing & Visualization
col1, col2 = st.columns(2)

with col1:
    st.subheader("Average Drift Error Over Time")
    
    # Calculate the mean drift at each second for both navigation modes
    drift_time = df.groupby(['time_since_gps_loss_s', 'nav_mode_active'])['drift_error_m'].mean().reset_index()
    
    fig_time = px.line(drift_time, 
                       x='time_since_gps_loss_s', 
                       y='drift_error_m', 
                       color='nav_mode_active',
                       title="Drift Accumulation: VIO vs IMU Only")
    
    # Add a visual threshold line representing a mission-critical error bound
    fig_time.add_hline(y=10, line_dash="dash", line_color="red", annotation_text="10m Critical Threshold")
    st.plotly_chart(fig_time, use_container_width=True)

with col2:
    st.subheader("Terminal Drift vs. Visual Feature Density")
    
    # Isolate the data at the very end of the 120-second simulation
    max_time = df['time_since_gps_loss_s'].max()
    df_end = df[df['time_since_gps_loss_s'] == max_time]
    
    fig_density = px.scatter(df_end, 
                             x='visual_feature_density', 
                             y='drift_error_m', 
                             color='nav_mode_active',
                             title=f"Total Drift at T={int(max_time)}s",
                             opacity=0.6)
    
    # Add a visual cutoff line where the software drops VIO
    fig_density.add_vline(x=0.4, line_dash="dash", line_color="red", annotation_text="VIO Cutoff (0.4)")
    st.plotly_chart(fig_density, use_container_width=True)

# 4. The Systems Engineering Context
st.markdown("---")
st.subheader("Systems Engineering Takeaways")
st.markdown("""
* **The Failure Point:** Look at the chart on the left. The `IMU_ONLY` mode breaches the 10-meter critical threshold long before the 120-second mark.
* **The Environmental Trigger:** Look at the chart on the right. When visual density drops below 0.4, the system abandons VIO, relying entirely on the noisy IMU, resulting in massive terminal drift. 
""")