# USER JOURNEY

1. Log-in view
    - check if user is subscribed
        - prompt user to subscribe
        - if subscribed, continue
    - **SELECT FROM logins**:
        - login_count
        - login_count += 1
    - **INSERT INTO logins**:
        - (datetime_login, login_count, email)
2. Show first form (no AI)
    - when user submits:
        - **INSERT INTO forms**:
            - (form_id, form_type_id, email, project_id, form_submitted_datetime)
        - **INTERT INTO fields_submitted**:
            - (field_id, prompt_for_field, field_filled_content, form_id, form_type_id, project_id)
3. Show generation w/ feedback table
    - Show feedback table:
        - 