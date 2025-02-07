
const API_BASE_URL = "";

export async function signupUser(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/signup`, {
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
  const response = await fetch(`${API_BASE_URL}/signin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  return response.json();
}

export async function signoutUser(token: string) {
  const response = await fetch(`${API_BASE_URL}/signout?user_token=${token}`, {
    method: "GET",
    headers: { "Authorization": `Bearer ${token}` },
  });

  return response.json();
}
