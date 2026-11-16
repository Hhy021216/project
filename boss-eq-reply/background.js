import {PROVIDERS,validateSettings,buildMessages,requestCompletion,probeConnection} from './core.js';

// Content scripts cannot read API keys or project data from chrome.storage.
const ready=chrome.storage.local.setAccessLevel({accessLevel:'TRUSTED_CONTEXTS'});
const requests=new Map();
let configRevision=0,configChanging=0,updateQueue=Promise.resolve();
const optionsURL=chrome.runtime.getURL('options.html');
// Extension options opened in a browser tab can have sender.tab; exact URL/id is the boundary.
const isOptions=sender=>sender.id===chrome.runtime.id&&sender.url===optionsURL;
const isChat=sender=>sender.id===chrome.runtime.id&&sender.tab?.id!=null&&sender.frameId===0&&/^https:\/\/www\.zhipin\.com\//.test(sender.url||'');
async function settings(){await ready;return (await chrome.storage.local.get('settings')).settings||{provider:'qwen',keys:{},models:{},project:''};}
function configured(s){try{validateSettings({provider:s.provider,apiKey:s.keys[s.provider],model:s.models[s.provider]});return true;}catch{return false;}}
async function notifySettingsChanged(){
 for(const c of requests.values())c.abort();requests.clear();
 const tabs=await chrome.tabs.query({url:'https://www.zhipin.com/*'});
 await Promise.all(tabs.map(tab=>chrome.tabs.sendMessage(tab.id,{type:'SETTINGS_CHANGED'}).catch(()=>{})));
}
// Register cancellation BEFORE any asynchronous preparation, not just the remote API call.
function networkTask(key,task){
 if(configChanging)throw new Error('设置正在更新，请稍后重新生成');
 const c=new AbortController(),revision=configRevision;requests.get(key)?.abort();requests.set(key,c);
 const ensureCurrent=()=>{if(c.signal.aborted||revision!==configRevision||configChanging)throw new Error('设置或会话已变更，请重新生成');};
 return (async()=>{
  try{await ready;ensureCurrent();return await task(c,ensureCurrent);}
  catch(e){ensureCurrent();throw e;}
  finally{if(requests.get(key)===c)requests.delete(key);}
 })();
}
function changeSettings(msg){
 configRevision++;configChanging++;for(const c of requests.values())c.abort();requests.clear();
 const operation=updateQueue.then(async()=>{
  await ready;
  if(msg.type==='CLEAR'){await chrome.storage.local.clear();}
  else{
   const c=validateSettings(msg),project=String(msg.project||'').trim();if(!project||project.length>60000)throw new Error('请填写项目经历，最多 60000 字');
   const s=await settings();s.provider=c.provider;s.keys[c.provider]=c.apiKey;s.models[c.provider]=c.model;s.project=project;
   await chrome.storage.local.set({settings:s});
  }
  await notifySettingsChanged();return {};
 });
 updateQueue=operation.catch(()=>{});return operation.finally(()=>{configChanging--;});
}
async function handle(msg,sender){
 if(!msg||(!isOptions(sender)&&!isChat(sender)))throw new Error('不允许的消息来源');
 if(msg.type==='CANCEL'){
  requests.get(sender.tab?.id)?.abort();requests.delete(sender.tab?.id);return {};
 }
 if(['SAVE_SETTINGS','CLEAR'].includes(msg.type)){
  if(!isOptions(sender))throw new Error('此操作仅允许在插件设置页执行');
  return changeSettings(msg);
 }
 if(msg.type==='GENERATE'){
  if(!isChat(sender)||msg.consent!==true)throw new Error('请先确认发送当前会话和项目经历给模型服务');
  return networkTask(sender.tab.id,async(c,ensure)=>{
   const s=await settings();ensure();
   const ref=await (await fetch(chrome.runtime.getURL('reference.json'),{signal:c.signal})).json();ensure();
   const messages=buildMessages({project:s.project,reference:ref.documents.map(d=>d.title+'\n'+d.text).join('\n\n'),snapshot:msg.snapshot});
   ensure();const replies=await requestCompletion({provider:s.provider,apiKey:s.keys[s.provider],model:s.models[s.provider],project:s.project,contextState:JSON.parse(messages[1].content).contextState},messages,fetch,c.signal);ensure();return {replies};
  });
 }
 if(msg.type==='DIAG_NETWORK'){
  if(!isOptions(sender))throw new Error('此操作仅允许在插件设置页执行');
  return networkTask('diag:'+String(sender.documentId||sender.tab?.id||'options'),async(c,ensure)=>{const result=await probeConnection(msg.provider,fetch,c.signal);ensure();return result;});
 }
 if(msg.type==='TEST'){
  if(!isOptions(sender))throw new Error('此操作仅允许在插件设置页执行');
  return networkTask('test:'+String(sender.documentId||sender.tab?.id||'options'),async(c,ensure)=>{
   const input=validateSettings(msg);ensure();await requestCompletion(input,[{role:'system',content:'只返回 JSON: {"replies":[{"text":"连接成功一","needsVerification":false},{"text":"连接成功二","needsVerification":false},{"text":"连接成功三","needsVerification":false}]}'},{role:'user',content:'测试 JSON 连接'}],fetch,c.signal);ensure();return {};
  });
 }
 await ready;
 if(msg.type==='OPEN_OPTIONS'){await chrome.runtime.openOptionsPage();return {};}
 if(msg.type==='GET_PUBLIC'){const s=await settings();const ui=(await chrome.storage.local.get('position')).position;return {provider:s.provider,configured:configured(s),projectReady:!!s.project?.trim(),position:ui};}
 if(msg.type==='POSITION'){
  if(!Number.isFinite(msg.x)||!Number.isFinite(msg.y))throw new Error('位置无效');
  await chrome.storage.local.set({position:{x:Math.max(0,Math.min(msg.x,10000)),y:Math.max(0,Math.min(msg.y,10000))}});return {};
 }
 if(!isOptions(sender))throw new Error('此操作仅允许在插件设置页执行');
 if(msg.type==='GET_SETTINGS')return await settings();
 throw new Error('未知操作');
}
chrome.runtime.onMessage.addListener((msg,sender,respond)=>{
 handle(msg,sender).then(data=>respond({ok:true,data}),e=>respond({ok:false,error:e.message}));return true;
});
chrome.action.onClicked.addListener(async tab=>{
 if(tab.id&&/^https:\/\/www\.zhipin\.com\//.test(tab.url||'')){
  try{await chrome.tabs.sendMessage(tab.id,{type:'TOGGLE_PANEL'});}catch{await chrome.runtime.openOptionsPage();}
 }else await chrome.runtime.openOptionsPage();
});
chrome.tabs.onRemoved.addListener(id=>{requests.get(id)?.abort();requests.delete(id);});
chrome.runtime.onInstalled.addListener(async details=>{await ready;if(details.reason==='install')await chrome.runtime.openOptionsPage();});
