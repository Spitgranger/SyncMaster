const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function getFiles() {
    try {
      const response = await fetch(`${API_BASE_URL}/documents/HC057/get_files`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
  
      if (!response.ok) {
        throw new Error("Failed to fetch files");
      }
  
      return await response.json();
    } catch (error) {
      console.error("Error fetching files:", error);
      throw error;
    }
  } 