//import { DocumentTreeStateContext } from '@/contexts/DocumentTreeContext';
//import { Breadcrumbs, List, ListItem, Typography } from '@mui/material';
//import Link from 'next/link';
//import { useRouter } from 'next/router';
//import React, { useContext } from 'react'
//
//const FilePathBreadCrumbComponent = (props: any) => {
//  const router = useRouter()
//  console.log(props);
//
//  const { breadcrumbPath } = props;
//  const state = useContext(DocumentTreeStateContext)
//  console.log(state);
//  // console.log(state["folders"]["sitespecific/folder1"]["title"])
//
//  console.log("herejaf;", breadcrumbPath)
//
//  // [{tite:"",path:""}]
//
//  return (
//    <Breadcrumbs separator=">">
//      {breadcrumbPath?.map(function (path: any) {
//        console.log("here", path);
//
//        return (
//          state["folders"][decodeURI(path)] &&
//          <Typography sx={{ cursor: "pointer" }} variant='h5' onClick={() => { router.push(`/dashboard/${path}`) }}>{state["folders"][decodeURI(path)]["title"]}</Typography>
//        )
//      })}
//    </Breadcrumbs>
//  )
//}
//
//export default FilePathBreadCrumbComponent