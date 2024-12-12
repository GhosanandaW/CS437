'use client';
import React from 'react';
// import { DefaultAzureCredential } from "@azure/identity";
import { InteractiveBrowserCredential } from "@azure/identity";
import { BlobServiceClient, generateBlobSASQueryParameters, ContainerClient, BlobClient, StorageSharedKeyCredential, BlobSASPermissions } from "@azure/storage-blob";

async function uploadImageToAzure(imageFile: any) {
  // // Replace with your Azure Storage connection string
  // const connectionString = 'YOUR_AZURE_STORAGE_CONNECTION_STRING';

  // // Create BlobServiceClient
  // const blobServiceClient = BlobServiceClient.fromConnectionString(connectionString);

  // Create a DefaultAzureCredential object
  // const credential = new DefaultAzureCredential();

  const pictureName=document.getElementById("pictureName").value;
  const credential = new InteractiveBrowserCredential({
    tenantId: "",
    clientId: ""
  });

  // Create BlobServiceClient using the credential
  // const blobServiceClient = new BlobServiceClient(
  //   "https://kv-alarm-codes.vault.azure.net/",
  //   credential
  // );

  const blobServiceClient = new BlobServiceClient(
    "https://adlalarmdata.blob.core.windows.net/",
    credential
  );

  // Create a unique name for the blob
  const blobName = `image-${Date.now()}.jpg`;

  // Get a reference to the container
  const containerClient = blobServiceClient.getContainerClient('captures/knownFaces/'+pictureName);

  // Create a block blob client
  const blockBlobClient = containerClient.getBlockBlobClient(blobName);

  // Upload the image to the blob (using uploadData instead)
  const uploadResponse = await blockBlobClient.uploadData(imageFile);

  // Return the public URL of the uploaded image
  const blobURL = blockBlobClient.url;
  console.log('blob URL is: ', blobURL)
  return blobURL;
}

async function downloadAllFromStorage() {

  const credential = new InteractiveBrowserCredential({
    tenantId: "",
    clientId: ""
  });

  const blobServiceClient = new BlobServiceClient(
    "https://adlalarmdata.blob.core.windows.net/",
    credential
  );

  const containerClient = blobServiceClient.getContainerClient('captures');
  let i = 1;

  for await (const blob of containerClient.listBlobsFlat()) {
    console.log(`Blob ${i++}: ${blob.name}`);
    if (blob.name.startsWith('knownFaces/') && blob.name.endsWith(".jpg")) {
      const blobClient = containerClient.getBlobClient(blob.name)
      const downloadBlockBlobResponse = await blobClient.download();
      if (downloadBlockBlobResponse) {
        const blobToDownload = await downloadBlockBlobResponse.blobBody;
        const downloadableUrl = URL.createObjectURL(blobToDownload);
        // Download using a hidden anchor tag (more browser-compatible)
        const hiddenLink = document.createElement('a');
        hiddenLink.href = downloadableUrl;
        hiddenLink.download = `${blob.name}`;
        document.body.appendChild(hiddenLink);
        hiddenLink.click();
        document.body.removeChild(hiddenLink);
        URL.revokeObjectURL(downloadableUrl);
      } else {
        console.error("Error downloading blob!");
      }
    }
  }

  // // Get a list of blobs in the container 
  // const blobs = containerClient.listBlobsFlat();
  // console.log('blobs are:', blobs)
  // console.log("next function:", blobs.next);
  // console.log("byPage function:", blobs.byPage());
  // console.log("next function source code:", blobs.next.toString());
  // // console.log ('blobs .bypage are:', blobs.byPage())
  // // Loop through each blob and generate the download URL 
  // for await (const blob of blobs) { 
  //   console.log('blob is: ', blob.name);
  //   const blobClient = containerClient.getBlobClient(blob.name); 
  //   await blobClient.downloadToFile("C:/Users/ghosa/Downloads/"+blob.name);
  //   // // Define SAS options 
  //   // const sasUrl = await blobClient.generateSasUrl({ 
  //   //   permissions: Storage.BlobSASPermissions.parse("r"), // Read permissions 
  //   //   expiresOn: new Date(new Date().valueOf() + 3600 * 1000) // 1 hour from now
  //   // })
  //   //   window.location.href = sasUrl;
  // }

  // const blobClient = containerClient.getBlobClient('image-1733912021870.jpg');
  // // console.log(await blobClient.downloadToFile("C:\\Users\\ghosa\\Downloads\\blobDownloadTest"))
  // // await blobClient.downloadToFile("C:/Users/ghosa/Downloads/blobDownloadTest")
  // // window.location.href = url
  // const downloadBlockBlobResponse = await blobClient.download();
  // if (downloadBlockBlobResponse) { 
  //   // const downloaded = await blobToString(await downloadBlockBlobResponse.blobBody);
  //   // console.log(
  //   //   "Downloaded blob content",
  //   //   downloaded
  //   // );
  //   const blob = await downloadBlockBlobResponse.blobBody;
  //   const downloadableUrl = URL.createObjectURL(blob);
  //   // Download using a hidden anchor tag (more browser-compatible)
  //   const hiddenLink = document.createElement('a');
  //   hiddenLink.href = downloadableUrl;
  //   hiddenLink.download = 'knownFace.jpg';
  //   document.body.appendChild(hiddenLink);
  //   hiddenLink.click();
  //   document.body.removeChild(hiddenLink);

  //   URL.revokeObjectURL(downloadableUrl);
  // } else {
  //   console.error("Error downloading blob!");
  // }


}

