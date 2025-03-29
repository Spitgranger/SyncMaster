'use client';

import React, { useEffect, useState } from 'react';
import { Container, Box, Typography, TextField, Button, Modal, Box as ModalBox, CircularProgress } from '@mui/material';
import TopNavBar from '@/components/TopNavBar';
import EndVisit from '@/components/EndVisit';
import BottomNavBar from '@/components/BottomNavBar';
import PortalLayout from '@/components/layouts/PortalLayout';
import WorkIcon from '@mui/icons-material/Work';
import EditIcon from '@mui/icons-material/Edit';
import { Construction } from '@mui/icons-material';
import FileAttachmentComponent from '@/components/FileAttachmentComponent';
import FileUploaderComponent from '@/components/FileUploaderComponent';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '@/state/store';
import { getSiteVisitDetails, updateWorkDescription, updateWorkOrderNumber } from '@/state/site/siteSlice';


export default function JobsPage() {
  const { idToken, siteId } = useSelector((state: RootState) => state.user);
  const { entryTime, attachments, work_order, description } = useSelector((state: RootState) => state.site);
  const dispatch = useDispatch<AppDispatch>();
  console.log(siteId);
  console.log(entryTime);

  const [workOrderModalOpen, setWorkOrderModalOpen] = useState(false);
  const [newWorkOrder, setNewWorkOrder] = useState('');
  const [commentsModalOpen, setCommentsModalOpen] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [isSubmittingWorkOrder, setIsSubmittingWorkOrder] = useState(false); // Track work order submission progress
  const [isSubmittingComment, setIsSubmittingComment] = useState(false); // Track comment submission progress
  const [workOrderError, setWorkOrderError] = useState<string | null>(null); // Track work order errors
  const [commentsError, setCommentsError] = useState<string | null>(null); // Track comments errors

  const handleWorkOrderSubmit = () => {
    console.log('New Work Order:', newWorkOrder);
    setIsSubmittingWorkOrder(true);
    setWorkOrderError(null); // Clear any previous error
    dispatch(updateWorkOrderNumber({
      site_id: siteId, idToken: idToken, entryTime: entryTime, work_order: Number(newWorkOrder),
    })).then((response) => {
      setIsSubmittingWorkOrder(false);
      if (response.meta.requestStatus === "fulfilled") {
        console.log("Work order updated successfully");
        dispatch(getSiteVisitDetails({ site_id: siteId, idToken: idToken, entryTime: entryTime }));
        setWorkOrderModalOpen(false); // Close modal only on success
        setNewWorkOrder(''); // Clear the state after closing the modal
      } else {
        console.log("Failed to update work order");
        setWorkOrderError("An error occurred while updating the work order. Please try again.");
      }
    });
  };

  const handleWorkOrderModalClose = () => {
    setWorkOrderModalOpen(false);
    setNewWorkOrder('');
    setWorkOrderError(null); // Reset error state
  };

  const handleCommentsSubmit = () => {
    console.log('New Comment:', newComment);
    setIsSubmittingComment(true);
    setCommentsError(null); // Clear any previous error
    dispatch(updateWorkDescription({
      site_id: siteId, idToken: idToken, entryTime: entryTime,
      description: newComment
    })).then((response) => {
      setIsSubmittingComment(false);
      if (response.meta.requestStatus === "fulfilled") {
        console.log("Comment updated successfully");
        dispatch(getSiteVisitDetails({ site_id: siteId, idToken: idToken, entryTime: entryTime }));
        setCommentsModalOpen(false); // Close modal only on success
        setNewComment(''); // Clear the state after closing the modal
      } else {
        console.log("Failed to update comment");
        setCommentsError("An error occurred while updating the comment. Please try again.");
      }
    });
  };

  const handleCommentsModalClose = () => {
    setCommentsModalOpen(false);
    setNewComment('');
    setCommentsError(null); // Reset error state
  };

  const handleEditWorkOrder = () => {
    setNewWorkOrder(work_order ? work_order.toString() : ''); // Pre-populate with existing value
    setWorkOrderModalOpen(true);
  };

  const handleEditComments = () => {
    setNewComment(description || ''); // Pre-populate with existing value
    setCommentsModalOpen(true);
  };

  const handleAddWorkOrder = () => {
    setNewWorkOrder(''); // Clear the state for adding a new work order
    setWorkOrderModalOpen(true);
  };

  useEffect(() => {
    dispatch(getSiteVisitDetails({ site_id: siteId, idToken: idToken, entryTime: entryTime })).then((response) => {
      if (response.meta.requestStatus === "fulfilled") {
        console.log("Site visit details fetched successfully");
        console.log(response)

      } else {
        console.log("Failed to fetch site visit details");
        console.log(response);
      }
    })
  }, []);
  return (
    <>
      <Container
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: 3,
          mb: 10,
        }}
      >
        <Typography variant="h5" fontWeight={"bold"} sx={{ mb: 2 }}>
          Visit Details
        </Typography>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <Box sx={{ display: "flex", width: "100%", justifyContent: "space-between", mb: 2, p: 1, alignItems: "center" }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }} >
              <WorkIcon />
              <Typography ml={1} variant='body1'>Work Order Number</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }} >
              {work_order ? (
                <>
                  {work_order}
                  <EditIcon sx={{ ml: 1, cursor: 'pointer' }} onClick={handleEditWorkOrder} />
                </>
              ) : (
                <Button
                  variant="text"
                  size='small'
                  onClick={handleAddWorkOrder} // Use the new handler for adding
                >
                  + Add
                </Button>
              )}
            </Box>

            {/* <Typography variant='body1'>123456</Typography> */}
          </Box>

          <Box sx={{ display: "flex", flexDirection: 'column', width: "100%", mb: 2, p: 1, }}>
            <Box sx={{ display: "flex", width: "100%", justifyContent: "space-between", mb: 1, alignItems: "center" }}>
              <Typography variant='h6'>
                Comments
              </Typography>
              {description ? (
                <EditIcon sx={{ cursor: 'pointer' }} onClick={handleEditComments} />
              ) : (
                <Button
                  variant="text"
                  size='small'
                  onClick={() => setCommentsModalOpen(true)}
                >
                  + Add
                </Button>
              )}
            </Box>
            {description ? (
              <TextField
                multiline
                rows={4}
                variant="outlined"
                value={description}
                disabled
              />
            ) : null}
          </Box>

          <Box sx={{ display: "flex", flexDirection: 'column', width: "100%", mb: 1, p: 1, }}>
            <Typography variant='h6' sx={{ mb: 2 }}>
              Files
            </Typography>
            {attachments && attachments.length > 0 ? (
              <>
                <Typography variant='body1' color='black' sx={{ mb: 1 }}>
                  Uploaded Files
                </Typography>
                {attachments.map((attachment, index) => (
                  <FileAttachmentComponent key={attachment.name} attachment={attachment} />
                ))}
              </>
            ) : (
              <Typography variant='body1' color='textSecondary'>
                No attachments found
              </Typography>
            )}
          </Box>

          <Box display={"flex"} sx={{ justifyContent: "flex-end", width: "100%", p: 1, my: 3 }}>
            <FileUploaderComponent siteId={siteId} idToken={idToken} entryTime={entryTime} />
          </Box>
        </Box>

        <EndVisit siteId={siteId} idToken={idToken} entryTime={entryTime} />

      </Container>

      <Modal
        open={workOrderModalOpen}
        onClose={handleWorkOrderModalClose}
      >
        <ModalBox
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: 400,
            bgcolor: 'background.paper',
            boxShadow: 24,
            p: 4,
            borderRadius: 2,
          }}
        >
          <Typography variant="h6" mb={2}>
            Enter Work Order Number
          </Typography>
          {workOrderError && (
            <Typography color="error" mb={2}>
              {workOrderError}
            </Typography>
          )}
          <TextField
            fullWidth
            variant="outlined"
            value={newWorkOrder}
            onChange={(e) => setNewWorkOrder(e.target.value)}
            placeholder="Work Order Number"
            sx={{ mb: 2 }}
          />
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              onClick={handleWorkOrderSubmit}
              sx={{ mr: 1 }}
              disabled={isSubmittingWorkOrder}
              startIcon={isSubmittingWorkOrder && <CircularProgress size={20} />}
            >
              {isSubmittingWorkOrder ? "Submitting..." : "Submit"}
            </Button>
            <Button
              variant="outlined"
              onClick={handleWorkOrderModalClose}
              disabled={isSubmittingWorkOrder}
            >
              Cancel
            </Button>
          </Box>
        </ModalBox>
      </Modal>

      <Modal
        open={commentsModalOpen}
        onClose={handleCommentsModalClose}
      >
        <ModalBox
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: 400,
            bgcolor: 'background.paper',
            boxShadow: 24,
            p: 4,
            borderRadius: 2,
          }}
        >
          <Typography variant="h6" mb={2}>
            Enter Comments
          </Typography>
          {commentsError && (
            <Typography color="error" mb={2}>
              {commentsError}
            </Typography>
          )}
          <TextField
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Add your comments here"
            sx={{ mb: 2 }}
          />
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              onClick={handleCommentsSubmit}
              sx={{ mr: 1 }}
              disabled={isSubmittingComment}
              startIcon={isSubmittingComment && <CircularProgress size={20} />}
            >
              {isSubmittingComment ? "Submitting..." : "Submit"}
            </Button>
            <Button
              variant="outlined"
              onClick={handleCommentsModalClose}
              disabled={isSubmittingComment}
            >
              Cancel
            </Button>
          </Box>
        </ModalBox>
      </Modal>
    </>
  );
};

JobsPage.getLayout = function getLayout(page: React.ReactElement) {
  return <PortalLayout>{page}</PortalLayout>
}