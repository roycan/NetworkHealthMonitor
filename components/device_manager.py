import streamlit as st
from utils import validate_ip

def render_device_manager(database):
    st.header("Device Manager")
    
    # Add new device form
    with st.expander("Add New Device"):
        with st.form("add_device"):
            ip_address = st.text_input("IP Address")
            description = st.text_input("Description")
            tags = st.text_input("Tags (comma-separated)")
            
            submitted = st.form_submit_button("Add Device")
            if submitted:
                if not validate_ip(ip_address):
                    st.error("Invalid IP address format")
                else:
                    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                    database.add_device(ip_address, description, tag_list)
                    st.success("Device added successfully!")

    # List and manage existing devices
    st.subheader("Existing Devices")
    devices = database.get_devices()
    
    for device in devices:
        with st.expander(f"{device['ip_address']} - {device['description']}"):
            with st.form(f"edit_device_{device['id']}"):
                new_ip = st.text_input("IP Address", value=device['ip_address'])
                new_desc = st.text_input("Description", value=device['description'])
                new_tags = st.text_input("Tags", value=",".join(device['tags'] if device['tags'] else []))
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Update"):
                        if not validate_ip(new_ip):
                            st.error("Invalid IP address format")
                        else:
                            tag_list = [tag.strip() for tag in new_tags.split(",") if tag.strip()]
                            database.update_device(device['id'], new_ip, new_desc, tag_list)
                            st.success("Device updated successfully!")
                            st.rerun()
                
                with col2:
                    if st.form_submit_button("Delete", type="primary"):
                        database.delete_device(device['id'])
                        st.success("Device deleted successfully!")
                        st.rerun()
