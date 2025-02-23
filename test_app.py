# tests/test_app.py

import pytest
import pandas as pd
from app import calculate_career_war, interpolate_delta, aging_projection

def test_interpolate_delta():
    age_deltas = {24: 0.1, 25: 0.2}
    assert interpolate_delta(age_deltas, 24.5) == pytest.approx(0.15)

def test_calculate_career_war():
    df = pd.DataFrame({
        'Age': [24, 25],
        'WAR': [2.0, 3.0]
    })
    result_df = calculate_career_war(df, is_pitcher=False, discount=False, flatten=False)
    assert 'CareerWAR' in result_df.columns
    assert result_df['CareerWAR'].iloc[0] > 2.0  # Example assertion

def test_interpolate_delta_exact_age():
    """Test interpolation with exact integer age"""
    age_deltas = {24: 0.1, 25: 0.2}
    assert interpolate_delta(age_deltas, 24.0) == pytest.approx(0.1)

def test_interpolate_delta_missing_age():
    """Test interpolation with missing age defaults to -2.5"""
    age_deltas = {24: 0.1}
    assert interpolate_delta(age_deltas, 26.0) == pytest.approx(-2.5)

def test_aging_projection_hitter():
    """Test aging projection for a young hitter"""
    row = {"Age": 22.0, "WAR": 3.0}
    result = aging_projection(row, is_pitcher=False, discount=False, flatten=False)
    assert result > 3.0  # Young hitter should project for more career WAR than current WAR

def test_aging_projection_old_player():
    """Test aging projection for an older player"""
    row = {"Age": 38.0, "WAR": 3.0}
    result = aging_projection(row, is_pitcher=False, discount=False, flatten=False)
    assert result > 0  # Should still project some positive value
    assert result < 20  # But not an unreasonable amount

def test_aging_projection_with_discount():
    """Test aging projection with discount rate applied"""
    row = {"Age": 24.0, "WAR": 3.0}
    no_discount = aging_projection(row, is_pitcher=False, discount=False, flatten=False)
    with_discount = aging_projection(row, is_pitcher=False, discount=True, flatten=False)
    assert with_discount < no_discount  # Discounted value should be lower

def test_aging_projection_pitcher_vs_hitter():
    """Test that pitcher and hitter aging curves are different"""
    row = {"Age": 24.0, "WAR": 3.0}
    pitcher_proj = aging_projection(row, is_pitcher=True, discount=False, flatten=False)
    hitter_proj = aging_projection(row, is_pitcher=False, discount=False, flatten=False)
    assert pitcher_proj != hitter_proj


def test_calculate_career_war_with_custom_columns():
    """Test calculate_career_war with custom column names"""
    df = pd.DataFrame({
        'Age': [24, 25],
        'ProjectedWAR': [2.0, 3.0]
    })
    result_df = calculate_career_war(
        df, 
        is_pitcher=False, 
        war_col="ProjectedWAR",
        new_col="TotalWAR"
    )
    assert 'TotalWAR' in result_df.columns
    assert not 'CareerWAR' in result_df.columns

def test_aging_projection_with_flattened_curve():
    """Test that flattened aging curves produce more conservative projections"""
    row = {"Age": 24.0, "WAR": 3.0}
    standard_proj = aging_projection(row, is_pitcher=False, discount=False, flatten=False)
    flat_proj = aging_projection(row, is_pitcher=False, discount=False, flatten=True)
    assert flat_proj < standard_proj  # Flattened projection should be more conservative

def test_age_monotonicity():
    """Test that younger age always projects equal or better than older age, all else equal"""
    base_war = 3.0
    
    # Test for both pitchers and hitters
    for is_pitcher in [True, False]:
        # Test across reasonable age range (18-42)
        prev_projection = float('inf')  # Start high to ensure first comparison works
        for age in range(18, 43):
            row = {"Age": age, "WAR": base_war}
            curr_projection = aging_projection(row, is_pitcher=is_pitcher, discount=False, flatten=False)
            
            # Current projection should be less than or equal to previous (younger) age
            assert curr_projection <= prev_projection, \
                f"{'Pitcher' if is_pitcher else 'Hitter'} age {age} projects to {curr_projection}, " \
                f"but age {age-1} projected to {prev_projection}"
            
            prev_projection = curr_projection

def test_war_monotonicity():
    """Test that higher WAR always projects better than lower WAR, all else equal"""
    test_age = 25.0
    
    # Test for both pitchers and hitters
    for is_pitcher in [True, False]:
        # Test across reasonable WAR range (0.1 to 8.0)
        prev_projection = 0  # Start at 0 to ensure first comparison works
        for war in [w/10.0 for w in range(1, 81)]:  # Test WAR from 0.1 to 8.0 in 0.1 increments
            row = {"Age": test_age, "WAR": war}
            curr_projection = aging_projection(row, is_pitcher=is_pitcher, discount=False, flatten=False)
            
            # Current projection should be greater than previous (lower) WAR
            assert curr_projection > prev_projection, \
                f"{'Pitcher' if is_pitcher else 'Hitter'} WAR {war} projects to {curr_projection}, " \
                f"but WAR {war-0.1} projected to {prev_projection}"
            
            prev_projection = curr_projection

# Add more tests for other functions