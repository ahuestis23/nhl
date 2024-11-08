import streamlit as st
import pandas as pd

# Load the dataset with updated caching
@st.cache_data
def load_data():
    return pd.read_csv('final_corr24.csv')

data = load_data()

# Set up Streamlit dashboard
st.title("NHL Player Correlations (2023 vs. 2024)")

# Optional: Filter by player or team
st.subheader("Filter by Player or Team")
player = st.text_input("Search for Player", "")
team = st.text_input("Search for Team", "")

# Credibility filters
st.subheader("Credibility Filters")
credibility_2024 = st.slider("2024 Credibility (Total Points A and Total Points B > X)", min_value=0, max_value=int(data[['Total Points A', 'Total Points B']].max().max()), value=0)
credibility_2023 = st.slider("2023 Credibility (Total Points A_2023 and Total Points B_2023 > X)", min_value=0, max_value=int(data[['Total Points A_2023', 'Total Points B_2023']].max().max()), value=0)

# Apply filters
filtered_data = data
if player:
    filtered_data = filtered_data[(filtered_data['Player A'].str.contains(player, case=False)) |
                                  (filtered_data['Player B'].str.contains(player, case=False))]
if team:
    filtered_data = filtered_data[(filtered_data['Team'] == team)]

# Apply 2024 and 2023 credibility filters
filtered_data = filtered_data[(filtered_data['Total Points A'] > credibility_2024) & 
                              (filtered_data['Total Points B'] > credibility_2024)]
filtered_data = filtered_data[(filtered_data['Total Points A_2023'] > credibility_2023) & 
                              (filtered_data['Total Points B_2023'] > credibility_2023)]

st.write("Filtered Data", filtered_data)

# Save filtered data option
st.download_button(
    label="Download Filtered Data",
    data=filtered_data.to_csv(index=False),
    file_name="filtered_corr_data.csv",
    mime="text/csv"
)

