import streamlit as st
import pandas as pd

# Set wider page layout
st.set_page_config(layout="wide")

# Title and description
st.title("Franchise Draft - Beetie Board")
st.write("Career WAR projections for the best players available")

# Add small toggle at the top
show_drafted = st.toggle("Show Drafted Players", value=False, 
                         key="show_drafted_toggle", label_visibility="visible")

# Read the CSV files
hitters_df = pd.read_csv('zips-hitters-2025.csv')
pitchers_df = pd.read_csv('zips-pitchers-2025.csv')

def interpolate_delta(age_deltas, age):
    """
    Interpolates between two ages based on decimal age.
    For example, age 24.8 will use 20% of age 24's delta and 80% of age 25's delta.
    """
    lower_age = int(age)
    upper_age = lower_age + 1
    decimal_part = age - lower_age

    lower_delta = age_deltas.get(lower_age, -2.5)
    upper_delta = age_deltas.get(upper_age, -2.5)

    return (1 - decimal_part) * lower_delta + decimal_part * upper_delta

def conservative_aging_curve(row):
    age = float(row["Age"])
    current_war = row["WAR"]
    total_future_war = 0

    # Modified deltas for more gradual decline
    low_end_deltas = {
        20: +0.15, 21: +0.15, 22: +0.08, 23: +0.08, 24: +0.08,
        25: +0.0, 26: +0.0, 27: -0.1, 28: -0.2, 29: -0.3,
        30: -0.4, 31: -0.5, 32: -0.6, 33: -0.7, 34: -0.8,
        35: -1.0, 36: -1.2, 37: -1.4, 38: -1.6, 39: -1.8,
        40: -2.0, 41: -2.2, 42: -2.4
    }

    # Project until age 42
    while age < 43:
        delta = interpolate_delta(low_end_deltas, age)
        current_war += delta
        
        if current_war <= 0:
            break
            
        total_future_war += current_war
        age += 1

    return total_future_war

def standard_aging_curve(row):
    age = float(row["Age"])
    current_war = row["WAR"]
    total_future_war = 0

    # Modified deltas for hitters - more gradual changes
    standard_deltas = {
        20: +0.3, 21: +0.25, 22: +0.25, 23: +0.15, 24: +0.15,
        25: +0.08, 26: +0.08, 27: +0.0, 28: -0.1, 29: -0.2,
        30: -0.3, 31: -0.4, 32: -0.5, 33: -0.6, 34: -0.7,
        35: -0.8, 36: -0.9, 37: -1.1, 38: -1.3, 39: -1.5,
        40: -1.7, 41: -1.9, 42: -2.1
    }

    # Project until age 42
    while age < 43:
        delta = interpolate_delta(standard_deltas, age)
        current_war += delta
        
        if current_war <= 0:
            break
            
        total_future_war += current_war
        age += 1

    return total_future_war

def optimistic_aging_curve(row):
    age = float(row["Age"])
    current_war = row["WAR"]
    total_future_war = 0

    # Modified deltas for more gradual changes
    high_end_deltas = {
        20: +0.4, 21: +0.3, 22: +0.3, 23: +0.25, 24: +0.25,
        25: +0.15, 26: +0.08, 27: +0.08, 28: +0.0, 29: +0.0,
        30: -0.1, 31: -0.2, 32: -0.3, 33: -0.4, 34: -0.5,
        35: -0.6, 36: -0.8, 37: -1.0, 38: -1.2, 39: -1.4,
        40: -1.6, 41: -1.8, 42: -2.0
    }

    # Project until age 42
    while age < 43:
        delta = interpolate_delta(high_end_deltas, age)
        current_war += delta
        
        if current_war <= 0:
            break
            
        total_future_war += current_war
        age += 1

    return total_future_war

def conservative_aging_curve_pitcher(row):
    age = float(row["Age"])
    current_war = row["WAR"]
    total_future_war = 0

    low_end_deltas = {
        20: +0.15, 21: +0.15, 22: +0.15, 23: +0.08, 24: +0.08,
        25: +0.0, 26: +0.0, 27: -0.1, 28: -0.1, 29: -0.2,
        30: -0.2, 31: -0.3, 32: -0.4, 33: -0.5, 34: -0.6,
        35: -0.7, 36: -0.8, 37: -0.9, 38: -1.0, 39: -1.1,
        40: -1.2, 41: -1.3, 42: -1.4
    }

    # Project until age 42
    while age < 43:
        delta = interpolate_delta(low_end_deltas, age)
        current_war += delta
        
        if current_war <= 0:
            break
            
        total_future_war += current_war
        age += 1

    return total_future_war

