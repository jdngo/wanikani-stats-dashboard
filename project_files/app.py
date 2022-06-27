import streamlit as st
import wanikani_helpers

st.set_page_config(
    page_title = "Wanikani Statistics"
)

st.title("Wanikani Statistics")

# Get Wanikani API key as text input from user
api_key = st.text_input(
    label = "Enter your Wanikani Personal Access Token.",
    value = "dd33b5df-77a1-4a59-aafe-fb841bc70a41",
    help = "Create or find your token here: https://www.wanikani.com/settings/personal_access_tokens",
    type = "password",
    autocomplete = "current-password",
)

st.markdown("#")

# Validate the API key; returns user data if valid
user_data = wanikani_helpers.check_wanikani_api_key(api_key)

# user_data is None if API key is invalid
if not user_data:
    st.markdown("<font color='red'>Hm... Did you enter a valid token?</font>", unsafe_allow_html = True)
else:
    # Welcome message
    st.markdown(f'Hi <font style="color:#48a9f8">**{user_data["username"]}**</font>, welcome to <font style="color:#e244a3">**Wanikani Statistics**</font>!', unsafe_allow_html = True)
    
    st.markdown("#")
        
    # Stats - Join date, time since joining, items learned
    st.metric(
        label = "You joined Wanikani on",
        value = f'{user_data["started_date"]}',
        delta = f'{user_data["elapsed_time"]} days ago'
    )
    
    st.markdown("#")
    
    st.subheader("Items Learned (Guru+)")
    
    learned_counts = wanikani_helpers.get_learned_counts(api_key)
    
    col1, col2, col3 = st.columns(3)
    
    col1.metric(
        label = "Radical 部首",
        value = learned_counts["radical"]
    )
    
    col2.metric(
        label = "Kanji 漢字",
        value = learned_counts["kanji"]
    )
    
    col3.metric(
        label = "Vocabulary 単語",
        value = learned_counts["vocabulary"]
    )
    
    st.markdown("#")
        
    # Stats - Overall level-up stats
    # | col1     | col2     | col3               |
    # |----------|----------|--------------------|
    # | average  | shortest | standard deviation |
    # |----------|----------|--------------------|
    # | median   | longest  | variance           |
    
    st.subheader("Level-Up Time Statistics")
    st.caption("Unit: Days")
    
    levels = wanikani_helpers.get_levels(api_key)
    
    level_up_stats = wanikani_helpers.get_level_up_stats(levels)
    
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
    st.plotly_chart(wanikani_helpers.plot_level_up_times(levels))
    
    # Stats - Individual level stats
    st.subheader("Individual Level Statistics")
    
    selected_level = st.selectbox(
        label = "Select a level.",
        options = sorted(levels.keys(), reverse = True),
        index = 0
    )

    level_stats = wanikani_helpers.get_level_stats(
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

