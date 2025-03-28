import React, { useState } from 'react';
import { Container, Typography, Checkbox, FormControlLabel, Button, Box, Link, Radio, RadioGroup, FormControl, FormLabel } from '@mui/material';

interface Document {
  document_id: string;
  document_name: string;
  s3_presigned_get: string;
}

interface AcknowledgmentFormProps {
  documents: Document[];
  onProceed: () => void;
}

const truncateText = (text: string, maxLength: number) => {
  return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
};

const AcknowledgmentForm: React.FC<AcknowledgmentFormProps> = ({ documents = [], onProceed }) => {
  const sortedDocuments = [...documents].sort((a, b) => a.document_name.localeCompare(b.document_name));

  const [acknowledged, setAcknowledged] = useState<Record<string, boolean>>(
    sortedDocuments.reduce((acc, doc) => ({ ...acc, [doc.document_id]: false }), {})
  );

  const [trainingCompleted, setTrainingCompleted] = useState<string | null>(null);
  const [accompaniedByEmployee, setAccompaniedByEmployee] = useState<string | null>(null);

  const handleCheckboxChange = (docId: string) => {
    setAcknowledged((prev) => ({ ...prev, [docId]: !prev[docId] }));
  };

  const handleTrainingChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setTrainingCompleted(event.target.value);
    if (event.target.value === "yes") {
      setAccompaniedByEmployee(null); // Reset the second question if "yes" is selected
    }
  };

  const handleAccompaniedChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setAccompaniedByEmployee(event.target.value);
  };

  const allAcknowledged = Object.values(acknowledged).every((value) => value);
  const canProceed =
    allAcknowledged &&
    trainingCompleted !== null &&
    (trainingCompleted === "yes" || (trainingCompleted === "no" && accompaniedByEmployee !== null));

  return (
    <Container sx={{ mt: 4, px: 2, textAlign: 'center' }}>
      <Typography variant="h5" fontWeight="bold" gutterBottom>
        Acknowledgment
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        The following document(s) must be read before accessing the site.
      </Typography>
      {sortedDocuments.length > 0 ? (
        sortedDocuments.map((doc) => (
          <Box key={doc.document_id} sx={{ my: 2, textAlign: 'left' }}>
            <Typography variant="h6">{truncateText(doc.document_name, 30)}</Typography>
            <Typography variant="body2">
              Link: <Link href={doc.s3_presigned_get} target="_blank" rel="noopener noreferrer">
                {truncateText(doc.s3_presigned_get, 40)}
              </Link>
            </Typography>
            <FormControlLabel
              control={<Checkbox checked={acknowledged[doc.document_id]} onChange={() => handleCheckboxChange(doc.document_id)} />}
              label="I acknowledge that I have read this document"
            />
          </Box>
        ))
      ) : (
        <Typography variant="body1" color="text.secondary">
          No documents available
        </Typography>
      )}
      <Typography variant="body1" color="text.secondary" gutterBottom sx={{ mt: 4 }}>
        The following training(s) must be completed before accessing the site.
      </Typography>

      <Box textAlign={'left'}>
        <FormControl component="fieldset" sx={{ mt: 2, textAlign: 'left' }}>
          <FormLabel component="legend"><Typography variant='body2' color='black'>Have you completed the Annual H&S Training?</Typography></FormLabel>
          <RadioGroup value={trainingCompleted} onChange={handleTrainingChange}>
            <FormControlLabel value="yes" control={<Radio />} label="Yes" />
            <FormControlLabel value="no" control={<Radio />} label="No" />
          </RadioGroup>
        </FormControl>
        {trainingCompleted === "no" && (
          <FormControl component="fieldset" sx={{ mt: 2, textAlign: 'left' }}>
            <FormLabel component="legend"><Typography variant='body2' color='black'>Are you accompanied by a City Employee?</Typography></FormLabel>
            <RadioGroup value={accompaniedByEmployee} onChange={handleAccompaniedChange}>
              <FormControlLabel value="yes" control={<Radio />} label="Yes" />
              <FormControlLabel value="no" control={<Radio />} label="No" />
            </RadioGroup>
          </FormControl>
        )}
      </Box>
      <Button
        variant="contained"
        color="primary"
        disabled={!canProceed}
        onClick={onProceed}
        sx={{ mt: 3 }}
      >
        CONTINUE
      </Button>
    </Container>
  );
};

export default AcknowledgmentForm;
