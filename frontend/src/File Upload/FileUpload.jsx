import React, { useState } from 'react';
import './FileUpload.css';
import axios from 'axios';

const FileSubmit = () => {

    const [file, setFile] = useState();

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    }

    const handleSubmit = async (event) =>{
        event.preventDefault();
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
        });

    }

    return (
        <div className='FileSubmit'>
            <form onSubmit={handleSubmit}>
                <input type='file' onChange={handleFileChange}/>
                <button type='submit'>Generate Skeleton</button>
            </form>
        </div>
    )

}

export default FileSubmit