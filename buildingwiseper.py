import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Building Permission Analysis Dashboard",
    page_icon="🏗️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stPlotlyChart {
        background-color: #ffffff;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

# Load the data
@st.cache_data
def load_data():
    data = pd.read_csv('building_permission_data_01-11-2024_30-11-2024.csv')  # Replace with your dataset
    return data

# Main title with styling
st.title('🏗️ Building Permission Analysis Dashboard')
st.markdown('---')

try:
    data = load_data()

    # Dashboard Layout
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('📊 Key Metrics Overview')
        total_districts = data['district_Name'].nunique()
        total_mandals = data['mandal_Name'].nunique()
        total_applications = data['total_No_of_Application_Received'].sum()
        within_sla = data['no_of_Application_Approve_with_in_BSLA'].sum()
        beyond_sla = data['no_of_Application_Approve_Beyond_BSLA'].sum()
        rejected_within_sla=data['no_of_Application_Reject_With_in_BSLA'].sum()
        rejected_beyond_sla=data['no_of_Application_Reject_Beyond_BSLA'].sum()

        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.metric("Total Districts", f"{total_districts:,}")
            st.metric("Total Mandals", f"{total_mandals:,}")
            st.metric("Total Application Rejected with in SLA",f"{int(rejected_within_sla):,}")
        with metrics_col2:
            st.metric("Total Applications", f"{int(total_applications):,}")
            st.metric("Applications Within SLA", f"{int(within_sla):,}")
            st.metric("Total Applications Rejected Beyond SAL", f"{int(rejected_beyond_sla):,}")

    with col2:
        st.subheader('📈 Application Trends by District')
        district_apps = data.groupby('district_Name')['total_No_of_Application_Received'].sum().sort_values(ascending=True)
        fig = px.bar(district_apps, orientation='h',
                     title='Applications by District',
                     labels={'value': 'Number of Applications', 'district_Name': 'District'})
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    # SLA Compliance Analysis
    st.markdown('---')
    st.header('⏳ SLA Compliance Analysis')
    compliance_data = pd.DataFrame({
        'Category': ['Within SLA', 'Beyond SLA'],
        'Count': [within_sla, beyond_sla]
    })
    fig = px.pie(compliance_data, values='Count', names='Category', title='SLA Compliance Distribution')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

    # Geographical Distribution
    col3, col4 = st.columns(2)

    with col3:
        st.subheader('📍 Mandal-wise Applications')
        mandal_apps = data.groupby('mandal_Name')['total_No_of_Application_Received'].sum().sort_values(ascending=False)
        fig = px.bar(mandal_apps, orientation='v',
                     title='Applications by Mandal',
                     labels={'value': 'Number of Applications', 'mandal_Name': 'Mandal'})
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader('🎯 SLA Compliance by Mandal')
        mandal_sla = data.groupby('mandal_Name')[['no_of_Application_Approve_with_in_BSLA', 'no_of_Application_Approve_Beyond_BSLA']].sum()
        fig = px.bar(mandal_sla, barmode='group',
                     title='SLA Compliance by Mandal',
                     labels={'value': 'Count', 'mandal_Name': 'Mandal'})
        st.plotly_chart(fig, use_container_width=True)

    # Correlation Analysis
    st.markdown('---')
    st.subheader('📊 Statistical Correlations')
    numeric_cols = ['total_No_of_Application_Received', 'no_of_Application_Approve_with_in_BSLA', 'no_of_Application_Approve_Beyond_BSLA']
    corr_matrix = data[numeric_cols].corr()
    fig = px.imshow(corr_matrix,
                    labels=dict(color="Correlation Coefficient"),
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    color_continuous_scale='RdBu')
    fig.update_layout(title='Correlation Matrix of Key Metrics')
    st.plotly_chart(fig, use_container_width=True)

    # Interactive Data Explorer
    st.markdown('---')
    st.header('🔍 Interactive Data Explorer')

    selected_district = st.selectbox('Select District', ['All'] + list(data['district_Name'].unique()))

    if selected_district != 'All':
        filtered_data = data[data['district_Name'] == selected_district]
    else:
        filtered_data = data

    metric_choice = st.selectbox('Select Metric to Visualize',
                                 ['Total Applications', 'Within SLA', 'Beyond SLA'])

    metric_map = {
        'Total Applications': 'total_No_of_Application_Received',
        'Within SLA': 'no_of_Application_Approve_with_in_BSLA',
        'Beyond SLA': 'no_of_Application_Approve_Beyond_BSLA'
    }

    selected_metric = metric_map[metric_choice]

    fig = px.bar(filtered_data.groupby('mandal_Name')[selected_metric].sum().reset_index(),
                 x='mandal_Name', y=selected_metric,
                 title=f'{metric_choice} by Mandal' + (f' in {selected_district}' if selected_district != 'All' else ''))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"An error occurred while loading or processing the data: {str(e)}")
    st.info("Please make sure the dataset file is in the correct location and contains the expected columns.")
