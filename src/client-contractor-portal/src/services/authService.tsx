export async function signupUser(email: string, password: string) {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/signup`, {
    method: "POST",
    headers: { 
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ email, password }),
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to sign in");
  }

  return response.json();
}

export async function resetPassword(email: string, password: string, newPassword: string) {
    try {
      // ✅ Get user location before making the request
      const location = await getUserLocation();
      console.log("User Location:", location);
  
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/reset-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          password,
          new_password: newPassword, // ✅ Correct field name
          location, // ✅ Include location in the request
        }),
      });
  
      if (!response.ok) {
        throw new Error(`Failed to reset password: ${response.statusText}`);
      }
  
      return response.json();
    } catch (err) {
      console.error("Error resetting password:", err);
      throw err;
    }
  }

export async function signinUser(email: string, password: string) {
    try {
      const location = await getUserLocation();
      console.log(location);
  
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/signin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, location }),
      });
  
      if (!response.ok) {
        throw { response }; // ✅ Ensure the correct error structure for catching 403
      }
  
      return response.json();
    } catch (err) {
      console.error("Error signing in:", err);
      throw err; // ✅ Ensure error is caught in `SignInForm.tsx`
    }
  }
  
  // Function to get user location
  async function getUserLocation(): Promise<[number, number]> {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject("Geolocation is not supported by this browser.");
      }
      navigator.geolocation.getCurrentPosition(
        (position) => resolve([position.coords.latitude, position.coords.longitude]),
        (error) => reject("Failed to retrieve location: " + error.message)
      );
    });
  }

export async function signoutUser(token: string) {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/signout?user_token=${token}`, {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` },
  });

  return response.json();
}
