# DATA DICTIONARY

# USER METADATA:

## users
- **email**: (PRIMARY KEY)
    - user's email/unique identifier
- **password**: 
    - password associated
- **TBD other user detail data to collect**

## logins
- **datetime_login**: (COMP. PRIMARY KEY)
    - datetime of login
- **login_count**: (COMP. PRIMARY KEY)
    - rolling count of times user has logged in
- **email**: (COMP. PRIMARY KEY)
    - user's email/unique identifier


# OBJECTS:

## projects
- **project_id**: (PRIMARY KEY)
    - unique identifier for a project (the document the user is trying to create with this app)
- **project_title**: 
    - user-facing unique name for project (user cannot have duplicates, but there can be duplicates in the database)
- **project_created_datetime**: 
    - datetime of initial project creation
- **email**: (FOREIGN KEY)
    - user who created project

## forms
- **form_id**:
    - ...
- **form_type_id**:
    - ...
- **email**:
    - user email for whom the form is being generated
- **project_id**:
    - ...
- **form_submitted_datetime**
    - ...

## fields_submitted
- **field_id**: (PRIMARY KEY)
    - ...
- **prompt_for_field**: 
    - ...
- **field_filled_content**: 
    - ...
- **form_id**:
    - ...
- **form_type_id**: 
    - ...
- **project_id**: 
    - ...


## form_level_feedback_submitted
- **overall_feedback_id**:
    - ...
- **form_type_id**: 
    - ...
- **form_id**:
    - ...
- **overall_form_feedback**: 
    - ...
- **decision_id**: 
    - ...

## field_level_feedback_submitted
- **field_level_feedback_id**: (PRIMARY KEY)
    - ...
- **field_id**: (FOREIGN KEY)
    - ...
    - **prompt_for_field**: 
        - ...
    - **field_content_type_id**: 
        - ...
    - **field_original_filled_content**:
        - ...
    - **field_level_decision_id**:
        - ...
    - **prompt_modification**:
        - ...
    - **content_modification**:
        - ...
    - **feedback_text**: 
        - ...
- **form_id**:
    - ...
    - **form_type_id**: 
        - ...
- **project_id**: 
    - ...


# LOOKUP TABLES:

## form_types
- **form_type_id**:
    - ...
- **form_type**:
    - ...

## form_decision_types
- **decision_id**: 
    - ...
- **decision_description**: 
    - start_over, regen_using_feedback, continue_adding_detail, finalize_document

## field_decision_types
- **field_level_decision_id**:
    - ...
- **field_level_decision**:
    - ...

## filled_content_types
- **filled_content_type_id**:
    - ...
- **filled_content_type**:
    - ...