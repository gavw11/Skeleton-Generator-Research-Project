import React, { useState } from 'react';
import axios from 'axios';
import { idContext } from '../idContext';
import Download from './Download';

const SkelGen = () => {

    const [file, setFile] = useState(null);
    const [fileID, setID] = useState(null);

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
    }

    const setUniqueID = (response) => {
        setID(response.data.id)
        console.log(`Set id to ${response.data.id}`)
    }

    const handleSubmit = async (event) => {
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
            setUniqueID(response)
        });

    }

    return (
        <div className="px-28 mr-24">
            <idContext.Provider value={fileID}>
            <div className='FileSubmit'>
                <form onSubmit={handleSubmit}>
                    <input type='file' className='rounded-lg' onChange={handleFileChange}/>
                    <button type='submit'>Generate Skeleton</button>
                </form>
            </div>
            <Download/>
        </idContext.Provider>          
        </div>
    )
};

export default SkelGen 