from datetime import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import pytz
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
        started_datetime = parse_timestamp(response["data"]["started_at"])
        return {
            "username": response["data"]["username"],
            "started_date": started_datetime.strftime("%B %d, %Y"),
            "elapsed_time": (datetime.now(tz = pytz.timezone(timezone)) - started_datetime).days
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
        
def parse_timestamp(timestamp, timezone = "America/Los_Angeles"):
    """
    Insert docstring here...
    """
    if timestamp is None:
        return None
    else:
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z").astimezone(tz = pytz.timezone(timezone))

def get_levels(api_key, timezone = "America/Los_Angeles"):
    """
    Insert docstring here...
    """
    current_datetime = datetime.now(tz = pytz.timezone(timezone))
    
    levels = {}
    for i in get_wanikani(api_key = api_key, url = "https://api.wanikani.com/v2/level_progressions")["data"]:
        l = i["data"]["level"]
        levels[l] = {
            "started_datetime": parse_timestamp(i["data"]["started_at"]),
            "passed_datetime": parse_timestamp(i["data"]["passed_at"])
        }
        
        if (levels[l]["started_datetime"] is not None) and (levels[l]["passed_datetime"] is not None):
            levels[l]["elapsed_time"] = levels[l]["passed_datetime"] - levels[l]["started_datetime"]
        elif levels[l]["started_datetime"] is not None:
            levels[l]["elapsed_time"] = current_datetime - levels[l]["started_datetime"]
        else:
            levels[l]["elapsed_time"] = None

    return levels

def get_level_up_stats(levels):
    """
    Insert docstring here...
    """
    times = [levels[key]["elapsed_time"].total_seconds() / 86400 for key in levels.keys() if levels[key]["elapsed_time"] is not None]
    
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

def get_level_stats(l, levels):
    """
    Insert docstring here...
    """
    time_on_level = levels[l]["elapsed_time"]
    time_on_level
    
    if time_on_level is not None:
        time_on_level = round(time_on_level.total_seconds() / 86400, 1)
    
    if l > 1:
        previous_level = l - 1
        time_on_previous_level = round(levels[previous_level]["elapsed_time"].total_seconds() / 86400, 1)
        if time_on_level is not None:
            time_difference = time_on_level - time_on_previous_level
        else:
            time_difference = None
    else:
        previous_level = None
        time_on_previous_level = None
        time_difference = None
    
    return {
        "level": l,
        "time_on_level": time_on_level,
        "previous_level": previous_level,
        "time_on_previous_level": time_on_previous_level,
        "delta": time_difference,
        "delta_color": "inverse"
    }

def plot_level_up_times(levels):
    """
    Insert docstring here...
    """
    x = sorted([key for key in levels.keys() if levels[key]["elapsed_time"] is not None])
    y = [round(levels[l]["elapsed_time"].total_seconds() / 86400, 1) for l in x]
        
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

@st.cache
def get_learned_counts(api_key):
    """
    Insert docstring here...
    """
    counts = {
        "radical": 0,
        "kanji": 0,
        "vocabulary": 0
    }
    
    response = get_wanikani(
        api_key = api_key,
        url = "https://api.wanikani.com/v2/assignments",
        params = {
            "srs_stages": "5,6,7,8,9",
            "hidden": "false"
        }
    )
    
    for d in response["data"]:
        counts[d["data"]["subject_type"]] += 1
        
    next_url = response["pages"]["next_url"]
    
    while next_url:
        response = get_wanikani(
            api_key = api_key,
            url = next_url
        )
        
        for d in response["data"]:
            counts[d["data"]["subject_type"]] += 1
        
        next_url = response["pages"]["next_url"]

    return counts
