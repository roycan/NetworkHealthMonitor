import streamlit as st
from utils import validate_ip

def render_device_manager(database):
    st.header("Device Manager")
    
    # Device type options
    DEVICE_TYPES = [
        "Server",
        "Network Switch",
        "Router",
        "Workstation",
        "IoT Device",
        "Other"
    ]
    
    # Add new device form
    with st.expander("Add New Device"):
        with st.form("add_device"):
            col1, col2 = st.columns(2)
            
            with col1:
                ip_address = st.text_input("IP Address")
                description = st.text_input("Description")
                tags = st.text_input("Tags (comma-separated)")
                device_type = st.selectbox("Device Type", [""] + DEVICE_TYPES)
            
            with col2:
                st.subheader("Performance Thresholds")
                response_time = st.number_input(
                    "Response Time Threshold (seconds)",
                    min_value=0.0,
                    value=1.0,
                    step=0.1,
                    help="Maximum acceptable response time"
                )
                packet_loss = st.number_input(
                    "Packet Loss Threshold (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=5.0,
                    step=1.0,
                    help="Maximum acceptable packet loss percentage"
                )
                jitter = st.number_input(
                    "Jitter Threshold (seconds)",
                    min_value=0.0,
                    value=0.1,
                    step=0.01,
                    help="Maximum acceptable jitter"
                )
            
            submitted = st.form_submit_button("Add Device")
            if submitted:
                if not validate_ip(ip_address):
                    st.error("Invalid IP address format")
                elif not device_type:
                    st.error("Please select a device type")
                else:
                    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                    database.add_device(
                        ip_address, description, tag_list, device_type,
                        response_time, packet_loss, jitter
                    )
                    st.success("Device added successfully!")

    # List and manage existing devices
    st.subheader("Existing Devices")
    devices = database.get_devices()
    
    for device in devices:
        with st.expander(f"{device['ip_address']} - {device['description']}"):
            with st.form(f"edit_device_{device['id']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_ip = st.text_input("IP Address", value=device['ip_address'])
                    new_desc = st.text_input("Description", value=device['description'])
                    new_tags = st.text_input(
                        "Tags",
                        value=",".join(device['tags'] if device['tags'] else [])
                    )
                    new_type = st.selectbox(
                        "Device Type",
                        [""] + DEVICE_TYPES,
                        index=DEVICE_TYPES.index(device['device_type']) + 1 
                        if device['device_type'] in DEVICE_TYPES else 0
                    )
                
                with col2:
                    st.subheader("Performance Thresholds")
                    new_response_time = st.number_input(
                        "Response Time Threshold (seconds)",
                        min_value=0.0,
                        value=float(device['response_time_threshold'] or 1.0),
                        step=0.1,
                        key=f"rt_{device['id']}"
                    )
                    new_packet_loss = st.number_input(
                        "Packet Loss Threshold (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=float(device['packet_loss_threshold'] or 5.0),
                        step=1.0,
                        key=f"pl_{device['id']}"
                    )
                    new_jitter = st.number_input(
                        "Jitter Threshold (seconds)",
                        min_value=0.0,
                        value=float(device['jitter_threshold'] or 0.1),
                        step=0.01,
                        key=f"j_{device['id']}"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Update"):
                        if not validate_ip(new_ip):
                            st.error("Invalid IP address format")
                        elif not new_type:
                            st.error("Please select a device type")
                        else:
                            tag_list = [tag.strip() for tag in new_tags.split(",") if tag.strip()]
                            database.update_device(
                                device['id'], new_ip, new_desc, tag_list,
                                new_type, new_response_time, new_packet_loss, new_jitter
                            )
                            st.success("Device updated successfully!")
                            st.rerun()
                
                with col2:
                    if st.form_submit_button("Delete", type="primary"):
                        database.delete_device(device['id'])
                        st.success("Device deleted successfully!")
                        st.rerun()
