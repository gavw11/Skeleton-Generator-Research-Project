import { useState } from 'react'

const Generate = () => {

    const [downloadReady, setDownloadReady] = useState(false);
    const [fileID, setFileID] = useState(null);
    const [file, setFile] = useState(null);
    const [fileURL, setFileURL] = useState('#')

    const handleUpload = (event) => {
        const uploadedFile = event.target.files[0];
        if (uploadedFile) {
            setFile(uploadedFile);

            const url = 'http://127.0.0.1:5000/upload';
            const formData = new FormData();
            formData.append('file', file);
            formData.append('fileName', file.name);
            const config = {
            headers: {
                'content-type': 'multipart/form-data',
            },
            };
            axios.post(url, formData, config).then((response) => {
                console.log(response.data.msg);
                setFileID(response);
                setDownloadReady(true);
            });
        }
    }

    const handleDownload = () => {
        if (fileID) {
            setFileURL(`http://127.0.0.1:5000/download/${fileID}`);
        }
    }

 
  return (
    <div className='flex flex-row'>
        <input type='file' onChange={handleUpload} className='hidden'/>
        {downloadReady && (
            <a href={fileURL}>Download Skeleton</a>
        )}
    </div>
  )
}

export default Generate
