import { useState } from "react";

import "./App.css";
import TextField from "@mui/material/TextField";
import { Button } from "@mui/material";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";

function App() {
  const [message, setMessage] = useState("");
  const [isToxic, setIsToxic] = useState(-1);
  const [isFething, setIsFetching] = useState(false);
  const handleMessageChange = (event) => {
    // 👇️ access textarea value
    setMessage(event.target.value);
  };

  const fetchIsToxic = async () => {
    setIsFetching(true);
    const res = await fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      headers: {
        "Content-type": "application/json",
      },
      body: JSON.stringify({
        text: message,
      }),
    });

    setIsFetching(false);

    const toxic = await res.json();
    console.log(toxic.result);
    setIsToxic(toxic.result);
  };

  const handleOnClick = (e) => {
    fetchIsToxic();
  };

  const showAlert = () => {
    if (isToxic === -1) {
      return <></>;
    } else if (isToxic === 1) {
      return <Alert severity="success">This is a friendly sentence : ）</Alert>;
    } else if (isToxic === 0) {
      return <Alert severity="error">This is not a polite sentence ：（</Alert>;
    }
  };

  return (
    <div className="App">
      <h1>TOXIC WORDS DETECTION</h1>
      <h2>Input Your Words And Click The Button</h2>
      <TextField
        id="outlined-multiline-static"
        sx={{ width: "50ch" }}
        label="Text"
        multiline
        rows={10}
        variant="outlined"
        onChange={handleMessageChange}
      />

      {isFething ? (
        <CircularProgress />
      ) : (
        <Button
          sx={{ margin: "25px" }}
          variant="contained"
          onClick={handleOnClick}
        >
          DETECT
        </Button>
      )}
      {showAlert()}
    </div>
  );
}

export default App;
