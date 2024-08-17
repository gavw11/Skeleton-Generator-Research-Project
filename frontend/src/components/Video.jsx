import React from 'react'
import demoVideo from '../assets/demo_vid-skeleton.mp4'

const Video = () => {
  return (
    <div>
      <video autoPlay loop muted className="rounded-lg w-1/2 border">
        <source src={demoVideo} type="video/mp4"/>
      </video>
    </div>
  )
}

export default Video