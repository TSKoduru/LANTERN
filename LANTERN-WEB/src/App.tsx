import lanternLogo from './assets/logo.png'
import {useCallback} from 'react'
import './App.css'
import {useDropzone} from 'react-dropzone'

function MyDropzone() {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Hide the dropzone
    const dropzone = document.getElementsByClassName('file-drop')[0]
    if (dropzone) {
      dropzone.classList.add('hidden')
    }

    // Display the file in the file viewer div
    // Make sure to only display the first file

    const file = acceptedFiles[0]
    const fileViewer = document.querySelector('.file-viewer')

    if (fileViewer) {
      fileViewer.innerHTML = '<img src="' + URL.createObjectURL(file) + '" />'
    }

    // Convert the image to base64, and send it to the backend
    const reader = new FileReader()
    reader.onload = function() {
      console.log(reader.result)
      const base64 = reader.result
      const xhr = new XMLHttpRequest()
      xhr.open('POST', 'http://127.0.0.1:5000/classify')
      xhr.setRequestHeader('Content-Type', 'application/json')
      xhr.send(JSON.stringify({image: base64}))
      xhr.onload = function() {
        const response = JSON.parse(xhr.responseText)
        console.log(response)
        const result = document.getElementById('result')
        if (result) {
          // Round result to 2 digits past the decimal

          result.innerHTML = (response['classification'] * 100).toFixed(2) + '%'
        }
      }
    }

    reader.readAsDataURL(file)


    // Make sure the results section is visible (Remove the hidden class)
    const results = document.getElementsByClassName('results')[0]

    if (results) {
      results.classList.remove('hidden')
    }

  }, [])
  const {getRootProps, getInputProps} = useDropzone({onDrop})

  return (
    <div {...getRootProps()}>
      <input{...getInputProps()} />
      {
        <div>
          <h2>Click <a>here</a> to add a file!.</h2>
          <p> Note that large or off-domain images might not yield accurate results.</p>
        </div>
      }
    </div>
  )
}

function reset() {
  const dropzone = document.getElementsByClassName('file-drop')[0]
  if (dropzone) {
    dropzone.classList.remove('hidden')
  }

  const results = document.getElementsByClassName('results')[0]
  if (results) {
    results.classList.add('hidden')
  }

  const fileViewer = document.querySelector('.file-viewer')
  if (fileViewer) {
    fileViewer.innerHTML = ''
  }
}


function App() {

  return (
    <>
      <img src={lanternLogo} className="lantern-logo" alt="LANTERN" />
      <h1>LANTERN</h1>
      <h3>AI-powered Lyme disease detection</h3>
      <p>By Teja Koduru </p>
      <hr />
      <div className="file-drop">
        <MyDropzone />
      </div>

      <div className = 'results hidden'>
        <div className = 'file-viewer'> </div>
        <h3 className = 'results-text'> This has a <a id = 'result'> 0% </a> likelihood of being a Lyme disease rash.</h3>
        <button className = 'results-button' onClick={reset}>Try another image?</button>
      </div>
    </>
  )
}

export default App
