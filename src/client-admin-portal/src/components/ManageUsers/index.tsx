"use client";
import React, { useEffect, useState } from 'react';
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
  Button,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  IconButton,
  TableSortLabel
} from '@mui/material';
import { useRouter } from 'next/router';
import { useDispatch, useSelector } from 'react-redux';
import { getUsers, updateUser } from '@/state/user/userManagementSlice';
import { RootState, AppDispatch } from '@/state/store';
import EditIcon from '@mui/icons-material/Edit';

interface User {
  name: string;
  email: string;
  role: string;
  company: string;
  status: string;
}

const ManageUsersTable: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const router = useRouter();
  const { users, loading, error } = useSelector((state: RootState) => state.userManagement);
  const { idToken } = useSelector((state: RootState) => state.user);

  // Local state for edit dialog and form values.
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [formValues, setFormValues] = useState({ name: '', company: '', role: '' });
  // Local state for sorting.
  const [sortField, setSortField] = useState<keyof User | ''>('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  useEffect(() => {
    if (!idToken) {
      console.error("Authentication token not found. Please sign in.");
      return;
    }
    dispatch(getUsers({}));
  }, [dispatch, idToken]);

  // Format the raw user data for display.
  const formattedUsers: User[] = users.map((user: any) => {
    const attributes = (user.Attributes || []).reduce((acc: any, attr: any) => {
      acc[attr.Name] = attr.Value;
      return acc;
    }, {});

    const statusMapping: Record<string, string> = {
      CONFIRMED: "Confirmed",
      UNCONFIRMED: "Pending",
      FORCE_CHANGE_PASSWORD: "Requires Password Change"
    };

    return {
      name: attributes["name"] || "N/A",
      email: attributes["email"] || "N/A",
      role: attributes["custom:role"] || "N/A",
      company: attributes["custom:company"] || "N/A",
      status: statusMapping[user.UserStatus] || user.UserStatus || "N/A",
    };
  });

  // Handle sorting logic.
  const handleSort = (field: keyof User) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const sortedUsers = React.useMemo(() => {
    if (!sortField) return formattedUsers;
    return [...formattedUsers].sort((a, b) => {
      const aVal = a[sortField] || '';
      const bVal = b[sortField] || '';
      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }, [formattedUsers, sortField, sortOrder]);

  // When the pen icon is clicked, open the edit dialog and populate form values.
  const handleEditClick = (user: User) => {
    setSelectedUser(user);
    setFormValues({ name: user.name, company: user.company, role: user.role });
    setEditDialogOpen(true);
  };

  // Update form values on change.
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormValues(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleDialogClose = () => {
    setEditDialogOpen(false);
    setSelectedUser(null);
  };

  // Dispatch the updateUser thunk with the new data and refresh the list.
  const handleUpdateUser = async () => {
    if (!selectedUser) return;
    try {
      await dispatch(updateUser({
        email: selectedUser.email,
        attributes: {
          name: formValues.name,
          "custom:company": formValues.company,
          "custom:role": formValues.role as "admin" | "contractor" | "employee"
        }
      })).unwrap();
      await dispatch(getUsers({}));
      handleDialogClose();
    } catch (error) {
      console.error("Failed to update user:", error);
    }
  };

  return (
    <>
      <Container sx={{ mt: 4, px: 2 }}>
        <Typography variant="h5" fontWeight="bold" textAlign="left" gutterBottom>
          Manage Users
        </Typography>
        <Button variant="contained" color="primary" sx={{ mb: 2 }} onClick={() => router.push('/dashboard/adduser')}>
          + ADD NEW USER
        </Button>
      </Container>
      <Container sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 6 }}>
        {loading ? (
          <CircularProgress />
        ) : error ? (
          <Typography color="error">{error}</Typography>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    <TableSortLabel
                      active={sortField === 'name'}
                      direction={sortField === 'name' ? sortOrder : 'asc'}
                      onClick={() => handleSort('name')}
                    >
                      <strong>Name</strong>
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={sortField === 'email'}
                      direction={sortField === 'email' ? sortOrder : 'asc'}
                      onClick={() => handleSort('email')}
                    >
                      <strong>Email</strong>
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={sortField === 'role'}
                      direction={sortField === 'role' ? sortOrder : 'asc'}
                      onClick={() => handleSort('role')}
                    >
                      <strong>Role</strong>
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={sortField === 'company'}
                      direction={sortField === 'company' ? sortOrder : 'asc'}
                      onClick={() => handleSort('company')}
                    >
                      <strong>Company</strong>
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={sortField === 'status'}
                      direction={sortField === 'status' ? sortOrder : 'asc'}
                      onClick={() => handleSort('status')}
                    >
                      <strong>Status</strong>
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <strong>Actions</strong>
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sortedUsers.length > 0 ? (
                  sortedUsers.map((user, index) => (
                    <TableRow key={index}>
                      <TableCell>{user.name}</TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>{user.role}</TableCell>
                      <TableCell>{user.company}</TableCell>
                      <TableCell>{user.status}</TableCell>
                      <TableCell>
                        <IconButton onClick={() => handleEditClick(user)}>
                          <EditIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={6} align="center">No users found</TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Container>
      <Dialog open={editDialogOpen} onClose={handleDialogClose}>
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            label="Name"
            name="name"
            fullWidth
            value={formValues.name}
            onChange={handleInputChange}
          />
          <TextField
            margin="dense"
            label="Company"
            name="company"
            fullWidth
            value={formValues.company}
            onChange={handleInputChange}
          />
          <TextField
            margin="dense"
            label="Role"
            name="role"
            fullWidth
            select
            value={formValues.role}
            onChange={handleInputChange}
          >
            <MenuItem value="admin">admin</MenuItem>
            <MenuItem value="contractor">contractor</MenuItem>
            <MenuItem value="employee">employee</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Cancel</Button>
          <Button onClick={handleUpdateUser} variant="contained" color="primary">
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ManageUsersTable;
