import { useState, useRef } from 'react'
import loadingSpinner from '../assets/loading_spinner.svg'
import axios from 'axios'

const Generate = () => {

    const [downloadReady, setDownloadReady] = useState(false);
    const [uploadFinished, setUploadFinished] = useState(false);
    const [videoURL, setVideoURL] = useState(null);
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
    

    const handleGenerate = async () => {
        if (file) {

            setGenerating(true);

            const url = 'http://127.0.0.1:5000/api/upload';
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
                setFileURL(`http://127.0.0.1:5000/api/download/${response.data.id}`);
                setDownloadReady(true);
                
                const viewUrl = `http://127.0.0.1:5000/api/view/${response.data.id}`;
                setVideoURL(viewUrl);

            }
            catch(error) {
                console.error('Error uploading file:', error);
            }
            finally {
                setGenerating(false);
            }

        }
    }

  return (
    <>
        <div className='w-full h-14 pt-28'>
            {generating && (
                <div className='flex flex-col items-center justify-center'>
                    <img className='w-10 h-10' src={loadingSpinner}/>
                    <p>
                        Generating Skeleton...
                    </p>
                </div>
            )}
        </div>
        <div className='flex flex-row w-full h-full justify-center pt-24'>
            <input type='file' onChange={handleFileChange} className='hidden' ref={inputFileRef}/>
            <div className='flex justify-center items-center px-10'>           
                <button onClick={handleInput} className='px-1 py-2 h-12 mx-5 bg-black border border-green-600 hover:bg-green-600
                                                        rounded-2xl text-xs shadow-md transition-all duration-500 
                                                        font-light md:text-2xl md:mx-12 md:px-6'>Upload File</button>
                {uploadFinished && (
                    <button onClick={handleGenerate} className='px-1 h-12 mx-5 bg-green-500 hover:bg-green-700
                                                            rounded-2xl text-xs font-light transition-all duration-500
                                                            md:text-2xl md:mx-12 md:px-6'
                                                            >Generate Skeleton</button>
                )}
            </div>
        </div>
        {downloadReady && (
            <div className='flex flex-col justify-center items-center w-full h-full pt-10'>
                <a href={fileURL} className='inline-flex items-center justify-center px-3 h-12 mx-12 bg-black border border-white
                                             hover:bg-white hover:text-black rounded-2xl text-2xl shadow-md transition-all 
                                             duration-700 font-light'>Download Skeleton</a>
                <video autoPlay loop className='mt-10 w-1/2 h-auto rounded-md border-4 border-green-400 object-cover'>
                    <source src={videoURL} type='video/mp4'/>
                </video>                
            </div>
            )}
    </>
  )
}

export default Generate
