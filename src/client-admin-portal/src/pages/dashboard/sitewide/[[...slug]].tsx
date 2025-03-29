"use client"
import DashboardLayout from '@/components/layouts/DashboardLayout'
import { AppDispatch, RootState } from '@/state/store'
import { Folder, InsertDriveFile } from '@mui/icons-material'
import { Box, Container, Table, TableBody, TableCell, TableHead, TableRow, Typography, Skeleton } from '@mui/material'
import { useRouter } from 'next/router'
import React, { } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { getDocuments } from '@/state/document/documentSlice' // Adjust the path as needed
import FileUploaderComponent from '@/components/FileUploaderComponent'
import TableSortLabel from '@mui/material/TableSortLabel';
import { visuallyHidden } from '@mui/utils';
import Checkbox from '@mui/material/Checkbox';
import { format } from 'date-fns';
import Toolbar from '@mui/material/Toolbar';
import Tooltip from '@mui/material/Tooltip';
import IconButton from '@mui/material/IconButton';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteFileComponent from '@/components/DeleteFileComponent'

const SiteWideDocuments = () => {
  const userState = useSelector((state: RootState) => state.user)
  const documentState = useSelector((state: RootState) => state.document)
  const { currentFolderFiles, isLoading } = documentState
  const { username, role, idToken, userId } = userState;

  const router = useRouter();
  const folderId = router.query.slug ? router.query.slug[0] : "root"; // Handle slug logic

  console.log("Folder ID:", folderId);

  const dispatch = useDispatch<AppDispatch>();
  React.useEffect(() => {
    dispatch(getDocuments({ site_id: "ALL", folder_id: folderId, idToken: userState.idToken })).then((response) => {
      if (response.meta.requestStatus === "fulfilled") {
        console.log("Documents fetched successfully");
      }
      else {
        console.log("Documents fetch failed");
        console.log(response);
      }
    });
  }, [folderId, dispatch, userState.idToken]); // Fetch documents when folderId changes

  const [order, setOrder] = React.useState<'asc' | 'desc'>('asc');
  const [orderBy, setOrderBy] = React.useState<string>('document_name');
  const [selected, setSelected] = React.useState<string | null>(null);

  const handleRequestSort = (property: string) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleClick = (id: string) => {
    setSelected((prevSelected) => (prevSelected === id ? null : id));
  };

  const handleDoubleClick = (file: { document_type: string; document_id: string }) => {
    if (file.document_type === "folder") {
      router.push(`/dashboard/sitewide/${file.document_id}`);
    }
  };

  const isSelected = (id: string) => selected === id;

  const sortedFiles = React.useMemo(() => {
    const files = currentFolderFiles || []; // Ensure it's always an array
    return [...files].sort((a, b) => {
      if (orderBy === 'document_name') {
        return order === 'asc'
          ? a.document_name.localeCompare(b.document_name)
          : b.document_name.localeCompare(a.document_name);
      } else if (orderBy === 'last_modified') {
        const dateA = new Date(a.last_modified);
        const dateB = new Date(b.last_modified);
        return order === 'asc' ? dateA.getTime() - dateB.getTime() : dateB.getTime() - dateA.getTime();
      }
      return 0;
    });
  }, [currentFolderFiles, order, orderBy]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return format(date, "MMMM d, yyyy 'at' h:mm a");
  };

  const selectedFile = React.useMemo(() => {
    if (!selected) return null;
    return currentFolderFiles.find((file) => file.document_id === selected);
  }, [selected, currentFolderFiles]);

  return (
    <Container>
      {isLoading ? (
        <Table sx={{ mb: 6 }}>
          <TableHead>
            <TableRow>
              <TableCell>
                <Skeleton variant="text" width="80%" />
              </TableCell>
              <TableCell>
                <Skeleton variant="text" width="50%" />
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {[...Array(5)].map((_, index) => (
              <TableRow key={index}>
                <TableCell>
                  <Skeleton variant="text" width="80%" />
                </TableCell>
                <TableCell>
                  <Skeleton variant="text" width="50%" />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      ) : (
        <>
          <br />
          <Table sx={{ mb: 6 }}>
            <TableHead >
              {selectedFile && selectedFile.document_type === "file" && (
                <TableRow sx={{ height: "20px" }}>
                  <TableCell sx={{ px: 0, py: 0 }} colSpan={4}>
                    <Toolbar
                      sx={{
                        minHeight: "40px !important",
                        bgcolor: (theme) => theme.palette.action.hover,
                        px: "0 !important",
                        py: "0 !important",
                      }}
                    >
                      <Tooltip title="Download">
                        <IconButton
                          href={selectedFile.s3_presigned_get}
                          target="_blank"
                          rel="noopener noreferrer"
                          sx={{ padding: 0, minHeight: "auto", minWidth: "auto" }}
                        >
                          <DownloadIcon color="primary" />
                          <Typography color="primary" variant="body1" sx={{ ml: 1 }}>
                            Download
                          </Typography>
                        </IconButton>
                      </Tooltip>
                    </Toolbar>
                  </TableCell>
                </TableRow>
              )}
              <TableRow>
                <TableCell padding="checkbox">
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'document_name'}
                    direction={order}
                    onClick={() => handleRequestSort('document_name')}
                  >
                    Name
                    {orderBy === 'document_name' ? (
                      <Box component="span" sx={visuallyHidden}>
                        {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                      </Box>
                    ) : null}
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'last_modified'}
                    direction={order}
                    onClick={() => handleRequestSort('last_modified')}
                  >
                    Date Modified
                    {orderBy === 'last_modified' ? (
                      <Box component="span" sx={visuallyHidden}>
                        {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                      </Box>
                    ) : null}
                  </TableSortLabel>
                </TableCell>
                <TableCell>Type</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedFiles.map((file) => {
                console.log(file)

                const isItemSelected = isSelected(file.document_id);
                return (
                  <TableRow
                    key={file.document_id}
                    sx={{ cursor: 'pointer' }}
                    onClick={() => handleClick(file.document_id)}
                    onDoubleClick={() => handleDoubleClick(file)}
                    selected={isItemSelected}
                  >
                    <TableCell padding="checkbox">
                      <Checkbox
                        color="primary"
                        checked={isItemSelected}
                      />
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center">
                        {file.document_type === "folder" ? <Folder /> : <InsertDriveFile />}
                        <Typography sx={{ marginLeft: 1, mt: "5px" }} variant="body1">
                          {file.document_name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body1">{formatDate(file.last_modified)}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body1">
                        {file.document_type.charAt(0).toUpperCase() + file.document_type.slice(1)}
                      </Typography>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <FileUploaderComponent site_id="ALL" parent_folder_id={folderId} document_path={"path"} user_id={userId} idToken={idToken} />
            {selectedFile && (
              <DeleteFileComponent site_id="ALL" parent_folder_id={folderId} document_id={selectedFile.document_id} idToken={idToken} />
            )}
          </Box>
        </>
      )}
    </Container>
  );
};

export default SiteWideDocuments;

SiteWideDocuments.getLayout = function getLayout(page: React.ReactElement) {
  return <DashboardLayout>{page}</DashboardLayout>;
}
