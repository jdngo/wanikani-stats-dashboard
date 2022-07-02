from data import colors
import helpers.helpers as hp
import helpers.wanikaniHelpers as wkh
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

def get_color(color, type):
    """
    Description
        Returns color code for a specified color and color code type.

    Input
        color: string; Name of a valid color.
        type:  string; Type of color code.Possible values: "hex", "rgb" (some colors only have one of these available)

    Output
        color_code: string; Color code corresponding to the input color and color code type

    Example
        get_color(color = "wanikani_blue", type = "hex")
    """
    color_code = colors.colors[color][type]

    return color_code

def insert_space(length = 40, color = 238):
    """
    Description
        Creates an empty space on the page. Use this to separate different sections of the app.

    Input
        length: int; Length (vertical height) of the space in number of pixels (default: 40).
        color: int; RGB color code used for all three channels (default: 238).

    Output
        None

    Example
        insert_page_break(length = 40, color = 238)
    """
    st.image(np.full((length, 1, 3), color))

    return None

def get_token():
    """
    Description
        Creates text box for user to input their Wanikani API key.

    Input
        None

    Output
        token: string; Input into the text box from the user.

    Example
        get_token()

        "ab12c3de-12a3-1a23-abcd-ab123cd45e67"
    """
    # TODO: Remove default value before app is published.
    token = st.text_input(
        label = "Enter your Wanikani Personal Access Token.",
        value = "dd33b5df-77a1-4a59-aafe-fb841bc70a41",
        help = "Create or find your token here: https://www.wanikani.com/settings/personal_access_tokens",
        type = "password",
        autocomplete = "current-password",
    )

    return token

def get_user_data(token):
    """
    Description
        Checks whether the token is valid. If so, return dict, else, return None.

    Input
        token: string; User supplied token.

    Output
        user_data: dict or None; Output from get_user_data that contains user's username.

    Example
        get_user_data(token = token)

        {
            "username": "jdngo",
            "started_date": "January 1, 2022",
            "elapsed_time": "180"
        }
    """
    user_data = wkh.check_token(token)

    return user_data

def display_token_error_message():
    """
    Description
        Displays an invalid token error message to the user.

    Input
        None

    Output
        None

    Example
        display_token_error_message()
    """
    st.markdown("<font color='red'>Hm... Did you enter a valid token?</font>", unsafe_allow_html = True)

    return None

def display_welcome_message(user_data):
    """
    Description
        Displays a welcome message to the user.

    Input
        user_data: dict; Output from get_user_data that contains user's username.

    Output
        None

    Example
        display_welcome_message(user_data = user_data)
    """
    st.markdown(
        f'Hi <font style="color:{get_color("wanikani_blue", "hex")}">**{user_data["username"]}**</font>, '
        f'welcome to <font style="color:{get_color("wanikani_pink", "hex")}">**Wanikani Statistics**</font>!',
        unsafe_allow_html = True
    )

    return None

def display_join_date(user_data):
    """
    Description
        Displays the date the user joined Wanikani and the days since that date.

    Input
        user_data: dict; Output from get_user_data that contains user's username.

    Output
        None

    Example
        display_join_date(user_data = user_data)
    """
    st.metric(
        label = "You joined Wanikani on",
        value = f'{user_data.get("started_date", None)}',
        delta = f'{user_data.get("elapsed_time", None)} days ago'
    )

    return None

def display_items_learned(token, srs_stage_start = 5, srs_stage_end = 9):
    """
    Description
        Displays a count of items learned for each item type (Radical, Kanji, Vocabulary) across 3 columns.
        Learned items are items that are at the Guru level or higher (SRS stages 5-9).

    Input
        token: string; User supplied token.
        srs_stage_start: int; The minimum SRS stage number to include when counting items learned (default: 5; Guru 1).
        sts_stage_end: int; The maximum SRS stage number to include when counting items learned (default: 9; Burned).

    Output
        None

    Example
        display_items_learned(token = token, srs_stage_start = 5, srs_stage_end = 9)
    """
    st.subheader("Items Learned (Guru+)")

    # items: ("radical", "kanji", "vocabulary")
    # item_labels: {'radical': 'Radical 部首', 'kanji': 'Kanji 漢字', 'vocabulary': 'Vocabulary 単語'}
    # counts: {1: {"radical": 0, "kanji": 0, "vocabulary": 0}, ..., 10: {"radical": 0, "kanji": 0, "vocabulary": 0}}
    items, item_labels, counts = wkh.get_learned_counts(token)

    for col, item in zip(st.columns(3), items):
        col.metric(
            label = item_labels[item],
            value = sum([counts[srs_stage][item] for srs_stage in range(srs_stage_start, srs_stage_end + 1)])
        )

    return None

