<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>WinGo DM Style</title>

<meta name="viewport" content="width=device-width, initial-scale=1">

<style>

body{
background:#0b1220;
font-family:Arial;
color:white;
text-align:center;
margin:0;
}

.header{
background:#111827;
padding:15px;
font-size:22px;
font-weight:bold;
}

.card{
background:#1f2937;
margin:12px;
padding:18px;
border-radius:12px;
}

.big{color:#22c55e;font-size:34px}
.small{color:#ef4444;font-size:34px}

.pred{font-size:40px;margin:8px}

.timer{
font-size:28px;
color:yellow;
}

.win{color:#00ff95;font-size:24px}
.loss{color:#ff4d4d;font-size:24px}

.row{
display:flex;
justify-content:space-between;
padding:8px;
border-bottom:1px solid #111;
}

.footer{
position:fixed;
bottom:0;
width:100%;
background:#020617;
padding:10px;
font-size:14px;
}

</style>
</head>

<body>

<div class="header">🎯 WinGo Live DM Pattern</div>

<div class="card">

<div>Current Period</div>
<div id="period">Loading...</div>

<div>Current Result</div>
<div id="result">--</div>

<div>Previous</div>
<div id="previous">--</div>

<div style="margin-top:10px">Next Prediction</div>
<div id="prediction" class="pred">BIG</div>

<div id="status"></div>

<div style="margin-top:10px">Timer</div>
<div id="timer" class="timer">60</div>

</div>

<div class="card">
<h3>History</h3>
<div id="history"></div>
</div>

<div class="footer">
Last Result → <span id="footer">--</span>
</div>

<script>

let t = 60
let lastIssue = ""
let prediction = rand()

function rand(){
return Math.random()>0.5 ? "BIG":"SMALL"
}

function size(n){
return n>=5 ? "BIG":"SMALL"
}

function color(s){
return s=="BIG"?"big":"small"
}

// DM style period
function dmPeriod(){

let d = new Date()

let yyyy = d.getFullYear()
let mm = String(d.getMonth()+1).padStart(2,'0')
let dd = String(d.getDate()).padStart(2,'0')

let totalMin = Math.floor(d.getTime()/60000)
let round = String(totalMin%1000).padStart(3,'0')

return `${yyyy}${mm}${dd}10001${round}`
}

function timer(){

setInterval(()=>{

t--

if(t<=0){
t=60
load()
prediction = rand()
document.getElementById("prediction").innerText = prediction
}

document.getElementById("timer").innerText = t

},1000)

}

function load(){

fetch("https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json?ts="+Date.now())
.then(r=>r.json())
.then(d=>{

let list = d.data.list

let cur = list[0]
let prev = list[1]

let curSize = size(parseInt(cur.number))
let prevSize = size(parseInt(prev.number))

document.getElementById("period").innerText = dmPeriod()

document.getElementById("result").innerHTML =
`<span class="${color(curSize)}">${curSize}</span>`

document.getElementById("previous").innerHTML =
prev.issueNumber+" → <span class='"+color(prevSize)+"'>"+prevSize+"</span>"

document.getElementById("footer").innerText =
prev.issueNumber+" → "+prevSize

// win loss
if(lastIssue != cur.issueNumber){

if(curSize == prediction){
document.getElementById("status").innerHTML="<div class='win'>WIN</div>"
}else{
document.getElementById("status").innerHTML="<div class='loss'>LOSS</div>"
}

addHistory(cur.issueNumber,curSize)

lastIssue = cur.issueNumber

}

})

}

function addHistory(issue,res){

let box = document.getElementById("history")

let div = document.createElement("div")
div.className="row"

div.innerHTML =
`<div>${issue}</div><div class="${color(res)}">${res}</div>`

box.prepend(div)

}

document.getElementById("prediction").innerText = prediction

timer()
load()

</script>

</body>
</html>
