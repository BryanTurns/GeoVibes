# Backend
Start the project by entering the backend folder. The backend is responsible for pulling data from news APIs, processing said data, and providing an API for the frontend to interact with the data saved in 'news.json' and 'emotions.json'. To start using this API Set up a venv and install the required dependancies. Next simply run the ```app.py``` file This will start the flask server that provides the API. 

# Frontend
To use the frontend designed for this project enter the 'frontend' folder. Next install all the required dependancies ('npm install'). Finally run 'npm start' and the frontend will start running using an online server that has already been setup. If the code is running properly the following map should be generated:
<img width="1186" alt="image" src="https://github.com/BryanTurns/GeoVibes/assets/95263942/07857c1f-ddac-4d5c-b85a-f2645c8848a9">


# IMPORTANT NOTES
The web server the frontend is connected to takes a while to spin up. This means on first loading into the frontend page it may take a few minutes before data can be succesfully pulled. An example of this behavior can be seen bellow. 
<img width="1189" alt="image" src="https://github.com/BryanTurns/GeoVibes/assets/95263942/57001170-16c4-44bb-8652-efd4ef5ab7d5">

