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

export async function signinUser(email: string, password: string) {
    try {
      // Get user location from the browser
      const location = await getUserLocation();
      console.log(location)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/signin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          password,
          location,  // Sending GPS coordinates
        }),
      });
      
      if (!response.ok) {
        throw new Error("Failed to sign in");
      }
  
      return response.json();
    } catch (error) {
      console.error("Error signing in:", error);
      throw error;
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
