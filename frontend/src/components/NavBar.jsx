import React from 'react'

const NavBar = () => {
  return (
        <>
          <nav className="sticky py-3 top-0 backdrop-blur-lg border-b  border-neutral-700/80">
            <div className="container flex justify-between text-xl items-center">
              <h1 className="text-5xl font-semibold px-10 py-3">Skel<span style={{ background: 'linear-gradient(90deg, rgb(206, 210, 104) 10.624%, rgb(106, 255, 237) 87.742%, rgb(0, 153, 73) 112.805%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                display: 'inline-block',
               }}>AI</span></h1>
              <a href="#" className="px-10 py-3">About Project</a>
            </div>
          </nav>
        </>
  )
}

export default NavBar
