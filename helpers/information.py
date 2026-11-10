import streamlit as st
from helpers.localization import normalize_language, translate


@st.dialog("Information")
def showinfo(info):
    st.markdown(info)
    language = normalize_language((st.session_state.get("profile") or {}).get("language"))
    if st.button(translate("OK", language)):
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
    language = normalize_language((st.session_state.get("profile") or {}).get("language"))
    translated_presets = {
        "zh-CN": {
            "admin": """欢迎使用学生管理系统！

1) **创建账户**：打开“管理账户”，选择“创建”以创建账户。您也可以从菜单发送密码重置邮件。

2) **公告**：打开“公告”并选择“创建”。在“内容”和“收件人”标签页中填写公告并选择对象。

3) **班级管理**：“班级”区域可查看和管理各班级的报告、课程表和活动。""",
            "coach": """欢迎使用学生管理系统！

1) **创建和管理班级**：在“仪表板”创建班级、设置课程表，并将班级代码分享给学生。

2) **查看班级详情**：选择班级查看课程表、活动和学生提交内容，也可记录考勤并查看报告。

3) **查看公告**：前往“收件箱”查看管理员发送的通知和学校的重要信息。""",
            "student": """欢迎使用学生管理系统！

1) **加入班级**：在“仪表板”选择“加入班级”并输入班级代码。

2) **完成活动**：打开班级查看课程表和活动，并在截止日期前提交作业。

3) **查看报告和通知**：在班级报告中查看学习进度，并在“收件箱”查看教练或学校的通知。""",
        },
        "ms": {
            "admin": """Selamat datang ke Sistem Pengurusan Pelajar!

1) **Cipta akaun**: Buka “Urus Akaun” dan pilih “Cipta”. Anda juga boleh menghantar e-mel tetapan semula kata laluan melalui menu.

2) **Pengumuman**: Buka “Pengumuman” dan pilih “Cipta”. Isi kandungan dan pilih penerima.

3) **Urus kelas**: Bahagian “Kelas” membolehkan anda melihat dan mengurus laporan, jadual dan aktiviti setiap kelas.""",
            "coach": """Selamat datang ke Sistem Pengurusan Pelajar!

1) **Cipta dan urus kelas**: Cipta kelas di “Papan Pemuka”, tetapkan jadual dan kongsi kod kelas dengan pelajar.

2) **Lihat butiran kelas**: Pilih kelas untuk melihat jadual, aktiviti dan penyerahan pelajar. Anda juga boleh merekod kehadiran dan melihat laporan.

3) **Semak pengumuman**: Buka “Peti Masuk” untuk melihat kemas kini pentadbir dan maklumat penting sekolah.""",
            "student": """Selamat datang ke Sistem Pengurusan Pelajar!

1) **Sertai kelas**: Pilih “Sertai Kelas” pada “Papan Pemuka” dan masukkan kod kelas.

2) **Selesaikan aktiviti**: Buka kelas untuk melihat jadual dan aktiviti, kemudian hantar tugasan sebelum tarikh akhir.

3) **Lihat laporan dan pemberitahuan**: Semak kemajuan dalam laporan kelas dan lihat mesej sekolah atau jurulatih dalam “Peti Masuk”.""",
        },
    }

    if st.button(translate(text, language), icon=icon, type="tertiary"):
        info = translated_presets.get(language, {}).get(preset, presets.get(preset))
        showinfo(info)