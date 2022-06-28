import streamlit as st
import wanikani_helpers as wh

def insert_page_break():
    """
    Insert docstring here...
    """
    return st.markdown("#")

def get_api_key_from_user():
    """
    Insert docstring here...
    """
    return st.text_input(
        label = "Enter your Wanikani Personal Access Token.",
        value = "dd33b5df-77a1-4a59-aafe-fb841bc70a41",
        help = "Create or find your token here: https://www.wanikani.com/settings/personal_access_tokens",
        type = "password",
        autocomplete = "current-password",
    )

def display_welcome_message(user_data):
    """
    Insert docstring here...
    """
    st.markdown(f'Hi <font style="color:#48a9f8">**{user_data["username"]}**</font>, welcome to <font style="color:#e244a3">**Wanikani Statistics**</font>!', unsafe_allow_html = True)
    
    st.metric(
        label = "You joined Wanikani on",
        value = f'{user_data["started_date"]}',
        delta = f'{user_data["elapsed_time"]} days ago'
    )
    
    return None

def display_items_learned(api_key):
    """
    Insert docstring here...
    """
    st.subheader("Items Learned (Guru+)")

    items, labels, counts = wh.get_learned_counts(api_key)

    for col, item in zip(st.columns(3), items):
        col.metric(
            label = labels[item],
            value = sum([counts[stage][item] for stage in range(5,10)])
        )

    # Inject CSS with Markdown to hide table index
    hide_row_index = """
        <style>
            tbody th {display:none}
            .blank {display:none}
        </style>
    """
    st.markdown(hide_row_index, unsafe_allow_html = True)
    st.table(wh.get_item_breakdown(counts))
    
    return None
