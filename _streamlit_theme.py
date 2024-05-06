def get_block_style():
    return """.block-container {
                    padding-top: 2rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
            """


# Style tab from https://discuss.streamlit.io/t/customizing-the-appearance-of-tabs/48913
def get_tabs_style():
    return """.stTabs [data-baseweb="tab-list"] {
                    gap: 2px;
                }
                .stTabs [data-baseweb="tab"] {
                    height: 30px;
                    width: 70px;
                    white-space: pre-wrap;
                    background-color: #F0F2F6;
                    border-radius: 4px 4px 0px 0px;
                    gap: 1px;
                    padding-top: 10px;
                    padding-bottom: 10px;
                    p {font-size: 15px};
                }
                .stTabs [aria-selected="true"] {
                    background-color: #002366;
                    color: #FFFFFF;
                }
                .stTabs [data-baseweb="tab-highlight"] {
                    background-color: #002366;
                }
            """
