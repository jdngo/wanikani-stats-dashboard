import app_helpers as ah
import pandas as pd
import streamlit as st
import wanikani_helpers as wh
import helpers

st.set_page_config(page_title = "Wanikani Statistics")

st.title("Wanikani Statistics")

def main():
    # Get Wanikani API Key from user
    api_key = ah.get_api_key_from_user()

    ah.insert_page_break()

    # Validate the API key; returns user data if valid or None if invalid
    user_data = wh.check_wanikani_api_key(api_key)

    if not user_data:
        st.markdown("<font color='red'>Hm... Did you enter a valid token?</font>", unsafe_allow_html = True)
    else:
        ah.display_welcome_message(user_data)

        ah.insert_page_break()
        
        ah.display_items_learned(api_key)

        ah.insert_page_break()
        
        
        
        
        

        # Stats - Overall level-up stats
        # | col1     | col2     | col3               |
        # |----------|----------|--------------------|
        # | average  | shortest | standard deviation |
        # |----------|----------|--------------------|
        # | median   | longest  | variance           |

        st.subheader("Level-Up Time Statistics")
        st.caption("Time (days) between level start (not unlocked) to level passed.")

        levels = wh.get_levels(api_key)

        level_up_stats = wh.get_level_up_stats(levels)

        col1, col2, col3 = st.columns(3)

        # Column 1
        col1.metric(
            label = "Average",
            value = f'{level_up_stats["mean"]:.1f}'
        )

        col1.metric(
            label = "Median",
            value = f'{level_up_stats["median"]:.1f}'
        )

        # Column 2
        col2.metric(
            label = "Shortest",
            value = f'{level_up_stats["min"]:.1f}'
        )

        col2.metric(
            label = "Longest",
            value = f'{level_up_stats["max"]:.1f}'
        )

        # Column 3
        col3.metric(
            label = "Standard Deviation",
            value = f'{level_up_stats["standard_deviation"]:.1f}'
        )

        col3.metric(
            label = "Variance",
            value = f'{level_up_stats["variance"]:.1f}'
        )

        # Plot - Level vs. Level-Up Time (Days)
        st.plotly_chart(wh.plot_level_up_times(levels))

        # Stats - Individual level stats
        st.subheader("Individual Level Statistics")

        selected_level = st.selectbox(
            label = "Select a level.",
            options = sorted(levels.keys(), reverse = True),
            index = 0
        )

        level_stats = wh.get_level_stats(
            l = selected_level,
            levels = levels
        )

        col1, col2 = st.columns(2)

        col1.metric(
            label = "Level",
            value = level_stats["level"]
        )

        value = level_stats["time_on_level"]
        delta = level_stats["delta"]
        col2.metric(
            label = "Days since starting level",
            value = None if not value else value,
            delta = None if not delta else f'{delta:.1f} vs. level {level_stats["level"] - 1}',
            delta_color = level_stats["delta_color"]
        )

    ah.insert_page_break()

    st.markdown("[Github](https://github.com/jdngo/wanikani-stats-dashboard)")
    
main()
