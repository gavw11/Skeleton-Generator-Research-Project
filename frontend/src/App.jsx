import React from 'react'
import SkelGen from './components/SkelGen'
import NavBar from './components/NavBar'
import Video from './components/Video'

function App() {

  return (
    <>
        <NavBar/>
        <div className="pt-3">
          <SkelGen/>
        </div> 
        <Video/>
       
    </>
  )
}

export default App
