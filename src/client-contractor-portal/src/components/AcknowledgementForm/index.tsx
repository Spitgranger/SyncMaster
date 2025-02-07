import React, { useState } from 'react';
import { Container, Typography, Checkbox, FormControlLabel, Button, Box, Link } from '@mui/material';

interface Document {
  name: string;
  url: string;
}

interface AcknowledgmentFormProps {
  documents: Document[];
  onProceed: () => void;
}

const AcknowledgmentForm: React.FC<AcknowledgmentFormProps> = ({ documents = [], onProceed }) => {
  const [acknowledged, setAcknowledged] = useState<Record<string, boolean>>(
    documents.reduce((acc, doc) => ({ ...acc, [doc.name]: false }), {})
  );

  const handleCheckboxChange = (docName: string) => {
    setAcknowledged((prev) => ({ ...prev, [docName]: !prev[docName] }));
  };

  const allAcknowledged = Object.values(acknowledged).every((value) => value);

  return (
    <Container sx={{ mt: 4, px: 2, textAlign: 'center' }}>
      <Typography variant="h5" fontWeight="bold" gutterBottom>
        Acknowledgment
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        The following document(s) must be read before accessing the site.
      </Typography>
      {documents.length > 0 ? (
        documents.map((doc) => (
          <Box key={doc.name} sx={{ my: 2, textAlign: 'left' }}>
            <Typography variant="h6">{doc.name}</Typography>
            <Typography variant="body2">
              Link: <Link href={doc.url} target="_blank" rel="noopener noreferrer">{doc.url}</Link>
            </Typography>
            <FormControlLabel
              control={<Checkbox checked={acknowledged[doc.name]} onChange={() => handleCheckboxChange(doc.name)} />}
              label="I acknowledge that I have read this document"
            />
          </Box>
        ))
      ) : (
        <Typography variant="body1" color="text.secondary">
          No documents available
        </Typography>
      )}
      <Button
        variant="contained"
        color="primary"
        disabled={!allAcknowledged}
        onClick={onProceed}
        sx={{ mt: 3 }}
      >
        CONTINUE
      </Button>
    </Container>
  );
};

export default AcknowledgmentForm;
