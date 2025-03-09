import React from "react";
import { Button, Typography, Container } from "@mui/material";
import { useRouter } from "next/router";
import { exitSite } from "@/services/siteService"; 

interface EndVisitProps {
  onEndVisit?: () => void;
}

const EndVisit: React.FC<EndVisitProps> = ({ onEndVisit }) => {
  const router = useRouter();

  const handleEndVisit = async () => {
    console.log("Ending visit...");

    const userId = localStorage.getItem("userId"); 
    if (!userId) {
      console.error("User ID not found in localStorage!");
      return;
    }

    const IdToken = localStorage.getItem("IdToken"); 
    if (!IdToken) {
      console.error("User ID not found in localStorage!");
      return;
    }

    try {
      await exitSite(userId, IdToken);
      console.log("Exited site successfully");

      // Clear user-related data
      localStorage.removeItem("userId");
      localStorage.removeItem("accessToken");

      // Navigate back to home
      router.push("/");

      // Call the optional onEndVisit callback if provided
      if (onEndVisit) {
        onEndVisit();
      }
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
