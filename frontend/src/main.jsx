import React, {useState, useEffect} from "react";
import {createRoot} from "react-dom/client";
import {FileSearch, Upload, Sparkles, ShieldCheck, Target, AlertCircle, CheckCircle2, History, ArrowRight} from "lucide-react";
import "./style.css";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const PUBLIC_DEMO = import.meta.env.VITE_PUBLIC_DEMO === "true";
function App(){
  const [resume,setResume]=useState("");
  const [job,setJob]=useState("");
  const [title,setTitle]=useState("");
  const [save,setSave]=useState(false);
  const [result,setResult]=useState(null);
  const [history,setHistory]=useState([]);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  const refresh=()=>fetch(API+"/api/history").then(r=>r.ok?r.json():[]).then(setHistory).catch(()=>{});
  useEffect(()=>{ if(!PUBLIC_DEMO) refresh(); },[]);
  async function clearHistory(){
    setError("");
    try {
      const response=await fetch(API+"/api/history",{method:"DELETE"});
      if(!response.ok)throw Error("Could not clear history.");
      setHistory([]);
    }catch(err){setError(err.message)}
  }
  async function upload(e){
    const file=e.target.files?.[0]; if(!file)return;
    if(file.size > 2*1024*1024){setError("File is too large (2 MB limit).");return;}
    setError("");setBusy(true);setResult(null);
    try{
      const data=new FormData();data.append("file",file);
      const response=await fetch(API+"/api/extract",{method:"POST",body:data});
      const body=await response.json();
      if(!response.ok)throw Error(body.detail||"Upload failed");
      setResume(body.text);
    }catch(err){setError(err.message)}finally{setBusy(false)}
  }
  async function submit(e){
    e.preventDefault();setBusy(true);setError("");setResult(null);
    try{
      const response=await fetch(API+"/api/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({resume_text:resume,job_description:job,job_title:title||"Untitled role",save})});
      const body=await response.json();
      if(!response.ok)throw Error(typeof body.detail==="string"?body.detail:"Analysis failed");
      setResult(body);if(save)refresh();
    }catch(err){setError(err.message+" — Check that the backend is running.")}finally{setBusy(false)}
  }
  return <div className="shell">
    <aside className="sidebar"><div className="brand"><div className="brand-icon"><FileSearch size={23}/></div><span>resume<span className="accent">lens</span><small>CAREER INTELLIGENCE</small></span></div>
      <div className="navitem selected"><Target size={17}/> Resume analysis</div>
      <div className="navitem"><History size={17}/> Recent analyses</div>
      <div className="sidebar-bottom"><ShieldCheck size={17}/> Private by default <p>{PUBLIC_DEMO ? "Public demo: use sample documents. History is disabled." : "Documents are processed by your configured backend. History saving is optional."}</p></div>
    </aside>
    <main className="content">
      <header><span className="eyebrow">WORKSPACE / ANALYSIS</span><div className="topright"><span className="statusdot"/> {PUBLIC_DEMO ? "PUBLIC DEMO" : "LOCAL WORKSPACE"}</div></header>
      <section className="hero"><div className="pill"><Sparkles size={13}/> RESUME INTELLIGENCE</div><h1>Make your experience<br/><em>stand out.</em></h1><p>Compare your resume to a job description, find skill gaps, and get practical suggestions to sharpen your application.</p></section>
      <form onSubmit={submit}><div className="inputgrid">
        <div className="panel"><div className="panelhead"><span className="step">01</span><div><h2>Your resume</h2><p>Paste your experience or upload a document.</p></div></div>
          <label className="upload"><Upload size={17}/> Upload PDF, DOCX, or TXT <input type="file" accept=".pdf,.docx,.txt" onChange={upload} disabled={busy} hidden/></label>
          <textarea maxLength={100000} aria-label="Resume text" placeholder="Paste your resume here..." value={resume} onChange={e=>setResume(e.target.value)}/><div className="charcount">{resume.length.toLocaleString()} characters</div></div>
        <div className="panel"><div className="panelhead"><span className="step">02</span><div><h2>Target role</h2><p>Add the job you're applying for.</p></div></div>
          <input aria-label="Job title" maxLength={200} className="titleinput" placeholder="Job title (e.g. Junior Python Developer)" value={title} onChange={e=>setTitle(e.target.value)}/>
          <textarea maxLength={100000} aria-label="Job description" placeholder="Paste the full job description here..." value={job} onChange={e=>setJob(e.target.value)}/><div className="charcount">{job.length.toLocaleString()} characters</div></div>
      </div>
      <div className="actionbar">{PUBLIC_DEMO ? <span>Public demo · history disabled</span> : <label className="check"><input type="checkbox" checked={save} onChange={e=>setSave(e.target.checked)}/> Save results to local history</label>}<button disabled={busy||!resume.trim()||!job.trim()}>{busy?"Working...":"Analyze match"} <ArrowRight size={17}/></button></div></form>
      {error&&<div className="error" role="alert"><AlertCircle size={18}/>{error}</div>}
      {result&&<section className="results"><div className="resultsheader"><div><span className="eyebrow">ANALYSIS COMPLETE</span><h2>Your match breakdown</h2></div><div className="score"><strong>{result.score===null?"N/A":`${result.score}%`}</strong><span>{result.score_label}</span><small>{result.coverage?.matched} of {result.coverage?.recognized} recognized requirements mentioned</small></div></div><div className="resultsgrid">
        <div className="resultcard"><h3><CheckCircle2 size={18}/> Matching skills</h3><div className="tags">{result.matched_skills.length?result.matched_skills.map(s=><span className="tag good" key={s}>{s}</span>):<p>No recognized matching skills</p>}</div></div>
        <div className="resultcard"><h3><AlertCircle size={18}/> Potential gaps</h3><div className="tags">{result.missing_skills.length?result.missing_skills.map(s=><span className="tag missing" key={s}>{s}</span>):<p>No gaps found in our skill dictionary</p>}</div></div>
      </div><div className="resultcard evidence"><h3><Target size={18}/> Requirement evidence</h3>{result.requirements?.length ? result.requirements.map((r,i)=><div className="evidencerow" key={i}><div><strong>{r.skill}</strong><span className={r.status==="mentioned"?"tag good":"tag missing"}>{r.status==="mentioned"?"Mentioned":"Not found"}</span><small>{r.priority}</small></div><p><b>Job:</b> {r.job_evidence||"Recognized requirement"}</p><p><b>Resume:</b> {r.resume_evidence||"No matching mention detected"}</p></div>) : <p>No requirements recognized. Try a more detailed job posting.</p>}</div><div className="resultcard tips"><h3><Sparkles size={18}/> Recommendations</h3>{result.suggestions.map((s,i)=><p key={i}><span>{String(i+1).padStart(2,"0")}</span>{s}</p>)}</div><p className="disclaimer">{result.method} A missing mention does not mean you lack the skill.</p></section>}
      {!PUBLIC_DEMO && <section className="history"><div><span className="eyebrow">YOUR WORKSPACE</span><h2>Recent analyses</h2></div>{history.length>0&&<button type="button" onClick={clearHistory}>Clear saved history</button>}{history.length?<div className="historylist">{history.map(h=><div className="historyrow" key={h.id}><span>{h.job_title}<small>{new Date(h.created_at).toLocaleString()}</small></span><strong>{h.score===null?"N/A":`${h.score}%`}</strong></div>)}</div>:<div className="empty">Saved analyses will appear here when you enable local history.</div>}</section>}
      <footer>ResumeLens · Built with React + FastAPI · Local-first portfolio project</footer>
    </main>
  </div>
}
createRoot(document.getElementById("root")).render(<App/>);
