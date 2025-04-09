import React, { useState, useEffect } from 'react';
import { Button, Typography, Box, List, ListItem, ListItemText } from '@mui/material';
import wallpaper_background from "../assets/wallpaper.jpg";
import axios from 'axios';
import { useLocation } from 'react-router-dom';

const HomePage = () => {
  const [loading, setLoadingData] = useState(false);
  const [formData, setformData] = useState(null);
  const [error, setError] = useState(null);
  const loc = useLocation();

  useEffect(() => {
    const searchArgs = new URLSearchParams(loc.search);
    const resumefilename = searchArgs.get('filename');

    if (resumefilename) {
      onRefresh(resumefilename);
    }
  }, [loc.search]);

  const onRefresh = async (filename) => {
    setLoadingData(true);
    setError(null);

    try {
      const response = await axios.get(
        `http://3.141.29.233:5000/get_recommended_courses?filename_prefix=${filename}`
      );
      setformData(response.data);
    } 
    catch (err) 
    
    {
      setError(err.message);
    } 
    
    finally 
    
    {
      setLoadingData(false);
    }
  };

  return (
    <fragment>
      <div
        style={{
          width: "100%",
          backgroundRepeat: "no-repeat",
          backgroundImage: `url(${wallpaper_background})`,
          backgroundPosition: "center",
          opacity: 0.8,
          height: 780,
          marginTop: -30,
          paddingTop: 70,
          backgroundSize: "cover"
        }}
      >
        <Typography
          variant="h3"
          color="white"
          sx={{
            marginTop: "5vh",
            marginBottom: "10vh"
          }}
        >
          <b style={{ marginLeft: "20rem" }}>Course Recommendation System</b>
        </Typography>

        <div>
          <Box
            sx={{
              minWidth: 300,
              marginLeft: "auto",
              backgroundColor: "white",
              borderRadius: "2vh",
              opacity: 0.8,
              marginRight: "auto",
              marginTop: 8,
              padding: "2rem",
              maxWidth: 480,
            }}
          >
            <Typography variant="h6" align="center" gutterBottom>
              Recommended Courses
            </Typography>

            <Button
              variant="contained"
              color="primary"
              onClick={() => {
                const searchArgs = new URLSearchParams(loc.search);

                const filename = searchArgs.get('filename');

                if (filename) {
                  onRefresh(filename);
                }
              }}
              sx={{ mt: 2, display: 'block', margin: '0 auto' }}
            >
              Refresh
            </Button>

            {loading && <Typography>Loading Recommendations...</Typography>}

            {error && <Typography color="error">{error}</Typography>}
            {formData && (
              <Box mt={2}>
                <List>
                  
                  {formData.map((course, index) => (
                    <ListItem key={index}>

                      <ListItemText

                        primary={course.course_name}

                        secondary={`Provider: ${course.provider}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </Box>
        </div>
      </div>
    </fragment>
  );
};

export default HomePage;