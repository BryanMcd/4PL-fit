import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import plotly.graph_objects as go
import streamlit.components.v1 as components

# --- 4PL Math Functions ---
def four_pl(x, A, B, C, D):
    return D + (A - D) / (1 + (x / C)**B)

def inverse_four_pl(y, A, B, C, D):
    try:
        term = (A - y) / (y - D)
        if term <= 0: return np.nan
        return C * (term**(1/B))
    except:
        return np.nan

# --- UI Configuration ---
st.set_page_config(page_title="4PL-fit", layout="wide")

# --- CSS to remove top padding gap ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("🔬 4PL Calculator")
st.subheader("Interpolating from a sigmoidal standard curve")

if 'df' not in st.session_state:
    st.session_state.df = None

# --- Data Input Section (Sidebar) ---
st.sidebar.header("Data Input")
upload_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if st.sidebar.button("Load example data"):
    example_data = pd.DataFrame({
        'Type': ['Standard']*8 + ['Sample']*8,
        'Sample Name': [None]*8 + ['Control', 'A1', 'A2', 'A3', 'A1 (1:10)', 'A2 (1:10)', 'A3 (1:10)', 'Blank'],
        'Conc': [5000, 2500, 1250, 625, 313, 156, 78.1, 0] + [None]*8,
        'OD_Rep1': [2.368, 1.475, 0.919, 0.509, 0.33, 0.209, 0.151, 0.091, 0.52, 3.59, 0.584, 3.852, 2.097, 0.18, 2.261, 0.091],
        'OD_Rep2': [2.344, 1.462, 0.889, 0.529, 0.322, 0.214, 0.151, 0.096, 0.507, 3.617, 0.588, 3.755, 2.037, 0.187, 2.224, 0.09]
    })
    st.session_state.df = example_data

if upload_file:
    st.session_state.df = pd.read_csv(upload_file)

# --- Main Editor ---
if st.session_state.df is not None:
    df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
    
    if st.button("Calculate"):
        try:
            od_cols = [c for c in df.columns if any(w in c.lower() for w in ['od', 'rep', 'abs'])]
            df['Mean_OD'] = df[od_cols].mean(axis=1)

            stds = df[df['Type'].str.lower().str.contains('std|standard', na=False)]
            stds_fit = stds[stds['Conc'] > 0].dropna(subset=['Conc'])
            x_fit, y_fit = stds_fit['Conc'].values, stds_fit['Mean_OD'].values

            p0 = [min(y_fit), 1.0, np.median(x_fit), max(y_fit)]
            popt, _ = curve_fit(four_pl, x_fit, y_fit, p0=p0, maxfev=10000)
            A, B, C, D = popt

            # Metrics
            st.write("---")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Bottom Asymptote (A)", f"{A:.4f}")
            m_col2.metric("HillSlope (B)", f"{B:.4f}")
            m_col3.metric("EC50 (C)", f"{C:.4f}")
            m_col4.metric("Top Asymptote (D)", f"{D:.4f}")

            # Calculations
            smpls = df[df['Type'].str.lower().str.contains('sample|unk', na=False)]
            results = []
            for _, row in smpls.iterrows():
                od = row['Mean_OD']
                conc = inverse_four_pl(od, A, B, C, D)
                status = "OK"
                display_conc = f"{conc:.2f}" if not np.isnan(conc) else "OOR"
                if od <= A: status, display_conc = "Below LOD", "< LOD"
                elif od >= D: status, display_conc = "Above Range", "> Range"
                elif od < min(y_fit): status = "Low (<Range)"
                elif od > max(y_fit): status = "High (>Range)"
                results.append({"Sample": row['Sample Name'], "Mean OD": round(od, 3), "Conc.": display_conc, "Status": status})
            
            res_df = pd.DataFrame(results)

            # --- Aligned Results Display ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Standard Curve")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x_fit, y=y_fit, mode='markers', name='Standards'))
                x_line = np.logspace(np.log10(min(x_fit)*0.1), np.log10(max(x_fit)*10), 100)
                fig.add_trace(go.Scatter(x=x_line, y=four_pl(x_line, *popt), mode='lines', name='4PL Fit'))
                fig.update_xaxes(type="log", title="Concentration")
                fig.update_yaxes(title="OD")
                # Remove top margin from the figure itself
                fig.update_layout(margin=dict(t=0))
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                st.subheader("Interpolated Results")
                st.dataframe(res_df, use_container_width=True, hide_index=True)
                
                tsv_data = res_df.to_csv(index=False, sep='\t').replace('\n', '\\n').replace('\r', '')
                copy_button_html = f"""
                <script>
                function copyToClipboard() {{
                    const text = `{tsv_data}`;
                    navigator.clipboard.writeText(text).then(() => {{
                        alert('Table copied to clipboard!');
                    }});
                }}
                </script>
                <div style="display: flex; justify-content: flex-start; margin-top: 10px;">
                    <button onclick="copyToClipboard()" style="
                        background-color: #2563eb; color: white; border: none; 
                        padding: 10px 20px; border-radius: 5px; cursor: pointer; 
                        font-weight: bold; height: 42px;">
                        📋 Copy Table to clipboard
                    </button>
                </div>
                """
                components.html(copy_button_html, height=55)

        except Exception as e:
            st.error(f"Fit failed: {e}")
else:
    st.info("👋 Please upload a CSV file or click 'Load example data' in the sidebar to begin.")