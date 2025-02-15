import streamlit as st
import pandas as pd
import numpy as np

# -------------------------------#
# 1. CONFIG AND PAGE METADATA
# -------------------------------#

st.set_page_config(
    page_title="Franchise Draft - Beetie Board",
    page_icon=":baseball:",
    layout="wide",
)

st.title("Franchise Draft - Beetie Board")
st.write("Career WAR projections for the best players available, merged across multiple systems.")

DISCOUNT_RATE = 0.10  # 10% discount rate

# -------------------------------#
# 2. STREAMLIT WIDGETS
# -------------------------------#

# Custom query
with st.expander("Custom Query"):
    st.markdown("""
    Enter a custom query using Python/Pandas syntax. Examples:
    - `SteamerWAR > 3 and Age < 25`
    - `Position == "SS" and BatXWAR > 2`
    - `Team == "LAD"` (if you have a Team column)
    """)
    custom_query = st.text_input("Query", key="custom_query", placeholder="Enter query here...")

col1, col2, col3 = st.columns(3)

with col1:
    show_drafted = st.toggle("Show Drafted Players", value=False, 
                             key="show_drafted_toggle", label_visibility="visible")
with col2:
    use_discount_rate = st.toggle(f"Apply {DISCOUNT_RATE:.0%} Discount Rate", value=False, 
                                  key="use_discount_rate",
                                  help=f"Discount future WAR by (1 + {DISCOUNT_RATE:.0%})^years")
with col3:
    use_flat_curve = st.toggle("Use Flattened Aging Curve", value=False, 
                               key="use_flat_curve", 
                               help="Uses a flattened aging curve, with less growth and less decline.")

# Add position filter
positions = ["C", "1B", "2B", "3B", "SS", "OF", "DH"]  # Common positions
selected_positions = st.multiselect(
    "Filter by Position(s)",
    options=positions,
    default=[],
    help="Select one or more positions to filter the hitters table"
)

# -------------------------------#
# 3. HELPER FUNCTIONS
# -------------------------------#

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

