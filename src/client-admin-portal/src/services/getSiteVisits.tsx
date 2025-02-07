const API_BASE_URL = "https://mjspvpszgg.execute-api.us-east-2.amazonaws.com/dev";

interface SiteVisit {
  site_id: string;
  user_id: string;
  entry_time: string;
  exit_time?: string;
}

interface GetSiteVisitsParams {
  user_role: "admin";
  from_time?: string;
  to_time?: string;
  limit?: number;
}

export async function getSiteVisits(params: GetSiteVisitsParams): Promise<SiteVisit[]> {
  try {
    const url = new URL(`${API_BASE_URL}/site/visits`);
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        url.searchParams.append(key, String(value));
      }
    });

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch site visits");
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching site visits:", error);
    throw error;
  }
}
