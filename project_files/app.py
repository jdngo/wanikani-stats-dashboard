import streamlit as st
import helpers.streamlitHelpers as sth

st.set_page_config(page_title = "Wanikani Statistics")

st.title("Wanikani Statistics")

def main():
    token = sth.get_token()

    sth.insert_space()

    user_data = sth.get_user_data(token)

    if not user_data:
        sth.display_token_error_message()
    else:
        sth.display_welcome_message(user_data)

        sth.display_join_date(user_data)

        sth.insert_space()

        sth.display_items_learned(token)

        breakdown_type = sth.get_breakdown_type()

        sth.display_items_breakdown(token, breakdown_type)

        sth.insert_space()

    sth.display_github_link()

main()

        # Stats - Overall level-up stats
        # | col1     | col2     | col3               |
        # |----------|----------|--------------------|
        # | average  | shortest | standard deviation |
        # |----------|----------|--------------------|
        # | median   | longest  | variance           |

        #         st.subheader("Level-Up Time Statistics")
        #         st.caption("Time (days) between level start (not unlocked) to level passed.")

        #         levels = wh.get_levels(token)

        #         level_up_stats = wh.get_level_up_stats(levels)

        #         col1, col2, col3 = st.columns(3)

        #         # Column 1
        #         col1.metric(
        #             label = "Average",
        #             value = f'{level_up_stats["mean"]:.1f}'
        #         )

        #         col1.metric(
        #             label = "Median",
        #             value = f'{level_up_stats["median"]:.1f}'
        #         )

        #         # Column 2
        #         col2.metric(
        #             label = "Shortest",
        #             value = f'{level_up_stats["min"]:.1f}'
        #         )

        #         col2.metric(
        #             label = "Longest",
        #             value = f'{level_up_stats["max"]:.1f}'
        #         )

        #         # Column 3
        #         col3.metric(
        #             label = "Standard Deviation",
        #             value = f'{level_up_stats["standard_deviation"]:.1f}'
        #         )

        #         col3.metric(
        #             label = "Variance",
        #             value = f'{level_up_stats["variance"]:.1f}'
        #         )

        #         # Plot - Level vs. Level-Up Time (Days)
        #         st.plotly_chart(sh.display_level_up_times_chart(levels))

        #         # Stats - Individual level stats
        #         st.subheader("Individual Level Statistics")

        #         selected_level = st.selectbox(
        #             label = "Select a level.",
        #             options = sorted(levels.keys(), reverse = True),
        #             index = 0
        #         )

        #         level_stats = wh.get_level_stats(
        #             selected_level = selected_level,
        #             levels = levels
        #         )

        #         col1, col2 = st.columns(2)

        #         col1.metric(
        #             label = "Level",
        #             value = level_stats["level"]
        #         )

        #         value = level_stats["time_on_level"]
        #         delta = level_stats["delta"]
        #         col2.metric(
        #             label = "Days since starting level",
        #             value = None if not value else value,
        #             delta = None if not delta else f'{delta:.1f} vs. level {level_stats["level"] - 1}',
        #             delta_color = level_stats["delta_color"]
        #         )
