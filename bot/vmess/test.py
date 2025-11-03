def add_to_config(user, uuid, days):
    exp_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    new_entry = f'}},"id": "{uuid}","email": "{user_lower}"}}'
    comment_line = f"## {user_lower} {exp_date}" 
    config_file = "/usr/local/etc/xray/config/04_inbounds.json"
    
    # Create a temporary file with the new content
    temp_content = f"{comment_line}\n{new_entry}\n"
    
    # Add to VMESS section
    subprocess.run([
    'sed', '-i', r'/#vmess$/r /dev/stdin', config_file
    ], input=temp_content.encode())
    

### cahya-VWTW 2025-11-26
},{"id": "ID","email": "email"
