const API_BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;

// Create User
export async function createUser(email: string, role: "admin" | "contractor" | "employee", company: string, name: string, IdToken: string) {
  const response = await fetch(`${API_BASE_URL}/protected/users/create_user`, {
    method: "POST",
    headers: { 
      "Authorization": `${IdToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email,
      attributes: {
        "custom:role": role,
        "custom:company": company,
        name,
      },
    }),
  });
  if (!response.ok) {
    throw new Error("Failed to create user");
  }
  return await response.json();
}

// Sign In User
export async function signInUser(email: string, password: string, newPassword?: string, location?: [number, number]) {
  const response = await fetch(`${API_BASE_URL}/unprotected/auth/signin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, new_password: newPassword, location }),
  });
  if (!response.ok) {
    throw new Error("Failed to sign in");
  }
  return await response.json();
}

// Get Users
export async function getUsers(attributes: Record<string, string>, IdToken: string) {
  const response = await fetch(`${API_BASE_URL}/protected/users/get_users`, {
    method: "POST",
    headers: { 
      "Authorization": `${IdToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ attributes }),
  });
  if (!response.ok) {
    throw new Error("Failed to fetch users");
  }
  console.log(response.json)
  return await response.json();
}

// Sign Out User
export async function signOutUser(userToken: string, IdToken: string) {
  const response = await fetch(`${API_BASE_URL}/protected/users/signout?user_token=${userToken}`, {
    method: "GET",
    headers: { 
      "Authorization": `${IdToken}`,
      "Content-Type": "application/json"
    },
  });
  if (!response.ok) {
    throw new Error("Failed to sign out");
  }
  return await response.json();
}

// Update User Attributes
export async function updateUser(email: string, attributes: { Name: string; Value: string }[], IdToken: string) {
  const response = await fetch(`${API_BASE_URL}/protected/users/update_user`, {
    method: "POST",
    headers: { 
      "Authorization": `${IdToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ attributes: { email, attributes } }),
  });
  if (!response.ok) {
    throw new Error("Failed to update user");
  }
  return await response.json();
}
