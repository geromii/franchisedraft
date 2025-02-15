import streamlit as st
import pandas as pd


#page metadata
st.set_page_config(
    page_title="Franchise Draft - Beetie Board",
    page_icon=":baseball:",
    layout="wide",
)

# Title and description
st.title("Franchise Draft - Beetie Board")
st.write("Career WAR projections for the best players available")

DISCOUNT_RATE = 0.10

# Add custom query box
with st.expander("Custom Query"):
    st.markdown("""
    Enter a custom query using Python/Pandas syntax. Examples:
    - `WAR > 3 and Age < 25`
    - `Position == "SS" and WAR > 2`
    - `Team == "LAD"`
    """)
    custom_query = st.text_input("Query", key="custom_query", placeholder="Enter query here...")

# Create three columns for the controls
col1, col2, col3 = st.columns(3)

# Add controls in separate columns
with col1:
    show_drafted = st.toggle("Show Drafted Players", value=False, 
                           key="show_drafted_toggle", label_visibility="visible")
with col2:
    use_discount_rate = st.toggle(f"Apply {DISCOUNT_RATE:.0%} Discount Rate", value=False, 
                                key="use_discount_rate", help=f"Discount future WAR by (1 + {DISCOUNT_RATE:.0%})^years")
with col3:
    projection_system = st.radio(
        "Projection System",
        ["ZiPS", "Steamer600"],
        horizontal=True,
        key="projection_system"
    )

# Function to apply custom query
def apply_custom_query(df):
    """
    Applies a custom query to the dataframe if one is provided.
    Returns the filtered dataframe.
    """
    if custom_query:
        try:
            return df.query(custom_query)
        except Exception as e:
            st.error(f"Invalid query: {str(e)}")
            return df
    return df

# Modify filter_drafted to include custom query
def filter_drafted(df):
    """
    If 'show_drafted' is False, return only non-drafted players.
    Also applies any custom query.
    """
    filtered_df = df if show_drafted else df[df["DraftPos"].isna()]
    return apply_custom_query(filtered_df)

# Move all function definitions to the top
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

 # Annual discount rate for future WAR projections

def standard_aging_curve(row):
    age = float(row["Age"])
    current_war = row["WAR"]
    total_future_war = max(0, current_war)  # Only count positive initial WAR
    years_from_now = 0

    # Modified deltas for hitters - expanded age range
    standard_deltas = {
        16: +0.35, 17: +0.30, 18: +0.30, 19: +0.25, 20: +0.25, 
        21: +0.20, 22: +0.20, 23: +0.10, 24: +0.10,
        25: +0.03, 26: +0.03, 27: -0.05, 28: -0.15, 29: -0.25,
        30: -0.35, 31: -0.45, 32: -0.55, 33: -0.65, 34: -0.75,
        35: -0.85, 36: -0.95, 37: -1.15, 38: -1.35, 39: -1.55,
        40: -1.75, 41: -1.95, 42: -2.15, 43: -2.35, 44: -2.55,
        45: -2.8
    }

    # Project until age 45
    while age < 46:
        delta = interpolate_delta(standard_deltas, age)
        current_war += delta
        
        # Only add positive WAR values to total, with optional discount
        if current_war > 0:
            if use_discount_rate:
                discount_factor = 1 / ((1 + DISCOUNT_RATE) ** years_from_now)
                total_future_war += current_war * discount_factor
            else:
                total_future_war += current_war
            
        age += 1
        years_from_now += 1

    return total_future_war

