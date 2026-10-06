const $=i=>document.getElementById(i);
let phoneStream=null,usePhone=false,facing="environment";

async function startPhoneCamera(){
  try{
    if(phoneStream) phoneStream.getTracks().forEach(t=>t.stop());
    phoneStream=await navigator.mediaDevices.getUserMedia({
      video:{facingMode:{ideal:facing},width:{ideal:1920},height:{ideal:1080}},
      audio:false
    });
    $("phoneCam").srcObject=phoneStream;
    $("phoneCam").style.display="block";
    $("feed").style.display="none";
    usePhone=true;
    $("cameraStart").textContent="📷 PHONE CAMERA ON";
  }catch(e){
    $("net").textContent="CAMERA PERMISSION ERROR";
    alert("Nexus needs camera permission. On iPhone, allow Camera access for this website, then try again.");
  }
}
async function flipCamera(){
  facing=facing==="environment"?"user":"environment";
  await startPhoneCamera();
}
function usePc(){
  usePhone=false;
  if(phoneStream){phoneStream.getTracks().forEach(t=>t.stop());phoneStream=null;}
  $("phoneCam").style.display="none";
  $("feed").style.display="block";
}
async function c(x){
  try{
    await fetch("/api/command",{method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({cmd:x,enabled:x!=="stop"&&x!=="estop"})});
  }catch(e){$("net").textContent="PC OFFLINE"}
}
$("cameraStart").onclick=startPhoneCamera;
$("flip").onclick=flipCamera;
$("usePc").onclick=usePc;
document.querySelectorAll("[data-c]").forEach(b=>{
  b.onpointerdown=()=>c(b.dataset.c);
  b.onpointerup=()=>c("stop");
  b.onpointerleave=()=>c("stop");
});
$("stop").onclick=()=>c("stop");
$("estop").onclick=()=>c("estop");
$("lock").onclick=()=>{$("ai").textContent="Target lock requested: "+$("target").value;c("lock")};
$("unlock").onclick=()=>c("stop");

setInterval(async()=>{
  try{
    let r=await fetch("/api/state"),s=await r.json();
    $("net").textContent="PC ONLINE";
    $("pos").textContent=`Pan ${s.pan??0}° • Tilt ${s.tilt??90}°`;
  }catch(e){$("net").textContent="PC OFFLINE"}
},700);

// Automatically request the iPhone rear camera when the user first taps Start.
