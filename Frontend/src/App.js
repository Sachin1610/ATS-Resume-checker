import logo from './logo.svg';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css';
import Home from './components/Home';
import Upload from './components/Upload'; 


function App() {
    return (
      
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Upload />} />
            <Route path="/home" element={<Home />} />
          
          </Routes>
        </BrowserRouter>
     
    );
  }
  
  export default App;