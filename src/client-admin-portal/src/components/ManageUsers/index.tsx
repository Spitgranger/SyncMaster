// components/ManageUsersTable.tsx
import React, { useState, useEffect } from 'react';
import { Container, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button } from '@mui/material';
import { useRouter } from 'next/router';
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
  const router = useRouter();

  useEffect(() => {
    const fetchUsers = async () => {
      // Retrieve the IdToken from localStorage.
      const idToken = localStorage.getItem('idToken');
      if (!idToken) {
        console.error("Authentication token not found. Please sign in.");
        // Optionally, you can redirect the user to the sign-in page here.
        return;
      }
      
      try {
        // Pass an empty attributes object and the idToken to getUsers.
        const fetchedUsers = await getUsers({}, idToken);
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
      <Button variant="contained" color="primary" sx={{ mb: 2 }} onClick={() => router.push('/dashboard/adduser')}>
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
