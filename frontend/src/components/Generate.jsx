import { useState, useRef, useEffect } from 'react'
import loadingSpinner from '../assets/loading_spinner.svg'
import sendButton from '../assets/send.svg'
import axios from 'axios'

const Generate = () => {

    const [downloadReady, setDownloadReady] = useState(false);
    const [uploadFinished, setUploadFinished] = useState(false);
    const [viewURL, setViewURL] = useState(null);
    const [file, setFile] = useState(null);
    const [fileURL, setFileURL] = useState('#');
    const [generating, setGenerating] = useState(false);
    const [generateDisabled, setGenerateDisabled] = useState(false);
    const [isImage, setIsImage] = useState(null);
    const [isVideo, setIsVideo] = useState(null);
    const [prompt, setPrompt] = useState(null);
    const [generationSettings, setGenerationSettings] = useState({
        confidence_level: 0.5,
        smoothing_factor: 7,
        downsample: 1
    })

    const inputFileRef = useRef(null);
    const videoRef = useRef(null);

    const handleSettingsChange = (event) => {
        const { name, value } = event.target;

        setGenerateDisabled(false);

        setGenerationSettings(prevSettings => ({
            ...prevSettings,
            [name]: parseFloat(value)
        }));
    };

    useEffect(() => {
        const currentVid = videoRef.current;

        if (currentVid) {
            // Explicitly reload the video to ensure new source is applied
            currentVid.load();
        }
    }, [viewURL]); // Reload video source changes

    const handlePromptChange = (event) => {
        setPrompt(event.target.value);
        setUploadFinished(true);
    }

    const handleFileChange = (event) => {
        const file = event.target.files[0];

        if (file) {
            const type = file.type;

            if (type.startsWith('image/')) {
                setIsImage(true);
                setIsVideo(false);
            }
            else if (type.startsWith('video/')) {
                setIsVideo(true);
                setIsImage(false);
            }
            
            setGenerateDisabled(false);
            setFile(file);

            setUploadFinished(true);

        }
    }

    const handleInput = () => {
        inputFileRef.current.click();
    }

    const handleAiGenerate = async () => {
        if (prompt) {
            setIsImage(true);
            setIsVideo(false);
            setGenerateDisabled(true);
            setGenerating(true);
            const url = 'http://127.0.0.1:5000/api/openai/upload';
            const data = {
                prompt: prompt,
                generationSettings: generationSettings,
            }
            const config = {
                headers: {
                    'content-type': 'application/json',
                },
                };
            
            try {

                const response = await axios.post(url, data, config);
            
                console.log(response.data.msg);
                setFileURL(`http://127.0.0.1:5000/api/download/${response.data.id}`);
                setDownloadReady(true);
                
                const viewUrl = `http://127.0.0.1:5000/api/view/${response.data.id}`;
                setViewURL(viewUrl);

            }
            catch(error) {
                console.error('Error uploading file:', error);
            }
            finally {
                setGenerating(false);
            }

        }
        else {
            alert("No Prompt!")
        }
    }
    

    const handleGenerate = async () => {
        if (file) {

            setGenerateDisabled(true);
            setGenerating(true);

            const url = 'http://127.0.0.1:5000/api/upload';
            const formData = new FormData();
            formData.append('file', file);
            formData.append('fileName', file.name);
            formData.append('generationSettings', JSON.stringify(generationSettings));
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
                setViewURL(viewUrl);

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
                <button onClick={handleGenerate} disabled={generateDisabled} className='px-1 h-12 mx-5 bg-green-500 hover:bg-green-700
                                                            rounded-2xl text-xs font-light transition-all duration-500
                                                            md:text-2xl md:mx-12 md:px-6'
                                                            >Generate Skeleton</button>
            </div>
        </div>
        <div className='flex flex-col w-full h-full justify-center items-center pt-14'>
                <h2 className='font-normal text-xl'>
                    Generate Image + Skeleton With AI:
                </h2>
                <div className='flex flex-row items-center justify-center mt-3'>
                    <input type='text'  onChange={handlePromptChange} placeholder='Enter Image Prompt...' className='border rounded-xl border-white w-96 h-10 px-5 font-light mr-2'/>
                    <button className='bg-green-400 rounded-xl hover:bg-green-700 transition-all duration-500 w-10 h-11 inline-flex items-center justify-center' onClick={handleAiGenerate}>
                        <img src={sendButton} className='w-6 h-6'/>
                    </button>
                </div>
        </div>
        <div className='flex flex-col justify-center items-center w-full pt-10'>
            <label class>
                Confidence Level:
                <input className='mx-4' type='range' name='confidence_level' min='0.1' max='1' step='0.05' value={generationSettings.confidence_level} onChange={handleSettingsChange}/>
                {generationSettings.confidence_level} 
            </label>
            <label>
                Smoothing Factor:
                <input className='mx-4' type='range' name='smoothing_factor' min='1' max='30' step='1' value={generationSettings.smoothing_factor} onChange={handleSettingsChange}/>
                {generationSettings.smoothing_factor}
            </label>
            <label>
                Downsample Factor:
                <input className='mx-4' type='range' name='downsample' min='1' max='8' step='1' value={generationSettings.downsample} onChange={handleSettingsChange}/>
                {generationSettings.downsample}
            </label>  
        </div>
        {downloadReady && isVideo && (
            <div className='flex flex-col justify-center items-center w-full h-full pt-10'>
                <a href={fileURL} className='inline-flex items-center justify-center px-3 h-12 mx-12 bg-black border border-white
                                             hover:bg-white hover:text-black rounded-2xl text-2xl shadow-md transition-all 
                                             duration-700 font-light'>Download Skeleton</a>
                <video autoPlay loop ref={videoRef} className='mt-10 w-1/2 h-auto rounded-md border-4 border-green-400 object-cover'>
                    <source src={viewURL} type='video/mp4'/>
                </video>                
            </div>
            )}
        {downloadReady && isImage && (
            <div className='flex flex-col justify-center items-center w-full h-full pt-10'>
            <a href={fileURL} className='inline-flex items-center justify-center px-3 h-12 mx-12 bg-black border border-white
                                            hover:bg-white hover:text-black rounded-2xl text-2xl shadow-md transition-all 
                                            duration-700 font-light'>Download Skeleton</a>
            <img src={viewURL} className='mt-10 w-1/2 h-auto rounded-md border-4 border-green-400 object-cover'/>
        </div>
        )}
    </>
  )
}

export default Generate
