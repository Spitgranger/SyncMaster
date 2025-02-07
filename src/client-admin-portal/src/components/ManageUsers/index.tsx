// components/ManageUsersTable.tsx
import React, { useState, useEffect } from 'react';
import { Container, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button } from '@mui/material';
import { getUsers } from '@/services/userService';

interface User {
  name: string;
  email: string;
  role: string;
}

const ManageUsersTable: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const fetchedUsers = await getUsers({}); // Fetch all users
        const formattedUsers = fetchedUsers.map((user: any) => ({
          name: user.name || "Unknown",
          email: user.email,
          role: user["custom:role"] || "Unknown",
        }));
        setUsers(formattedUsers);
      } catch (error) {
        console.error("Failed to fetch users", error);
      }
    };

    fetchUsers();
  }, []);

  return (
    <Container sx={{ mt: 4, px: 2 }}>
      <Typography variant="h5" fontWeight="bold" textAlign="left" gutterBottom>
        Manage Users
      </Typography>
      <Button variant="contained" color="primary" sx={{ mb: 2 }}>
        + ADD NEW USER
      </Button>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Name</strong></TableCell>
              <TableCell><strong>Email</strong></TableCell>
              <TableCell><strong>Role</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.length > 0 ? (
              users.map((user, index) => (
                <TableRow key={index}>
                  <TableCell>{user.name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.role}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={3} align="center">No users found</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default ManageUsersTable;
