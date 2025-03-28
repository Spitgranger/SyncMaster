"use client"
import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Container,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  TableSortLabel,
  Collapse,
  Button
} from '@mui/material';
import { getSiteVisits } from '@/state/site/siteVisitsSlice';
import { RootState, AppDispatch } from '@/state/store';

interface Attachment {
  name: string;
  url: string;
}

interface Visit {
  site_id: string;
  user_id: string;
  user_email: string;
  entry_time: string;
  exit_time: string;
  allowed_tracking: boolean;
  ack_status: boolean;
  work_order: number;
  description: string;
  on_site: boolean;
  employee_id: string;
  attachments: Attachment[];
}

type Order = 'asc' | 'desc';

// Helper to convert values for comparison
function getComparableValue(visit: Visit, orderBy: keyof Visit) {
  let value = visit[orderBy];
  if (orderBy === 'entry_time' || orderBy === 'exit_time') {
    return new Date(value as string).getTime();
  }
  if (typeof value === 'boolean') {
    return value ? 1 : 0;
  }
  return value;
}

function descendingComparator(a: Visit, b: Visit, orderBy: keyof Visit) {
  const valueA = getComparableValue(a, orderBy);
  const valueB = getComparableValue(b, orderBy);
  if (valueB < valueA) {
    return -1;
  }
  if (valueB > valueA) {
    return 1;
  }
  return 0;
}

function getComparator(order: Order, orderBy: keyof Visit) {
  return order === 'desc'
    ? (a: Visit, b: Visit) => descendingComparator(a, b, orderBy)
    : (a: Visit, b: Visit) => -descendingComparator(a, b, orderBy);
}

function stableSort(array: Visit[], comparator: (a: Visit, b: Visit) => number) {
  const stabilizedThis = array.map((el, index) => [el, index] as [Visit, number]);
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) return order;
    return a[1] - b[1];
  });
  return stabilizedThis.map((el) => el[0]);
}

// Updated columns array to include user_email and employee_id
const columns = [
  { id: 'site_id', label: 'Site ID' },
  { id: 'user_id', label: 'User ID' },
  { id: 'user_email', label: 'User Email' },
  { id: 'employee_id', label: 'Employee ID' },
  { id: 'entry_time', label: 'Entry Time' },
  { id: 'exit_time', label: 'Exit Time' },
  { id: 'allowed_tracking', label: 'Allowed Tracking' },
  { id: 'ack_status', label: 'Acknowledgment Status' },
  { id: 'work_order', label: 'Work Order' },
  { id: 'on_site', label: 'On Site' },
];

