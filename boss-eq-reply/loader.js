// Dynamic module imports run in Chrome's isolated content-script world.
import(chrome.runtime.getURL('panel.js')).catch(()=>console.warn('BOSS 回复助手加载失败，请刷新页面或重新加载插件。'));
