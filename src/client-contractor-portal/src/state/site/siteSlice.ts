import { getEntryTimeFromLocalStorage } from '@/utils/siteHelpers';
import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { v4 as uuidv4 } from 'uuid';

interface SiteState {
  entryTime: string | null;
  isEnteringOrExitingSite: boolean;
  attachments: any[];
  work_order: number | null;
  description: string | null;
  isLoadingSiteVisitDetails: boolean;
}

const initialState: SiteState = {
  entryTime: getEntryTimeFromLocalStorage(),
  isEnteringOrExitingSite: false,
  attachments: [],
  work_order: null,
  description: null,
  isLoadingSiteVisitDetails: false,
};

const siteSlice = createSlice({
  name: 'site',
  initialState,
  reducers: {
    setEntryTime(state, action) {
      state.entryTime = action.payload.entryTime;
    },
    clearEntryTime(state) {
      state.entryTime = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(enterSite.pending, (state) => {
        state.isEnteringOrExitingSite = true;
      })
      .addCase(enterSite.fulfilled, (state) => {
        state.isEnteringOrExitingSite = false;
      })
      .addCase(enterSite.rejected, (state) => {
        state.isEnteringOrExitingSite = false;
      })
      .addCase(getSiteVisitDetails.pending, (state) => {
        state.isLoadingSiteVisitDetails = true;
      })
      .addCase(getSiteVisitDetails.fulfilled, (state, action) => {
        state.work_order =
          action.payload.work_order !== undefined
            ? action.payload.work_order
            : state.work_order;
        state.description =
          action.payload.description !== undefined
            ? action.payload.description
            : state.description;
        state.attachments = action.payload.attachments;
        state.isLoadingSiteVisitDetails = false;
      })
      .addCase(getSiteVisitDetails.rejected, (state) => {
        state.isLoadingSiteVisitDetails = false;
      });
  },
});

export const enterSite = createAsyncThunk(
  'site/enterSite',
  async ({
    site_id,
    idToken,
    allowed_tracking,
    ack_status,
    on_site,
    employee_id,
  }: {
    site_id: string | null;
    idToken: string | null;
    allowed_tracking: boolean;
    ack_status: boolean;
    on_site: boolean;
    employee_id: string | null;
  }) => {
    let requestBody = null;

    if (employee_id !== null) {
      requestBody = {
        allowed_tracking: allowed_tracking,
        ack_status: ack_status,
        on_site: on_site,
        employee_id: employee_id,
      };
    } else {
      requestBody = {
        allowed_tracking: allowed_tracking,
        ack_status: ack_status,
        on_site: on_site,
      };
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/site/${site_id}/enter`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `${idToken}`,
        },
        body: JSON.stringify(requestBody),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to enter site');
    }
    return response.json();
  }
);

export const uploadAttachment = createAsyncThunk(
  'site/uploadAttachment',
  async (uploadData: any) => {
    console.log('uploadData in file attachment', uploadData);

    const { site_id, idToken, entryTime, fileName, fileBlob } = uploadData;
    const s3_key = uuidv4();
    const formData = new FormData();
    const s3PresignedURLResponse = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/documents/get_presigned_url/${s3_key}`,
      {
        method: 'GET',
        headers: {
          Authorization: `${idToken}`,
        },
      }
    );
    if (!s3PresignedURLResponse.ok) {
      throw new Error('Error in fetching presigned URL from S3');
    }
    const s3PresignedURLResponsejson = await s3PresignedURLResponse.json();
    Object.entries(
      s3PresignedURLResponsejson['s3_presigned_url']['fields']
    ).forEach(([key, value]) => {
      formData.append(key, value as string);
    });
    formData.append('file', fileBlob);
    const s3FileUploadResponse = await fetch(
      s3PresignedURLResponsejson['s3_presigned_url']['url'],
      {
        method: 'POST',
        body: formData,
      }
    );
    if (!s3FileUploadResponse.ok) {
      throw new Error('Error in uploading the file to S3');
    }
    const requestBody = {
      name: fileName,
      s3_key: s3_key,
    };

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/site/${site_id}/visit/${entryTime}/attachments/add`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `${idToken}`,
        },
        body: JSON.stringify(requestBody),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to upload attachment');
    }
    return true;
  }
);

export const removeAttachment = createAsyncThunk(
  'site/removeAttachment',
  async (removeData: any) => {
    const { site_id, idToken, entryTime, fileName } = removeData;
    const requestBody = {
      name: fileName,
    };
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/site/${site_id}/visit/${entryTime}/attachments/remove`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `${idToken}`,
        },
        body: JSON.stringify(requestBody),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to remove attachment');
    }
    return true;
  }
);

export const exitSite = createAsyncThunk(
  'site/exitSite',
  async ({
    site_id,
    idToken,
    entryTime,
  }: {
    site_id: string | null;
    idToken: string | null;
    entryTime: string | null;
  }) => {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/site/${site_id}/exit/${entryTime}`,
      {
        method: 'PATCH',
        headers: {
          Authorization: `${idToken}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error('Failed to exit site');
    }
    return true;
  }
);

export const getSiteVisitDetails = createAsyncThunk(
  'site/getSiteVisitDetails',
  async ({
    site_id,
    idToken,
    entryTime,
  }: {
    site_id: string | null;
    idToken: string | null;
    entryTime: string | null;
  }) => {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/site/${site_id}/visit/${entryTime}`,
      {
        method: 'GET',
        headers: {
          Authorization: `${idToken}`,
        },
      }
    );
    if (!response.ok) {
      throw new Error('Failed to get site visit details');
    }
    const data = await response.json();
    return data;
  }
);

export const updateWorkOrderNumber = createAsyncThunk(
  'site/updateWorkOrderDescription',
  async ({
    site_id,
    idToken,
    entryTime,
    work_order,
  }: {
    site_id: string | null;
    idToken: string | null;
    entryTime: string | null;
    work_order: number;
  }) => {
    const requestBody = {
      work_order: work_order,
    };
    console.log('requestBody in updateWorkOrderNumber', requestBody);

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/site/${site_id}/visit/${entryTime}`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `${idToken}`,
        },
        body: JSON.stringify(requestBody),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to update work order number');
    }
    return true;
  }
);

export const updateWorkDescription = createAsyncThunk(
  'site/updateWorkDescription',
  async ({
    site_id,
    idToken,
    entryTime,
    description,
  }: {
    site_id: string | null;
    idToken: string | null;
    entryTime: string | null;
    description: string;
  }) => {
    const requestBody = {
      description: description,
    };
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/site/${site_id}/visit/${entryTime}`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `${idToken}`,
        },
        body: JSON.stringify(requestBody),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to update work description');
    }
    return true;
  }
);

export const { setEntryTime, clearEntryTime } = siteSlice.actions;

export default siteSlice.reducer;
