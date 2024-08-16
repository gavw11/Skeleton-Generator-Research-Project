import React, { useContext } from "react";
import { idContext } from '../idContext';

const Download = () => {

    const fileID = useContext(idContext)

    const fileURL = fileID ? `http://127.0.0.1:5000/download/${fileID}` : '';

    return(
        <div className="Download">
            <a href={fileURL}>Download Skeleton</a>
        </div>
    )
}

export default Download