def standard_aging_curve_pitcher(row):
    age = float(row["Age"])
    current_war = row["WAR"]
    total_future_war = max(0, current_war)
    years_from_now = 0

    # Modified deltas for pitchers - expanded age range
    standard_deltas = {
        16: +0.30, 17: +0.25, 18: +0.25, 19: +0.20, 20: +0.20, 
        21: +0.20, 22: +0.10, 23: +0.10, 24: +0.10,
        25: +0.03, 26: +0.03, 27: -0.05, 28: -0.15, 29: -0.15,
        30: -0.25, 31: -0.25, 32: -0.35, 33: -0.35, 34: -0.45,
        35: -0.55, 36: -0.65, 37: -0.75, 38: -0.85, 39: -0.95,
        40: -1.05, 41: -1.15, 42: -1.25, 43: -1.35, 44: -1.45,
        45: -1.55
    }

    # Project until age 45
    while age < 46:
        delta = interpolate_delta(standard_deltas, age)
        current_war += delta
        
        if current_war > 0:
            if use_discount_rate:
                discount_factor = 1 / ((1 + DISCOUNT_RATE) ** years_from_now)
                total_future_war += current_war * discount_factor
            else:
                total_future_war += current_war
            
        age += 1
        years_from_now += 1

    return total_future_war

def flat_aging_curve(row):
    age = float(row["Age"])
    current_war = row["WAR"]
    total_future_war = max(0, current_war)
    years_from_now = 0

    # Flattened deltas for hitters - expanded age range
    flat_deltas = {
        16: +0.05, 17: +0.03, 18: +0.02, 19: +0.01, 20: +0.01,
        21: +0.01, 22: -0.03, 23: -0.06, 24: -0.09,
        25: -0.13, 26: -0.17, 27: -0.21, 28: -0.25, 29: -0.30,
        30: -0.35, 31: -0.40, 32: -0.45, 33: -0.50, 34: -0.55,
        35: -0.60, 36: -0.70, 37: -0.80, 38: -0.90, 39: -1.00,
        40: -1.10, 41: -1.20, 42: -1.30, 43: -1.40, 44: -1.50,
        45: -1.60
    }

    # Project until age 45
    while age < 46:
        delta = interpolate_delta(flat_deltas, age)
        current_war += delta
        
        if current_war > 0:
            if use_discount_rate:
                discount_factor = 1 / ((1 + DISCOUNT_RATE) ** years_from_now)
                total_future_war += current_war * discount_factor
            else:
                total_future_war += current_war
            
        age += 1
        years_from_now += 1

    return total_future_war

def flat_aging_curve_pitcher(row):
    age = float(row["Age"])
    current_war = row["WAR"]
    total_future_war = max(0, current_war)
    years_from_now = 0

    # Flattened deltas for pitchers - expanded age range
    flat_deltas = {
        16: +0.02, 17: +0.01, 18: +0.00, 19: -0.01, 20: -0.02,
        21: -0.02, 22: -0.05, 23: -0.08, 24: -0.08,
        25: -0.11, 26: -0.14, 27: -0.17, 28: -0.22, 29: -0.22,
        30: -0.25, 31: -0.25, 32: -0.30, 33: -0.30, 34: -0.33,
        35: -0.37, 36: -0.41, 37: -0.45, 38: -0.50, 39: -0.55,
        40: -0.60, 41: -0.65, 42: -0.70, 43: -0.75, 44: -0.80,
        45: -0.85
    }

    # Project until age 45
    while age < 46:
        delta = interpolate_delta(flat_deltas, age)
        current_war += delta
        
        if current_war > 0:
            if use_discount_rate:
                discount_factor = 1 / ((1 + DISCOUNT_RATE) ** years_from_now)
                total_future_war += current_war * discount_factor
            else:
                total_future_war += current_war
            
        age += 1
        years_from_now += 1

    return total_future_war

# Modify add_projections to calculate both curves
def add_projections(df, is_pitcher=False):
    if is_pitcher:
        df["ProjectedCareerWAR"] = df.apply(standard_aging_curve_pitcher, axis=1).round(1)
        df["FlatProjectedCareerWAR"] = df.apply(flat_aging_curve_pitcher, axis=1).round(1)
    else:
        df["ProjectedCareerWAR"] = df.apply(standard_aging_curve, axis=1).round(1)
        df["FlatProjectedCareerWAR"] = df.apply(flat_aging_curve, axis=1).round(1)
    
    df["WAR"] = df["WAR"].round(1)
    return df

