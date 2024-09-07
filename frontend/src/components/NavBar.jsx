import React from 'react'

const NavBar = () => {
  return (
          <nav className="sticky w-full py-3 top-0 backdrop-blur-md border-b border-neutral-700/80 z-50">
            <div className="container flex justify-between text-xl items-center">
              <h1 className="text-3xl py-3 px-5  font-semibold lg:text-5xl lg:px-14 ">Skel<span style={{ background: 'linear-gradient(90deg, rgb(206, 210, 104) 10.624%, rgb(106, 255, 237) 87.742%, rgb(0, 153, 73) 112.805%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                display: 'inline-block',
               }}>AI</span></h1>
              <div className="">
                <a href="https://github.com/gavw11/Skeleton-Generator-Research-Project/tree/main" target="_blank" rel="noopener noreferrer" className="py-3 px-5 text-[0.9rem] lg:px-14 lg:text-xl">About Project</a>
              </div>
            </div>
          </nav>
  )
}

export default NavBar
