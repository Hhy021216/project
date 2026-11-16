import {ConversationGate} from './core.js';
import {readConversation,currentIdentity,capturePaneState,hasPaneTransition,readerDiagnostics,CHAT_ITEM_SELECTOR} from './reader.js';

if(!document.getElementById('boss-eq-assistant'))await mount();
async function mount(){
 const host=document.createElement('div');host.id='boss-eq-assistant';
 host.style.cssText=`position:fixed;width:372px;left:${Math.max(10,innerWidth-392)}px;top:90px;z-index:2147483600`;
 const shadow=host.attachShadow({mode:'open'});
 const css=document.createElement('link');css.rel='stylesheet';css.href=chrome.runtime.getURL('panel.css');
 const cssReady=new Promise(resolve=>{css.onload=resolve;css.onerror=resolve;});shadow.append(css);
 const shell=document.createElement('section');shell.id='shell';shell.setAttribute('aria-label','BOSS 高情商回复助手');
 // Static, developer-owned markup only. All chat/model text is assigned through textContent.
 shell.innerHTML=`<header><div id="drag" tabindex="0" role="button" aria-label="移动回复浮窗，可用方向键移动"><span class="subtitle">只辅助，不代发</span>高情商回复助手</div><button id="settings" title="打开设置">设置</button><button id="fold" aria-expanded="true" title="折叠浮窗">收起</button></header><div id="body"><div id="chatlabel">正在识别当前会话……</div><div id="scope">只读取当前页面已加载的文字消息</div><div class="read-row"><span id="readtime">尚未读取</span><button id="refresh">重新读取</button></div><details><summary>查看本次读取的聊天</summary><pre id="preview">等待读取</pre></details><label class="consent"><input id="consent" type="checkbox"><span>允许将当前会话、我的项目经历和参考话术发送给所选模型服务（可能计费）。</span></label><button id="generate" disabled>生成 3 条候选回复</button><p id="status" role="status" aria-live="polite"></p><div id="replies"><div class="empty">先读取会话，再选择适合你的回复。<br>不会自动填入或发送聊天消息。</div></div><details class="manual"><summary>未读到消息？手动粘贴当前聊天</summary><p class="hint">仅在当前会话身份已识别时可用；切换会话会自动清空。请标明“招聘方 / 我”。</p><label for="manual">当前会话文字</label><textarea id="manual" maxlength="24000" placeholder="招聘方：您好，会 Milvus 吗？"></textarea><button id="manual-use">使用这段手动上下文</button></details><footer>技术问题积极回应；请核实技能与所有承诺后复制。<div id="move"><span>移动位置</span><button id="move-left" aria-label="向左移动">左</button><button id="move-up" aria-label="向上移动">上</button><button id="move-down" aria-label="向下移动">下</button><button id="move-right" aria-label="向右移动">右</button><button id="reset">靠右</button></div></footer></div>`;
 shadow.append(shell);document.documentElement.append(host);
 const $=id=>shadow.getElementById(id),gate=new ConversationGate();
 let config={configured:false,projectReady:false,provider:'qwen'},busy=false,serial=0,lastIdentity='',transition=false,timer,manualSnapshot=null,manualPaneStamp='',ticketRendered=null,confirmedPane=[],transitionStarted=0,transitionBlocked=false;
 const diagnose=document.createElement('button');diagnose.id='diagnose';diagnose.textContent='复制读取诊断';$('refresh').after(diagnose);
 diagnose.onclick=async()=>{
  const data={version:chrome.runtime.getManifest().version,...readerDiagnostics(),generation:{configured:!!config.configured,projectReady:!!config.projectReady,consent:$('consent').checked,busy,hasSnapshot:!!gate.snapshot,blockedByTransition:transition},wait:{state:transitionBlocked?'blocked':transition?'waiting':'ready',elapsedMs:transition?Date.now()-transitionStarted:0}};
  try{await navigator.clipboard.writeText(JSON.stringify(data,null,2));status('已复制读取诊断（仅结构和数量，不含聊天正文或密钥），可粘贴给开发者排查。');}catch{status('诊断复制失败，请检查浏览器剪贴板权限。',true);}
 };
 let x=window.innerWidth-392,y=90;
 let docked=false,expandedPosition=null;
 const minimize=document.createElement('button');minimize.id='minimize';minimize.textContent='最小化';minimize.title='收成右侧小矩形';$('settings').after(minimize);
 const dock=document.createElement('button');dock.id='dock';dock.hidden=true;dock.textContent='回复';dock.setAttribute('aria-label','展开高情商回复助手');dock.style.cssText='width:60px;height:36px;background:#087f8c;color:white;border-radius:6px;font-weight:bold';shadow.append(dock);
 minimize.onclick=()=>{expandedPosition={x,y};docked=true;shell.hidden=true;dock.hidden=false;host.style.width='60px';position();dock.focus();};
 dock.onclick=()=>{docked=false;dock.hidden=true;shell.hidden=false;host.style.width='372px';if(expandedPosition){x=expandedPosition.x;y=expandedPosition.y;}position();minimize.focus();};
 function position(save=false){if(docked)x=innerWidth-70;x=Math.max(10,Math.min(x,innerWidth-host.getBoundingClientRect().width-10));y=Math.max(10,Math.min(y,innerHeight-Math.min(host.getBoundingClientRect().height,innerHeight-20)-10));host.style.left=x+'px';host.style.top=y+'px';if(save)send({type:'POSITION',x,y}).catch(()=>{});}
 function status(message,error=false){$('status').textContent=message;$('status').classList.toggle('error',error);}
 async function send(msg){const response=await chrome.runtime.sendMessage(msg);if(!response?.ok)throw new Error(response?.error||'插件连接已断开，请刷新 BOSS 页面');return response.data;}
 function availability(){
  $('generate').disabled=busy||transition||!gate.snapshot||!config.configured||!config.projectReady||!$('consent').checked;
  $('generate').textContent=busy?'正在生成，请稍候……':'生成 3 条候选回复';
  if(!busy&&!transition){
   if(!config.configured)status('生成不可用：请在设置页填写所选模型的 API 密钥并保存。',true);
   else if(!config.projectReady)status('生成不可用：请在设置页上传或粘贴项目经历，并点击保存。',true);
   else if(!gate.snapshot)status('生成不可用：请重新读取当前聊天，确认会话内容。',true);
   else if(!$('consent').checked)status('请先勾选发送当前会话及项目经历给模型服务的授权。');
  }
 }
 function empty(){ticketRendered=null;$('replies').replaceChildren();const e=document.createElement('div');e.className='empty';e.textContent='旧候选已清空。确认当前会话后重新生成。';$('replies').append(e);}
 function invalidate(message,clearManual=true){
  serial++;gate.invalidate();busy=false;empty();if(clearManual){manualSnapshot=null;$('manual').value='';}send({type:'CANCEL'}).catch(()=>{});if(message)status(message);availability();
 }
 function paneSignature(){const s=readConversation();return s?JSON.stringify(s.messages):'';}
 function scan(){
  if(transition)return;
  const identity=currentIdentity();
  if(manualSnapshot&&identity?.id!==manualSnapshot.id){invalidate('会话已切换，请重新读取。');}
  if(manualSnapshot&&paneSignature()!==manualPaneStamp){invalidate('当前聊天已更新，请重新读取或粘贴最新上下文。');}
  const next=manualSnapshot||readConversation();const old=gate.epoch;gate.update(next);
  if(gate.epoch!==old){serial++;busy=false;empty();send({type:'CANCEL'}).catch(()=>{});}
  if(identity)lastIdentity=identity.id;
  if(next){confirmedPane=capturePaneState();$('chatlabel').textContent=next.label;$('scope').textContent=next.scope||'手动提供的当前会话上下文';$('preview').textContent=next.messages.map(m=>(m.role==='self'?'我：':'招聘方：')+m.text).join('\n\n');$('readtime').textContent='读取于 '+new Date().toLocaleTimeString('zh-CN',{hour12:false});}
  else{$('chatlabel').textContent=identity?identity.label+' · 未读到文字':'未能确认当前会话';$('preview').textContent='当前布局未识别或聊天尚未加载，暂不生成，避免串话。';$('readtime').textContent='等待重新读取';}
  availability();
 }
 function beginTransition(){
  transition=true;transitionStarted=Date.now();transitionBlocked=false;invalidate('会话切换中，等待消息区域完成切换；无法确认时可手动粘贴新上下文。');$('chatlabel').textContent='正在重新读取会话……';$('preview').textContent='旧会话内容已清空';availability();
 }
 function settle(){
  // Coalesce rather than debounce: background DOM churn must not starve the readiness check.
  if(timer||!transition)return;
  timer=setTimeout(()=>{
   timer=null;if(!transition)return;
   if(currentIdentity()&&hasPaneTransition(confirmedPane)&&readConversation()){
    transition=false;transitionBlocked=false;manualSnapshot=null;status('已切换会话，候选已清空，请重新生成。');scan();return;
   }
   if(Date.now()-transitionStarted>=8000){
    if(!transitionBlocked){transitionBlocked=true;$('chatlabel').textContent='读取未完成，请重试或诊断';$('readtime').textContent='读取已停止等待';status(currentIdentity()?'未能确认新消息已加载。可粘贴当前聊天，或复制读取诊断。':'当前联系人结构未识别。请复制读取诊断，便于适配当前页面。',true);}
    return;
   }
   settle();
  },200);
 }
 function switchIntent(e){
  const target=e.target instanceof Element?e.target.closest(CHAT_ITEM_SELECTOR):null;
  if(target&&target!==currentIdentity()?.active){beginTransition();settle();}
 }
 document.addEventListener('pointerdown',switchIntent,true);document.addEventListener('click',switchIntent,true);
 document.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' ')switchIntent(e);},true);
 const observer=new MutationObserver(records=>{
  const pane=records.some(r=>(r.target instanceof Element?r.target:r.target.parentElement)?.closest('.chat-conversation,.chat-message-list,.message-list,.chat-record'));
  const identity=currentIdentity();
  if(!transition&&lastIdentity&&identity&&identity.id!==lastIdentity)beginTransition();
  if(pane&&manualSnapshot)invalidate('聊天区域已更新，手动上下文已失效，请重新粘贴。');
  if(transition)settle();else scan();
 });
 observer.observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['class','data-id','data-uid','data-user-id','data-encrypt-id','data-mid']});
 // Poll complements DOM changes (for SPA history changes and virtualization), never merges chats.
 let href=location.href;
 const poll=setInterval(()=>{if(!host.isConnected){observer.disconnect();clearInterval(poll);return;}if(location.href!==href){href=location.href;beginTransition();settle();}else if(!transition)scan();},1000);
 $('refresh').onclick=()=>{if(transition){transitionStarted=Date.now();transitionBlocked=false;$('chatlabel').textContent='正在重新读取会话……';status('正在重试；不会将旧会话消息用于新联系人。');settle();return;}invalidate('正在重新读取……');scan();if(!gate.snapshot)status('未能识别当前联系人或文字消息，请复制读取诊断。',true);};
 $('consent').onchange=availability;
 $('settings').onclick=()=>send({type:'OPEN_OPTIONS'}).catch(e=>status(e.message,true));
 $('fold').onclick=()=>{const folded=!$('body').hidden;$('body').hidden=folded;$('fold').textContent=folded?'展开':'收起';$('fold').setAttribute('aria-expanded',String(!folded));position();};
 let hidden=false;
 chrome.runtime.onMessage.addListener(msg=>{
  if(msg.type==='TOGGLE_PANEL'){hidden=!hidden;host.style.display=hidden?'none':'';if(!hidden)position();}
  if(msg.type==='SETTINGS_CHANGED'){invalidate('设置已更新，请重新生成。');$('consent').checked=false;loadConfig();scan();}
 });
 chrome.storage.onChanged.addListener((_changes,area)=>{if(area==='local')loadConfig();});
 async function loadConfig(){try{config=await send({type:'GET_PUBLIC'});if(!config.configured||!config.projectReady)status('先点“设置”，填写 API 密钥并保存项目经历。');availability();}catch(e){status(e.message,true);}}
 $('manual-use').onclick=()=>{
  const identity=currentIdentity(),value=$('manual').value.trim();if(!identity){status('无法确认当前会话身份，请等待加载或重新读取。',true);return;}
  if(!value){status('请粘贴当前会话文字。',true);return;}
  const messages=value.split(/\n+/).filter(s=>s.trim()).map(line=>({role:/^(我|本人)[：:]/.test(line)?'self':'recruiter',text:line.replace(/^(我|本人|招聘方|HR)[：:]\s*/i,'').trim()}));
  if(messages.length>80||messages.some(m=>m.text.length>6000)){status('请减少上下文，最多 80 条，每条 6000 字。',true);return;}
  transition=false;clearTimeout(timer);timer=null;invalidate('',false);manualSnapshot={id:identity.id,label:identity.label,messages,scope:'手动粘贴内容，请核对确属当前会话'};manualPaneStamp=paneSignature();scan();status('已采用手动上下文；切换会话后会清空。');
 };
 $('generate').onclick=async()=>{
  scan();if($('generate').disabled)return;
  let ticket;try{ticket=gate.begin();}catch(e){status(e.message,true);return;}
  const thisRun=++serial;busy=true;availability();status('正在结合项目经历与当前聊天生成……');empty();
  try{
   const data=await send({type:'GENERATE',snapshot:gate.snapshot,consent:$('consent').checked});scan();
   if(thisRun!==serial||!gate.accepts(ticket))return;
   ticketRendered=ticket;$('replies').replaceChildren();
   data.replies.forEach((r,i)=>{
    const card=document.createElement('article');card.className='reply';const head=document.createElement('div');head.className='reply-head';
    const label=document.createElement('span');label.className='style';label.textContent=`0${i+1}  ${r.style}`;
    const copy=document.createElement('button');copy.className='copy';copy.textContent='复制';copy.setAttribute('aria-label',`复制第 ${i+1} 条回复`);head.append(label,copy);
    const p=document.createElement('p');p.textContent=r.text;card.append(head,p);
    if(r.needsVerification){const w=document.createElement('small');w.className='warning';w.textContent='含待核实技能或承诺，请确认后复制。';card.append(w);}
    if(r.evidence?.length){const detail=document.createElement('details'),summary=document.createElement('summary'),quote=document.createElement('p');summary.textContent='查看项目原文依据';quote.textContent=r.evidence.join('\n');detail.append(summary,quote);card.append(detail);}
    copy.onclick=async()=>{
     scan();if(!gate.accepts(ticket)||ticketRendered!==ticket){status('会话已更新，旧候选不可复制，请重新生成。',true);return;}
     try{await navigator.clipboard.writeText(r.text);copy.textContent='已复制';status('已复制，请自行粘贴到 BOSS 输入框并确认后发送。');}catch{status('剪贴板不可用，请选中候选文字手动复制。',true);}
    };$('replies').append(card);
   });status('已生成 3 条候选，请核实内容后选择复制。');position();
  }catch(e){if(thisRun===serial&&gate.accepts(ticket))status(e.message,true);}
  finally{if(thisRun===serial){busy=false;availability();}}
 };
 let drag;
 $('drag').onpointerdown=e=>{drag={px:e.clientX,py:e.clientY,x,y};$('drag').setPointerCapture(e.pointerId);};
 $('drag').onpointermove=e=>{if(!drag)return;x=drag.x+e.clientX-drag.px;y=drag.y+e.clientY-drag.py;position();};
 $('drag').onpointerup=()=>{drag=null;position(true);};$('drag').onpointercancel=()=>{drag=null;};
 const movements={ArrowLeft:[-30,0],ArrowRight:[30,0],ArrowUp:[0,-30],ArrowDown:[0,30]};
 function move(dx,dy){x+=dx;y+=dy;position(true);}
 $('drag').onkeydown=e=>{if(movements[e.key]){e.preventDefault();move(...movements[e.key]);}};
 for(const [id,delta] of Object.entries({'move-left':[-30,0],'move-right':[30,0],'move-up':[0,-30],'move-down':[0,30]}))$(id).onclick=()=>move(...delta);
 $('reset').onclick=()=>{x=innerWidth-392;y=90;position(true);};window.addEventListener('resize',()=>position());
 await cssReady;await loadConfig();if(config.position){x=config.position.x;y=config.position.y;}position();scan();
}
