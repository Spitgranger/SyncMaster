"use client";

import React, { useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/router";
import { Container } from "@mui/material";
import AcknowledgmentForm from "@/components/AcknowledgementForm";
import NonNavbarLogo from "@/components/NonNavbarLogo";
import { AppDispatch } from "@/state/store";
import { useDispatch, useSelector } from "react-redux";
import { getAcknowledgementDocuments } from "@/state/document/documentSlice";
import { RootState } from "@/state/store";
import { sign } from "crypto";
import { signOutUser } from "@/state/user/userSlice";
import { enterSite } from "@/state/site/siteSlice";

const AcknowledgementPage = () => {
  const isAuthenticated = useAuth();
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();
  const id = router.query.id as string | undefined;
  const { idToken } = useSelector((state: RootState) => state.user);
  const { isLoading, acknowledgementDocuments } = useSelector((state: RootState) => state.document);
  const { isEnteringOrExitingSite } = useSelector((state: RootState) => state.site);

  const fakeDocuments = [
    { name: "HSE Document", url: "https://web.hamilton/entry-exit-protocols" },
    { name: "Fire Protocol Document", url: "https://web.hamilton/entry-exit-protocols" },
  ];

  const handleProceed = async ({ acknowledgedAll, hasCompletedTraining, accompaniedByEmployee, employeeID }:
    {
      acknowledgedAll: boolean; hasCompletedTraining: boolean;
      accompaniedByEmployee: boolean; employeeID: string | null
    }) => {
    console.log("Proceeding with the following data:", {
      acknowledgedAll,
      hasCompletedTraining,
      accompaniedByEmployee,
      employeeID,
    });

    const proceedAction = () => {
      dispatch(enterSite({
        site_id: id,
        idToken: idToken,
        allowed_tracking: true,
        ack_status: acknowledgedAll,
        on_site: true,
        employee_id: employeeID
      })).then((response) => {
        if (response.meta.requestStatus === "fulfilled") {
          console.log("Entered site successfully");
          router.push("/portal/jobs");
        } else {
          console.error("Failed to enter site");
        }
      });
    };

    if (!hasCompletedTraining && !accompaniedByEmployee) {
      dispatch(signOutUser()).then((response) => {
        console.log("Signing out...");
        if (response.meta.requestStatus === "fulfilled") {
          console.log("Token revoked successfully");
        } else {
          console.log("Failed to revoke token");
        }
        localStorage.removeItem("accessToken");
        localStorage.removeItem("idToken");
        router.push("/login");
      });
    } else {
      proceedAction();
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
