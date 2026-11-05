const form=document.querySelector("#chat-form");
const input=document.querySelector("#message");
const messages=document.querySelector("#messages");
const statusEl=document.querySelector("#status");
const language=document.querySelector("#language");
let history=[];
let busy=false;

function addMessage(text,who){
  const el=document.createElement("article");
  el.className="bubble "+who;
  el.textContent=text;
  messages.appendChild(el);
  messages.scrollTop=messages.scrollHeight;
}
form.addEventListener("submit",async e=>{
  e.preventDefault();
  const message=input.value.trim();
  if(!message||busy)return;
  addMessage(message,"user");
  input.value="";
  busy=true;statusEl.textContent="Thinking…";
  try{
    const res=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message,language:language.value,history})});
    const data=await res.json();
    if(!res.ok)throw new Error(data.detail||"Request failed");
    addMessage(data.reply,"assistant");
    history.push({role:"user",text:message},{role:"model",text:data.reply});
    history=history.slice(-20);
  }catch(err){addMessage("Sorry, the service is unavailable right now. Please try again.","assistant");statusEl.textContent=err.message;}
  finally{busy=false;if(statusEl.textContent==="Thinking…")statusEl.textContent="";}
});
document.querySelector("#new-chat").addEventListener("click",()=>{
  history=[];messages.replaceChildren();addMessage("Hello! నమస్కారం! नमस्ते! How can I help you today?","assistant");statusEl.textContent="";
});
const mic=document.querySelector("#mic");
const SpeechRecognition=window.SpeechRecognition||window.webkitSpeechRecognition;
if(!SpeechRecognition){mic.disabled=true;mic.title="Speech recognition is not supported in this browser";}
else{
  mic.addEventListener("click",()=>{
    const rec=new SpeechRecognition();rec.interimResults=false;rec.maxAlternatives=1;
    rec.lang=({auto:"en-IN",en:"en-IN",te:"te-IN",hi:"hi-IN"})[language.value];
    rec.onstart=()=>statusEl.textContent="Listening…";
    rec.onerror=()=>statusEl.textContent="Microphone unavailable. Check browser permission.";
    rec.onresult=e=>{input.value=e.results[0][0].transcript;form.requestSubmit();};
    rec.onend=()=>{if(statusEl.textContent==="Listening…")statusEl.textContent="";};
    rec.start();
  });
}