def standard_aging_curve_pitcher(row):
    age = float(row["Age"])
    current_war = row["WAR"]
    total_future_war = 0

    # Modified deltas for pitchers - even slower decline
    standard_deltas = {
        20: +0.25, 21: +0.25, 22: +0.15, 23: +0.15, 24: +0.15,
        25: +0.08, 26: +0.08, 27: +0.0, 28: -0.1, 29: -0.1,
        30: -0.2, 31: -0.2, 32: -0.3, 33: -0.3, 34: -0.4,
        35: -0.5, 36: -0.6, 37: -0.7, 38: -0.8, 39: -0.9,
        40: -1.0, 41: -1.1, 42: -1.2
    }

    # Project until age 42
    while age < 43:
        delta = interpolate_delta(standard_deltas, age)
        current_war += delta
        
        if current_war <= 0:
            break
            
        total_future_war += current_war
        age += 1

    return total_future_war

def optimistic_aging_curve_pitcher(row):
    age = float(row["Age"])
    current_war = row["WAR"]
    total_future_war = 0

    high_end_deltas = {
        20: +0.3, 21: +0.25, 22: +0.25, 23: +0.15, 24: +0.15,
        25: +0.08, 26: +0.08, 27: +0.0, 28: +0.0, 29: -0.1,
        30: -0.1, 31: -0.2, 32: -0.2, 33: -0.3, 34: -0.3,
        35: -0.4, 36: -0.5, 37: -0.6, 38: -0.7, 39: -0.8,
        40: -0.9, 41: -1.0, 42: -1.1
    }

    # Project until age 42
    while age < 43:
        delta = interpolate_delta(high_end_deltas, age)
        current_war += delta
        
        if current_war <= 0:
            break
            
        total_future_war += current_war
        age += 1

    return total_future_war

# Modify add_projections to handle both hitters and pitchers
def add_projections(df, is_pitcher=False):
    if is_pitcher:
        df["ProjectedCareerWAR"] = df.apply(standard_aging_curve_pitcher, axis=1).round(1)
    else:
        df["ProjectedCareerWAR"] = df.apply(standard_aging_curve, axis=1).round(1)
    
    # Round the WAR column as well
    df["WAR"] = df["WAR"].round(1)
    return df

# Read the drafted players CSV
@st.cache_data
def load_drafted_players():
    df = pd.read_csv(
        'https://docs.google.com/spreadsheets/d/'
        '1kfOLdBmdbnr0fNgwdLDYQ3CyY-R0m5RZiCslCNjwMb4'
        '/export?format=csv&gid=306625921'
    )
    # Create a dictionary of player names and whether they're a pitcher
    drafted_dict = {
        row['Player']: row['Position'] in ['RHP', 'LHP']
        for _, row in df.iterrows() if pd.notna(row['Player'])
    }
    return drafted_dict

# Load drafted players
drafted_players = load_drafted_players()

# Function to add a Drafted column
def mark_drafted_column(df):
    """
    Adds a 'Drafted' boolean column indicating
    if the player's name is in drafted_players.
    """
    df["Drafted"] = df["NameASCII"].isin(drafted_players.keys())
    return df

# Filter function
def filter_drafted(df):
    """
    If 'show_drafted' is False, return only non-drafted players.
    Otherwise, return all players.
    """
    if not show_drafted:
        return df[df["Drafted"] == False]
    return df

