//@ts-nocheck
import { randomUUID } from "crypto";
import { useState } from "react";




const FileUploaderComponent = () => {
    const uploadFile = async () => {
        const formData = new FormData()
        const s3PresignedURLResponse: any = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/documents/get_presigned_url/test4.docx`, {
            method: "GET",
        })

        const s3PresignedURLResponsejson = await s3PresignedURLResponse.json();


        Object.entries(s3PresignedURLResponsejson["s3_presigned_url"]["fields"]).forEach(
            ([key, value]: any) => {
                formData.append(key, value)
            }
        )

        formData.append("file", file)

        for (const pair of formData.entries()) {
            console.log(pair[0], pair[1]);
        }

        try {
            const httpResponse = await fetch(s3PresignedURLResponsejson["s3_presigned_url"]["url"], {
                method: "POST",
                body: formData
            })
            console.log(httpResponse.headers);
            for (const pair of httpResponse.headers.entries()) {
                console.log(pair[0] + ': ' + pair[1]);
            }


        }
        catch (err) {
            console.log("An error occured while uploading the file", err);
        }

        try {
            const requestBody = {
                site_id: "HC057",
                document_path: "/sitespecific/test/test45.docx",
                s3_key: `test4.docx`,
                e_tag: "34243245jlkfjkljaklfe",
                user_id: "23432432jkljkljl",
                requires_ack: true
            }
            const requetJson = JSON.stringify(requestBody)
            console.log(requetJson);

            const documentUploadResponse = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/documents/upload`, {
                headers: {
                    "Content-Type": "application/json"
                },
                method: "POST",
                body: requetJson
            })
            console.log(documentUploadResponse.headers);
            for (const pair of documentUploadResponse.headers.entries()) {
                console.log(pair[0] + ': ' + pair[1]);
            }
        } catch (err) {
            console.log("An error occured while adding the file entry to dynamo", err);

        }

    };

    const [file, setFile] = useState(null);
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0]; // Get the first file selected
        if (selectedFile) {
            const reader = new FileReader();

            // Set up the onload event to handle when file is read
            reader.onload = () => {
                const byteStream = reader.result as ArrayBuffer; // This will be an ArrayBuffer

                // Convert ArrayBuffer to Blob
                const blob = new Blob([byteStream], { type: selectedFile.type });

                setFile(blob); // Set the Blob to the state
                console.log(blob); // Log the Blob for debugging
            };

            reader.onerror = (error) => {
                console.error("Error reading file:", error);
            };

            // Read the file as an ArrayBuffer (byte stream)
            reader.readAsArrayBuffer(selectedFile);
        }
    };
    return (
        <div className="App">
            <div>
                <input type="file" onChange={handleFileChange} />
                <button onClick={uploadFile}>Upload</button>
            </div>
        </div>
    );
}

export default FileUploaderComponent