// components/ManageUsersTable.tsx
import React, { useState, useEffect } from 'react';
import { Container, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button } from '@mui/material';
import { getUsers } from '@/services/userService';

interface User {
  name: string;
  email: string;
  role: string;
  company: string;
  status: string;
}

const ManageUsersTable: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const fetchedUsers = await getUsers({}); // Fetch all users
        const formattedUsers = fetchedUsers.map((user: any) => {
          const attributes = user.Attributes.reduce((acc: any, attr: any) => {
            acc[attr.Name] = attr.Value;
            return acc;
          }, {});
          return {
            name: attributes["name"] || "N/A",
            email: attributes["email"] || "N/A",
            role: attributes["custom:role"] || "N/A",
            company: attributes["custom:company"] || "N/A",
            status: user.UserStatus || "N/A",
          };
        });
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
              <TableCell><strong>Company</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.length > 0 ? (
              users.map((user, index) => (
                <TableRow key={index}>
                  <TableCell>{user.name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.role}</TableCell>
                  <TableCell>{user.company}</TableCell>
                  <TableCell>{user.status}</TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} align="center">No users found</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default ManageUsersTable;