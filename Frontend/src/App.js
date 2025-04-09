import logo from './logo.svg';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './App.css';
import Home from './components/Home';



function App() {
    return (
      
        <BrowserRouter>
          <Routes>
            <Route path="/home" element={<Home />} />
          
          </Routes>
        </BrowserRouter> 
    );
  }
  
  export default App;
