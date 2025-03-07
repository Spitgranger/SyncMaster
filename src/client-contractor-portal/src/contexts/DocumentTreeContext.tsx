//@ts-nocheck
import convertToState from '@/utils/convertToState';
import React, { useReducer, createContext, useEffect, useState } from 'react';

const DocumentTreeStateContext = createContext<any | undefined>(undefined);
const DocumentTreeDispatchContext = createContext<React.Dispatch<any> | undefined>(undefined);

const reducer = (state: any, action: { type: any; payload: any }) => {
  const { type, payload } = action;
  switch (type) {
    case 'INIT_DATA':
      if(!("sitewide" in payload.data.folders)){
        payload.data.folders["sitewide"] = {
            id: 'sitewide',
            title: 'Site Wide Documents',
            childFolders: [],
            childFiles: [],
            path: 'sitewide',
            parentId: null,
        }
      }
      if(!("sitespecific" in payload.data.folders)){
        payload.data.folders["sitespecific"] = {
            id: 'sitewide',
            title: 'Site Specific Documents',
            childFolders: [],
            childFiles: [],
            path: 'sitespecific',
            parentId: null,
        }
      }
      return {
        ...payload.data
      }
    case 'REFRESH_DATA':
      const convertedState = convertToState(payload.data);
      console.log("refreshed",convertedState);
      
      return {
        folders: {
          ...state["folders"],
          ...convertedState["folders"],
        },
        files: {
          ...state["files"],
          ...convertedState["files"],
        }
      };
      case 'ADD_NEW_FOLDER':
        console.log("new folder act", payload);
      
        const parentFolderId = payload.data.parentId;
        const folderId = payload.data.folderId;
      
        // Get the current childFolders for the parent folder
        const currentChildFolders = state["folders"][parentFolderId]?.["childFolders"] || [];
      
        // Check if the folderId is not already in childFolders
        if (!currentChildFolders.includes(folderId)) {
          // Create a new array with the new folderId added
          const updatedChildFolders = [...currentChildFolders, folderId];
      
          // Update the state with the new childFolders array
          return {
            folders: {
              ...state["folders"],
              [parentFolderId]: {
                ...state["folders"][parentFolderId],
                childFolders: updatedChildFolders,
              },
              ...payload.data.folderObject, // Adding new folderObject here as well
            },
            files: {
              ...state["files"],
            }
          };
        }
    default:
      return state;
  }
};

let initialState = {
  folders: {
    // sitewide: {
    //   id: 'sitewide',
    //   title: 'Site Wide Documents',
    //   childFolders: [],
    //   childFiles: ['sitewide/file3.txt'],
    //   path: 'sitewide',
    //   parentId: null,
    // },
    // sitespecific: {
    //   id: 'sitespecific',
    //   title: 'Site Specific Documents',
    //   childFolders: ['sitespecific/folder1', 'sitespecific/Folder3'],
    //   childFiles: [],
    //   path: 'sitespecific',
    //   parentId: null,
    // },
    // 'sitespecific/folder1': {
    //   id: 'sitespecific/folder1',
    //   title: 'folder1',
    //   childFolders: ['sitespecific/folder1/folder2'],
    //   childFiles: ['sitespecific/folder1/file2.txt'],
    //   path: 'sitespecific/folder1',
    //   parentId: 'sitespecific',
    // },
    // 'sitespecific/folder1/folder2': {
    //   id: 'sitespecific/folder1/folder2',
    //   title: 'folder2',
    //   childFolders: [],
    //   childFiles: ['sitespecific/folder1/folder2/file1.txt'],
    //   path: 'sitespecific/folder1/folder2',
    //   parentId: 'sitespecific/folder1',
    // },
    // 'sitespecific/Folder3': {
    //   id: 'sitespecific/Folder3',
    //   title: 'Folder3',
    //   childFolders: [],
    //   childFiles: [],
    //   path: 'sitespecific/Folder3',
    //   parentId: 'sitespecific',
    // },
  },
  files: {
    // 'sitespecific/folder1/folder2/file1.txt': {
    //   id: 'sitespecific/folder1/folder2/file1.txt',
    //   title: 'file1.txt',
    //   link: 'https://mui.com/material-ui/material-icons/?srsltid=AfmBOorOQDAvfTRCZ0we0QqFD8pbvUcV3_kK6pVhwuXEhutOmw32kwV2&query=docum&selected=InsertDriveFile',
    //   pathname: 'sitespecific/folder1/folder2/file1.txt',
    // },
    // 'sitespecific/folder1/file2.txt': {
    //   id: 'sitespecific/folder1/file2.txt',
    //   title: 'file2.txt',
    //   link: 'https://mui.com/material-ui/material-icons/?srsltid=AfmBOorOQDAvfTRCZ0we0QqFD8pbvUcV3_kK6pVhwuXEhutOmw32kwV2&query=docum&selected=InsertDriveFile',
    //   pathname: 'sitespecific/folder1/file2.txt',
    // },
    // 'sitewide/file3.txt': {
    //   id: 'sitewide/file3.txt',
    //   title: 'file3.txt',
    //   link: 'https://mui.com/material-ui/material-icons/?srsltid=AfmBOorOQDAvfTRCZ0we0QqFD8pbvUcV3_kK6pVhwuXEhutOmw32kwV2&query=docum&selected=InsertDriveFile',
    //   pathname: 'sitewide/file3.txt',
    // },
  },
};

const DocumentTreeContextProvider = ({ children }: any) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [loading, setLoading] = useState(true); // Track loading state

  useEffect(() => {
    const fetchData = async () => {
      let siteFiles = {};
      let siteWideFiles = {};

      try {
        const sitespecific = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/documents/HC057/get_files`);
        siteFiles = convertToState(await sitespecific.json());

        const siteWideData = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/documents/ALL/get_files`);
        siteWideFiles = convertToState(await siteWideData.json());

        const updatedState = {
          folders: { ...siteWideFiles.folders, ...siteFiles.folders },
          files: { ...siteWideFiles.files, ...siteFiles.files },
        };

        dispatch({ type: 'INIT_DATA', payload: { data: updatedState } });
        setLoading(false); // Set loading to false once the data is fetched and state is updated
      } catch (error) {
        console.error(error);
        setLoading(false); // Set loading to false in case of an error
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div>Loading...</div>; // Show a loading state while data is being fetched
  }

  return (
    <DocumentTreeStateContext.Provider value={state}>
      <DocumentTreeDispatchContext.Provider value={dispatch}>
        {children}
      </DocumentTreeDispatchContext.Provider>
    </DocumentTreeStateContext.Provider>
  );
};

export { DocumentTreeStateContext, DocumentTreeDispatchContext, DocumentTreeContextProvider };
