/* Run: node examples/check_cellbook_pairs.js <library-root>
 * Standard-library-only finite replay. No network, writes, search or solvers.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
if(process.argv.length!==3)throw Error('Usage: node check_cellbook_pairs.js <library-root>');
const root=path.resolve(process.argv[2]),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'data/cellbook/manifest.json')));
const report=JSON.parse(fs.readFileSync(path.join(root,'data/cellbook/pair-replay.json')));
const reference=path.join(root,'sha256-replay.js'),REFERENCE='a08df68ee8b4a98949d94896486fc04cabad9e71087f3a0719003088a3fa1b8c';
assert.equal(hash(fs.readFileSync(reference)),REFERENCE);assert.equal(report.reference_sha256,REFERENCE);
const H=require(reference),equal=(a,b)=>a.every((v,i)=>v===b[i]);
for(const bytes of [Buffer.alloc(0),Buffer.from('abc'),Buffer.from(Array.from({length:55},(_,i)=>i))]){
 const block=Buffer.alloc(64);bytes.copy(block);block[bytes.length]=128;block.writeBigUInt64BE(BigInt(bytes.length*8),56);
 const words=Array.from({length:16},(_,i)=>block.readUInt32BE(i*4));
 assert.equal(H.compress(words,H.IV,64).output.map(H.hex).join(''),crypto.createHash('sha256').update(bytes).digest('hex'));
}
function words(v,n){if(typeof v==='string')v=v.trim().split(/\s+/);assert(Array.isArray(v)&&v.length===n);return v.map(x=>{if(typeof x==='string'){assert(/^(?:0x)?[0-9a-fA-F]{8}$/.test(x));x=parseInt(x,16);}assert(Number.isInteger(x)&&x>=0&&x<=0xffffffff);return x;});}
const expected=new Map(report.results.map(r=>[r.record_id,r])),seen=new Set(),pairs=new Set();let count=0,standardIV=0;
for(const group of manifest.groups.filter(g=>g.kind==='pair-witness'))for(const pin of group.chunks){
 assert(/^data\/cellbook\/[A-Za-z0-9_.-]+\.json$/.test(pin.url));
 const raw=fs.readFileSync(path.join(root,pin.url));assert.equal(raw.length,pin.bytes);assert.equal(hash(raw),pin.sha256);
 for(const r of JSON.parse(raw)){
  assert(!seen.has(r.id));seen.add(r.id);assert.equal(Number(r.width),32);assert(Number.isInteger(r.rounds)&&r.rounds>=1&&r.rounds<=64);
  const cv=words(r.fields.cv,8),a=words(r.fields.M1,16),b=words(r.fields.M2,16);assert(!equal(a,b));
  const A=H.compress(a,cv,r.rounds),B=H.compress(b,cv,r.rounds);assert(equal(A.state,B.state));assert(equal(A.output,B.output));
  const e=expected.get(r.id);assert(e&&e.state_equal&&e.output_equal);assert.equal(e.rounds,r.rounds);
  const isStandard=equal(cv,H.IV);assert.equal(isStandard,e.standard_iv);standardIV+=Number(isStandard);
  const changed=b.slice();changed[0]=(changed[0]^1)>>>0;assert.equal(equal(A.output,H.compress(changed,cv,r.rounds).output),e.mutated_message_equal);
  const next=r.rounds<64?equal(H.compress(a,cv,r.rounds+1).output,H.compress(b,cv,r.rounds+1).output):null;assert.equal(next,e.next_round_equal);
  pairs.add(JSON.stringify([cv,[a,b].sort((x,y)=>{for(let i=0;i<16;i++)if(x[i]!==y[i])return x[i]-y[i];return 0;})]));count++;
 }
}
assert.equal(count,expected.size);assert.equal(count,report.replayed_record_payloads);assert.equal(pairs.size,report.distinct_unordered_cv_message_pairs);assert.equal(standardIV,report.standard_iv_records);
console.log(JSON.stringify({passed:true,known_answers:3,replayed_records:count,distinct_unordered_cv_message_pairs:pairs.size,standard_iv_records:standardIV,scope:'Saved compression pairs and recorded controls only; no solver, success-rate estimate or attack-cost claim.'}));
