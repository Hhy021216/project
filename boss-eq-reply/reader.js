// shortcut: BOSS DOM is not a public API; unknown layouts fail closed and offer manual context.
export const CHAT_ITEM_SELECTOR='.user-list .friend-content,.user-list li,.user-list .user-item,.user-list .chat-user,.chat-user-list .user-item,.chat-list .chat-item';
// Official chat-new v5575 renders selection on the inner friend-content, not its wrapping li.
const ACTIVE='.user-list .friend-content.selected,.user-list li.selected,.user-list li.active,.user-list .user-item.selected,.user-list .user-item.active,.user-list .chat-user.selected,.user-list .chat-user.active,.user-list [aria-selected="true"],.chat-user-list .user-item.active,.chat-list .chat-item.active,.chat-list .chat-item.selected';
const HEADER='.chat-conversation .user-info-wrap .name-content .name-text,.chat-user-info .name,.chat-info .name,.chat-header .name,.chat-header .user-name,.chat-head .name,.chat-title .name';
const PANES='.chat-conversation,.chat-box .chat-message-list,.chat-box .message-list,.chat-record';
const ITEMS='.message-item,.item-friend,.item-myself';
const LOADING='.chat-conversation[aria-busy="true"],.chat-box [aria-busy="true"],.chat-conversation.loading,.chat-box .loading,.chat-box .loading-mask,.chat-conversation .chat-record .pre-loading';
const visible=el=>!!el&&el.getClientRects().length>0&&getComputedStyle(el).visibility!=='hidden'&&getComputedStyle(el).display!=='none';
const normalize=s=>(s||'').replace(/\s+/g,' ').trim();
const pick=(root,selectors)=>[...root.querySelectorAll(selectors)].find(visible);
function messageItems(root){
 const nodes=[...root.querySelectorAll(ITEMS)].filter(node=>visible(node)&&!node.matches('.item-system'));
 return nodes.filter(node=>!nodes.some(other=>other!==node&&other.contains(node)));
}
function messageValue(item){
 const value=normalize(pick(item,'.message-text,.text,.text-content')?.textContent);
 // Read only a visible resume-card label, never fetch or parse the attachment itself.
 const displayed=normalize(item.innerText);
 if(/点击预览附件简历/.test(displayed))return '[简历附件卡片]'+(value?' '+value:'');
 return value;
}
export function capturePaneState(doc=document){
 const panes=[...doc.querySelectorAll(PANES)].filter(visible),nodes=[...new Set(panes.flatMap(messageItems))];
 return nodes.map(node=>({node,mid:node.getAttribute('data-mid')||'',text:messageValue(node)})).filter(item=>item.text);
}
export function hasPaneTransition(before,doc=document){
 const after=capturePaneState(doc);if(!after.length)return false;
 if(pick(doc,LOADING))return false;
 if(!before?.length)return true;
 // Equal words do not mean equal conversations. Track replaced nodes or changed message IDs.
 return !before.some(old=>after.some(now=>
  old.mid&&now.mid ? old.mid===now.mid : now.node===old.node&&now.text===old.text
 ));
}
function activeIdentity(doc){
 const list=[...new Set([...doc.querySelectorAll(ACTIVE)].filter(visible).map(node=>node.matches('.friend-content')?node:pick(node,'.friend-content')||node.closest(CHAT_ITEM_SELECTOR)||node))];if(list.length!==1)return null;
 const active=list[0];
 const name=normalize(pick(active,'.name,.user-name,.geek-name,.name-text')?.textContent);
 const header=normalize(pick(doc,HEADER)?.textContent);
 // A switched list with a stale header is not a loaded new conversation.
 if(!name||!header||name!==header)return null;
 const attributes=['data-id','data-uid','data-user-id','data-encrypt-id'].map(k=>active.getAttribute(k)||'');
 const contact=normalize(pick(active,'.name-box')?.textContent)||name;
 // Vue may recreate a row on every message. DOM allocation is not contact identity.
 if(!attributes.some(Boolean)){
  const candidates=[...new Set([...doc.querySelectorAll(CHAT_ITEM_SELECTOR)].filter(visible).map(node=>node.matches('.friend-content')?node:pick(node,'.friend-content')||node.closest(CHAT_ITEM_SELECTOR)||node))];
  const duplicates=candidates.filter(node=>(normalize(pick(node,'.name-box')?.textContent)||normalize(pick(node,'.name,.user-name,.geek-name,.name-text')?.textContent))===contact);
  if(duplicates.length!==1)return null;
 }
 return {id:JSON.stringify([attributes,contact]),label:header,active};
}
export function currentIdentity(doc=document){return activeIdentity(doc);}
export function readConversation(doc=document){
 const identity=activeIdentity(doc);if(!identity)return null;
 if(pick(doc,LOADING))return null;
 const roots=[...doc.querySelectorAll(PANES)].filter(visible);
 // Nested alternative selectors refer to the same pane; prefer the deepest root.
 const panes=roots.filter(r=>!roots.some(other=>other!==r&&r.contains(other)));if(panes.length!==1)return null;
 const root=panes[0],messages=[];
 for(const item of messageItems(root)){
  if(!visible(item))continue;
  const value=messageValue(item);if(!value)continue;
  let role;
  if(item.matches('.item-myself,.is-self,.right,[data-role="self"]')||pick(item,'.item-myself,[data-role="self"]'))role='self';
  else if(item.matches('.item-friend,.is-friend,.left,[data-role="recruiter"]')||pick(item,'.item-friend,[data-role="recruiter"]'))role='recruiter';
  else return null;
  messages.push({role,text:value});
 }
 if(!messages.length)return null;
 return {id:identity.id,label:identity.label,messages:messages.slice(-80),scope:'当前页面已加载的最近文字及简历卡片（最多 80 条，图片与附件正文未解析）'};
}
export function readerDiagnostics(doc=document){
 const selectors={active:ACTIVE,header:HEADER,panes:PANES,messages:ITEMS,content:'.message-text,.text,.text-content'};
 const describe=node=>({tag:node.tagName.toLowerCase(),classes:[...node.classList].filter(s=>/^[a-zA-Z][a-zA-Z0-9_-]{0,49}$/.test(s)).slice(0,12)});
 const stats=Object.fromEntries(Object.entries(selectors).map(([key,value])=>[key,{total:doc.querySelectorAll(value).length,visible:[...doc.querySelectorAll(value)].filter(visible).length}]));
 // Never include text, names, IDs, attributes, URLs, HTML, API keys or project contents.
 return {identityRecognized:!!currentIdentity(doc),snapshotReadable:!!readConversation(doc),selectors:stats,structure:{active:[...doc.querySelectorAll(ACTIVE)].slice(0,3).map(describe),header:[...doc.querySelectorAll(HEADER)].slice(0,3).map(describe),panes:[...doc.querySelectorAll(PANES)].slice(0,3).map(describe),messages:messageItems(doc).slice(0,6).map(describe)}};
}
