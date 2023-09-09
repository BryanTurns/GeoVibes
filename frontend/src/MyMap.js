import React, { useState, useEffect } from "react";
import {
  GeoJSON,
  MapContainer,
  TileLayer,
  Popup,
  Tooltip,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import data from "./custom.geo.json";
import axios from "axios";

const MyMap = () => {
  // const [center, setCenter] = useState([48.8566, 2.3522]);
  // const ZOOM_LEVEL = 9;
  const [isLoading, setIsLoading] = useState(true);
  const [emotionData, setEmotionData] = useState([]);
  useEffect(() => {
    async function fetchData() {
      try {
        const { data } = await axios.get(
          "https://geovibesbackend.onrender.com/api/getEmotions"
        );
        setEmotionData(data);

        setIsLoading(false);
      } catch (error) {
        console.log(error);
        // setIsLoading(true)
      }
    }
    fetchData();
  }, []);
  const [sources, setSources] = useState([]);
  const [tooltipContent, setTooltipContent] = useState("");
  const [emotion, setEmotion] = useState("Happy");
  const [isSourceLoading, setIsSourceLoading] = useState(false);

  const style = (feature) => {
    let fillColor;
    const country = emotionData.find((obj) => {
      return (
        obj.countryCode.toLowerCase() ===
        feature.properties.iso_a2_eh.toLowerCase()
      );
    });
    console.log("TEST 1: ");
    console.log(emotionData);
    console.log(emotion);
    let opacity = getOpacityByPercentile(
      emotionData,
      emotion,
      country?.countryCode
    );

    switch (emotion) {
      case "Happy":
        fillColor = "green";
        break;
      case "Fear":
        fillColor = "black";
        break;
      case "Anger":
        fillColor = "red";
        break;
      case "Sad":
        fillColor = "orange";
        break;
      case "Surprise":
        fillColor = "blue";
        break;
      default:
        fillColor = "green";
        setEmotion("happy");
        break;
    }

    if (country === undefined || country.emotions.Angry === 0) {
      opacity = 1;
      fillColor = "gray";
    }

    return {
      fillColor: fillColor,
      weight: 1,
      opacity: 1,
      color: "white",
      // dashArray: "3",
      fillOpacity: opacity,
    };
  };
  function handleMouseOver(e, feature) {
    setTooltipContent(feature.properties.name);
  }

  const handleClick = async (e, feature) => {
    setIsSourceLoading(true);
    const { data } = await axios.get(
      `https://geovibesbackend.onrender.com/api/getCountryNews/${feature.properties.iso_a2}`
    );
    setSources(data.articles.splice(0, 5));
    setIsSourceLoading(false);
  };

  function onEachFeature(feature, layer) {
    layer.on({
      mouseover: (e) => {
        handleMouseOver(e, feature);
      },
      click: (e) => {
        handleClick(e, feature);
      },
    });
  }

  if (!isLoading) {
    return (
      <>
        <MapContainer center={[48.8566, 2.3522]} zoom={2} zoomControl={false}>
          {/* OPEN STREEN MAPS TILES */}
          <TileLayer
            key="tile"
            attribution={`<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>`}
            url="https://api.maptiler.com/maps/basic-v2/256/{z}/{x}/{y}.png?key=Uh3uIcsVZjDBcvtIfe9C"
          />
          {data && (
            <GeoJSON
              key="hel"
              data={data}
              style={style}
              onEachFeature={onEachFeature}
            >
              <Popup className="" key="popup">
                <h1 className="text-xl font-bold">Sources</h1>
                <div className="flex flex-col w-full ">
                  {sources.map((article, index) => {
                    return (
                      <p key={index} className="m-0">
                        {isSourceLoading ? (
                          <b className="text">Loading ...</b>
                        ) : (
                          <>
                            <b className="font-bold m-0">{index + 1}.</b>
                            <a
                              href={article.url}
                              style={{ fontSize: "1rem", width: "100%" }}
                              target="_blank"
                            >
                              {" "}
                              {article.title}
                            </a>
                          </>
                        )}
                      </p>
                    );
                  })}
                </div>
              </Popup>
              <Tooltip sticky>{tooltipContent}</Tooltip>
            </GeoJSON>
          )}
        </MapContainer>
        <div className="flex flex-col items-start py-4">
          <h3 className="text-xl font-kadwa">Select an emotion</h3>
          <div className="flex gap-2">
            <button
              className="text-white bg-green-500 px-3 py-2 rounded"
              onClick={() => setEmotion("Happy")}
            >
              happiness
            </button>
            <button
              className="text-white bg-red-500 px-3 py-2 rounded"
              onClick={() => setEmotion("Anger")}
            >
              anger
            </button>
            <button
              className="text-white bg-black px-3 py-2 rounded"
              onClick={() => setEmotion("Fear")}
            >
              fear
            </button>
            <button
              className="text-white bg-orange-500 px-3 py-2 rounded"
              onClick={() => setEmotion("Sad")}
            >
              sad
            </button>
            <button
              className="text-white bg-blue-500 px-3 py-2 rounded"
              onClick={() => setEmotion("Surprise")}
            >
              supprise
            </button>
          </div>
        </div>
      </>
    );
  } else {
    return <h3>Loading</h3>;
  }
};

function sortByEmotion(countryData, emotion) {
  countryData.sort((a, b) => {
    return a.emotions[emotion] - b.emotions[emotion];
  });
  return countryData;
}

function getOpacityByPercentile(countryData, emotion, countryCode) {
  countryData = sortByEmotion(countryData, emotion);

  let conversionFactor = 0.0035;

  for (let i = 0; i < countryData.length; i++) {
    if (countryData[i].countryCode == countryCode) {
      if (countryData[i].emotions[emotion] == 0) {
        return 0;
      } else if (i * conversionFactor > 1) {
        return 1;
      }

      return Math.pow(i / countryData.length, 2);
    }
  }
}

export default MyMap;
