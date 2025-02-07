import React, { useState } from "react";
import { Container, Typography, TextField, Button, IconButton, InputAdornment, Box } from "@mui/material";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import { signinUser } from "@/services/authService";
import { useRouter } from "next/router";
import { jwtDecode } from "jwt-decode"; // Install this: npm install jwt-decode

const SignInForm = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    try {
      const data = await signinUser(email, password);

      if (data.AccessToken) {
        console.log("Authentication response:", data);

        // ✅ Store Access Token
        localStorage.setItem("accessToken", data.AccessToken);

        // ✅ Decode and store User ID from IdToken
        if (data.IdToken) {
          const decodedToken: any = jwtDecode(data.IdToken);
          const userId = decodedToken?.sub; // "sub" typically contains the User ID

          if (userId) {
            localStorage.setItem("userId", userId);
            console.log("User ID stored:", userId);
          }
        }

        // ✅ Redirect after login
        window.location.href = "/acknowledgement";
      } else {
        console.log("Invalid email or password.");
      }
    } catch (err: any) {
      if (err.response?.status === 403) {
        console.log("Redirecting to reset password page...");
        router.push(`/reset-password?email=${encodeURIComponent(email)}`);
      } else {
        console.error("Login failed. Please check your credentials.");
      }
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8, px: 2 }}>
      <Typography variant="h5" fontWeight="bold" textAlign="center" gutterBottom>
        Identification Information
      </Typography>
      <Typography variant="body1" color="text.secondary" textAlign="center" gutterBottom>
        Please enter your email and password below.
      </Typography>

      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 4 }}>
        <TextField
          fullWidth
          label="Email"
          variant="filled"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          sx={{ mb: 3, backgroundColor: "#f5f5f5" }}
        />

        <TextField
          fullWidth
          label="Password"
          variant="filled"
          type={showPassword ? "text" : "password"}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          sx={{ mb: 4, backgroundColor: "#f5f5f5" }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        <Button type="submit" variant="contained" color="primary" fullWidth sx={{ py: 1.5 }}>
          CONTINUE
        </Button>
      </Box>
    </Container>
  );
};

export default SignInForm;
