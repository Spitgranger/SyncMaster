import { useEffect } from "react";
import { useRouter } from "next/router";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    router.push("/login"); // Redirect to the login page on load
  }, [router]);

  return null; // No content needed as the page redirects immediately
}
