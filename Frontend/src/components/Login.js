import React, { useState } from 'react';
import {Box,Button,Typography,MenuItem,Select,InputLabel,FormControl,
} from '@mui/material';
import wallpaper_background from "../assets/wallpaper.jpg";
import { useNavigate } from 'react-router-dom';

const ImageUpload = () => {
  const [title, setitle] = useState('');

  const [resume, setSelectedResume] = useState(null);

  const navigate = useNavigate();

  const onResumeChange = (event) => {

    const resumefile = event.target.files[0];

    if (resumefile && resumefile.type === 'application/pdf') 
      {

      setSelectedResume(resumefile);

    } 
    else 
    {
      alert('Please upload a valid resume pdf file.');
    }
  };

  const handleTitleChange = (event) => {
    setitle(event.target.value);
  };

  const onSubmit = async (event) => {
    event.preventDefault();

    if (!title || !resume)
       {
      alert('Please select a job title and upload a resume.');
      return;
    }

    const formData = new FormData();

    formData.append('jobTitle', title);
    formData.append('resume', resume);


    try {
      const response = await fetch('http://3.141.29.233:5000/upload_data', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        console.log('Upload successful');
        alert('Form submitted successfully!');

        const filename_prefix = resume.name.split('.')[0]; 
        navigate(`/home?filename=${filename_prefix}`);
      } 
      else {

        console.error(' File Upload failed');
      }
    } catch (error) {
      console.error('Error:', error);
    }

    onClear();
  };

  const onClear = () => {
    setSelectedResume(null);
    setitle('');
  };

  return (
    <fragment>
      <div
        style={{
          width: "100%",
          height: 780,
          backgroundImage: `url(${wallpaper_background})`,
          backgroundPosition: "center",
          marginTop: -30,
          paddingTop: 70,
          backgroundSize: "cover",
          backgroundRepeat: "no-repeat",
          opacity: 0.8,
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
              backgroundColor: "white",
              borderRadius: "2vh",
              opacity: 0.8,
              marginLeft: "auto",
              marginRight: "auto",
              marginTop: 8,
              padding: "2rem",
              maxWidth: 480,
            }}
          >
            <Typography variant="h6" align="center" gutterBottom>
              Upload Your Resume and Select Job Title
            
            </Typography>

            <form onSubmit={onSubmit}>
              
              <FormControl fullWidth variant="standard" margin="normal">
                
                <InputLabel>Job Title</InputLabel>

                <Select
                  value={title}
                  onChange={handleTitleChange}
                  required
                >
                  <MenuItem value={"Software Developer"}>Software Developer</MenuItem>
                  <MenuItem value={"GCP Data Engineer"}>Cloud Architect</MenuItem>
                </Select>
              </FormControl>

              <Button
                variant="contained"
                component="label"
                sx={{ mt: 2 }}
              >
                Upload Resume (PDF)
                <input
                  type="file"
                  hidden
                  accept="application/pdf"
                  onChange={onResumeChange}
                  required
                />
              </Button>

              {resume && (
                <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
                  {resume.name}
                </Typography>
              )}

              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={!title || !resume}
                >
                  Submit
                </Button>
                <Button
                  variant="outlined"
                  color="primary"
                  onClick={onClear}
                  disabled={!resume && !title}
                >
                  Clear
                </Button>
              </Box>
            </form>
          </Box>
        </div>
      </div>
    </fragment>
  );
};

export default ImageUpload;