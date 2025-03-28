"use client";

import React, { useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/router";
import { Container } from "@mui/material";
import AcknowledgmentForm from "@/components/AcknowledgementForm";
import NonNavbarLogo from "@/components/NonNavbarLogo";
import { enterSite } from "@/services/siteService";
import { AppDispatch } from "@/state/store";
import { useDispatch, useSelector } from "react-redux";
import { getAcknowledgementDocuments } from "@/state/document/documentSlice";
import { RootState } from "@/state/store";

const AcknowledgementPage = () => {
  const isAuthenticated = useAuth();
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();
  const { id } = router.query;
  const { idToken } = useSelector((state: RootState) => state.user);
  const { isLoading, acknowledgementDocuments } = useSelector((state: RootState) => state.document);

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

    const IdToken = localStorage.getItem("IdToken");
    if (!IdToken) {
      console.error("User ID not found in localStorage!");
      return;
    }

    try {
      const response = await enterSite(userId, IdToken);
      console.log("Entered site successfully:", response);
      router.push("/jobs");
    } catch (err) {
      console.error("Failed to enter site:", err);
    }
  };

  useEffect(() => {
    console.log(id);

    if (id) {
      dispatch(getAcknowledgementDocuments({ site_id: id, idToken: idToken })).then((response) => {
        if (response.meta.requestStatus === "fulfilled") {
          console.log("Acknowledgement documents fetched successfully");
        } else {
          console.error("Failed to fetch acknowledgement documents");
        }
      });
    }
  }, [router]);

  if (isAuthenticated === null) return <p>Loading...</p>;

  return (
    isLoading || !acknowledgementDocuments ? (
      <p>Loading...</p>
    ) : (
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
        <AcknowledgmentForm documents={acknowledgementDocuments} onProceed={handleProceed} />
      </Container>
    )
  );
};

export default AcknowledgementPage;
