"use client";

import React, { useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/router";
import { Container } from "@mui/material";
import AcknowledgmentForm from "@/components/AcknowledgementForm";
import NonNavbarLogo from "@/components/NonNavbarLogo";
import { enterSite } from "@/services/siteService";

const AcknowledgementPage = () => {
  const isAuthenticated = useAuth();
  const router = useRouter();

  const fakeDocuments = [
    { name: "HSE Document", url: "https://web.hamilton/entry-exit-protocols" },
    { name: "Fire Protocol Document", url: "https://web.hamilton/entry-exit-protocols" },
  ];

  const handleProceed = async () => {
    console.log("Acknowledged and proceeding...");

    const userId = localStorage.getItem("userId");
    if (!userId) {
      console.error("User ID not found in localStorage!");
      return;
    }

    try {
      const response = await enterSite(userId);
      console.log("Entered site successfully:", response);
      router.push("/jobs");
    } catch (err) {
      console.error("Failed to enter site:", err);
    }
  };

  useEffect(() => {
    if (isAuthenticated === false) {
      router.push("/");
    }
  }, [isAuthenticated, router]);

  if (isAuthenticated === null) return <p>Loading...</p>;

  return (
    <Container
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        py: 4,
      }}
    >
      <NonNavbarLogo />
      <AcknowledgmentForm documents={fakeDocuments} onProceed={handleProceed} />
    </Container>
  );
};

export default AcknowledgementPage;
