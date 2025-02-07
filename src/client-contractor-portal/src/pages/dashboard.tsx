import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/router";
import { useEffect } from "react";

const Dashboard = () => {
  const isAuthenticated = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated === false) {
      router.push("/"); // Redirect to login if not authenticated
    }
  }, [isAuthenticated, router]);

  if (isAuthenticated === null) return <p>Loading...</p>;

  return <h1>Welcome to the Dashboard</h1>;
};

export default Dashboard;
