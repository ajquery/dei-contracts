import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from pathlib import Path

# Define color palette
COLORS = {
    'primary': '#7A9E9F',     # Muted teal
    'secondary': '#B8D8D8',   # Light sage
    'accent': '#FE5F55',      # Muted coral
    'background': '#F4F1DE',  # Cream
    'text': '#4A4A4A',        # Dark gray
    'palette': ['#7A9E9F', '#B8D8D8', '#FE5F55', '#EFD3D7', '#CDDAFD', '#E2ECE9', '#DDB892', '#B7B7A4']
}

# Set page config with custom theme
st.set_page_config(
    page_title="Federal DEI Contracts Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimalist theme
st.markdown("""
    <style>
    .stApp {
        background-color: #F4F1DE;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric:hover {
        transform: translateY(-2px);
        transition: transform 0.2s;
    }
    .stDataFrame {
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stPlotlyChart {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #4A4A4A;
    }
    .stSidebar {
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Data loading and preprocessing
@st.cache_data
def load_data():
    """Load and preprocess the data"""
    try:
        file_path = Path('dei_contracts_master.csv')
        df = pd.read_csv(file_path)
        
        # Convert date columns
        date_columns = ['action_date', 'contract_start_date', 'contract_end_date']
        for col in date_columns:
            df[col] = pd.to_datetime(df[col])
        
        # Convert amount to numeric, removing any currency symbols and commas
        df['award_amount'] = df['award_amount'].replace(r'[$,]', '', regex=True).astype(float)
        
        # Consolidate agency names
        agency_mappings = {
            'Agency for International Development (USAID)': 'Agency for International Development',
            'Agency for International Development': 'Agency for International Development',
            'Department of Health and Human Services (HHS)': 'Department of Health and Human Services',
            'Department of Health and Human Services': 'Department of Health and Human Services',
            'National Science Foundation (NSF)': 'National Science Foundation',
            'National Science Foundation': 'National Science Foundation',
            'Department of Justice (DOJ)': 'Department of Justice',
            'Department of Justice': 'Department of Justice',
            'Department of Defense (DOD)': 'Department of Defense',
            'Department of Defense': 'Department of Defense',
            'Department of Education (ED)': 'Department of Education',
            'Department of Education': 'Department of Education',
            'Environmental Protection Agency (EPA)': 'Environmental Protection Agency',
            'Environmental Protection Agency': 'Environmental Protection Agency'
        }
        
        df['awarding_agency_name'] = df['awarding_agency_name'].replace(agency_mappings)
        
        # Calculate contract duration if not already present
        if 'contract_duration_days' not in df.columns:
            df['contract_duration_days'] = (df['contract_end_date'] - df['contract_start_date']).dt.days
        
        # Create award size categories if not present
        if 'award_size_category' not in df.columns:
            df['award_size_category'] = pd.cut(
                df['award_amount'],
                bins=[0, 10000, 100000, 1000000, 10000000, float('inf')],
                labels=['Micro (< $10K)', 'Small ($10K - $100K)', 'Medium ($100K - $1M)', 
                       'Large ($1M - $10M)', 'Major (> $10M)']
            )
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Load data
df = load_data()

if df is not None:
    # Sidebar filters
    with st.sidebar:
        st.title("Filters")
        st.markdown("""
            <style>
            .sidebar-text {
                color: #4A4A4A;
                font-size: 14px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Date range filter
        st.subheader("Date Range")
        min_date = df['action_date'].min()
        max_date = df['action_date'].max()
        date_range = st.date_input(
            "Select date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Agency filter
        agencies = ['All'] + sorted(df['awarding_agency_name'].unique().tolist())
        selected_agency = st.selectbox("Select Agency", agencies)
        
        # Award size filter
        award_sizes = ['All'] + sorted(df['award_size_category'].unique().tolist())
        selected_size = st.selectbox("Select Award Size", award_sizes)
        
        # DEI Theme filter
        theme_columns = [col for col in df.columns if col.startswith('theme_')]
        selected_themes = st.multiselect(
            "Select DEI Themes",
            options=[col.replace('theme_', '').replace('_', ' ').title() for col in theme_columns],
            default=[]
        )
    
    # Apply filters
    mask = (df['action_date'].dt.date >= date_range[0]) & (df['action_date'].dt.date <= date_range[1])
    if selected_agency != 'All':
        mask &= df['awarding_agency_name'] == selected_agency
    if selected_size != 'All':
        mask &= df['award_size_category'] == selected_size
    if selected_themes:
        theme_mask = pd.Series([False] * len(df))
        for theme in selected_themes:
            col = f"theme_{theme.lower().replace(' ', '_')}"
            theme_mask |= df[col]
        mask &= theme_mask
    
    filtered_df = df[mask]
    
    # Main dashboard
    st.title("Federal DEI Contracts Dashboard Jan. 2023 to Feb. 2025")
    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)  # Spacing
    
    # Key metrics with custom styling
    col1, col2, col3 = st.columns(3)
    metric_style = """
        <style>
        [data-testid="stMetricValue"] {
            font-size: 24px;
            color: #4A4A4A;
        }
        [data-testid="stMetricLabel"] {
            font-size: 14px;
            color: #7A9E9F;
        }
        </style>
    """
    st.markdown(metric_style, unsafe_allow_html=True)
    
    with col1:
        st.metric("Total Contracts", f"{len(filtered_df):,}")
    with col2:
        st.metric("Total Award Amount", f"${filtered_df['award_amount'].sum():,.2f}")
    with col3:
        st.metric("Unique Recipients", 
                 f"{filtered_df['recipient_name'].nunique():,}")
    
    st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)  # Spacing
    
    # Charts with custom styling
    chart_config = {
        'template': 'simple_white',
        'font': {'color': COLORS['text'], 'size': 12},
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'margin': {'t': 50, 'b': 50, 'l': 50, 'r': 50}  # Added margins
    }
    
    # DEI Themes Distribution
    st.subheader("DEI Themes Distribution")
    theme_data = filtered_df[theme_columns].sum()
    theme_data.index = theme_data.index.str.replace('theme_', '').str.replace('_', ' ').str.title()
    fig_themes = px.bar(
        theme_data,
        title='Number of Contracts by DEI Theme',
        color_discrete_sequence=COLORS['palette'],
        height=500  # Height specified here
    )
    fig_themes.update_layout(
        xaxis_title="Theme",
        yaxis_title="Number of Contracts",
        xaxis={'tickangle': 45, 'title_font': {'color': 'black'}, 'tickfont': {'color': 'black'}},  # Black text
        yaxis={'title_font': {'color': 'black'}, 'tickfont': {'color': 'black'}},  # Black text
        **{k: v for k, v in chart_config.items() if k != 'height'}  # Exclude height from config
    )
    st.plotly_chart(fig_themes, use_container_width=True)
    
    st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)  # Increased spacing
    
    # Award Amount Distribution (Top 10 Agencies)
    st.subheader("Award Amount Distribution by Top 10 Agencies")
    
    # Get top 10 agencies by award amount
    top_10_agencies = (
        filtered_df.groupby('awarding_agency_name')['award_amount']
        .sum()
        .sort_values(ascending=True)  # Sort ascending for bottom-to-top bar chart
        .tail(10)  # Get top 10
    ).reset_index()
    
    fig_awards = px.bar(
        top_10_agencies,
        x='award_amount',
        y='awarding_agency_name',
        title='Total Award Amount by Top 10 Agencies',
        color_discrete_sequence=[COLORS['primary']],
        height=500  # Height only specified here
    )
    fig_awards.update_layout(
        xaxis_title="Total Award Amount ($)",
        yaxis_title="Agency",
        xaxis={'tickformat': '$,.0f', 'title_font': {'color': 'black'}, 'tickfont': {'color': 'black'}},  # Black text
        yaxis={'title_font': {'color': 'black'}, 'tickfont': {'color': 'black'}},  # Black text
        showlegend=False,
        **chart_config
    )
    st.plotly_chart(fig_awards, use_container_width=True)
    
    st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)  # Increased spacing
    
    # Timeline of Awards
    st.subheader("Timeline of Awards")
    timeline_data = filtered_df.groupby(filtered_df['action_date'].dt.to_period('M')).agg({
        'award_amount': 'sum',
        'award_id': 'count'
    }).reset_index()
    timeline_data['action_date'] = timeline_data['action_date'].astype(str)
    
    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Scatter(
        x=timeline_data['action_date'],
        y=timeline_data['award_amount'],
        name='Award Amount',
        mode='lines+markers',
        line={'color': COLORS['accent'], 'width': 2},
        marker={'color': COLORS['primary'], 'size': 8}
    ))
    fig_timeline.update_layout(
        title='Monthly Award Amounts',
        xaxis_title='Month',
        yaxis_title='Total Award Amount ($)',
        xaxis={'title_font': {'color': 'black'}, 'tickfont': {'color': 'black'}},  # Black text
        yaxis={'tickformat': '$,.0f', 'title_font': {'color': 'black'}, 'tickfont': {'color': 'black'}},  # Black text
        height=500,  # Height specified here
        **{k: v for k, v in chart_config.items() if k != 'height'}  # Exclude height from config
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)  # Increased spacing
    
    # Data Table with custom styling
    st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)  # Spacing
    st.subheader("Detailed Contract Data")
    display_cols = [
        'award_id', 'recipient_name', 'awarding_agency_name', 
        'award_amount', 'action_date', 'award_description'
    ]
    st.dataframe(
        filtered_df[display_cols].sort_values('action_date', ascending=False).style.format({
            'award_amount': '${:,.2f}',
            'action_date': lambda x: x.strftime('%Y-%m-%d')
        }),
        use_container_width=True,
        height=400
    )
    
    st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)  # Spacing before chyron
    
    # Rolling chyron of recent awards (moved to bottom)
    st.subheader("Featured Awards")
    st.markdown("""
        <style>
        .recent-award {
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .award-amount {
            color: #7A9E9F;
            font-weight: bold;
            font-size: 18px;
        }
        .award-recipient {
            color: #4A4A4A;
            font-weight: bold;
        }
        .award-description {
            color: #666666;
            font-style: italic;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Get random sample of awards instead of recent awards
    random_awards = filtered_df.sample(n=min(5, len(filtered_df)))
    for _, award in random_awards.iterrows():
        description = award['award_description']
        if description and len(description) > 500:
            # Split into words and rejoin first 500 words
            words = description.split()
            if len(words) > 500:
                description = ' '.join(words[:500]) + "..."
        
        # Add date to the display
        award_date = award['action_date'].strftime('%B %d, %Y')
        
        st.markdown(f"""
            <div class="recent-award">
                <span class="award-amount">${award['award_amount']:,.2f}</span> awarded to 
                <span class="award-recipient">{award['recipient_name']}</span> on {award_date}<br>
                <span class="award-description">{description}</span>
            </div>
        """, unsafe_allow_html=True)
    
else:
    st.error("Unable to load data. Please check the data file and try again.") 