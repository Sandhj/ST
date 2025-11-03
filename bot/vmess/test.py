def add_to_config(user, uuid, days):
    exp_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    new_entry = f'{{"id": "{uuid}", "alterId": 0, "email": "{user_lower}"}},'  # Use lowercase username
    comment_line = f"## {user_lower} {exp_date}"  # Use lowercase username
    config_file = "/usr/local/etc/xray/config/04_inbounds.json"
    
    # Create a temporary file with the new content
    temp_content = f"{comment_line}\n{new_entry}\n"
    
    # Add to VMESS section
    subprocess.run([
    'sed', '-i', r'/#vmess$/r /dev/stdin', config_file
    ], input=temp_content.encode())
    
