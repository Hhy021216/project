const MAX_FILE=8*1024*1024,MAX_XML=4*1024*1024;
async function unzipDocument(buffer){
 const view=new DataView(buffer),bytes=new Uint8Array(buffer);let end=-1;
 for(let i=bytes.length-22;i>=Math.max(0,bytes.length-65557);i--)if(view.getUint32(i,true)===0x06054b50){end=i;break;}
 if(end<0)throw new Error('DOCX 文件损坏或不是有效的 Word 文档');
 if(view.getUint16(end+4,true)||view.getUint16(end+6,true))throw new Error('不支持分卷 DOCX');
 const entries=view.getUint16(end+10,true);let offset=view.getUint32(end+16,true);
 if(entries>4096||offset>=bytes.length)throw new Error('DOCX 目录异常');
 for(let i=0;i<entries;i++){
  if(offset+46>bytes.length||view.getUint32(offset,true)!==0x02014b50)throw new Error('DOCX 目录损坏');
  const flag=view.getUint16(offset+8,true),method=view.getUint16(offset+10,true),compressed=view.getUint32(offset+20,true),size=view.getUint32(offset+24,true),n=view.getUint16(offset+28,true),extra=view.getUint16(offset+30,true),comment=view.getUint16(offset+32,true),local=view.getUint32(offset+42,true);
  if(offset+46+n+extra+comment>bytes.length)throw new Error('DOCX 目录越界');
  const name=new TextDecoder().decode(bytes.subarray(offset+46,offset+46+n));offset+=46+n+extra+comment;
  if(name!=='word/document.xml')continue;
  if(flag&1)throw new Error('请先解除 Word 文档密码');
  if(size>MAX_XML||compressed>MAX_FILE||local+30>bytes.length||view.getUint32(local,true)!==0x04034b50)throw new Error('DOCX 正文过大或损坏');
  const start=local+30+view.getUint16(local+26,true)+view.getUint16(local+28,true);
  if(start+compressed>bytes.length)throw new Error('DOCX 正文越界');
  const data=bytes.subarray(start,start+compressed);let output;
  if(method===0)output=data;
  else if(method===8){
   const reader=new Blob([data]).stream().pipeThrough(new DecompressionStream('deflate-raw')).getReader();const chunks=[];let length=0;
   try{while(true){const part=await reader.read();if(part.done)break;length+=part.value.length;if(length>MAX_XML){await reader.cancel();throw new Error('DOCX 解压正文过大');}chunks.push(part.value);}}finally{reader.releaseLock();}
   output=new Uint8Array(length);let at=0;for(const chunk of chunks){output.set(chunk,at);at+=chunk.length;}
  }else throw new Error('不支持此 DOCX 压缩方式，请另存为标准 DOCX');
  if(output.length!==size)throw new Error('DOCX 正文长度异常');return new TextDecoder('utf-8',{fatal:true}).decode(output);
 }
 throw new Error('DOCX 缺少正文，请导出为标准 Word 文档');
}
export async function extractProject(file){
 if(!file||file.size>MAX_FILE)throw new Error('文件不能超过 8 MB');
 const ext=file.name.split('.').pop().toLowerCase();let result;
 if(ext==='docx'){
  const xml=await unzipDocument(await file.arrayBuffer());
  if(/<!DOCTYPE|<!ENTITY/i.test(xml))throw new Error('不接受包含自定义实体的 DOCX');
  const doc=new DOMParser().parseFromString(xml,'application/xml');if(doc.querySelector('parsererror'))throw new Error('DOCX 正文解析失败');
  const ns='http://schemas.openxmlformats.org/wordprocessingml/2006/main';
  result=[...doc.getElementsByTagNameNS(ns,'p')].map(p=>[...p.getElementsByTagNameNS(ns,'t')].map(n=>n.textContent).join('')).filter(Boolean).join('\n');
 }else if(['txt','md'].includes(ext))result=new TextDecoder('utf-8',{fatal:true}).decode(await file.arrayBuffer());
 else throw new Error('请上传 DOCX、UTF-8 TXT 或 Markdown 文件');
 result=result.replace(/\r\n/g,'\n').trim();
 if(!result)throw new Error('文档没有可读取文字，扫描图片请先转为文字');
 if(result.length>60000)throw new Error('项目内容超过 60000 字，请只保留简历中的项目经历');
 return result;
}