# Cache the data loading with TTL of 1 day (in seconds)
@st.cache_data(ttl=24*3600)  # 24 hours * 3600 seconds
def load_csv_files():
    """Cache the loading of CSV files to improve startup time"""
    zips_hitters = pd.read_csv('zips-hitters-2025.csv')
    zips_pitchers = pd.read_csv('zips-pitchers-2025.csv')
    steamer_hitters = pd.read_csv('steamer600-hitters-2025.csv')
    steamer_pitchers = pd.read_csv('steamer600-pitchers-2025.csv')
    ba_top_100 = pd.read_csv('ba_top_100.csv')
    return zips_hitters, zips_pitchers, steamer_hitters, steamer_pitchers, ba_top_100

# Cache the projection calculations with TTL of 1 day
@st.cache_data(ttl=24*3600)  # 24 hours * 3600 seconds
def calculate_projections(df, is_pitcher=False):
    """Cache the WAR projections calculations"""
    return add_projections(df, is_pitcher)

# Cache the drafted players with TTL of 1 day
@st.cache_data(ttl=24*3600)  # 24 hours * 3600 seconds
def load_drafted_players():
    df = pd.read_csv(
        'https://docs.google.com/spreadsheets/d/'
        '1kfOLdBmdbnr0fNgwdLDYQ3CyY-R0m5RZiCslCNjwMb4'
        '/export?format=csv&gid=306625921'
    )
    # Create a dictionary of player names to their draft position
    drafted_dict = {}
    for idx, row in df.iterrows():
        if pd.notna(row['Player']):
            # idx + 1 represents draft position (1-based indexing)
            drafted_dict[row['Player']] = idx + 1
    return drafted_dict

# Read the CSV files
zips_hitters_df, zips_pitchers_df, steamer_hitters_df, steamer_pitchers_df, ba_top_100_df = load_csv_files()

# Select appropriate dataframe based on projection system
hitters_df = steamer_hitters_df if projection_system == "Steamer600" else zips_hitters_df
pitchers_df = steamer_pitchers_df if projection_system == "Steamer600" else zips_pitchers_df

# Calculate projections using cached function
if "Age" in hitters_df.columns and "WAR" in hitters_df.columns:
    hitters_df = calculate_projections(hitters_df)

if "Age" in pitchers_df.columns and "WAR" in pitchers_df.columns:
    pitchers_df = calculate_projections(pitchers_df, is_pitcher=True)

# Load drafted players
drafted_players = load_drafted_players()

# Function to add a Draft Position column
def mark_drafted_column(df):
    """
    Adds a 'DraftPos' integer column indicating
    the position where the player was drafted (empty if undrafted)
    """
    name_column = "NameASCII" if "NameASCII" in df.columns else "Name"
    df["DraftPos"] = df[name_column].map(drafted_players)
    return df

