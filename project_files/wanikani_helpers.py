import helpers as hp
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

@st.cache
def check_wanikani_api_key(api_key, wanikani_revision = "20170710", timezone = "America/Los_Angeles"):
    """
    Insert docstring here...
    """
    response = requests.get(
        url = "https://api.wanikani.com/v2/user",
        params = {},
        headers = {
            "Wanikani-Revision": wanikani_revision,
            "Authorization": f"Bearer {api_key}"
        }
    ).json()
    
    if response.get("code") == 401:
        return None
    else:
        started_datetime = hp.parse_timestamp(response["data"]["started_at"])
        
        return {
            "username": response["data"]["username"],
            "started_date": started_datetime.strftime("%B %d, %Y"),
            "elapsed_time": (hp.get_current_timestamp() - started_datetime).days
        }

@st.cache
def get_wanikani(api_key, url, params = {}, wanikani_revision = "20170710"):
    """
    Insert docstring here...
    """
    return requests.get(
        url = url,
        params = params,
        headers = {
            "Wanikani-Revision": wanikani_revision,
            "Authorization": f"Bearer {api_key}"
        }
    ).json()

def get_standard_data():
    """
    Insert docstring here...
    """        
    items = ("radical", "kanji", "vocabulary")
    
    labels = {
        "radical": "Radical 部首",
        "kanji": "Kanji 漢字",
        "vocabulary": "Vocabulary 単語"
    }
    
    stages = ("Apprentice", "Guru", "Master", "Enlightened", "Burned")
    
    srs_stages = {
        "Apprentice": {"start": 1, "end": 4},
        "Guru": {"start": 5, "end": 6},
        "Master": {"start": 7, "end": 7},
        "Enlightened": {"start": 8, "end": 8},
        "Burned": {"start": 9, "end": 9}
    }
    
    return items, labels, stages, srs_stages

def get_learned_counts(api_key):
    """
    Insert docstring here...
    """
    items, labels, _, _ = get_standard_data()
    
    counts = {}
    for stage in range(1,10):
        counts[stage] = {}
        for item in items:
            counts[stage][item] = 0
    
    response = get_wanikani(
        api_key = api_key,
        url = "https://api.wanikani.com/v2/assignments",
        params = {
            "srs_stages": "5,6,7,8,9",
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
            api_key = api_key,
            url = next_url
        )
        
        for d in response["data"]:
            srs_stage = d["data"]["srs_stage"]
            subject_type = d["data"]["subject_type"]
            counts[srs_stage][subject_type] += 1
        
        next_url = response["pages"]["next_url"]
    
    return items, labels, counts

def get_item_breakdown(counts):
    """
    Insert docstring here...
    """
    items, labels, stages, srs_stages = get_standard_data()
    
    df = {"Stage": stages}
    for item in items:
        df[labels[item]] = [sum([counts[s][item] for s in range(srs_stages[stage]["start"], srs_stages[stage]["end"] + 1)]) for stage in stages]
    
    df = pd.DataFrame(df)
    
    df.loc[len(df.index)] = [
        "All",
        df["Radical 部首"].sum(),
        df["Kanji 漢字"].sum(),
        df["Vocabulary 単語"].sum()
    ]
    
    return df

def get_levels(api_key, timezone = "America/Los_Angeles"):
    """
    Insert docstring here...
    """    
    levels = {}
    
    for i in get_wanikani(api_key = api_key, url = "https://api.wanikani.com/v2/level_progressions")["data"]:
        l = i["data"]["level"]
        
        levels[l] = {
            "started_datetime": hp.parse_timestamp(i["data"]["started_at"]),
            "passed_datetime": hp.parse_timestamp(i["data"]["passed_at"])
        }
        
        if (levels[l]["started_datetime"] is not None) and (levels[l]["passed_datetime"] is not None):
            levels[l]["elapsed_time"] = levels[l]["passed_datetime"] - levels[l]["started_datetime"]
        elif levels[l]["started_datetime"] is not None:
            levels[l]["elapsed_time"] = hp.get_current_timestamp() - levels[l]["started_datetime"]
        else:
            levels[l]["elapsed_time"] = None

    return levels

def get_level_up_stats(levels):
    """
    Insert docstring here...
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

def plot_level_up_times(levels):
    """
    Insert docstring here...
    """
    x = sorted([key for key in levels.keys() if levels[key]["elapsed_time"] is not None])
    y = [round(hp.seconds_to_days(levels[l]["elapsed_time"].total_seconds()), 1) for l in x]
        
    fig = px.bar(
        data_frame = pd.DataFrame({
            "level": x,
            "time": y
        }),
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

def get_level_stats(selected_level, levels):
    """
    Insert docstring here...
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
