import React from "react";
import { Button, Typography, Container } from "@mui/material";
import { useRouter } from "next/router";
import { exitSite } from "@/services/siteService"; 

const EndVisit: React.FC = () => {
  const router = useRouter();

  const handleEndVisit = async () => {
    console.log("Ending visit...");

    const userId = localStorage.getItem("userId"); 
    if (!userId) {
      console.error("User ID not found in localStorage!");
      return;
    }

    try {
      await exitSite(userId);
      console.log("Exited site successfully");

      
      localStorage.removeItem("userId");
      localStorage.removeItem("accessToken");

      
      router.push("/");
    } catch (err) {
      console.error("Failed to exit site:", err);
    }
  };

  return (
    <Container
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        px: 3,
      }}
    >
      <Typography variant="h6" color="text.secondary" textAlign="center" gutterBottom>
        Kindly remember to end your session before leaving the site.
      </Typography>
      <Button
        variant="contained"
        color="success"
        sx={{
          mt: 2,
          px: 6,
          py: 1.5,
          boxShadow: 2,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          gap: 1,
        }}
        onClick={handleEndVisit}
      >
        End Visit
      </Button>
    </Container>
  );
};

export default EndVisit;
