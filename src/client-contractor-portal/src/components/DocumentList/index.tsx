import React, { useState, useEffect } from 'react';
import { List, ListItemButton, ListItemIcon, ListItemText, Collapse, Typography, Container } from '@mui/material';
import FolderIcon from '@mui/icons-material/Folder';
import DescriptionIcon from '@mui/icons-material/Description';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import { getFiles } from '@/services/documentService';

interface File {
  name: string;
  url: string;
}

interface Folder {
  name: string;
  files: File[];
}

const DocumentList: React.FC = () => {
  const [documents, setDocuments] = useState<Folder[]>([]);
  const [openFolders, setOpenFolders] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const loadDocuments = async () => {
      try {
        const files = await getFiles();
        const groupedFiles: Record<string, File[]> = {};

        files.forEach((file: any) => {
          const folderName = file.document_path.split('/').slice(-2, -1)[0] || 'General';
          if (!groupedFiles[folderName]) {
            groupedFiles[folderName] = [];
          }
          groupedFiles[folderName].push({
            name: file.document_path.split('/').pop(),
            url: file.s3_presigned_get,
          });
        });

        const formattedDocuments = Object.entries(groupedFiles).map(([name, files]) => ({ name, files }));
        setDocuments(formattedDocuments);
      } catch (error) {
        console.error('Failed to load documents', error);
      }
    };

    loadDocuments();
  }, []);

  const handleToggleFolder = (folderName: string) => {
    setOpenFolders((prev) => ({
      ...prev,
      [folderName]: !prev[folderName],
    }));
  };

  return (
    <Container sx={{ mt: 4, px: 2 }}>
      <Typography variant="h5" fontWeight="bold" textAlign="center" gutterBottom>
        Documents
      </Typography>
      <List>
        {documents.length > 0 ? (
          documents.map((folder, index) => (
            <React.Fragment key={index}>
              <ListItemButton onClick={() => handleToggleFolder(folder.name)}>
                <ListItemIcon>
                  <FolderIcon />
                </ListItemIcon>
                <ListItemText primary={folder.name} />
                {openFolders[folder.name] ? <ExpandLess /> : <ExpandMore />}
              </ListItemButton>
              <Collapse in={openFolders[folder.name]} timeout="auto" unmountOnExit>
                <List disablePadding>
                  {folder.files.map((file, fileIndex) => (
                    <ListItemButton key={fileIndex} sx={{ pl: 4 }} component="a" href={file.url} target="_blank">
                      <ListItemIcon>
                        <DescriptionIcon />
                      </ListItemIcon>
                      <ListItemText primary={file.name} />
                    </ListItemButton>
                  ))}
                </List>
              </Collapse>
            </React.Fragment>
          ))
        ) : (
          <Typography variant="body1" color="text.secondary" textAlign="center">
            No documents available
          </Typography>
        )}
      </List>
    </Container>
  );
};

export default DocumentList;
