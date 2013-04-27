//
// Acknowledgement
// This code follows an example of pitch detection from https://github.com/cwilso/PitchDetect
//

//
// Documentation on webAudio can be found at:
// http://docs.webplatform.org/wiki/apis/webaudio/
// https://dvcs.w3.org/hg/audio/raw-file/tip/webaudio/specification.html
//


// The AudioContext represents a set of AudioNode objects and their connections
var audioContext;

// Should the audio loop?
var loopAudio = true;

// Is the audio currently playing?
var isPlaying = false;

// The audio source
var sourceNode = null;

// Node for real-time analysis
var analyser = null;

// Audio data
var theBuffer = null;

// Audio analysis output to screen
var detectorElem, 
	canvasElem,
	pitchElem,
	noteElem,
	detuneElem,
	detuneAmount;


window.onload = function() {

	//
	// Verify browser support
	//
	function init() {
		try {
	    	audioContext = new webkitAudioContext();
	  	}
	  	catch(e) {
	    	alert('Web Audio API is not supported in this browser');
	  	}
	}
	init();


	//
	// Get audio buffer
	//
	var request = new XMLHttpRequest();
// TO-DO - get uploaded file with vizualizrfile in line below
// trigger with form post, no Python?
	request.open("GET", "vizualizrfile", true);
	request.responseType = "arraybuffer";

	request.onload = function() {
	  	
	  	console.log('audio loaded');
	  	
	  	// Asynchronously decode the audio file data contained in the ArrayBuffer
	  	audioContext.decodeAudioData( request.response, function(buffer) { 
    		
    		theBuffer = buffer;
    		
    		togglePlayback();
			
		});
		
	}

	request.send();

	//
	// Get elements for audio analysis output to screen
	//
	detectorElem = document.getElementById( "detector" );
	canvasElem = document.getElementById( "output" );
	pitchElem = document.getElementById( "pitch" );
	noteElem = document.getElementById( "note" );
	detuneElem = document.getElementById( "detune" );
	detuneAmount = document.getElementById( "detune_amt" );

	// 
	// Drag and drop audio file
	//
// TO-DO - how can Chrome be told to upload the audio file, rather than play it ondrop?
	/*
	detectorElem.ondragenter = function () { 
		this.classList.add("droptarget"); 
		return false; };

	detectorElem.ondragleave = function () { this.classList.remove("droptarget"); return false; };
	
	detectorElem.ondrop = function (e) {
  		this.classList.remove("droptarget");
  		e.preventDefault();
		theBuffer = null;

	  	var reader = new FileReader();
	  	reader.onload = function (event) {
	  		audioContext.decodeAudioData( event.target.result, function(buffer) {
	    		theBuffer = buffer;
	    		console.log('loaded-123');
	    		togglePlayback();
	  		}, function(){alert("error loading!");} ); 

	  	};
	  	reader.onerror = function (event) {
	  		alert("Error: " + reader.error );
		};
	  	reader.readAsArrayBuffer(e.dataTransfer.files[0]);
	  	return false;
	};
	*/

}


//
// Audio output to browser
//
function togglePlayback() {

    var now = audioContext.currentTime;

    // Is the audio playing? Defaults to false
    if (isPlaying) {
        // Stop playing and return
        sourceNode.noteOff( now );
        sourceNode = null;
        analyser = null;
        isPlaying = false;
        webkitCancelAnimationFrame( rafID );
        return "start";
    }

    // Create a audio source
    sourceNode = audioContext.createBufferSource();

    // Provide actual audio to source
    sourceNode.buffer = theBuffer;

    // Loop audio?
    sourceNode.loop = loopAudio;

    // createAnalyser() represents a node which is able to provide real-time frequency and time-domain analysis information
    // The size of the analyser.fftSize (FFT) used for frequency-domain analysis defaults to 2048
    analyser = audioContext.createAnalyser();
    
    // The size of the FFT used for frequency-domain analysis. This must be a power of two.
    //analyser.fftSize = 2048;// Really need to set this? Default value is 2048 - https://dvcs.w3.org/hg/audio/raw-file/tip/webaudio/specification.html
    
    // Connect analyser to audio source
    sourceNode.connect( analyser );
    
    // Connect the audio to the the speakers
    analyser.connect( audioContext.destination );
    
    // Play audio now
    sourceNode.noteOn( now );

    isPlaying = true;
    isLiveInput = false;
    
    updatePitch();

    return "stop";

}


//
// Audio analysis
//

// assigned to window.webkitRequestAnimationFrame
var rafID = null;

//var tracks = null;

// buffer length
var buflen = 1024;

// buffer array
var buf = new Uint8Array( buflen );

// level of minimum detected signal 
// 128 == zero
var MINVAL = 134;


