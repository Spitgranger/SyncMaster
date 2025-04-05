import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { v4 as uuidv4 } from 'uuid';

interface DocumentState {
  currentFolderFiles: any[];
  isLoading: boolean;
}

const initialState: DocumentState = {
  currentFolderFiles: [],
  isLoading: false,
};

const documentSlice = createSlice({
  name: 'document',
  initialState,
  reducers: {
    setIsLoading: (state, action) => {
      state.isLoading = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(getDocuments.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(getDocuments.fulfilled, (state, action) => {
        state.currentFolderFiles = action.payload;
        state.isLoading = false;
      })
      .addCase(getDocuments.rejected, (state) => {
        state.isLoading = false;
      });
  },
});

export const getDocuments = createAsyncThunk(
  'document/getDocuments',
  async (pathData: any) => {
    /*site_id = ALL for site wide*/

    const { site_id, folder_id, idToken } = pathData;
    const requestPath = `protected/documents/${site_id}/${folder_id}/get_files`;
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/${requestPath}`,
      {
        method: 'GET',
        headers: {
          Authorization: `${idToken}`,
          'Content-Type': 'application/json',
        },
      }
    );
    if (response.ok) {
      return response.json();
    }
  }
);

export const uploadDocument = createAsyncThunk(
  'document/uploadDocument',
  async (uploadData: any) => {
    /**
     * site_id,
     * document_name,
     * document_type,
     * parent_folder_id,
     * document_path,
     * s3_key,
     * e_tag,
     * user_id,
     * requires_ack
     * document_expiry (optional)
     */
    console.log('here');

    const {
      site_id,
      document_name,
      document_type,
      parent_folder_id,
      document_path,
      user_id,
      idToken,
      requires_ack,
      document_expiry,
      fileBlob,
    } = uploadData;
    console.log('uploadData here:', uploadData);

    const s3_key = uuidv4();

    if (document_type === 'file') {
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
      console.log(document_name);

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
    }
    let requestBody = null;
    if (document_expiry === null) {
      requestBody = {
        site_id: site_id,
        document_name: document_name,
        document_type: document_type,
        parent_folder_id: parent_folder_id,
        document_path: document_path,
        s3_key: s3_key,
        e_tag: '34243245jklfjkljaklfe',
        user_id: user_id,
        requires_ack: requires_ack,
      };
    } else {
      requestBody = {
        site_id: site_id,
        document_name: document_name,
        document_type: document_type,
        parent_folder_id: parent_folder_id,
        document_path: document_path,
        s3_key: s3_key,
        e_tag: '34243245jklfjkljaklfe',
        user_id: user_id,
        requires_ack: requires_ack,
        document_expiry: document_expiry,
      };
    }
    console.log('request body here', requestBody);

    const requetJson = JSON.stringify(requestBody);
    const documentEntryUploadResponse = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/documents/upload`,
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `${idToken}`,
        },
        method: 'POST',
        body: requetJson,
      }
    );

    if (!documentEntryUploadResponse.ok) {
      throw new Error('Error in uploading the file entry to Dynamo');
    }
    return documentEntryUploadResponse.json();
  }
);

export const deleteDocument = createAsyncThunk(
  'document/deleteDocument',
  async (deleteData: any) => {
    const { site_id, parent_folder_id, document_id, idToken } = deleteData;
    const queryParams = new URLSearchParams({
      site_id: site_id,
      parent_folder_id: parent_folder_id,
      document_id: document_id,
    }).toString();

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/protected/documents/delete?${queryParams}`,
      {
        headers: {
          Authorization: `${idToken}`,
        },
        method: 'DELETE',
      }
    );

    if (!response.ok) {
      throw new Error('Error in deleting the document');
    }
    return true;
  }
);

export default documentSlice.reducer;
