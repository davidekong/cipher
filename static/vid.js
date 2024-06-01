const demosSection = document.getElementById('demos');
const video = document.getElementById("webcam");
const liveView = document.getElementById('liveView');
const enableWebcamButton = document.getElementById('webcamButton');

var model = undefined;
var children = [];
var hand_model = undefined;

document.body.classList.add('blurred');


// Before we can use COCO-SSD class we must wait for it to finish loading.
cocoSsd.load().then(function (loadedModel) {
  model = loadedModel;
  demosSection.classList.remove('invisible');
});


function hasGetUserMedia() {
  return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
}

if (hasGetUserMedia()) {
  enableWebcamButton.addEventListener('click', enableCam);
} else {
  console.warn('getUserMedia() is not supported by your browser');
}

function enableCam(event) {
  if (!model) {
    console.log('Wait! Model not loaded yet.');
    return;
  }


  const constraints = {
    video: true
  };

  navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
    video.srcObject = stream;
    video.addEventListener('loadeddata', function () {
      document.body.classList.remove('blurred');
      predictWebcam();
    });
  }).catch(function (error) {
    console.error('Error accessing webcam: ', error);
  });
}

function predictWebcam() {
  
  model.detect(video).then(function (predictions) {
    for (let i = 0; i < children.length; i++) {
      liveView.removeChild(children[i]);
    }
    children.splice(0);

    let cellPhoneDetected = false;
    for (let n = 0; n < predictions.length; n++) {
      if (predictions[n].score > 0.50) {
        if (predictions[n].class === 'cell phone') {
          cellPhoneDetected = true;
        }

        const p = document.createElement('p');
        p.innerText = predictions[n].class + ' - with ' 
            + Math.round(parseFloat(predictions[n].score) * 100) 
            + '% confidence.';
        p.style = 'left: ' + predictions[n].bbox[0] + 'px;' +
            'top: ' + predictions[n].bbox[1] + 'px;' + 
            'width: ' + (predictions[n].bbox[2] - 10) + 'px;';

        const highlighter = document.createElement('div');
        highlighter.setAttribute('class', 'highlighter');
        highlighter.style = 'left: ' + predictions[n].bbox[0] + 'px; top: '
            + predictions[n].bbox[1] + 'px; width: ' 
            + predictions[n].bbox[2] + 'px; height: '
            + predictions[n].bbox[3] + 'px;';

        liveView.appendChild(highlighter);
        liveView.appendChild(p);

        children.push(highlighter);
        children.push(p);
      }
    }

    if (cellPhoneDetected) {
      document.body.classList.add('blurred');
    } else {
      document.body.classList.remove('blurred');
    }
    // Disable right-click context menu
document.addEventListener('contextmenu', function(event) {
  event.preventDefault();
});


    window.requestAnimationFrame(predictWebcam);
  });
}
