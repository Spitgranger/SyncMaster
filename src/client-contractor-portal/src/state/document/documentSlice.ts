import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

interface DocumentState {
    currentFolderFiles: any[];
    isLoading: boolean;
    acknowledgementDocuments: any[];
}

const initialState: DocumentState = {
    currentFolderFiles: [],
    isLoading: false,
    acknowledgementDocuments: []
}

const documentSlice = createSlice({
    name: "document",
    initialState,
    reducers: {
        setIsLoading: (state, action) => {
            state.isLoading = action.payload
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(getDocuments.pending, (state) => {
                state.isLoading = true
            })
            .addCase(getDocuments.fulfilled, (state, action) => {
                state.currentFolderFiles = action.payload
                state.isLoading = false
            })
            .addCase(getDocuments.rejected, (state) => {
                state.isLoading = false
            })
            .addCase(getAcknowledgementDocuments.pending, (state) => {
                state.isLoading = true;
            }
            )
            .addCase(getAcknowledgementDocuments.fulfilled, (state, action) => {
                state.acknowledgementDocuments = action.payload;
                state.isLoading = false;
            }
            )
            .addCase(getAcknowledgementDocuments.rejected, (state) => {
                state.isLoading = false;
            }
            )
    }
})

export const getDocuments = createAsyncThunk(
    "document/getDocuments",
    async (pathData: any) => {
        /*site_id = ALL for site wide*/

        const { site_id, folder_id, idToken } = pathData
        let requestPath = `protected/documents/${site_id}/${folder_id}/get_files`
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/${requestPath}`, {
            method: "GET",
            headers: {
                "Authorization": `${idToken}`,
                "Content-Type": "application/json"
            }
        })
        if (response.ok) {
            return response.json()
        }


    }
)

export const getAcknowledgementDocuments = createAsyncThunk(
    "document/getAcknowledgementDocuments",
    async (pathData: any) => {
        const { site_id, idToken } = pathData;
        console.log("inside getting ack",site_id, idToken);
        
        let folder_id = "root";
        let generalRequestPath = `protected/documents/ALL/${folder_id}/get_files`;
        let siteSpecificRequestPath = `protected/documents/${site_id}/${folder_id}/get_files`;

        const fetchDocuments = async (requestPath: string) => {
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/${requestPath}`, {
                method: "GET",
                headers: {
                    "Authorization": `${idToken}`,
                    "Content-Type": "application/json",
                },
            });
            if (!response.ok) {
                throw new Error(`Failed to fetch documents from ${requestPath}`);
            }
            return response.json();
        };

        const generalLayer1Documents = await fetchDocuments(generalRequestPath);
        const siteSpecificLayer1Documents = await fetchDocuments(siteSpecificRequestPath);

        const acknowledgementDocuments: any[] = [];

        const processDocuments = async (documents: any[]) => {
            for (const document of documents) {
                if (document.document_type === "file" && document.requires_ack) {
                    acknowledgementDocuments.push(document);
                } else if (document.document_type === "folder") {
                    const folderRequestPath = `protected/documents/${document.site_id}/${document.document_id}/get_files`;
                    const folderDocuments = await fetchDocuments(folderRequestPath);
                    folderDocuments.forEach((doc: any) => {
                        if (doc.document_type === "file" && doc.requires_ack) {
                            acknowledgementDocuments.push(doc);
                        }
                    });
                }
            }
        };

        await Promise.all([
            processDocuments(generalLayer1Documents),
            processDocuments(siteSpecificLayer1Documents),
        ]);

        console.log("Acknowledgement documents:", acknowledgementDocuments);

        return acknowledgementDocuments;
    }
);

export default documentSlice.reducer