# Create tabs with emojis
tab1, tab2, tab3, tab4 = st.tabs([
    "🏃 Hitters", 
    "⚾ Pitchers", 
    "🎯 Relievers", 
    "⭐ BA Top 100"
])

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
        
        # Add custom CSS for muted styling
        st.markdown("""
            <style>
            div[data-baseweb="select"] span {
                background-color: #666666 !important;
                border-color: #d1d5db !important;
            }
            div[data-baseweb="tag"] {
                background-color: #f0f2f6 !important;
                border-color: #d1d5db !important;
            }
            </style>
        """, unsafe_allow_html=True)

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
            "NameASCII", "Position", "Team", "Age", "WAR",
            "ProjectedCareerWAR", "FlatProjectedCareerWAR",
            "FangraphsURL"
        ]
        if show_drafted:
            columns_to_display.insert(0, "DraftPos")
        
        st.dataframe(
            filtered_hitters[columns_to_display]
                .sort_values("ProjectedCareerWAR", ascending=False),
            hide_index=True,
            column_config={
                col: st.column_config.NumberColumn(
                    col,
                    format="%.1f"
                )
                for col in columns_to_display
                if "WAR" in col and col not in ["NameASCII", "Team", "Position", "DraftPos", "FangraphsURL"]
            } | ({
                "DraftPos": st.column_config.NumberColumn(
                    "Drafted",
                    format="%d",
                    default=""
                )
            } if show_drafted else {}) | {
                "FangraphsURL": st.column_config.LinkColumn(
                    "Fangraphs",
                    display_text="Stats"
                ),
                "WAR": st.column_config.NumberColumn(
                    f"{projection_system} WAR",  # Update column header
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
            "NameASCII", "Team", "Age", "WAR", "IP",
            "ProjectedCareerWAR", "FlatProjectedCareerWAR",
            "FangraphsURL"
        ]
        if show_drafted:
            columns_to_display.insert(0, "DraftPos")
        
        st.dataframe(
            filtered_pitchers[columns_to_display]
                .sort_values("ProjectedCareerWAR", ascending=False),
            hide_index=True,
            column_config={
                col: st.column_config.NumberColumn(
                    col,
                    format="%.1f"
                )
                for col in columns_to_display
                if "WAR" in col and col not in ["NameASCII", "Team", "DraftPos", "FangraphsURL"]
            } | ({
                "DraftPos": st.column_config.NumberColumn(
                    "Draft #",
                    format="%d",
                    default=""
                )
            } if show_drafted else {}) | {
                "FangraphsURL": st.column_config.LinkColumn(
                    "Fangraphs",
                    display_text="Stats"
                ),
                "WAR": st.column_config.NumberColumn(
                    f"{projection_system} WAR",  # Update column header
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
        columns_to_display = ["NameASCII", "Team", "Age", "WAR", "IP", "ERA", "FIP", "FangraphsURL"]  # Already in correct order
        if show_drafted:
            columns_to_display.insert(0, "DraftPos")
        
        st.dataframe(
            filtered_relievers[columns_to_display]
                .sort_values("WAR", ascending=False),  # Sort by WAR (higher is better)
            hide_index=True,
            column_config={
                col: st.column_config.NumberColumn(
                    col,
                    format="%.1f"
                )
                for col in columns_to_display
                if "WAR" in col and col not in ["NameASCII", "Team", "DraftPos", "FangraphsURL"]
            } | ({
                "DraftPos": st.column_config.NumberColumn(
                    "Draft #",
                    format="%d",
                    default=""
                )
            } if show_drafted else {}) | {
                "FangraphsURL": st.column_config.LinkColumn(
                    "Fangraphs",
                    display_text="Stats"
                ),
                "WAR": st.column_config.NumberColumn(
                    f"{projection_system} WAR",  # Update column header
                    format="%.1f"
                )
            },
            height=500,
            use_container_width=True
        )
    else:
        st.warning("Make sure pitchers CSV includes 'G', 'GS', 'IP', 'ERA', 'FIP', and 'WAR' columns.")

# BA Top 100 tab
with tab4:
    st.subheader("Baseball America Top 100")
    
    # Mark drafted players in BA Top 100
    ba_top_100_df = mark_drafted_column(ba_top_100_df)
    
    # Apply drafted players filter
    filtered_ba = filter_drafted(ba_top_100_df)
    
    # Define columns to display
    columns_to_display = ["Rank", "Name", "Team", "Position"]
    if show_drafted:
        columns_to_display.insert(0, "DraftPos")
    
    st.dataframe(
        filtered_ba[columns_to_display]
            .sort_values("Rank"),
        hide_index=True,
        column_config={
            "Rank": st.column_config.NumberColumn(
                "Rank",
                format="%d"  # No decimal places for rank
            )
        } | ({
            "DraftPos": st.column_config.NumberColumn(
                "Draft #",
                format="%d",
                default=""
            )
        } if show_drafted else {}),
        height=500,
        use_container_width=True
    )
