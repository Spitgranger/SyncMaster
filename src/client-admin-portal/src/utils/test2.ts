import { v4 as uuidv4 } from 'uuid';

interface FileData {
    name: string;
    path: string;
    link: string;
}

interface Folder {
    id: string;
    title: string;
    childFolders: string[];
    childFiles: string[];
    path: string;
}

interface File {
    id: string;
    title: string;
    link: string;
}

interface OutputStructure {
    folders: { [key: string]: Folder };
    files: { [key: string]: File };
}

// Input data
const files: FileData[] = [
    { name: 'file1.txt', path: 'Root1/folder1/folder2/file1.txt', link: 'filelink' },
    { name: 'file2.txt', path: 'Root2/folder1/file2.txt', link: 'filelink' },
    { name: 'file3.txt', path: 'Root1/file3.txt', link: 'filelink' },
    { name: '', path: 'Root2/Folder3', link: '' }
];

// Initialize storage for folders and files
const folders: { [key: string]: Folder } = {};
const filesOutput: { [key: string]: File } = {};

// Start with root folders already present (keys 0 and 1)
folders['0'] = {
    id: '0',
    title: 'Root1',
    childFolders: [],
    childFiles: [],
    path: 'Root1'
};

folders['1'] = {
    id: '1',
    title: 'Root2',
    childFolders: [],
    childFiles: [],
    path: 'Root2'
};

// Function to process paths and create folder hierarchy
export default function processPath(path: string, fileData: FileData) {
    const pathParts = path.split('/');

    // Create or reference the necessary folders
    let parentFolderId = '0'; // Root folder for the start (either Root1 or Root2)

    for (let idx = 0; idx < pathParts.length; idx++) {
        const part = pathParts[idx];
        const folderPath = pathParts.slice(0, idx + 1).join('/');

        // Check if folder exists, if not, create it
        let folderId: string | null = null;
        for (const folderKey in folders) {
            if (folders[folderKey].path === folderPath) {
                folderId = folderKey;
                break;
            }
        }

        // If folder doesn't exist, create it with a new UUID (except for root folders)
        if (!folderId) {
            folderId = uuidv4(); // Using UUID for non-root folders
            folders[folderId] = {
                id: folderId,
                title: part,
                childFolders: [],
                childFiles: [],
                path: folderPath
            };
        }

        // Add this folder as a child of its parent
        if (idx > 0) {
            const parentFolder = folders[parentFolderId];
            if (!parentFolder.childFolders.includes(folderId)) {
                parentFolder.childFolders.push(folderId);
            }
        }

        parentFolderId = folderId;
    }

    // If a file exists, add it to the correct folder
    if (fileData.name) {
        const fileId = uuidv4(); // Using UUID for files
        filesOutput[fileId] = {
            id: fileId,
            title: fileData.name,
            link: fileData.link
        };
        if (parentFolderId) {
            folders[parentFolderId].childFiles.push(fileId);
        }
    }
}

// Process each file/folder in the input data
files.forEach(fileData => {
    processPath(fileData.path, fileData);
});

// Prepare final output structure
const output: OutputStructure = {
    folders: {},
    files: {}
};

// Ensure each folder's ID matches its key and keep UUIDs for non-root folders
Object.keys(folders).forEach(key => {
    if (key !== '0' && key !== '1') {
        folders[key].id = key; // Ensure that non-root folders have UUID as both key and id
    }
    output.folders[key] = folders[key];
});

// Ensure each file's ID matches its key and keep UUIDs
Object.keys(filesOutput).forEach(key => {
    filesOutput[key].id = key; // Ensure files' IDs are UUIDs (matching the key)
    output.files[key] = filesOutput[key];
});

// Output result
console.log(JSON.stringify(output, null, 2));
