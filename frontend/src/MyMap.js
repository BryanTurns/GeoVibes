import React, { useState } from 'react';
import { GeoJSON, MapContainer, TileLayer,Popup,Tooltip } from 'react-leaflet';
import "leaflet/dist/leaflet.css"
import data from "./custom.geo.json"

const newsData = {
  "countryCode": "JP",
  "articles": [
     {
       "title": "Something",
       "text": "Something something something something.",
        "url": "https://bbc.com/something",
        "image": "https://bbc.com/image.jpg",
        "publish_date": "2023-06-03 20:20:55",             "author": "admin", 
        "language": "en", 
        "source_country": "af", 
        "sentiment": -0.191,
        "emotions": {
          'Angry': 0.03975000000000001, 
          'Fear': 0.4335, 
          'Happy': 0.14325000000000002, 
          'Sad': 0.19875000000000004, 
          'Surprise': 0.16075
        }
      },
      
     ]
  }




const MyMap = () => {
  // const [center, setCenter] = useState([48.8566, 2.3522]);
  // const ZOOM_LEVEL = 9;
  const [sources,setSources] = useState([])
  const [tooltipContent,setTooltipContent] = useState("")
  const [emotion,setEmotion] = useState("happy")
  const style = (feature) =>{
    let fillColor;
    switch (emotion) {
      case 'happy':
        fillColor='green'
        break;
      case 'fear':
        fillColor = "black"
        break;
      case 'anger':
        fillColor= "red"
        break
      case 'sad':
        fillColor = 'orange'
        break;
      case 'suprise':
        fillColor = 'blue'
        break;
      default:
        fillColor = 'green'
        setEmotion('happy')
        break;
    }
    return {
      fillColor: fillColor,
      weight: 1,
      opacity: 1,
      color: "white",
      // dashArray: "3",
      fillOpacity: 0.6
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
    setSources(newsData.articles)
  }
  
  function onEachFeature(feature, layer) {
    layer.on({
      mouseover: (e) => {handleMouseOver(e,feature)},
      // mouseout: resetHighlight,
      click: (e) =>{handleClick(e,feature)}
    });
  }

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
};

export default MyMap;
