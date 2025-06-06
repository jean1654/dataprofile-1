# https://blank-app-gt9r8r4xjbi.streamlit.app/
# https://upgraded-space-guide-g6676w946q9cq45-8501.app.github.dev/
# https://upgraded-space-guide-g6676w946q9cq45-8503.app.github.dev/ 

import streamlit as st

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

pg = st.navigation([
    # st.Page("pages/home.py", title="Home", default=True, icon=":material/home:"),
    # st.Page("pages/homedataset.py", title="Dataset", icon=":material/dataset:"),
    # st.Page("pages/datasetprofile.py", title="Dataset Profile Report", icon=":material/dataset:"),
    st.Page("pages/validatephone.py", title="Validate Phone Numbers", icon=":material/dataset:"),
])

try:
    pg.run()
except Exception as e:
   st.error(f"Something went wrong: {str(e)}", icon=":material/error:")

st.sidebar.success("For more details, refer to Dataset tab.")

# References below

# st.set_page_config(page_title="Data Profile Reports", page_icon=":material/article:")

# Widgets shared by all the pages
# selected_data = st.sidebar.selectbox("Choose Preferred Dataset", ["Dataset1", "Dataset2", "Dataset3"], key="dataset")

#def datasetpage():
#    st.write(st.session_state.dataset)