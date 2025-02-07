//@ts-nocheck
import FilePathBreadCrumbComponent from '@/components/FilePathBreadCrumbComponent'
import FileUploaderComponent from '@/components/FileUploaderComponent'
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { DocumentTreeContextProvider, DocumentTreeDispatchContext, DocumentTreeStateContext } from '@/contexts/DocumentTreeContext'
import { CreateNewFolder, Folder, InsertDriveFile } from '@mui/icons-material'
import { Box, Dialog, DialogTitle, DialogContent, TextField, DialogActions, Container, Table, TableBody, TableCell, TableHead, TableRow, Typography, Button, Menu, MenuItem } from '@mui/material'
import Link from 'next/link'
import { useRouter } from 'next/router'
import React, { useContext, useState, useEffect, useRef } from 'react'


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

  const [folderName, setFolderName] = useState(''); // state to store folder name
  const [openDialog, setOpenDialog] = useState(false); // state to control dialog visibility

  const breadcrumbs = (decodeURI(router.asPath).split("/").slice(2))
  const currentRoot = decodeURI(router.asPath.replace("/dashboard/", ""))

  const breadcrumbPath = convertPathToArray(router.asPath.replace("/dashboard/", ""))

  const [selectedRow, setSelectedRow] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null); // For context menu
  const [contextMenuPosition, setContextMenuPosition] = useState({ top: 0, left: 0 }); // Context menu position
  const tableRef = useRef(null); // Reference to the table


  // Handle "Add New Folder" option
  const handleAddNewFolder = () => {
    setOpenDialog(true); // Open the dialog for the user to enter the folder name
  };

  // Handle modal submit
  const handleSubmitFolder = () => {
    if (folderName.trim()) {
      dispatch({
        type: "ADD_NEW_FOLDER", payload: {
          data: {
            folderObject: {
              [`${currentRoot}/${folderName}`]: {
                id: `${currentRoot}/${folderName}`,
                title: folderName, // Use the actual name
                childFiles: [],
                childFolders: [],
                path: `${currentRoot}/${folderName}`,
                parentId: `${currentRoot}`
              }
            },
            parentId: currentRoot,
            folderId: `${currentRoot}/${folderName}`
          }
        }
      });
      setOpenDialog(false); // Close the dialog after submitting
      setFolderName(''); // Reset folder name
    } else {
      alert('Please enter a valid folder name'); // Optional validation for empty folder name
    }
  };


  const deleteItem = async (pathname) => {
    try {
      const deleteResponse = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/documents/delete?file_path=${encodeURIComponent(pathname)}&site_id=ALL`, {
        method: "DELETE",
      });
    
      if (!deleteResponse.ok) {
        throw new Error("Error while deleting the document");
      }
    
      const data = await deleteResponse.json();
      console.log(data);
    } catch (error) {
      console.error("Error:", error);
    }
  }

  // Handle row selection
  const handleRowClick = (rowId) => {
    setSelectedRow(rowId === selectedRow ? null : rowId); // Toggle selection
  };

  // Delete the selected row (dummy function)
  const handleDelete = async () => {
    if (selectedRow) {
      // Add your delete logic here
      console.log('Delete item with ID:', selectedRow);
      await deleteItem(selectedRow);
      setSelectedRow(null); // Deselect after deletion
      // window.location.reload()
    }
  };

  // Handle right-click (context menu)
  const handleRightClick = (event) => {
    event.preventDefault(); // Prevent default context menu

    // Check if context menu is already open. If it is, close it, otherwise open it.
    if (anchorEl) {
      setAnchorEl(null); // Close the context menu
    } else {
      setContextMenuPosition({ top: event.clientY, left: event.clientX }); // Set menu position
      setAnchorEl(event.currentTarget); // Open context menu
    }
  };

  // Handle closing the context menu
  const handleCloseContextMenu = () => {
    setAnchorEl(null);
  };

  // Handle "Add New Folder" option
  // const handleAddNewFolder = () => {
  //   console.log('Adding a new folder...');
  //   dispatch({
  //     type: "ADD_NEW_FOLDER", payload: {
  //       data: {
  //         folderObject: {
  //           [`${currentRoot}/new folder ez`]: {
  //             id: `${currentRoot}/new folder ez`,
  //             title: "new folder ez",
  //             childFiles: [],
  //             childFolders: [],
  //             path: `${currentRoot}/new folder ez`,
  //             parentId: `${currentRoot}`
  //           }
  //         },
  //         parentId: currentRoot,
  //         folderId: `${currentRoot}/new folder ez`
  //       }
  //     }
  //   })
  //   // Your custom function to add a new folder
  //   handleCloseContextMenu(); // Close the context menu
  // };

  // Handle double-click on folders or files
  const handleDoubleClick = (itemId, isFolder) => {
    if (isFolder) {
      router.push(`/dashboard/${state["folders"][itemId]["path"]}`); // Navigate to the folder
    } else {
      window.open(state["files"][itemId]["link"], '_blank'); // Open the file in a new tab
    }
  };

  // Add the event listener to handle clicks outside
  useEffect(() => {
    document.addEventListener('click', () => setAnchorEl(null)); // Close context menu on click outside

    // Clean up the event listener when component is unmounted or page is navigated
    return () => {
      document.removeEventListener('click', () => setAnchorEl(null));
    };
  }, []);

  // Clear selection on page navigation
  useEffect(() => {
    setSelectedRow(null); // Reset the selected row when the page changes
  }, [router.asPath]);
  console.log(state);
  console.log(state["folders"]);
  console.log("current root", currentRoot);



  return (
    <Container>
      {router.isReady && (
        <>
          <FilePathBreadCrumbComponent breadcrumbPath={breadcrumbPath} />
          <br />
          <Table sx={{ mb: 6 }} ref={tableRef} onContextMenu={handleRightClick}> {/* Added right-click handler */}
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Type</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {
                state["folders"][currentRoot] &&
                state["folders"][currentRoot]["childFolders"].map(function (folderId: string) {
                  return (
                    <TableRow
                      key={folderId}
                      onClick={() => handleRowClick(folderId)}
                      onDoubleClick={() => handleDoubleClick(folderId, true)} // Double click to open folder
                      sx={{ cursor: 'pointer', backgroundColor: selectedRow === folderId ? 'rgba(0, 0, 0, 0.1)' : 'transparent' }}
                    >
                      <TableCell align='center' >
                        <Box display="flex" alignItems="center" >
                          <Folder />
                          <Typography sx={{ display: "inline", marginLeft: 1, mt: "5px", cursor: "pointer" }} variant='body1'>
                            {state["folders"][folderId]["title"]}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell >
                        <Typography variant='body1'>Folder</Typography>
                      </TableCell>
                    </TableRow>
                  )
                })
              }
              {
                state["folders"][currentRoot] &&
                state["folders"][currentRoot]["childFiles"].map(function (fileId: string) {
                  return (
                    <TableRow
                      key={fileId}
                      onClick={() => handleRowClick(fileId)}
                      onDoubleClick={() => handleDoubleClick(fileId, false)} // Double click to open file
                      sx={{ cursor: 'pointer', backgroundColor: selectedRow === fileId ? 'rgba(0, 0, 0, 0.1)' : 'transparent' }}
                    >
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <InsertDriveFile />
                          <Link style={{ textDecoration: "none", color: "inherit", marginLeft: "8px", marginTop: "5px" }} href={state["files"][fileId]["link"]}>
                            {state["files"][fileId]["title"]}
                          </Link>
                        </Box>
                      </TableCell>
                      <TableCell >
                        <Typography variant='body1'>File</Typography>
                      </TableCell>
                    </TableRow>
                  )
                })
              }
            </TableBody>
          </Table>

          {/* Context Menu */}
          <Menu
            anchorReference="anchorPosition"
            anchorPosition={anchorEl ? { top: contextMenuPosition.top + 10, left: contextMenuPosition.left + 10 } : undefined}
            open={Boolean(anchorEl)}
            onClose={handleCloseContextMenu}
          >
            <MenuItem autoFocus onClick={handleAddNewFolder}>                        <Box display="flex" alignItems="center">
              <CreateNewFolder sx={{ mr: 1 }}></CreateNewFolder>
              <Typography variant='subtitle1'>
                Add New Folder
              </Typography>
            </Box></MenuItem>
          </Menu>


          <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
            <DialogTitle>Enter a Folder Name</DialogTitle>
            <DialogContent>
              <TextField
                autoFocus
                fullWidth
                variant="filled"
                label="Folder Name"
                value={folderName}
                onChange={(e) => setFolderName(e.target.value)} // update folder name as the user types
              />
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setOpenDialog(false)} color="primary">
                Cancel
              </Button>
              <Button onClick={handleSubmitFolder} color="primary">
                Submit
              </Button>
            </DialogActions>
          </Dialog>

        </>
      )}
      <Box sx={{ display: "flex", justifyContent: "space-between" }}>
        <FileUploaderComponent filepath={currentRoot} />
        {selectedRow && <Button variant="contained" color="error" onClick={handleDelete}>Delete Selected</Button>}
      </Box>
    </Container>
  );
};

export default ejfakle;

ejfakle.getLayout = function getLayout(page: React.ReactElement) {
  return <DashboardLayout><DocumentTreeContextProvider>{page}</DocumentTreeContextProvider></DashboardLayout>;
}
