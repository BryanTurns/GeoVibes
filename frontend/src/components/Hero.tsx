import React from 'react'
import globe from "../images/world-globe.jpg"
import {FiChevronsDown} from "react-icons/fi"
export default function Hero() {
  return (
    <div className='w-full relative'>
      <div className='absolute inset-0 flex flex-col items-start px-10 justify-center bg-transparent'>
        <div className='flex flex-col items-start gap-2'>
          <h1 className=' text-left text-4xl font-bold font-kadwa '>Check vibes about news</h1>
          <p className='text-left text-xl'>Read news and check how it's covered around the globe</p>
          <button className='bg-[#d80000] px-3 py-2  font-sans font-bold  text-white'>Start Reading</button>
        </div>
      </div>
      <div className='absolute left-0 right-0 bottom-0 text-[#d80000] text-5xl flex flex-col items-center'>
        
        <FiChevronsDown/>
      </div>
      <img src={globe} className="w-full h-[100vh] object-cover  "   alt=""/>
    </div>
  )
}