// 
// Positive next positive point in sound wave oscillation
//
function findNextPositiveZeroCrossing( start ) {
	
	var i = Math.ceil( start );
	var last_zero = -1;
	
	// Advance until we're zero or negative
	while (i < buflen && (buf[i] > 128 ) )
		i++;
	if (i >= buflen)
		return -1;

	// Advance until we're above MINVAL, keeping track of last zero
	while (i < buflen && ((t=buf[i]) < MINVAL )) {
		
		if (t >= 128) {
			if (last_zero == -1)
				last_zero = i;
		
		} else
			last_zero = -1;
		
		i++;

	}

	// We may have jumped over MINVAL in one sample
	if (last_zero == -1)
		last_zero = i;

	// We didn't find any more positive zero crossings
	if (i == buflen)
		return -1;

	// The first sample might be a zero
	// If so, return it
	if (last_zero == 0)
		return 0;

	// Otherwise, the zero might be between two values, so we need to scale it
	var t = ( 128 - buf[last_zero - 1] ) / (buf[last_zero] - buf[last_zero - 1]);

	return last_zero + t;

}


var noteStrings = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];


function updatePitch( time ) {

	var cycles = new Array;

	// Copy the current time-domain (waveform) data into var buf, the passed unsigned byte array
	analyser.getByteTimeDomainData( buf );

	var i = 0;

	// Find the first point
	var last_zero = findNextPositiveZeroCrossing( 0 );

	var n = 0;

	// Keep finding points, adding cycle lengths to array
	while ( last_zero != -1) {
		var next_zero = findNextPositiveZeroCrossing( last_zero + 1 );
		if (next_zero > -1)
			cycles.push( next_zero - last_zero );
		last_zero = next_zero;

		n++;
		if (n > 1000)
			break;
	}


//
// TO-DO - need to use getByteFrequencyData ?
//

	// Average the array
	var num_cycles = cycles.length;
	var sum = 0;
	var pitch = 0;

	for (var i = 0; i < num_cycles; i++) {
		sum += cycles[i];
	}

	if (num_cycles) {
		sum /= num_cycles;
		pitch = audioContext.sampleRate/sum;
	}


 	// Output to html elements
 	if (num_cycles == 0) {

	 	pitchElem.innerText = "--";
		noteElem.innerText = "-";
		detuneElem.className = "";
		detuneAmount.innerText = "--";

 	} else {

	 	pitchElem.innerText = Math.floor( pitch );
	 	var note =  noteFromPitch( pitch );
		noteElem.innerText = noteStrings[note%12];
		var detune = centsOffFromPitch( pitch, note );
		
		if (detune == 0 ) {
			detuneElem.className = "";
			detuneAmount.innerText = "--";
		} else {
			if (detune < 0)
				detuneElem.className = "flat";
			else
				detuneElem.className = "sharp";
			detuneAmount.innerText = Math.abs( detune );
		}
	}

	rafID = window.webkitRequestAnimationFrame( updatePitch );

}


function noteFromPitch( frequency ) {
	var noteNum = 12 * (Math.log( frequency / 440 )/Math.log(2) );
	return Math.round( noteNum ) + 69;
}


function frequencyFromNoteNumber( note ) {
	return 440 * Math.pow(2,(note-69)/12);
}


function centsOffFromPitch( frequency, note ) {
	return Math.floor( 1200 * Math.log( frequency / frequencyFromNoteNumber( note ))/Math.log(2) );
}


//
// Live input support
//

// TO-DO - Is this only needed to accommodate computers with 1-2 speakers ?
function convertToMono( input ) {
    
    // Split audio to channels
    var splitter = audioContext.createChannelSplitter(2);
    var merger = audioContext.createChannelMerger(2);

    input.connect( splitter );
    splitter.connect( merger, 0, 0 );
    splitter.connect( merger, 0, 1 );

    return merger;

}


function getUserMedia( dictionary, callback ) {
    
    try {
        navigator.webkitGetUserMedia(dictionary, callback, error);
    } catch (e) {
        alert('webkitGetUserMedia threw exception :' + e);
    }

}


function gotStream( stream ) {

    // Create an AudioNode from the stream.
    var mediaStreamSource = audioContext.createMediaStreamSource(stream);

    // Connect it to the destination.
    analyser = audioContext.createAnalyser();
    //analyser.fftSize = 2048; // this is the default
    convertToMono( mediaStreamSource ).connect( analyser );
    updatePitch();

}


function toggleLiveInput() {
    getUserMedia({audio:true}, gotStream);
}


function error() {
    alert('Stream generation failed.');
}


//
// ** removed from updatePitch()
//
// confidence = num_cycles / num_possible_cycles = num_cycles / (audioContext.sampleRate/)
//	var confidence = (num_cycles ? ((num_cycles/(pitch * buflen / audioContext.sampleRate)) * 100) : 0);


//	console.log(
//		"Cycles: " + num_cycles +
//		" - average length: " + sum +
//		" - pitch: " + pitch + "Hz " +
//		" - note: " + noteFromPitch( pitch ) +
//		" - confidence: " + confidence + "% "
//		);


	// possible other approach to confidence: sort the array, take the median; go through the array and compute the average deviation

 //	detectorElem.className = (confidence>50)?"confident":"vague";
	// TODO: Paint confidence meter on canvasElem here.