async function blobToString(blob: Blob): Promise<string> {
  const fileReader = new FileReader();
  return new Promise<string>((resolve, reject) => {
    fileReader.onloadend = (ev: any) => {
      resolve(ev.target!.result);
    };
    fileReader.onerror = reject;
    fileReader.readAsText(blob);
  });
}

function showPicture() {
  return (
    <div><img height={400} width={600} src='https://www.idahostatesman.com/latest-news/w4ojx5/picture277864073/alternates/FREE_1140/0801%2006%20state%20street%20crashes.jpg' ></img></div>
  )
}


const facelibrary = () => {
  // const handleUpload = () => {
  //   const fileInput = document.getElementById('file') as HTMLInputElement;
  //   const files = fileInput.files;

  //   if (files && files.length > 0) {
  //     const filename = files[0].name;
  //     uploadPicture(filename);
  //   } else {
  //     console.error('No file selected.');
  //     // You might want to display an error message to the user here
  //   }
  // };
  // const uploadPicture = (fileName: string) => {
  //   console.log('Uploading picture, ' + fileName);
  //   // Your actual upload logic here, using the filename
  // }
  return (
    <div className="container-fluid p-3">
      <label htmlFor="file" className='mb-2'>Upload picture here!</label>
      <img id="picture" src="#" alt="picture" style={{ display: "none" }} onError={() => {
        const img = document.getElementById('picture');
        if (img.complete && img.naturalWidth > 0) {
          img.style.display = 'block';
        } else {
          // Image failed to load
          img.style.display = 'none';
        }
      }} />
      <div className="row mt-3">
        <div className="col">
          <input id="file" name="file" type="file" onChange={() => {
            const fileInput = document.getElementById('file') as HTMLInputElement;
            const selectedFile = fileInput.files![0];
            const reader = new FileReader();
            reader.onload = (e) => {
              document.getElementById('picture').src = reader.result as string;
            };
            reader.readAsDataURL(selectedFile);
            const img = document.getElementById('picture');
            img.style.display = 'block'
          }} />
        </div>
      </div>
      <div className='row mt-3'>
        <div className="col">
          <input id='pictureName' type='text' className="bg-transparent placeholder:text-green-400 text-green-700 text-sm border border-green-200 rounded-md px-3 py-2 transition duration-300 ease focus:outline-none focus:border-green-500 hover:border-green-300 shadow-sm focus:shadow"/>
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full ms-3"
            onClick={() => {
              const fileInput = document.getElementById('file') as HTMLInputElement;
              const selectedFile = fileInput.files![0]; // Assuming there's always one file selected
              uploadImageToAzure(selectedFile);
            }}>Upload</button>
        </div>
      </div>
      <div className='row mt-3'>
        <div className="col">
          <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-full"
            onClick={() => { downloadAllFromStorage() }}>Download</button>
        </div>
      </div>
    </div>
  );
};

export default facelibrary;


