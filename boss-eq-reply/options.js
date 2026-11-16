import {PROVIDERS} from './core.js';
import {extractProject} from './documents.js';
const $=id=>document.getElementById(id);let saved={keys:{},models:{}};
function status(message,error=false){$('status').textContent=message;$('status').classList.toggle('error',error);}
async function send(msg){const r=await chrome.runtime.sendMessage(msg);if(!r?.ok)throw new Error(r?.error||'插件连接失败，请重新加载');return r.data;}
function loadProvider(){const p=$('provider').value;$('key').value=saved.keys[p]||'';$('model').value=saved.models[p]||PROVIDERS[p].model;$('endpoint').textContent='官方接口：'+PROVIDERS[p].url;}
function count(){$('count').textContent=$('project').value.length;}
async function initialize(){try{saved=await send({type:'GET_SETTINGS'});$('provider').value=saved.provider||'qwen';$('project').value=saved.project||'';loadProvider();count();}catch(e){status(e.message,true);}}
$('provider').addEventListener('change',loadProvider);
$('project').addEventListener('input',count);
$('reveal').onclick=()=>{const show=$('key').type==='password';$('key').type=show?'text':'password';$('reveal').textContent=show?'隐藏':'显示';$('reveal').setAttribute('aria-pressed',String(show));};
let importVersion=0;
$('upload').onchange=async()=>{const version=++importVersion,file=$('upload').files[0];if(!file)return;status('正在本地读取文档……');$('save').disabled=true;
 try{const value=await extractProject(file);if(version!==importVersion)return;$('project').value=value;count();status('已提取文字，请检查项目经历后点击保存。');}catch(e){if(version===importVersion)status(e.message||'文档解析失败，请粘贴文字',true);}finally{if(version===importVersion){$('save').disabled=false;$('upload').value='';}}};
$('form').onsubmit=async e=>{e.preventDefault();$('save').disabled=true;try{
 const input={type:'SAVE_SETTINGS',provider:$('provider').value,apiKey:$('key').value,model:$('model').value,project:$('project').value};await send(input);saved=await send({type:'GET_SETTINGS'});status('已保存。现在可以打开 BOSS 聊天使用右侧浮窗。');
 }catch(err){status(err.message,true);}finally{$('save').disabled=false;}};
$('test').onclick=async()=>{$('test').disabled=true;status('正在测试官方接口连接……');try{await send({type:'TEST',provider:$('provider').value,apiKey:$('key').value,model:$('model').value});status('连接成功。测试不发送项目经历或聊天内容。');}catch(e){status(e.message,true);}finally{$('test').disabled=false;}};
$('clear').onclick=async()=>{if(!confirm('清空此插件保存的所有 API 密钥、项目经历和浮窗位置？'))return;try{++importVersion;await send({type:'CLEAR'});saved={keys:{},models:{}};$('project').value='';loadProvider();count();status('已清空本地资料。');}catch(e){status(e.message,true);}};
const diagnostic=document.createElement('button');diagnostic.type='button';diagnostic.id='network-diagnostic';diagnostic.textContent='诊断网络（不发送密钥或资料）';diagnostic.className='secondary';$('test').after(diagnostic);
diagnostic.onclick=async()=>{diagnostic.disabled=true;status('正在检测官方接口是否可达，不发送密钥或资料……');try{const r=await send({type:'DIAG_NETWORK',provider:$('provider').value});status(r.status===401?'官方接口可达（HTTP 401：未携带密钥的预期响应）。请再点“测试连接”检查密钥、模型和余额。':`已取得官方接口响应（HTTP ${r.status}），并非完全断网；请再测试密钥和模型。`);}catch(e){status(e.message,true);}finally{diagnostic.disabled=false;}};
initialize();
