from data import wanikani
import helpers.helpers as hp
import numpy as np
import pandas as pd
import requests
import streamlit as st

@st.cache
def check_token(token, wanikani_revision = "20170710", timezone = "America/Los_Angeles"):
    """
    Description
        Checks whether the token is valid. If so, return dict, else, return None.
         For valid tokens, dict will contain username, date user joined Wanikani, and elapsed time since joining.

    Input
        token: string; User supplied token.
        wanikani_revision: string; Wanikani's API version.
        timezone: string; Timezone that timestamps should be converted to.

    Output
        user_data: dict or None; Output from get_user_data that contains user's username.

    Example
        check_token(token = token, wanikani_revision = "20170710", timezone = "America/Los_Angeles")

        {
            "username": "jdngo",
            "started_date": "January 1, 2022",
            "elapsed_time": "180"
        }
    """
    response = requests.get(
        url = "https://api.wanikani.com/v2/user",
        params = {},
        headers = {
            "Wanikani-Revision": wanikani_revision,
            "Authorization": f"Bearer {token}"
        }
    ).json()

    if response.get("code", None) == 401:
        user_data = None

        return user_data
    else:
        started_datetime = hp.parse_timestamp(response["data"]["started_at"], timezone = timezone)

        user_data = {
            "username": response["data"]["username"],
            "started_date": started_datetime.strftime("%B %d, %Y"),
            "elapsed_time": (hp.get_current_timestamp(timezone) - started_datetime).days
        }

        return user_data

@st.cache
def get_wanikani(token, url, params = {}, wanikani_revision = "20170710"):
    """
    Description

    Input

    Output

    Example

    """
    return requests.get(
        url = url,
        params = params,
        headers = {
            "Wanikani-Revision": wanikani_revision,
            "Authorization": f"Bearer {token}"
        }
    ).json()

def get_standard_data():
    """
    Description

    Input

    Output

    Example

    """
    return wanikani.items, wanikani.item_labels, wanikani.stages, wanikani.srs_stages

@st.cache
def get_learned_counts(token):
    """
    Description

    Input

    Output

    Example

    """
    items, item_labels, _, _ = get_standard_data()

    counts = {}
    for stage in range(1,10):
        counts[stage] = {}
        for item in items:
            counts[stage][item] = 0

    response = get_wanikani(
        token = token,
        url = "https://api.wanikani.com/v2/assignments",
        params = {
            "srs_stages": "1,2,3,4,5,6,7,8,9",
            "hidden": "false"
        }
    )

    for d in response["data"]:
        srs_stage = d["data"]["srs_stage"]
        subject_type = d["data"]["subject_type"]
        counts[srs_stage][subject_type] += 1

    next_url = response["pages"]["next_url"]

    while next_url:
        response = get_wanikani(
            token = token,
            url = next_url
        )

        for d in response["data"]:
            srs_stage = d["data"]["srs_stage"]
            subject_type = d["data"]["subject_type"]
            counts[srs_stage][subject_type] += 1

        next_url = response["pages"]["next_url"]

    return items, item_labels, counts

@st.cache
def get_item_breakdown(counts, breakdown_type):
    """
    Description

    Input

    Output

    Example

    """
    items, item_labels, stages, srs_stages = get_standard_data()

    if breakdown_type == "Bar Chart":
        df = pd.DataFrame(columns = ["Item", "Stage", "Count"])
        for item in items:
            for stage in stages:
                df.loc[len(df.index)] = [
                    item_labels[item],
                    stage,
                    sum([counts[s][item] for s in range(srs_stages[stage]["start"], srs_stages[stage]["end"] + 1)])
                ]

    elif breakdown_type == "Table":
        df = {"Stage": stages}
        for item in items:
            df[item_labels[item]] = [sum([counts[s][item] for s in range(srs_stages[stage]["start"], srs_stages[stage]["end"] + 1)]) for stage in stages]

        df = pd.DataFrame(df)

        df.loc[len(df.index)] = [
            "All",
            df["Radical 部首"].sum(),
            df["Kanji 漢字"].sum(),
            df["Vocabulary 単語"].sum()
        ]

    return df

@st.cache
def get_levels(token, timezone = "America/Los_Angeles"):
    """
    Description

    Input

    Output

    Example

    """
    levels = {}

    for i in get_wanikani(token = token, url = "https://api.wanikani.com/v2/level_progressions")["data"]:
        l = i["data"]["level"]

        levels[l] = {
            "started_datetime": hp.parse_timestamp(i["data"]["started_at"], timezone = timezone),
            "passed_datetime": hp.parse_timestamp(i["data"]["passed_at"], timezone = timezone)
        }

        if (levels[l]["started_datetime"] is not None) and (levels[l]["passed_datetime"] is not None):
            levels[l]["elapsed_time"] = levels[l]["passed_datetime"] - levels[l]["started_datetime"]
        elif levels[l]["started_datetime"] is not None:
            levels[l]["elapsed_time"] = hp.get_current_timestamp(timezone) - levels[l]["started_datetime"]
        else:
            levels[l]["elapsed_time"] = None

    return levels

@st.cache
def get_level_up_stats(levels):
    """
    Description

    Input

    Output

    Example

    """
    times = [hp.seconds_to_days(levels[key]["elapsed_time"].total_seconds()) for key in levels.keys() if levels[key]["elapsed_time"] is not None]

    if len(times) == 0:
        return {
            "mean": None,
            "median": None,
            "variance": None,
            "standard_deviation": None,
            "min": None,
            "max": None
        }
    else:
        return {
            "mean": round(np.mean(times), 1),
            "median": round(np.median(times), 1),
            "variance": round(np.var(times), 1),
            "standard_deviation": round(np.std(times), 1),
            "min": round(np.min(times), 1),
            "max": round(np.max(times), 1)
        }

@st.cache
def get_level_stats(selected_level, levels):
    """
    Description

    Input

    Output

    Example
        
    """
    time_on_level = levels[selected_level]["elapsed_time"]

    if time_on_level is not None:
        time_on_level = round(hp.seconds_to_days(time_on_level.total_seconds()), 1)

    if selected_level > 1:
        previous_level = selected_level - 1
        time_on_previous_level = round(hp.seconds_to_days(levels[previous_level]["elapsed_time"].total_seconds()), 1)
        time_difference = time_on_level - time_on_previous_level if time_on_level is not None else None
    else:
        previous_level = None
        time_on_previous_level = None
        time_difference = None

    return {
        "level": selected_level,
        "time_on_level": time_on_level,
        "previous_level": previous_level,
        "time_on_previous_level": time_on_previous_level,
        "delta": time_difference,
        "delta_color": "inverse"
    }
