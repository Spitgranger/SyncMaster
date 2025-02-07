import React, { useReducer, createContext, useEffect } from 'react'

const DocumentTreeStateContext = createContext<any | undefined>(undefined)
const DocumentTreeDispatchContext = createContext<React.Dispatch<any> | undefined>(undefined)


const reducer = (state: any, action: { type: any; payload: any }) => {
  const { type, payload } = action
  switch (type) {
    case "CHANGE_MODE":
      return {
        ...state,
        darkMode: payload
      }
    default:
      return state
  }
}

const initialState = {
  "folders": {
    "sitewide": {
      "id": "sitewide",
      "title": "Site Wide Documents",
      "childFolders": [],
      "childFiles": [
        "sitewide/file3.txt"
      ],
      "path": "sitewide",
      "parentId": null
    },
    "sitespecific": {
      "id": "sitespecific",
      "title": "Site Specific Documents",
      "childFolders": [
        "sitespecific/folder1",
        "sitespecific/Folder3"
      ],
      "childFiles": [],
      "path": "sitespecific",
      "parentId": null
    },
    "sitespecific/folder1": {
      "id": "sitespecific/folder1",
      "title": "folder1",
      "childFolders": [
        "sitespecific/folder1/folder2"
      ],
      "childFiles": [
        "sitespecific/folder1/file2.txt"
      ],
      "path": "sitespecific/folder1",
      "parentId": "sitespecific"
    },
    "sitespecific/folder1/folder2": {
      "id": "sitespecific/folder1/folder2",
      "title": "folder2",
      "childFolders": [],
      "childFiles": [
        "sitespecific/folder1/folder2/file1.txt"
      ],
      "path": "sitespecific/folder1/folder2",
      "parentId": "sitespecific/folder1"
    },
    "sitespecific/Folder3": {
      "id": "sitespecific/Folder3",
      "title": "Folder3",
      "childFolders": [],
      "childFiles": [],
      "path": "sitespecific/Folder3",
      "parentId": "sitespecific"
    }
  },
  "files": {
    "sitespecific/folder1/folder2/file1.txt": {
      "id": "sitespecific/folder1/folder2/file1.txt",
      "title": "file1.txt",
      "link": "filelink",
      "pathname": "sitespecific/folder1/folder2/file1.txt"
    },
    "sitespecific/folder1/file2.txt": {
      "id": "sitespecific/folder1/file2.txt",
      "title": "file2.txt",
      "link": "filelink",
      "pathname": "sitespecific/folder1/file2.txt"
    },
    "sitewide/file3.txt": {
      "id": "sitewide/file3.txt",
      "title": "file3.txt",
      "link": "filelink",
      "pathname": "sitewide/file3.txt"
    }
  }
}

const DocumentTreeContextProvider = ({ children }: any) => {


  const [state, dispatch] = useReducer(reducer, initialState)


  return (
    <DocumentTreeStateContext.Provider value={state}>
      <DocumentTreeDispatchContext.Provider value={dispatch}>
        {children}
      </DocumentTreeDispatchContext.Provider>
    </DocumentTreeStateContext.Provider>
  )
}

export { DocumentTreeStateContext, DocumentTreeDispatchContext, DocumentTreeContextProvider }