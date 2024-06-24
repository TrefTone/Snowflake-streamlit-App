import pandas as pd
import snowflake.connector
import streamlit as st
import plotly.express as px

mydb = snowflake.connector.connect(
    user=st.secrets["user"],
    password=st.secrets["password"],
    account=st.secrets["account"],
    warehouse='compute_wh',
    database='COVID_DATA',
    schema='PUBLIC'
)

mycursor = mydb.cursor()

st.set_page_config(
    page_title="Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if st.button("Generate dashboard"):
    st.empty()
    query = """
        SELECT *
        FROM covid_data_view
        WHERE iso_code NOT LIKE 'OWID%';
        """
    df = pd.read_sql(query, mydb)

    total_cases = df['NEW_CASES'].sum()
    total_deaths = df['NEW_DEATHS'].sum()

    # Worldwide
    df_sum_case = df.groupby('DATE')['NEW_CASES'].sum().reset_index()
    df_sum_death = df.groupby('DATE')['NEW_DEATHS'].sum().reset_index()
    # Plot using Plotly line chart
    fig_case_date = px.area(df_sum_case, title='Daily new cases Worldwide',height=300, x='DATE', y='NEW_CASES',
                            labels={'DATE': 'Date', 'NEW_CASES': 'New Cases'})
    fig_death_date = px.area(df_sum_death, title='Daily new cases Worldwide',height=300, x='DATE', y='NEW_DEATHS',
                             labels={'DATE': 'Date', 'NEW_DEATHS': 'New Deaths'})

    # India
    df_india = df[df['ISO_CODE'] == 'IND']

    # Group by date and sum new cases and new deaths
    df_sum_case_ind = df_india.groupby('DATE')['NEW_CASES'].sum().reset_index()
    df_sum_death_ind = df_india.groupby('DATE')['NEW_DEATHS'].sum().reset_index()

    # Plot using Plotly line chart
    fig_case_date_ind = px.area(df_sum_case_ind, title='Daily new cases India',height=300, x='DATE', y='NEW_CASES',
                                labels={'DATE': 'Date', 'NEW_CASES': 'New Cases'})
    fig_death_date_ind = px.area(df_sum_death_ind, title='Daily new deaths India',height=300, x='DATE', y='NEW_DEATHS',
                                 labels={'DATE': 'Date', 'NEW_DEATHS': 'New Deaths'})

    # Top 10 by total cases
    df_cases = df.groupby('ISO_CODE')['NEW_CASES'].sum().reset_index()

    # Sort by total cases in descending order
    df_cases = df_cases.sort_values(by='NEW_CASES', ascending=False).head(10)

    # Plotting using Plotly bar chart
    fig_highest_case = px.bar(df_cases, x='ISO_CODE', y='NEW_CASES',height=500,
                              labels={'ISO_CODE': 'Country', 'NEW_CASES': 'Total Cases'},
                              title='Top 10 Countries with Highest Total Cases')

    # Top 10 by death
    df_cases = df.groupby('ISO_CODE')['NEW_DEATHS'].sum().reset_index()

    # Sort by total cases in descending order
    df_cases = df_cases.sort_values(by='NEW_DEATHS', ascending=False).head(10)

    # Plotting using Plotly bar chart
    fig_highest_death = px.bar(df_cases, x='ISO_CODE', y='NEW_DEATHS',height=500,
                               labels={'ISO_CODE': 'Country', 'NEW_DEATHS': 'Total Deaths'},
                               title='Top 10 Countries with Highest Total Cases')

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("<h2>Total Cases and Total Deaths</h2>", unsafe_allow_html=True)
        cases, deaths = st.columns(2)
        with cases:

            st.markdown(f"""
                <div style="background-color:#ebd2b9; padding:10px; border-radius:5px; height:155px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <h5 style="text-align:center;">Total Cases</h5>
                    <h3 style="text-align:center; margin: auto;">{total_cases:,}</h3>
                </div>
                """, unsafe_allow_html=True)
        with deaths:
            st.markdown(f"""
                <div style="background-color:#ebd2b9; padding:10px; border-radius:5px; height:155px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <h5 style="text-align:center;">Total Deaths</h5>
                    <h3 style="text-align:center; margin: auto;">{total_deaths:,}</h3>
                </div>
                """, unsafe_allow_html=True)

        # Display the Top 10 by cases using Streamlit
        st.plotly_chart(fig_highest_case)

        # Display the Top 10 by death using Streamlit
        st.plotly_chart(fig_highest_death)

    with right_col:
        # Display the plots using Streamlit
        st.plotly_chart(fig_case_date_ind)
        st.plotly_chart(fig_case_date)
        st.plotly_chart(fig_death_date_ind)
        st.plotly_chart(fig_death_date)
