import os
import sys

def fix_permissions():
    """Fix permissions for the network monitoring application"""
    try:
        # Ensure database file is readable/writable
        if os.path.exists('network_monitor.db'):
            os.chmod('network_monitor.db', 0o644)
            print("✓ Set database file permissions")

        # Make Python files executable
        for root, _, files in os.walk('.'):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    os.chmod(file_path, 0o755)
        print("✓ Set Python files permissions")

        # Ensure streamlit config directory exists and is accessible
        streamlit_config_dir = os.path.expanduser('~/.streamlit')
        os.makedirs(streamlit_config_dir, exist_ok=True)
        os.chmod(streamlit_config_dir, 0o755)
        
        # Ensure streamlit config file has correct permissions
        config_file = os.path.join(streamlit_config_dir, 'config.toml')
        if os.path.exists(config_file):
            os.chmod(config_file, 0o644)
        print("✓ Set Streamlit config permissions")

        return True
    except Exception as e:
        print(f"Error fixing permissions: {e}")
        return False

if __name__ == '__main__':
    if fix_permissions():
        print("\nPermissions successfully fixed!")
        sys.exit(0)
    else:
        print("\nFailed to fix permissions!")
        sys.exit(1)