def get_breakdown_type():
    """
    Description
        Get the type of breakdown visualization from the user using radio button selections.

    Input
        None

    Output
        breakdown_type: string; The user-selected type of breakdown visualization. Possible values: "Bar Chart", "Table"

    Example
        get_breakdown_type()
    """
    breakdown_type = st.radio(label = "Items Learned Breakdown", options = ["Bar Chart", "Table"], index = 0)

    return breakdown_type

def display_items_breakdown(token, breakdown_type):
    """
    Description
        This is the description

    Input
        token: string; User supplied token.
        breakdown_type: string; The user-selected type of breakdown visualization. Possible values: "Bar Chart", "Table"

    Output
        None

    Example
        display_items_breakdown(token = token, breakdown_type = breakdown_type)
    """
    # counts: {1: {"radical": 0, "kanji": 0, "vocabulary": 0}, ..., 10: {"radical": 0, "kanji": 0, "vocabulary": 0}}
    _, _, counts = wkh.get_learned_counts(token)

    if breakdown_type == "Bar Chart":
        # df:
        # | Item            | Stage      | Count |
        # |-----------------|------------|-------|
        # | Radical 部首     | Apprentice | 5     |
        # | Kanji 漢字       | Apprentice | 10    |
        # | Vocabulary 単語  | Apprentice | 20    |
        # | ...             | ...        | ...   |
        df = wkh.get_item_breakdown(counts, breakdown_type)

        color_discrete_map = {}
        for stage in df["Stage"].unique():
            color_discrete_map[stage] = get_color(stage.lower(), "rgb")

        fig = px.bar(
            data_frame = df, x = "Item", y = "Count", color = "Stage",
            barmode = "group", color_discrete_map = color_discrete_map
        )

        st.plotly_chart(fig)

    elif breakdown_type == "Table":
        # df:
        # | Stage       | Radical 部首 | Kanji 漢字 | Vocabulary 単語 |
        # |-------------|--------------|------------|---------------|
        # | Apprentice  | 1            | 38         | 70            |
        # | Guru        | 14           | 53         | 131           |
        # | Master      | 11           | 34         | 109           |
        # | Enlightened | 38           | 136        | 470           |
        # | Burned      | 225          | 300        | 901           |
        # | All         | 289          | 561        | 1681          |
        df = wkh.get_item_breakdown(counts, breakdown_type)

        # Inject CSS with Markdown to hide table index
        hide_row_index = """
            <style>
                tbody th {display:none}
                .blank {display:none}
            </style>
        """
        st.markdown(hide_row_index, unsafe_allow_html = True)
        st.table(df)

    return None

def display_level_up_times_chart(levels):
    """
    ...
    """
    x = sorted([key for key in levels.keys() if levels[key]["elapsed_time"] is not None])
    y = [round(hp.seconds_to_days(levels[l]["elapsed_time"].total_seconds()), 1) for l in x]

    df = pd.DataFrame({
        "level": x,
        "time": y
    })

    fig = px.bar(
        data_frame = df,
        x = "level",
        y = "time",
        labels = {
            "level": "Level",
            "time": "Level-Up Time (Days)"
        }
    ).update_xaxes(
        dtick = 1
    ).update_traces(
        marker_color='rgb(72,169,248)'
    )

    return fig

def display_github_link():
    """
    Description
        Display the text "GitHub" with a link to the GitHub repository page for this app.

    Input
        None

    Output
        None

    Example
        display_github_link()
    """
    url = "https://github.com/jdngo/wanikani-stats-dashboard"

    st.markdown(f"[GitHub]({url})")

    return None
