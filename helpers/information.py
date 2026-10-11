import streamlit as st

@st.dialog("Information")
def showinfo(info):
    st.markdown(info)
    if st.button("OK"):
        st.rerun()

def infobox(info="", preset="none", text="", icon=":material/help:"):
    presets = {"admin":'''Welcome to Student Management System!
                
1) **Create Accounts**

    Open the **:material/manage_accounts: Manage Accounts** tab and select **:material/add: Create** to create an account.

    Once you have created the account, you may send a reset password email by selecting the **:material/more_vert: > Reset Password** to let them create their own password.

    With that, they will be able to log into their accounts.
    
2) **Announcements**

    To send announcements to certain users, open the **:material/campaign: Announcements** tab and select **:material/add: Create** to create an announcement.
    
    The **Content** tab is for editing the announcement content, and the **Receipients** tab allows you to select which roles or users to send it to.
    
3) **Class Management**

    The **Classes** section allows you to view and manage each class respective :material/analytics: Reports, :material/calendar_month: Schedules, and :material/directions_run: Activities.''',
    "coach":'''Welcome to Student Management System!

1) **Create and Manage Classes**

    Open the **:material/school: Dashboard** to create a class, assign a class schedule, and share the class code with students so they can join.

    You may also remove classes that are no longer needed from your class list.

2) **View Class Details**

    Select a class to view its schedule, activities, and student submissions.

    This lets you manage each class in one place and keep track of the work assigned to students.

    You may record attendance of students, and view reports to view a summary of your student's progress in this screen.

3) **Stay Updated**

    Check your **:material/inbox: Inbox** for updates from admins or important class and school communications.''',
    "student":'''Welcome to Student Management System!

1) **Join a Class**

    Open the **:material/school: Dashboard** and select **:material/add: Join Class** to enter your class code.

    Once joined, your class will appear in your student dashboard.

2) **Complete Activities**

    Open a class to view its schedule and activities, then submit and manage your work before each deadline.

    You can view assigned tasks, upload files, and track your submission status.

3) **View Report**

    You may use the **Reports** section of the class view to see a summary of your progress and attendance.

3) **Check Notifications**

    Use the **:material/inbox: Inbox** tab to keep up with messages, reminders, and important updates from your coach or school.''',
    "none":info}
    if st.button(text, icon=icon, type="tertiary"):
        showinfo(presets.get(preset))