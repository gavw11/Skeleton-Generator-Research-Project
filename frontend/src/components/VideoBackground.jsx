import { useState, useRef, useEffect } from 'react';
import video1 from "../assets/demo_vid-skeleton.mp4";
import video2 from "../assets/demo_vid2-skeleton.mp4";

const VideoBackground = () => {
    const videos = [video1, video2];
    const [currentVidIndex, setCurrentVidIndex] = useState(0);
    const videoRef = useRef(null);

    const handleVidEnd = () => {
        setCurrentVidIndex((prevIndex) => (prevIndex + 1) % videos.length);
    };

    useEffect(() => {
        const currentVid = videoRef.current;

        if (currentVid) {
            currentVid.addEventListener('ended', handleVidEnd);

            // Cleanup function
            return () => {
                if (currentVid) {
                    currentVid.removeEventListener('ended', handleVidEnd);
                }
            };
        }
    }, [currentVidIndex]); // Dependency array ensures effect runs on index change

    useEffect(() => {
        const currentVid = videoRef.current;

        if (currentVid) {
            // Explicitly reload the video to ensure new source is applied
            currentVid.load();
        }
    }, [currentVidIndex]); // Reload video when index changes

    return (
        <div className='relative h-full w-full'>
            <video
                ref={videoRef}
                autoPlay
                muted
                loop={false}
                className="w-full h-3/4 opacity-30 mx-auto my-auto object-cover"
            >
                <source src={videos[currentVidIndex]} type="video/mp4" />
                Your browser does not support the video tag.
            </video>
        </div>
    );
};

export default VideoBackground;
