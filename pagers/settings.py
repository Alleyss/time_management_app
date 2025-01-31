# pages/settings.py

import streamlit as st
from datetime import datetime
import pytz  # For time zone handling

# Import functions from the data package
from data import (
    get_user_by_username,
    get_settings,
    add_setting,
    # Category management functions
    get_categories,
    add_category,
    update_category,
    delete_category,
    # Data management functions
    export_user_data,
    import_user_data,
)

# Authentication check
def is_authenticated():
    return 'authenticated' in st.session_state and st.session_state['authenticated']

def get_current_user():
    if 'username' in st.session_state:
        return get_user_by_username(st.session_state['username'])
    else:
        return None

def settings_page():
    st.title("User Settings")

    if not is_authenticated():
        st.warning("Please log in to access settings.")
        return

    user = get_current_user()
    if not user:
        st.error("User not found.")
        return

    user_id = user[0]  # Extract user_id from the tuple

    # Fetch user settings
    settings = get_settings(user_id)
    settings_dict = {setting[0]: setting[1] for setting in settings}  # setting_name: setting_value
    if 'edit_category_states' not in st.session_state:
        st.session_state['edit_category_states'] = {}
    # Tabs for different settings sections
    tab1, tab2, tab3 = st.tabs(["Personal Settings", "Category Management", "Data Management"])

    # -------------------------
    # Personal Settings Tab
    # -------------------------
    with tab1:
        st.subheader("Personal Settings")

        # Time Zone Setting
        timezones = pytz.all_timezones
        current_timezone = settings_dict.get('timezone', 'UTC')
        timezone_selection = st.selectbox("Time Zone", timezones, index=timezones.index(current_timezone))

        # Date Format Setting
        date_formats = [
            ('%Y-%m-%d', 'YYYY-MM-DD'),
            ('%d/%m/%Y', 'DD/MM/YYYY'),
            ('%m/%d/%Y', 'MM/DD/YYYY'),
        ]
        date_format_dict = {fmt: desc for fmt, desc in date_formats}
        current_date_format = settings_dict.get('date_format', '%Y-%m-%d')
        date_format_selection = st.selectbox("Date Format", [desc for fmt, desc in date_formats],
                                             index=[desc for fmt, desc in date_formats].index(date_format_dict[current_date_format]))

        # Map selected description back to format
        selected_date_format = [fmt for fmt, desc in date_formats if desc == date_format_selection][0]

        # Notification Preferences
        notifications_enabled = settings_dict.get('notifications_enabled', 'True') == 'True'
        notifications_selection = st.checkbox("Enable Notifications", value=notifications_enabled)

        # Save Settings
        if st.button("Save Settings"):
            add_setting(user_id, 'timezone', timezone_selection)
            add_setting(user_id, 'date_format', selected_date_format)
            add_setting(user_id, 'notifications_enabled', str(notifications_selection))
            st.success("Settings saved successfully.")

    # -------------------------
    # Category Management Tab
    # -------------------------
    with tab2:
        st.subheader("Category Management")

        # Fetch categories
        categories = get_categories(user_id)
        category_dict = {cat[0]: cat[1] for cat in categories}  # category_id: name

        # Display existing categories with edit and delete options
        for category in categories:
            category_id = category[0]
            category_name = category[1]
            category_description = category[2]
            st.write(f"### {category_name}")
            st.write(f"{category_description or ''}")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Edit", key=f"edit_category_{category_id}"):
                    st.session_state[f"edit_category_state_{category_id}"] = True
            with col2:
                if st.button("Delete", key=f"delete_category_{category_id}"):
                    delete_category(category_id)
                    st.success("Category deleted successfully.")
                    st.rerun()

            # Edit Category Form
            if st.session_state.get(f"edit_category_{category_id}", False):
                st.subheader("Edit Category")
                with st.form(key=f"edit_category_form_{category_id}"):
                    new_name = st.text_input("Category Name", value=category_name,key=f"edit_name_{category_id}")
                    new_description = st.text_area("Description", value=category_description or '',key=f"edit_desc_{category_id}")
                    submitted = st.form_submit_button("Update Category")
                    if submitted:
                        if not new_name:
                            st.error("Please enter a category name.")
                        else:
                            update_category(category_id, new_name, new_description)
                            st.success("Category updated successfully.")
                            st.session_state[f"edit_category_{category_id}"] = False
                            st.rerun()
            else:
                st.session_state[f"edit_category_state{category_id}"]=False

        # Add New Category
        st.subheader("Add New Category")
        with st.form(key="add_category_form"):
            category_name = st.text_input("Category Name")
            category_description = st.text_area("Description")
            submitted = st.form_submit_button("Add Category")
            if submitted:
                if not category_name:
                    st.error("Please enter a category name.")
                else:
                    add_category(user_id, category_name, category_description)
                    st.success("Category added successfully.")
                    st.rerun()

    # -------------------------
    # Data Management Tab
    # -------------------------
    with tab3:
        st.subheader("Data Management")

        # Export Data
        st.write("### Export Data")
        st.write("Download your data for backup or analysis.")
        if st.button("Export Data"):
            data = export_user_data(user_id)
            csv_data = data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name='user_data_export.csv',
                mime='text/csv'
            )

        # Import Data
        st.write("### Import Data")
        st.write("Upload data to import activities and settings.")
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        if uploaded_file is not None:
            if st.button("Import Data"):
                import_user_data(user_id, uploaded_file)
                st.success("Data imported successfully.")
                st.rerun()

if __name__ == "__main__":
    settings_page()