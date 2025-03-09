const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function enterSite(userId: string, IdToken: string) {
  try {
    console.log(userId)
    const response = await fetch(`${API_BASE_URL}/protected/site/ITB/enter?user_id=${encodeURIComponent(userId)}`, {
      method: "POST",
      headers: { 
        "Authorization": `${IdToken}`,
        "Content-Type": "application/json"
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to enter site: ${response.statusText}`);
    }

    return response.json();
  } catch (err) {
    console.error("Error entering site:", err);
    throw err;
  }
}

export async function exitSite(userId: string, IdToken: string) {
  try {
    const response = await fetch(`${API_BASE_URL}/protected/site/ITB/exit?user_id=${encodeURIComponent(userId)}`, {
      method: "PATCH",
      headers: { 
        "Authorization": `${IdToken}`,
        "Content-Type": "application/json"
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to exit site: ${response.statusText}`);
    }

    return response.json();
  } catch (err) {
    console.error("Error exiting site:", err);
    throw err;
  }
}
