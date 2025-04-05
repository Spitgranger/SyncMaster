//@ts-nocheck
function convertToState(data) {
  if (data.length == 0) {
    return {
      folders: {},
      files: {},
    };
  }
  console.log(data);

  // Initialize storage for folders and files
  const folders = {};
  const filesOutput = {};

  // Function to process the document path and create file/folder structure
  function processDocumentPath(path, fileData) {
    const pathParts = path.split('/');

    let parentFolderId = null;
    let currentFolderId = null;

    // Iterate through path parts to create folders
    for (let idx = 0; idx < pathParts.length; idx++) {
      const part = pathParts[idx];

      // If we encounter a dot, treat it as a file and add it under the current folder
      if (part.includes('.')) {
        const fileId = path; // Use full path as the file ID
        filesOutput[fileId] = {
          id: fileId,
          title: part,
          link: fileData.s3_presigned_get,
          pathname: path,
        };

        if (currentFolderId) {
          // If we are inside a folder, add this file to the childFiles of that folder
          folders[currentFolderId].childFiles.push(fileId);
        } else {
          // If no current folder, add file under the root (top-level)
          folders[pathParts[0]].childFiles.push(fileId);
        }
        break; // Stop processing further since the rest of the parts are the file name
      } else {
        // If it's a folder, handle it as part of the folder structure
        const folderId = pathParts.slice(0, idx + 1).join('/');

        // If the folder doesn't exist, create it
        if (!folders[folderId]) {
          folders[folderId] = {
            id: folderId,
            title:
              part === 'sitewide'
                ? 'Site Wide Documents'
                : part === 'sitespecific'
                  ? 'Site Specific Documents'
                  : part, // Conditional replacement
            childFolders: [],
            childFiles: [],
            path: folderId,
            parentId: parentFolderId,
          };

          // If there's a parent folder, add this folder as a child of that parent
          if (parentFolderId) {
            folders[parentFolderId].childFolders.push(folderId);
          }
        }

        // Update parent folder ID for the next iteration
        parentFolderId = folderId;
        currentFolderId = folderId;
      }
    }
  }

  // Process each document
  console.log(data);

  data.forEach((fileData) => {
    processDocumentPath(fileData.document_path, fileData);
  });

  // Prepare final output structure
  const output = {
    folders: {},
    files: {},
  };

  // Copy all folder data into the output
  Object.keys(folders).forEach((key) => {
    output.folders[key] = folders[key];
  });

  // Copy all file data into the output
  Object.keys(filesOutput).forEach((key) => {
    output.files[key] = filesOutput[key];
  });

  // Output result
  //   console.log(JSON.stringify(output, null, 2));
  return output;
}

export default convertToState;
