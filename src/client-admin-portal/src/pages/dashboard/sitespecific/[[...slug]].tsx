import FilePathBreadCrumbComponent from '@/components/FilePathBreadCrumbComponent'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { DocumentTreeContextProvider, DocumentTreeDispatchContext, DocumentTreeStateContext } from '@/contexts/DocumentTreeContext'
import { useRouter } from 'next/router'
import React, { useContext } from 'react'


function convertPathToArray(path: string) {
  const parts = path.split('/');
  let result = [];
  let currentPath = '';

  // Iterate over the parts and build the paths incrementally
  for (let i = 0; i < parts.length; i++) {
    currentPath += (i === 0 ? '' : '/') + parts[i]; // Add '/' between parts except the first one
    result.push(currentPath);
  }

  return result;
}

const ejfakle = () => {
  const router = useRouter()
  const state = useContext(DocumentTreeStateContext)
  const dispatch = useContext(DocumentTreeDispatchContext)

  console.log(router);

  const breadcrumbs = (decodeURI(router.asPath).split("/").slice(2))
  const currentRoot = router.asPath.replace("/dashboard/", "")

  const breadcrumbPath = convertPathToArray(router.asPath.replace("/dashboard/", ""))

  // console.log(router.query.slug);


  // console.log(breadcrumbs);
  // const breadcrumbs = router.query.slug;
  console.log(breadcrumbPath);
  console.log(state["folders"][currentRoot]);
  

  // const childFoldersList = state["folders"][currentRoot]["childFolders"]
  // const childFilesList = state["folders"][currentRoot]["childFiles"]

  // console.log(childFilesList);
  // console.log(childFoldersList);
  



  return (
    <>
      {/* <button onClick={() => { router.push(`${router.asPath}/Folder 1`) }}>ejfakle</button> */}
      {router.isReady && (
        <>
          {/* <div>current path: {currentRoot}</div> */}
          <FilePathBreadCrumbComponent breadcrumbPath={breadcrumbPath} />
          <br />
          <div>Folders in this directory</div>
          {
            state["folders"][currentRoot]["childFolders"].map(function(folderId:string){
              return <div onClick={()=>{router.push(`/dashboard/${state["folders"][folderId]["path"]}`)}}>{state["folders"][folderId]["title"]}</div>
            })
          }
          <br />
          <div>Files in this directory</div>
          {
            state["folders"][currentRoot]["childFiles"].map(function(fileId:string){
              return <div>{state["files"][fileId]["title"]}</div>
            })
          }
        </>
      )}

    </>
  )
}

export default ejfakle

ejfakle.getLayout = function getLayout(page: React.ReactElement) {
  return <DashboardLayout><DocumentTreeContextProvider>{page}</DocumentTreeContextProvider></DashboardLayout>
}