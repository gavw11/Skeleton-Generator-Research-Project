import VideoBackground from "./VideoBackground"
import Generate from "./Generate"
import NavBar from "./NavBar"

const HeroSection = () => {
  return (
    <section className="w-full z-0">
      <NavBar/>
      <div className="fixed top-0 z-0 w-full">
        <VideoBackground/>
      </div>
      <div className='relative flex-col flex-wrap-reverse justify-center  w-full h-full py-5 px-3 z-40 lg:flex-nowrap'>
        <div className="flex flex-col items-center w-full pt-3 px-4">
            <h1 className="pb-10 pt-10 text-3xl md:text-7xl text font-semibold">
              <span className="bg-gradient-to-r from-green-200 to-green-500 bg-clip-text text-transparent">Skeletonize</span> Objects
            </h1>
            <h2 className="text-center text-xl md:text-3xl font-medium">
              Just Upload, Generate, & Download
            </h2>
            <p className="text-xs md:text-xl pt-11 font-light">
              Powered by YOLOv8, OpenCV, & Python
            </p>
        </div>
        <Generate/>
      </div>
    </section>
    )
}

export default HeroSection
