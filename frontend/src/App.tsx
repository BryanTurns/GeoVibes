import React from "react";
// import logo from "./logo.svg";
import "./App.css";
// import MapChart from "./MapChart";
import Map from "./MyMap";
import Hero from "./components/Hero";
import Navbar from "./components/Navbar";

function App() {
  return (
    <div className="App">
      <div className="max-w-[100vw]">
      <Navbar/>
      <Hero/>
      </div>
      <div className="py-10 px-5">
        <h2 className="text-2xl font-bold font-kadwa">News from around the world</h2>
        <Map></Map>
      </div>
      {/* <Map /> */}
    </div>
  );
}

export default App;