# Add custom CSS for muted multiselect colors
st.markdown("""
    <style>
    /* Muted background for selected items */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #777777 !important;
        color: #0e1117 !important;
    }
    
    /* Muted hover color for selected items' delete button */
    .stMultiSelect [data-baseweb="tag"]:hover {
        background-color: #e6e9ef !important;
    }
    
    /* Muted color for the dropdown items when hovered */
    .stMultiSelect [role="option"]:hover {
        background-color: #f0f2f6 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["Hitters", "Pitchers", "Relievers"])

# Function to create Fangraphs URL
def create_fangraphs_url(player_id):
    return f"https://www.fangraphs.com/players/placeholder/{player_id}/stats"

# Hitters tab
with tab1:
    st.subheader("Top Hitters")
    
    # Ensure the needed columns exist
    if "Age" in hitters_df.columns and "WAR" in hitters_df.columns:
        hitters_df = add_projections(hitters_df)
        hitters_df = mark_drafted_column(hitters_df)
        
        filtered_hitters = filter_drafted(hitters_df)
        
        # Define baseball-logical position order
        position_order = [
            "C",    # 2
            "1B",   # 3
            "2B",   # 4
            "3B",   # 5
            "SS",   # 6
            "LF",   # 7
            "CF",   # 8
            "RF",   # 9
            "DH",   
            "OF",   # Generic outfield
            "IF",   # Generic infield
            "TWP"   # Two-way player
        ]
        
        # Sort all_positions based on the position_order
        all_positions = sorted(
            filtered_hitters["Position"].unique(),
            key=lambda x: position_order.index(x) if x in position_order else len(position_order)
        )
        
        selected_positions = st.multiselect(
            "Filter by Position",
            options=all_positions,
            default=all_positions,
            key="position_filter"
        )
        
        # Apply position filter
        filtered_hitters = filtered_hitters[filtered_hitters["Position"].isin(selected_positions)]
        
        # Add Fangraphs URL column
        filtered_hitters["FangraphsURL"] = filtered_hitters["PlayerId"].apply(create_fangraphs_url)
        
        # Hitters tab columns
        columns_to_display = [
            "NameASCII", "Position", "Team", "WAR", "Age",
            "ProjectedCareerWAR",
            "FangraphsURL"
        ]
        if show_drafted:
            columns_to_display.insert(0, "Drafted")
        
        st.dataframe(
            filtered_hitters[columns_to_display]
                .sort_values("ProjectedCareerWAR", ascending=False),
            hide_index=True,
            column_config={
                col: st.column_config.NumberColumn(
                    col,
                    format="%.1f"  # Force 1 decimal place
                )
                for col in columns_to_display
                if "WAR" in col and col not in ["NameASCII", "Team", "Position", "Drafted", "FangraphsURL"]
            } | ({
                "Drafted": st.column_config.CheckboxColumn("Drafted")
            } if show_drafted else {}) | {
                "FangraphsURL": st.column_config.LinkColumn(
                    "Fangraphs",
                    display_text="Stats"
                ),
                "WAR": st.column_config.NumberColumn(
                    "ZiPS WAR",
                    format="%.1f"
                )
            },
            height=500,
            use_container_width=True
        )
    else:
        st.warning("Make sure hitters CSV includes 'Age' and 'WAR' columns.")

# Pitchers tab
with tab2:
    st.subheader("Top Pitchers")
    
    # Ensure the needed columns exist
    if "Age" in pitchers_df.columns and "WAR" in pitchers_df.columns:
        pitchers_df = add_projections(pitchers_df, is_pitcher=True)
        pitchers_df = mark_drafted_column(pitchers_df)  # Add Drafted column
        
        # Apply drafted players filter
        filtered_pitchers = filter_drafted(pitchers_df)
        
        # Add Fangraphs URL column
        filtered_pitchers["FangraphsURL"] = filtered_pitchers["PlayerId"].apply(create_fangraphs_url)
        
        # Pitchers tab columns
        columns_to_display = [
            "NameASCII", "Team", "IP", "WAR", "Age",
            "ProjectedCareerWAR",
            "FangraphsURL"
        ]
        if show_drafted:
            columns_to_display.insert(0, "Drafted")
        
        st.dataframe(
            filtered_pitchers[columns_to_display]
                .sort_values("ProjectedCareerWAR", ascending=False),
            hide_index=True,
            column_config={
                col: st.column_config.NumberColumn(
                    col,
                    format="%.1f"  # Force 1 decimal place
                )
                for col in columns_to_display
                if "WAR" in col and col not in ["NameASCII", "Team", "Drafted", "FangraphsURL"]
            } | ({
                "Drafted": st.column_config.CheckboxColumn("Drafted")
            } if show_drafted else {}) | {
                "FangraphsURL": st.column_config.LinkColumn(
                    "Fangraphs",
                    display_text="Stats"
                ),
                "WAR": st.column_config.NumberColumn(
                    "ZiPS WAR",
                    format="%.1f"
                )
            },
            height=500,
            use_container_width=True
        )
    else:
        st.warning("Make sure pitchers CSV includes 'Age' and 'WAR' columns.")

# Relievers tab
with tab3:
    st.subheader("Relievers")
    
    # Ensure the needed columns exist
    if all(col in pitchers_df.columns for col in ["G", "GS", "IP", "ERA", "FIP", "WAR"]):
        # Create a copy of the pitchers dataframe for relievers
        relievers_df = pitchers_df[pitchers_df["G"] > 5 * pitchers_df["GS"]].copy()
        relievers_df = mark_drafted_column(relievers_df)  # Add Drafted column
        
        # Apply drafted players filter
        filtered_relievers = filter_drafted(relievers_df)
        
        # Add Fangraphs URL column
        filtered_relievers["FangraphsURL"] = filtered_relievers["PlayerId"].apply(create_fangraphs_url)
        
        # Columns to display for relievers
        columns_to_display = ["NameASCII", "Team", "Age", "WAR", "IP", "ERA", "FIP", "FangraphsURL"]  # Swapped IP and Age
        if show_drafted:
            columns_to_display.insert(0, "Drafted")
        
        st.dataframe(
            filtered_relievers[columns_to_display]
                .sort_values("WAR", ascending=False),  # Sort by WAR (higher is better)
            hide_index=True,
            column_config={
                col: st.column_config.NumberColumn(
                    col,
                    format="%.1f"  # Force 1 decimal place
                )
                for col in columns_to_display
                if "WAR" in col and col not in ["NameASCII", "Team", "Drafted", "FangraphsURL"]
            } | ({
                "Drafted": st.column_config.CheckboxColumn("Drafted")
            } if show_drafted else {}) | {
                "FangraphsURL": st.column_config.LinkColumn(
                    "Fangraphs",
                    display_text="Stats"
                ),
                "WAR": st.column_config.NumberColumn(
                    "ZiPS WAR",
                    format="%.1f"
                )
            },
            height=500,
            use_container_width=True
        )
    else:
        st.warning("Make sure pitchers CSV includes 'G', 'GS', 'IP', 'ERA', 'FIP', and 'WAR' columns.")