const SiteVisitsTable: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { idToken } = useSelector((state: RootState) => state.user);
  const { visits, isLoading } = useSelector((state: RootState) => state.siteVisits);

  const [order, setOrder] = useState<Order>('asc');
  const [orderBy, setOrderBy] = useState<keyof Visit>('site_id');
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  useEffect(() => {
    if (!idToken) {
      console.error('Authentication token not found. Please sign in.');
      return;
    }
    dispatch(getSiteVisits({ params: {}, idToken }));
  }, [dispatch, idToken]);

  const handleRequestSort = (property: keyof Visit) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleRowClick = (index: number) => {
    setExpandedRow(expandedRow === index ? null : index);
  };

  const sortedVisits = visits ? stableSort(visits, getComparator(order, orderBy)) : [];

  const handleExport = () => {
    if (!sortedVisits || sortedVisits.length === 0) return;

    const exportData = sortedVisits.map(visit => ({
      "Site ID": visit.site_id,
      "User ID": visit.user_id,
      "User Email": visit.user_email,
      "Employee ID": visit.employee_id,
      "Entry Time": new Date(visit.entry_time).toLocaleString(),
      "Exit Time": visit.exit_time ? new Date(visit.exit_time).toLocaleString() : 'N/A',
      "Allowed Tracking": visit.allowed_tracking ? 'Yes' : 'No',
      "Acknowledgment Status": visit.ack_status ? 'Yes' : 'No',
      "Work Order": visit.work_order,
      "On Site": visit.on_site ? 'Yes' : 'No',
      "Description": visit.description,
      "Attachments": visit.attachments && visit.attachments.length > 0 ? visit.attachments.map(a => a.name).join(', ') : ''
    }));

    // Convert the export data to a CSV string
    const headers = Object.keys(exportData[0]);
    const csvRows = [];
    // Add header row
    csvRows.push(headers.join(','));
    // Add data rows
    for (const row of exportData) {
      const values = headers.map(header => {
        const escaped = String(row[header]).replace(/"/g, '""');
        return `"${escaped}"`;
      });
      csvRows.push(values.join(','));
    }
    const csvString = csvRows.join('\n');

    // Create a Blob from the CSV string and trigger a download
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'site_visits.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <Container maxWidth={false} disableGutters sx={{ mt: 0, px: 2 }}>
        <Typography variant="h5" fontWeight="bold" textAlign="left" gutterBottom>
          Site Visits
        </Typography>
        <Button variant="contained" onClick={handleExport}>
          Export to CSV
        </Button>
      </Container>
      <Container maxWidth={false} disableGutters sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 6, px: 2 }}>
        {isLoading ? (
          <CircularProgress />
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  {columns.map((column) => (
                    <TableCell key={column.id}>
                      <TableSortLabel
                        active={orderBy === column.id}
                        direction={orderBy === column.id ? order : 'asc'}
                        onClick={() => handleRequestSort(column.id as keyof Visit)}
                      >
                        <strong>{column.label}</strong>
                      </TableSortLabel>
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {sortedVisits && sortedVisits.length > 0 ? (
                  sortedVisits.map((visit, index) => (
                    <React.Fragment key={index}>
                      <TableRow
                        hover
                        onClick={() => handleRowClick(index)}
                        style={{ cursor: 'pointer' }}
                      >
                        <TableCell>{visit.site_id}</TableCell>
                        <TableCell>{visit.user_id}</TableCell>
                        <TableCell>{visit.user_email}</TableCell>
                        <TableCell>{visit.employee_id}</TableCell>
                        <TableCell>{new Date(visit.entry_time).toLocaleString()}</TableCell>
                        <TableCell>{visit.exit_time ? new Date(visit.exit_time).toLocaleString() : 'N/A'}</TableCell>
                        <TableCell>{visit.allowed_tracking ? 'Yes' : 'No'}</TableCell>
                        <TableCell>{visit.ack_status ? 'Yes' : 'No'}</TableCell>
                        <TableCell>{visit.work_order}</TableCell>
                        <TableCell>{visit.on_site ? 'Yes' : 'No'}</TableCell>
                      </TableRow>
                      {expandedRow === index && (
                        <TableRow>
                          <TableCell colSpan={columns.length}>
                            <Collapse in={expandedRow === index} timeout="auto" unmountOnExit>
                              <Container sx={{ py: 2 }}>
                                <Typography variant="subtitle1" gutterBottom>
                                  Description:
                                </Typography>
                                <Typography variant="body2" gutterBottom>
                                  {visit.description}
                                </Typography>
                                <Typography variant="subtitle1" gutterBottom>
                                  Attachments:
                                </Typography>
                                {visit.attachments && visit.attachments.length > 0 ? (
                                  visit.attachments.map((attachment, i) => (
                                    <div key={i}>
                                      <a href={attachment.url} target="_blank" rel="noopener noreferrer">
                                        {attachment.name}
                                      </a>
                                    </div>
                                  ))
                                ) : (
                                  <Typography variant="body2">No attachments</Typography>
                                )}
                              </Container>
                            </Collapse>
                          </TableCell>
                        </TableRow>
                      )}
                    </React.Fragment>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={columns.length} align="center">
                      No site visits found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Container>
    </>
  );
};

export default SiteVisitsTable;
