import streamlit as st


def make_multi_column(col1, col2, data, column, column_name="Skill"):
    with col1:
        col_1_optins = st.multiselect(f"Select required {column_name}", data[column])

    with col2:
        col_2_options = st.text_input(
            f"Add others {column_name}, separate words with comma (,)",
        )
    return col_1_optins, col_2_options


def format_text(dic_person_skill, string_skills, person, key="skills", color="green"):
    if key in dic_person_skill[person].keys():
        string_skills += f"Matching {key}:  "
        if key == "description":
            string_skills += "... "
        string_skills += ", ".join(
            [
                f":{color}[" + dic_person_skill[person][key][i].replace("http://RH.org/", "") + "]"
                for i in range(len(dic_person_skill[person][key]))
            ]
        )
        string_skills += "\n\n"
        if key == "description":
            string_skills += "... "
    return string_skills


def format_request(options_skill, options_skill_more):
    if len(options_skill_more) > 0:
        return (
            options_skill + options_skill_more.split(",")
            if "," in options_skill_more
            else list(options_skill) + [options_skill_more]
        )
    else:
        return list(options_skill)


def add_line():
    st.markdown(
        """<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """,
        unsafe_allow_html=True,
    )


def main_page_streamlit(data):
    col1, col2 = st.columns(2)
    options_skill, options_skill_more = make_multi_column(
        col1, col2, data, "required_skills", column_name="Skill"
    )
    options_exp, options_exp_add = make_multi_column(
        col1, col2, data, "job_title", column_name="Experiences"
    )
    options_text = st.text_input(
        "Add other requirements",
        data["job_description"],
        key=5,
    )
    return options_skill, options_skill_more, options_exp, options_exp_add, options_text
