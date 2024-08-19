import { useState, useRef } from 'react'
import loadingSpinner from '../assets/loading_spinner.svg'
import axios from 'axios'

const Generate = () => {

    const [downloadReady, setDownloadReady] = useState(false);
    const [uploadFinished, setUploadFinished] = useState(false);
    const [fileID, setFileID] = useState(null);
    const [file, setFile] = useState(null);
    const [fileURL, setFileURL] = useState('#');
    const [generating, setGenerating] = useState(false);

    const inputFileRef = useRef(null);

    const handleFileChange = (event) => {
        setFile(event.target.files[0])

        if (event.target.files[0])
            setUploadFinished(true);
    }

    const handleInput = () => {
        inputFileRef.current.click();
    }
    

    const handleUpload = async (event) => {
        if (file) {

            setGenerating(true);

            const url = 'http://127.0.0.1:5000/upload';
            const formData = new FormData();
            formData.append('file', file);
            formData.append('fileName', file.name);
            const config = {
            headers: {
                'content-type': 'multipart/form-data',
            },
            };

            try {

                const response = await axios.post(url, formData, config);
            
                console.log(response.data.msg);
                setFileID(response.data.id);
                setFileURL(`http://127.0.0.1:5000/download/${response.data.id}`);
                setDownloadReady(true);

            }
            catch(error) {
                console.error('Error uploading file:', error);
            }
            finally {
                setGenerating(false);
            }

        }
    }

    const handleDownload = () => {
        if (fileID) {
            ;
        }
    }

 
  return (
    <>
        <div className='flex justify-center items-center w-full h-14 pt-28'>
            {generating && (
                <img className='w-10 h-10' src={loadingSpinner}/>
            )}
        </div>
        <div className='flex flex-row w-full h-full justify-center pt-24'>
            <input type='file' onChange={handleFileChange} className='hidden' ref={inputFileRef}/>
            <div className='flex justify-center items-center px-10'>           
                <button onClick={handleInput} className='px-3 w-48 h-12 mx-12 bg-black border border-green-600 hover:bg-green-600
                                                        rounded-2xl text-2xl shadow-md transition-all duration-500 
                                                        font-light'>Upload File</button>
                {uploadFinished && (
                    <button onClick={handleUpload} className='px-6 h-12 mx-12 bg-green-500 hover:bg-green-700
                                                            rounded-2xl text-2xl font-light transition-all duration-500'
                                                            >Generate Skeleton</button>
                )}
            </div>

            {downloadReady && (
                <a href={fileURL}>Download Skeleton</a>
            )}
        </div>
    </>
  )
}

export default Generate
