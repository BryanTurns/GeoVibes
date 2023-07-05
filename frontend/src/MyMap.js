import React, { useState,useEffect } from 'react';
import { GeoJSON, MapContainer, TileLayer,Popup,Tooltip } from 'react-leaflet';
import "leaflet/dist/leaflet.css"
import data from "./custom.geo.json"
import axios from "axios"






const MyMap = () => {
  // const [center, setCenter] = useState([48.8566, 2.3522]);
  // const ZOOM_LEVEL = 9;
  const [isLoading,setIsLoading]  =useState(true)
  const [emotionData,setEmotionData] = useState([])
  useEffect( () =>{
    async function fetchData(){
      try{

        const {data} = await axios.get('https://geovibesbackend.onrender.com/api/getEmotions')
        setEmotionData(data)
        console.log(data)
        setIsLoading(false)
      }
      catch(error){
        console.log(error)
        // setIsLoading(true)
      }
    }
    fetchData()
  },[])
  const [sources,setSources] = useState([])
  const [tooltipContent,setTooltipContent] = useState("")
  const [emotion,setEmotion] = useState("happy")

  const style = (feature) =>{
    // console.log(feature.properties.iso_a2)
    let fillColor;
    const country =  emotionData.find(obj =>{
      
      return obj.countryCode.toLowerCase() === feature.properties.iso_a2.toLowerCase()
    })
    // console.log(country?.emotions?.Angry)
    
    let opacity;
    switch (emotion) {
      case 'happy':
        fillColor='green'
        if(country === undefined){
          opacity=1
        }
        else{

          opacity = country.emotions.Happy
          // console.log(opacity)
        }

        break;
      case 'fear':
        fillColor = "black"
        if(country === undefined){
          opacity=1
        }
        else{
        opacity = country.emotions.Fear
        }
        break;
      case 'anger':
        fillColor= "red"
        if(country === undefined){
          opacity=1
        }
        else{
        opacity = country.emotions.Angry
        }
        break
      case 'sad':
        fillColor = 'orange'
        if(country === undefined){
          opacity=1
        }
        else{
        opacity = country.emotions.Sad
        }
        break;
      case 'suprise':
        fillColor = 'blue'
        if(country === undefined){
          opacity=1
        }
        else{
        opacity = country.emotions.Surprise
        }
        break;
      default:
        fillColor = 'green'
        if(country === undefined){
          opacity=1
        }
        else{
          
        opacity = country.emotions.Happy
        }
        setEmotion('happy')
        break;
    }
    if(feature.properties.iso_a2 =="IN"){

      console.log(opacity)
    }
    return {
      fillColor: fillColor,
      weight: 1,
      opacity: 1,
      color: "white",
      // dashArray: "3",
      fillOpacity: opacity
    }
  }
  function handleMouseOver(e,feature){
    // const layer = e.target;
    // layer.setStyle({
    //   fillColor:"green"
    // })
    setTooltipContent(feature.properties.name)
    // if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
    //   layer.bringToFront();
    // }
  }
  const resetHighlight = (e) =>{
    e.target.setStyle({
      fillColor:"red"
    })
  }
  const handleClick = (e,feature) =>{
    // setSources(newsData.articles)
  }
  
  function onEachFeature(feature, layer) {
    layer.on({
      mouseover: (e) => {handleMouseOver(e,feature)},
      // mouseout: resetHighlight,
      click: (e) =>{handleClick(e,feature)}
    });
  }

  if(!isLoading){
    
  
  return (
    
    <>

    <MapContainer center={[48.8566, 2.3522]} zoom={2} zoomControl={false}   >
      {/* OPEN STREEN MAPS TILES */}
      <TileLayer
        attribution={`<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>`}
        url="https://api.maptiler.com/maps/basic-v2/256/{z}/{x}/{y}.png?key=Uh3uIcsVZjDBcvtIfe9C"
      />
      {data && (
        <GeoJSON key='hel' data={data} style={style} onEachFeature={onEachFeature} >
          <Popup className="">
            <h1 className='text-xl font-bold'>Soruces</h1>
            <div className='flex flex-col w-full '>

            {sources.map((article)=>{
              return <>
                <a href={article.url} style={{fontSize:"1rem",width:"100%"}} target="_blank">1. {article.text}</a>
                <a href={article.url} style={{fontSize:"1rem",width:"100%"}} target="_blank">1. {article.text}</a>
                <a href={article.url} style={{fontSize:"1rem",width:"100%"}} target="_blank">1. {article.text}</a>
                <a href={article.url} style={{fontSize:"1rem",width:"100%"}} target="_blank">1. {article.text}</a>
                <a href={article.url} style={{fontSize:"1rem",width:"100%"}} target="_blank">1. {article.text}</a>
              </>
            })}
            </div>
          </Popup>
          <Tooltip sticky >{tooltipContent}</Tooltip>
        </GeoJSON>
      )}
     


    </MapContainer>
    <div className='flex flex-col items-start py-4'>
    <h3 className='text-xl font-kadwa'>Select an emotion</h3>
    <div className="flex gap-2">
    <button className='text-white bg-green-500 px-3 py-2 rounded' onClick={()=>setEmotion("happy")}>happiness</button>
    <button className='text-white bg-red-500 px-3 py-2 rounded' onClick={()=>setEmotion("anger")}>anger</button>
    <button className='text-white bg-black px-3 py-2 rounded' onClick={()=>setEmotion("fear")}>fear</button>
    <button className='text-white bg-orange-500 px-3 py-2 rounded' onClick={()=>setEmotion("sad")}>sad</button>
    <button className='text-white bg-blue-500 px-3 py-2 rounded' onClick={()=>setEmotion("suprise")}>supprise</button>
    </div>
    </div>
    </>
    
  );
  }
  else{
    return(<h3>Loading</h3>)
  }
};

export default MyMap;