def aging_projection(row, is_pitcher, discount, flatten):
    """
    Calculates career WAR from current WAR and age, 
    optionally using a flattened or standard aging curve,
    and optionally discounting future WAR.
    """
    age = float(row["Age"])
    current_war = row["WAR"]  # System-specific single-year WAR
    total_future_war = max(0, current_war)
    years_from_now = 0

    # Choose deltas based on whether it's a pitcher or hitter, and whether flattening is used
    if is_pitcher:
        if not flatten:
            # Standard pitcher deltas
            deltas = {
                16: +0.30, 17: +0.25, 18: +0.25, 19: +0.20, 20: +0.20, 
                21: +0.20, 22: +0.10, 23: +0.10, 24: +0.10,
                25: +0.03, 26: +0.03, 27: -0.05, 28: -0.15, 29: -0.15,
                30: -0.25, 31: -0.25, 32: -0.35, 33: -0.35, 34: -0.45,
                35: -0.55, 36: -0.65, 37: -0.75, 38: -0.85, 39: -0.95,
                40: -1.05, 41: -1.15, 42: -1.25, 43: -1.35, 44: -1.45,
                45: -1.55
            }
        else:
            # Flattened pitcher deltas
            deltas = {
                16: +0.02, 17: +0.01, 18: +0.00, 19: -0.01, 20: -0.02,
                21: -0.02, 22: -0.05, 23: -0.08, 24: -0.08,
                25: -0.11, 26: -0.14, 27: -0.17, 28: -0.22, 29: -0.22,
                30: -0.25, 31: -0.25, 32: -0.30, 33: -0.30, 34: -0.33,
                35: -0.37, 36: -0.41, 37: -0.45, 38: -0.50, 39: -0.55,
                40: -0.60, 41: -0.65, 42: -0.70, 43: -0.75, 44: -0.80,
                45: -0.85
            }
    else:
        if not flatten:
            # Standard hitter deltas
            deltas = {
                16: +0.35, 17: +0.30, 18: +0.30, 19: +0.25, 20: +0.25, 
                21: +0.20, 22: +0.20, 23: +0.10, 24: +0.10,
                25: +0.03, 26: +0.03, 27: -0.05, 28: -0.15, 29: -0.25,
                30: -0.35, 31: -0.45, 32: -0.55, 33: -0.65, 34: -0.75,
                35: -0.85, 36: -0.95, 37: -1.15, 38: -1.35, 39: -1.55,
                40: -1.75, 41: -1.95, 42: -2.15, 43: -2.35, 44: -2.55,
                45: -2.80
            }
        else:
            # Flattened hitter deltas
            deltas = {
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
        delta = interpolate_delta(deltas, age)
        current_war += delta

        if current_war > 0:
            if discount:
                discount_factor = 1 / ((1 + DISCOUNT_RATE) ** years_from_now)
                total_future_war += current_war * discount_factor
            else:
                total_future_war += current_war

        age += 1
        years_from_now += 1

    return total_future_war


def calculate_career_war(df, is_pitcher=False, discount=False, flatten=False, war_col="WAR", new_col="CareerWAR"):
    """
    Adds a column `new_col` to df that calculates the career WAR 
    given the current (war_col), age, and an aging-curve approach.
    """
    # Make sure Age and WAR columns are numeric
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df[war_col] = pd.to_numeric(df[war_col], errors="coerce")
    
    df[new_col] = df.apply(
        lambda row: aging_projection(
            row={
                "Age": row["Age"], 
                "WAR": row[war_col]
            },
            is_pitcher=is_pitcher,
            discount=discount,
            flatten=flatten
        ),
        axis=1
    ).round(1)

    return df

def apply_custom_query(df):
    """Applies a custom query to the dataframe if one is provided."""
    if custom_query:
        try:
            return df.query(custom_query)
        except Exception as e:
            st.error(f"Invalid query: {str(e)}")
            return df
    return df

@st.cache_data(ttl=24*3600)
def load_drafted_players():
    """
    Load the Google Sheet with draft picks. 
    Return a dict {player_name : draft_position} 
    The names in the sheet are already in ASCII format.
    """
    df = pd.read_csv(
        'https://docs.google.com/spreadsheets/d/'
        '1kfOLdBmdbnr0fNgwdLDYQ3CyY-R0m5RZiCslCNjwMb4'
        '/export?format=csv&gid=306625921'
    )
    drafted_dict = {}
    for idx, row in df.iterrows():
        if pd.notna(row['Player']):
            # idx + 1 is the draft position
            drafted_dict[row['Player']] = idx + 1  # Use 'Player' since it's already ASCII
    return drafted_dict

def filter_drafted(df, show_drafted):
    """
    If show_drafted=False, only show those not drafted.
    If show_drafted=True, show all (or highlight).
    """
    if not show_drafted:
        return df[df["DraftPos"].isna()]
    else:
        return df

def create_fangraphs_url(player_id):
    """Creates a Fangraphs URL from a player ID"""
    if pd.isna(player_id):
        return None
    return f"https://www.fangraphs.com/players/placeholder/{player_id}/stats"

# -------------------------------#
# 4. LOAD ALL CSV FILES
# -------------------------------#

@st.cache_data(ttl=24*3600)
def load_csv_files():
    """
    Load all the raw CSVs.
    Make sure each has:
       - MLBAMID (unique identifier)
       - WAR (2025 projection)
       - Age
       - Position
       - etc.
    """
    zips_hitters = pd.read_csv('zips-hitters-2025.csv')
    zips_pitchers = pd.read_csv('zips-pitchers-2025.csv')
    steamer_hitters = pd.read_csv('steamer600-hitters-2025.csv')
    steamer_pitchers = pd.read_csv('steamer600-pitchers-2025.csv')
    batx_hitters = pd.read_csv('batx-hitters-2025.csv')
    ba_top_100 = pd.read_csv('ba_top_100.csv')
    return zips_hitters, zips_pitchers, steamer_hitters, steamer_pitchers, batx_hitters, ba_top_100

zips_hitters_df, zips_pitchers_df, steamer_hitters_df, steamer_pitchers_df, batx_hitters_df, ba_top_100_df = load_csv_files()

drafted_dict = load_drafted_players()  # {playerName -> draftPos}

# -------------------------------#
# 5. PREPARE MERGED DATAFRAMES
# -------------------------------#

# ---- HELPER: rename columns after computing career WAR ----
def prep_projection_df(
    df, 
    system_name, 
    is_pitcher=False, 
    discount=False, 
    flatten=False,
    war_col="WAR",
    rename_age_pos=False
):
    """
    1) Calculate career WAR (standard & flatten).
    2) Rename columns from 'WAR' -> '{system_name}WAR' 
       and 'CareerWAR' -> '{system_name}Career'.
    3) Return the subset of columns we want: 
       [MLBAMID, {system_name}WAR, {system_name}Career, (optionally Age, Position, NameASCII)]
    4) If rename_age_pos=True, we keep the Age, Position, NameASCII from this df 
       for later merges (i.e. Steamer is the "source" for age/position).
    """
    df = df.copy()
    # Calculate career WAR in a column "CareerWAR"
    df = calculate_career_war(
        df, 
        is_pitcher=is_pitcher, 
        discount=discount, 
        flatten=flatten, 
        war_col=war_col,
        new_col="CareerWAR"
    )
    
    # Round single-year WAR
    df[war_col] = df[war_col].round(1)

    # Rename columns for clarity
    df.rename(
        columns={
            war_col: f"{system_name}WAR",
            "CareerWAR": f"{system_name}Career"
        }, 
        inplace=True
    )
    
    # Decide what columns to keep
    keep_cols = ["MLBAMID", f"{system_name}WAR", f"{system_name}Career", "PlayerId"]  # Added PlayerId
    if rename_age_pos:
        # Keep Age, Position, NameASCII from this system (Steamer recommended)
        for c in ["Age", "Position", "NameASCII", "Team"]:
            if c in df.columns:
                keep_cols.append(c)
    
    # Only keep columns that exist in the dataframe
    keep_cols = [col for col in keep_cols if col in df.columns]
    return df[keep_cols].copy()


# -------------------------------#
# 5A. MERGE HITTERS
# -------------------------------#

@st.cache_data(ttl=24*3600)
def build_merged_hitters_df(discount=False, flatten=False):
    """
    Merge (ZiPS, Steamer, BATX) hitters on MLBAMID.
    Position, Age, Name come from Steamer by default, falling back to ZiPS then BatX.
    """
    # First, prep each projection's df
    # Keep Age/Position/Name from all systems for fallback
    zips_h = prep_projection_df(zips_hitters_df, "ZiPS", is_pitcher=False, discount=discount, flatten=flatten, war_col="WAR", rename_age_pos=True)
    steamer_h = prep_projection_df(steamer_hitters_df, "Steamer", is_pitcher=False, discount=discount, flatten=flatten, war_col="WAR", rename_age_pos=True)
    batx_h = prep_projection_df(batx_hitters_df, "BatX", is_pitcher=False, discount=discount, flatten=flatten, war_col="WAR", rename_age_pos=True)

    # Merge on MLBAMID
    merged = steamer_h.merge(zips_h, on="MLBAMID", how="outer", suffixes=("", "_ZiPS"))
    merged = merged.merge(batx_h, on="MLBAMID", how="outer", suffixes=("", "_BatX"))
    
    # Fill missing demographic data from ZiPS then BatX
    for col in ["Age", "Position", "NameASCII", "Team"]:
        if col in merged.columns:
            merged[col] = merged[col].fillna(merged[f"{col}_ZiPS"] if f"{col}_ZiPS" in merged.columns else np.nan)
            merged[col] = merged[col].fillna(merged[f"{col}_BatX"] if f"{col}_BatX" in merged.columns else np.nan)
    
    # Drop the extra demographic columns
    cols_to_drop = [c for c in merged.columns if c.endswith(("_ZiPS", "_BatX")) and c.split("_")[0] in ["Age", "Position", "NameASCII", "Team"]]
    merged = merged.drop(columns=cols_to_drop)
    
    return merged


# -------------------------------#
# 5B. MERGE PITCHERS
# -------------------------------#

@st.cache_data(ttl=24*3600)
def build_merged_pitchers_df(discount=False, flatten=False):
    """
    Merge ZiPS and Steamer pitchers on MLBAMID.
    Position, Age, Name come from Steamer by default, falling back to ZiPS.
    """
    zips_p = prep_projection_df(zips_pitchers_df, "ZiPS", is_pitcher=True, discount=discount, flatten=flatten, war_col="WAR", rename_age_pos=True)
    steamer_p = prep_projection_df(steamer_pitchers_df, "Steamer", is_pitcher=True, discount=discount, flatten=flatten, war_col="WAR", rename_age_pos=True)

    merged = steamer_p.merge(zips_p, on="MLBAMID", how="outer", suffixes=("", "_ZiPS"))
    
    # Fill missing demographic data from ZiPS
    for col in ["Age", "Position", "NameASCII", "Team"]:
        if col in merged.columns:
            merged[col] = merged[col].fillna(merged[f"{col}_ZiPS"] if f"{col}_ZiPS" in merged.columns else np.nan)
    
    # Drop the extra demographic columns
    cols_to_drop = [c for c in merged.columns if c.endswith("_ZiPS") and c.split("_")[0] in ["Age", "Position", "NameASCII", "Team"]]
    merged = merged.drop(columns=cols_to_drop)
    
    return merged


# -------------------------------#
# 6. BUILD FINAL DATAFRAMES
# -------------------------------#

hitters_merged = build_merged_hitters_df(discount=use_discount_rate, flatten=use_flat_curve)
pitchers_merged = build_merged_pitchers_df(discount=use_discount_rate, flatten=use_flat_curve)

# Add a "DraftPos" column by matching the player's *NameASCII* to your drafted_dict
# (If you have a better unique identifier (MLBAMID -> draftpos), adapt accordingly.)
def mark_drafted_column(df):
    df = df.copy()
    if "NameASCII" in df.columns:
        df["DraftPos"] = df["NameASCII"].map(drafted_dict)
    else:
        df["DraftPos"] = None
    return df

hitters_merged = mark_drafted_column(hitters_merged)
pitchers_merged = mark_drafted_column(pitchers_merged)

# Filter drafted or not, based on toggle
hitters_final = filter_drafted(hitters_merged, show_drafted)
pitchers_final = filter_drafted(pitchers_merged, show_drafted)

# Apply custom query if needed
hitters_final = apply_custom_query(hitters_final)
pitchers_final = apply_custom_query(pitchers_final)

# -------------------------------#
# 7. DISPLAY TABS
# -------------------------------#

tab1, tab2, tab3, tab4 = st.tabs([
    "🏃 Hitters", 
    "⚾ Pitchers",
    "🎯 Relievers",
    "⭐ BA Top 100"
])

with tab1:
    st.subheader("Hitters - ZiPS, Steamer, & BATX")
    
    # Filter by selected positions if any are chosen
    if selected_positions:
        # Create expanded position list that includes specific OF positions when "OF" is selected
        expanded_positions = []
        for pos in selected_positions:
            if pos == "OF":
                expanded_positions.extend(["OF", "LF", "CF", "RF"])
            else:
                expanded_positions.append(pos)
        hitters_final = hitters_final[hitters_final["Position"].isin(expanded_positions)]
    
    # Add FangraphsURL to columns
    columns_to_show = [
        "NameASCII", 
        "Position", 
        "Age", 
        "ZiPSWAR", 
        "SteamerWAR", 
        "BatXWAR", 
        "ZiPSCareer", 
        "SteamerCareer", 
        "BatXCareer",
        "FangraphsURL"
    ]
    if show_drafted:
        columns_to_show.insert(0, "DraftPos")
    
    # Create FangraphsURL column before displaying
    hitters_final = hitters_final.copy()
    hitters_final["FangraphsURL"] = hitters_final["PlayerId"].apply(create_fangraphs_url)
    
    # Make sure the columns exist in final df (some might be NaN if not projected by BatX, etc.)
    columns_to_show = [c for c in columns_to_show if c in hitters_final.columns]
    
    st.dataframe(
        hitters_final[columns_to_show].sort_values("SteamerCareer", ascending=False),
        hide_index=True,
        use_container_width=True,
        height=600,
        column_config={
            "DraftPos": st.column_config.NumberColumn("Drafted", format="%d"),
            "ZiPSWAR":  st.column_config.NumberColumn("ZiPS WAR", format="%.1f"),
            "SteamerWAR": st.column_config.NumberColumn("Steamer600 WAR", format="%.1f"),
            "BatXWAR":  st.column_config.NumberColumn("BatX WAR", format="%.1f"),
            "ZiPSCareer":  st.column_config.NumberColumn("ZiPS Career", format="%.1f"),
            "SteamerCareer": st.column_config.NumberColumn("Steamer600 Career", format="%.1f"),
            "BatXCareer":  st.column_config.NumberColumn("BatX Career", format="%.1f"),
            "FangraphsURL": st.column_config.LinkColumn(
                "Fangraphs",
                display_text="Stats"
            ),
        }
    )

with tab2:
    st.subheader("Pitchers - ZiPS & Steamer")
    
    columns_to_show = [
        "NameASCII",
        "Position",
        "Age",
        "ZiPSWAR",
        "SteamerWAR",
        "ZiPSCareer",
        "SteamerCareer",
        "FangraphsURL"
    ]
    if show_drafted:
        columns_to_show.insert(0, "DraftPos")
    
    # Create FangraphsURL column before displaying
    pitchers_final = pitchers_final.copy()
    pitchers_final["FangraphsURL"] = pitchers_final["PlayerId"].apply(create_fangraphs_url)
    
    columns_to_show = [c for c in columns_to_show if c in pitchers_final.columns]
    
    st.dataframe(
        pitchers_final[columns_to_show].sort_values("SteamerCareer", ascending=False),
        hide_index=True,
        use_container_width=True,
        height=600,
        column_config={
            "DraftPos": st.column_config.NumberColumn("Drafted", format="%d"),
            "ZiPSWAR":  st.column_config.NumberColumn("ZiPS WAR", format="%.1f"),
            "SteamerWAR": st.column_config.NumberColumn("Steamer600 WAR", format="%.1f"),
            "ZiPSCareer":  st.column_config.NumberColumn("ZiPS Career", format="%.1f"),
            "SteamerCareer": st.column_config.NumberColumn("Steamer600 Career", format="%.1f"),
            "FangraphsURL": st.column_config.LinkColumn(
                "Fangraphs",
                display_text="Stats"
            ),
        }
    )

with tab3:
    st.subheader("Relievers")
    st.write("Showing pitchers with 4× more Games than Games Started in ZiPS projections.")
    
    # Create reliever-specific dataframe from ZiPS data
    if all(col in zips_pitchers_df.columns for col in ["G", "GS"]):
        # Start with ZiPS data and filter for relievers
        relievers_df = zips_pitchers_df[
            zips_pitchers_df["G"] > 4 * zips_pitchers_df["GS"]
        ].copy()
        
        # Keep relevant ZiPS columns
        zips_cols = ["MLBAMID", "NameASCII", "IP", "ERA", "FIP", "WAR", "PlayerId"]  # Added PlayerId
        relievers_df = relievers_df[
            [col for col in zips_cols if col in relievers_df.columns]
        ].copy()
        
        # Rename ZiPS columns (except MLBAMID, NameASCII, and PlayerId)
        rename_cols = {col: f"ZiPS_{col}" for col in zips_cols[2:-1]}  # Skip MLBAMID, NameASCII, PlayerId
        relievers_df.columns = ["MLBAMID", "NameASCII"] + [f"ZiPS_{col}" for col in zips_cols[2:-1]] + ["PlayerId"]
        
        # Merge with Steamer data
        steamer_cols = ["MLBAMID", "Age", "ERA", "FIP", "WAR"]
        steamer_relief = steamer_pitchers_df[steamer_cols].copy()
        steamer_relief.columns = ["MLBAMID", "Age"] + [f"Steamer_{col}" for col in steamer_cols[2:]]
        
        # Merge ZiPS and Steamer
        relievers_df = relievers_df.merge(
            steamer_relief, 
            on="MLBAMID", 
            how="left"
        )
        
        # Mark drafted players
        relievers_df = mark_drafted_column(relievers_df)
        relievers_df = filter_drafted(relievers_df, show_drafted)
        relievers_df = apply_custom_query(relievers_df)

        # Add FangraphsURL column
        if "PlayerId" in relievers_df.columns:
            relievers_df["FangraphsURL"] = relievers_df["PlayerId"].apply(create_fangraphs_url)
        else:
            relievers_df["FangraphsURL"] = None
            st.warning("PlayerId column not found - Fangraphs links unavailable")

        # Columns to display - reordered to group similar stats
        columns_to_show = [
            "NameASCII",
            "Age",
            "ZiPS_IP",
            "ZiPS_ERA",
            "Steamer_ERA",
            "ZiPS_FIP",
            "Steamer_FIP",
            "ZiPS_WAR",
            "Steamer_WAR",
            "FangraphsURL"
        ]
        if show_drafted:
            columns_to_show.insert(0, "DraftPos")

        st.dataframe(
            relievers_df[columns_to_show].sort_values("ZiPS_WAR", ascending=False),
            hide_index=True,
            use_container_width=True,
            height=600,
            column_config={
                "DraftPos": st.column_config.NumberColumn("Drafted", format="%d"),
                "Age": st.column_config.NumberColumn("Age", format="%.1f"),  # Show decimal ages
                "ZiPS_IP": st.column_config.NumberColumn("IP (ZiPS)", format="%.1f"),
                "ZiPS_ERA": st.column_config.NumberColumn("ERA (ZiPS)", format="%.2f"),
                "Steamer_ERA": st.column_config.NumberColumn("ERA (Steamer)", format="%.2f"),
                "ZiPS_FIP": st.column_config.NumberColumn("FIP (ZiPS)", format="%.2f"),
                "Steamer_FIP": st.column_config.NumberColumn("FIP (Steamer)", format="%.2f"),
                "ZiPS_WAR": st.column_config.NumberColumn("WAR (ZiPS)", format="%.1f"),
                "Steamer_WAR": st.column_config.NumberColumn("WAR (Steamer)", format="%.1f"),
                "FangraphsURL": st.column_config.LinkColumn(
                    "Fangraphs",
                    display_text="Stats"
                ),
            }
        )
    else:
        st.info("Missing required columns (G, GS) in ZiPS pitchers data to identify relievers.")

with tab4:
    st.subheader("Baseball America Top 100")
    
    # Display
    columns_to_display = ["Rank", "Name", "Team", "Position"]
    if show_drafted:
        columns_to_display.insert(0, "DraftPos")
    
    # Mark drafted players in BA Top 100
    ba_top_100_df = ba_top_100_df.copy()
    ba_top_100_df["DraftPos"] = ba_top_100_df["Name"].map(drafted_dict)
    filtered_ba = filter_drafted(ba_top_100_df, show_drafted)
    filtered_ba = apply_custom_query(filtered_ba)

    # Display
    columns_to_display = [c for c in columns_to_display if c in filtered_ba.columns]
    
    st.dataframe(
        filtered_ba[columns_to_display].sort_values("Rank"),
        hide_index=True,
        use_container_width=True,
        height=600,
        column_config={
            "DraftPos": st.column_config.NumberColumn("Drafted", format="%d"),
            "Rank": st.column_config.NumberColumn("Rank", format="%d")
        }
    )
