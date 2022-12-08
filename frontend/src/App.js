import { useRef, useState } from "react";

import "./App.css";
import TextField from "@mui/material/TextField";
import { Button } from "@mui/material";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";

function App() {
  const [message, setMessage] = useState("");
  const [isToxic, setIsToxic] = useState([]);
  const [isFething, setIsFetching] = useState(false);
  const [isShowResult, setIsShowResult] = useState(false);
  const [sents, setSents] = useState([]);
  const ref = useRef(null);
  const handleMessageChange = (event) => {
    // 👇️ access textarea value
    setMessage(event.target.value);
  };

  const fetchIsToxic = async () => {
    setSents(ref.current.value.split("\n"));
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
    setIsToxic(toxic.result);
    setIsShowResult(true);
  };

  const handleOnClick = (e) => {
    if (isShowResult === true){
      setIsShowResult(false)
    }else {
      fetchIsToxic();
    }
  };

  // const showAlert = () => {
  //   if (isToxic === -1) {
  //     return <></>;
  //   } else if (isToxic === 1) {
  //     return <Alert severity="success">This is a friendly sentence : ）</Alert>;
  //   } else if (isToxic === 0) {
  //     return <Alert severity="error">This is not a polite sentence ：（</Alert>;
  //   }
  // };

  return (
    <div className="App">
      <h1>TOXIC WORDS DETECTION</h1>
      <h2>Input Your Words And Click The Button</h2>
      {isShowResult ? (
        <>
          {sents?.map((s, i) => (
            <Alert sx={{width: "50ch", marginBottom: "5px"}} key={i} severity={isToxic[i] === 1 ? "success" : "waring"}>
              {" "}
              {s}{" "}
            </Alert>
          ))}
        </>
      ) : (
        <TextField
          id="outlined-multiline-static"
          sx={{ width: "50ch" }}
          label="Text"
          multiline
          rows={10}
          variant="outlined"
          onChange={handleMessageChange}
          inputRef={ref}
        />
      )}

      {isFething ? (
        <CircularProgress />
      ) : (
        <Button
          sx={{ margin: "25px" }}
          variant="contained"
          onClick={handleOnClick}
        >
         {isShowResult ? "INPUT" : "DETECT"}
        </Button>
      )}
    </div>
  );
}

export default App;
