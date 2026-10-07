from pymongo import MongoClient
from gridfs import GridFS
import streamlit as st
from bson import ObjectId

client = MongoClient(st.secrets["mongodb"]["uri"])
db = client["StudentMgmtSystem"]
fs = GridFS(db)

# mongodb implementation for file upload and download

def upload(file, filename=None, contentType=None):

    if filename is None and hasattr(file, "name"):
        filename = file.name

    if contentType is None and hasattr(file, "type"):
        contentType = file.type

    if hasattr(file, "getvalue"):
        file_data = file.getvalue()
    elif hasattr(file, "read"):
        file_data = file.read()
    else:
        file_data = file

    fileid = fs.put(
        file_data,
        filename=filename,
        contentType=contentType
    )

    return str(fileid)

@st.cache_data(show_spinner=False)
def download(fileid):

    from bson import ObjectId

    file = fs.get(ObjectId(fileid))

    return {
        "data": file.read(),
        "filename": file.filename,
        "contentType": file.contentType
    }


def delete(fileid):
    fs.delete(ObjectId(fileid))