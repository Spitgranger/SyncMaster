interface SessionResponse {
    uuid: string;
  }
  
  interface LocationVerificationResponse {
    token: string;
    message: string;
  }

interface EmitResponse {
    message: string;
  }
  
const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  
async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${baseUrl}/${endpoint}`;
  
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
  
    if (!response.ok) {
      const errorDetails = await response.json();
      throw new Error(errorDetails.message || 'An error occurred');
    }
  
    return response.json();
  }
  
export async function createSession(): Promise<SessionResponse> {
    return apiFetch<SessionResponse>('api/users/create-session', { method: 'POST' });
  }
  
export async function verifyLocation(userId: string, latitude: number, longitude: number): Promise<LocationVerificationResponse> {
    return apiFetch<LocationVerificationResponse>('api/users/verify-location', {
      method: 'POST',
      body: JSON.stringify({ userId, latitude, longitude }),
    });
  }

export async function emitConnection(userId: string): Promise<EmitResponse> {
    return apiFetch<LocationVerificationResponse>('api/users/emit-connection', {
      method: 'POST',
      body: JSON.stringify({ userId }),
    });
  }
